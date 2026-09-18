"""AI 对话、剧情流式交互与会话管理领域服务。

负责管理用户与角色之间的 ChatSession、DAG 剧情分支、消息落库、
Prompt 组装、SSE 流式下发与 CSO 金融级 Token 扣费审计。

Usage:
    >>> from app.services.chat_service import ChatService
    >>> session = await ChatService.get_or_create_session(db, user_id, character_id)
    >>> async for sse_chunk in ChatService.send_message_stream(db, user_id, session.id, payload):
    >>>     print(sse_chunk)
"""

import json
import logging
import re
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified

from datetime import datetime
from app.models.character import Character
from app.models.chat import (
    ChatControlPanel,
    ChatMessage,
    ChatNarrativeState,
    ChatSession,
    StoryBranch,
)
from app.models.user import UserProfile, UserWallet
from app.schemas.chat import (
    ChatMessageDTO,
    ChatSessionListItemDTO,
    ChatSessionResponse,
    ControlPanelDTO,
    ForkSessionRequest,
    NarrativeStateDTO,
    SendMessageRequest,
    StoryBranchDTO,
)
from app.services.llm_gateway import llm_gateway
from app.services.wallet_service import WalletService
from app.core.prompts import FIXED_CHARACTER_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class ChatService:
    """AI 对话与剧情树核心服务。"""

    @classmethod
    async def clean_ai_text(
        cls,
        text: str,
        character: Character | None = None,
        user_id: uuid.UUID | None = None,
        db: AsyncSession | None = None,
        tavern_preset: Any | None = None,
        placement: int = 2,
        model_id: str | None = None,
    ) -> str:
        """清洗 AI 文本（开场白或大模型输出消息）。

        依次执行:
        1. 酒馆专属/全局预设正则流水线 (Placement 2 & 999)
        2. 角色卡私有正则脚本流水线 (extensions.regex_scripts)
        3. 酒馆高级格式化流水线 (Advanced Formatting 多余换行、修剪不完整句等)

        Usage:
            >>> cleaned = await ChatService.clean_ai_text(greeting, character, user_id, db, model_id="deepseek-chat")
        """
        if not text:
            return ""

        from app.services.tavern_service import TavernService
        from app.schemas.tavern import TavernRegexScript

        cleaned = text

        # 1. 尝试获取模型专属或全局预设
        if tavern_preset is None and db is not None:
            try:
                tavern_preset = await TavernService.get_preset_for_model(model_id=model_id, db=db)
            except Exception as err:
                logger.warning("[Tavern] 获取预设异常: %s", err)
                tavern_preset = None

        # 2. 执行预设正则脚本
        if tavern_preset and tavern_preset.is_active and tavern_preset.regex_scripts:
            cleaned = TavernService.execute_regex_scripts(
                text=cleaned,
                scripts=tavern_preset.regex_scripts,
                placement=placement,
            )

        # 3. 执行角色专属私有正则脚本
        if character:
            char_ext = character.extensions or {}
            char_regex_list = char_ext.get("regex_scripts")
            if char_regex_list and isinstance(char_regex_list, list):
                try:
                    parsed_scripts = [
                        TavernRegexScript(**s) if isinstance(s, dict) else s
                        for s in char_regex_list
                    ]
                    cleaned = TavernService.execute_regex_scripts(
                        text=cleaned,
                        scripts=parsed_scripts,
                        placement=placement,
                    )
                except Exception as reg_err:
                    logger.warning("执行角色私有正则脚本异常: %s", reg_err)

        # 4. 执行酒馆高级格式化文本清洗
        if tavern_preset and getattr(tavern_preset, "advanced_formatting", None):
            cleaned = TavernService.clean_output_text(
                text=cleaned,
                formatting=tavern_preset.advanced_formatting,
            )

        # 5. 平台级沉浸与安全兜底清洗:
        # 彻底移除残留的底层变量定义块 (<initvar>, <UpdateVariable>)、状态机增量标签 (<narrative_delta>) 与未被正则捕获的插件占位符 (<SceneHeaderPlaceHolder/>, <StatusPlaceHolderImpl/>)
        cleaned = re.sub(r"<narrative_delta>[\s\S]*?</narrative_delta>", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<initvar>[\s\S]*?</initvar>", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<UpdateVariable>[\s\S]*?</UpdateVariable>", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<(?:SceneHeaderPlaceHolder|StatusPlaceHolderImpl)\s*/?>", "", cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()

        return cleaned

    @classmethod
    def extract_and_strip_narrative_delta(cls, text: str) -> tuple[str, dict[str, Any] | None]:
        """提取大模型回复末尾的叙梦增量状态，并彻底从正文中切除所有 JSON/Tag 结构。

        支持三种形态兼容：
        1. <narrative_delta>...</narrative_delta> (标准标签)
        2. ```json ... ``` (Markdown 代码块包裹的增量 JSON)
        3. 末尾裸 JSON 字典 {"new_event": ...} / {"date_text": ...} / {"player_states": ...} 等。

        Returns:
            tuple[str, dict[str, Any] | None]: (彻底净化后的正文, 解析出的增量字典)
        """
        if not text:
            return "", None

        delta_obj: dict[str, Any] | None = None
        cleaned_text = text

        # 1. 优先尝试从 <narrative_delta> 提取
        tag_match = re.search(r"<narrative_delta>([\s\S]*?)</narrative_delta>", cleaned_text, flags=re.IGNORECASE)
        if tag_match:
            raw_json = tag_match.group(1).strip()
            if raw_json.startswith("```json"):
                raw_json = raw_json[7:]
            if raw_json.startswith("```"):
                raw_json = raw_json[3:]
            if raw_json.endswith("```"):
                raw_json = raw_json[:-3]
            try:
                delta_obj = json.loads(raw_json.strip())
            except Exception as err:
                logger.warning("[Narrative Delta] Tag JSON 解析异常: %s | 原文: %s", err, raw_json)

        # 剔除 <narrative_delta> 标签（无论闭合与否）
        cleaned_text = re.sub(r"<narrative_delta>[\s\S]*?</narrative_delta>", "", cleaned_text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"<narrative_delta>[\s\S]*?$", "", cleaned_text, flags=re.IGNORECASE)

        # 2. 若未提取到，尝试检测末尾的 ```json ... ``` 代码块
        if not delta_obj:
            codeblock_match = re.search(r"```(?:json)?\s*(\{[\s\S]*?\})\s*```\s*$", cleaned_text, flags=re.IGNORECASE)
            if codeblock_match:
                raw_block = codeblock_match.group(1).strip()
                try:
                    parsed = json.loads(raw_block)
                    if isinstance(parsed, dict) and any(
                        k in parsed for k in (
                            "new_event", "history_events", "player_states", "variables",
                            "location", "date_text", "time_text", "tasks", "consumables", "social_relations"
                        )
                    ):
                        delta_obj = parsed
                        cleaned_text = cleaned_text[:codeblock_match.start()].strip()
                except Exception:
                    pass

        # 3. 若仍未提取到，尝试检测末尾的裸 JSON 对象 { "new_event": ... }
        if not delta_obj:
            bare_json_match = re.search(
                r"(\{\s*\"(?:new_event|history_events|player_states|variables|location|date_text|time_text|tasks|consumables|social_relations)\"[\s\S]*\})\s*$",
                cleaned_text,
            )
            if bare_json_match:
                raw_bare = bare_json_match.group(1).strip()
                try:
                    parsed = json.loads(raw_bare)
                    if isinstance(parsed, dict):
                        delta_obj = parsed
                        cleaned_text = cleaned_text[:bare_json_match.start()].strip()
                except Exception:
                    pass

        # 4. 防御性全面二次切除：无论是否成功解析为 delta_obj，末尾包含叙梦状态键的 JSON 必须彻底剥离
        cleaned_text = re.sub(
            r"```(?:json)?\s*\{[\s\S]*?\"(?:new_event|history_events|player_states|variables|location|date_text|time_text|tasks|consumables|social_relations)\"[\s\S]*?\}\s*```\s*$",
            "",
            cleaned_text,
            flags=re.IGNORECASE,
        )
        cleaned_text = re.sub(
            r"\{\s*\"(?:new_event|history_events|player_states|variables|location|date_text|time_text|tasks|consumables|social_relations)\"[\s\S]*?\}\s*$",
            "",
            cleaned_text,
            flags=re.IGNORECASE,
        )

        return cleaned_text.strip(), delta_obj


    @classmethod
    async def get_or_create_session(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        character_id: uuid.UUID,
        model_id: str = "mimo-v2.5",
        mode: str = "story",
    ) -> ChatSession:
        """获取用户与目标角色的活跃会话，不存在则初始化新会话与默认主线分支。

        Args:
            db: 异步数据库会话。
            user_id: 当前用户 ID。
            character_id: 对话目标角色 ID。
            model_id: 选用模型标识。
            mode: 对话模式 ("story" / "room")。

        Returns:
            ChatSession: 关联了分支与面板的会话实体。
        """
        # 1. 验证目标角色存在性
        char_stmt = select(Character).where(Character.id == character_id)
        char_res = await db.execute(char_stmt)
        character = char_res.scalar_one_or_none()
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"目标角色不存在 (ID: {character_id})",
            )

        # 2. 查询该用户针对该角色的最新会话
        stmt = (
            select(ChatSession)
            .where(
                ChatSession.user_id == user_id,
                ChatSession.character_id == character_id,
            )
            .options(
                selectinload(ChatSession.branches),
                selectinload(ChatSession.control_panel),
                selectinload(ChatSession.narrative_state),
                selectinload(ChatSession.character),
            )
            .order_by(desc(ChatSession.updated_at))
            .limit(1)
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()

        if session:
            # 自愈已存在的旧会话中可能为空的 narrative_state
            if not session.narrative_state or (
                not session.narrative_state.player_states
                and not session.narrative_state.consumables
                and not session.narrative_state.important_items
                and not session.narrative_state.skills
                and not session.narrative_state.social_relations
                and not session.narrative_state.tasks
            ):
                char = session.character
                char_name = char.name if char else "神秘伙伴"
                loc = (char.scenario.split("。")[0].split("\n")[0][:40] if char and char.scenario else "") or "木叶村残破废墟"
                if not session.narrative_state:
                    session.narrative_state = ChatNarrativeState(session_id=session.id)
                    db.add(session.narrative_state)

                session.narrative_state.date_text = "第一幕 · 初始篇"
                session.narrative_state.time_text = "清晨"
                session.narrative_state.location = loc
                session.narrative_state.present_characters = ["{{user}}", char_name]
                session.narrative_state.player_states = [
                    {"id": 1, "type": "基础属性", "name": "精神状态", "currentVal": 100, "maxVal": "100", "desc": "当前意识清醒，处于最佳探索状态"},
                    {"id": 2, "type": "环境感知", "name": "场景熟悉度", "currentVal": 15, "maxVal": "100", "desc": f"初抵【{loc}】，正在探索四周"}
                ]
                session.narrative_state.consumables = [
                    {"id": 1, "name": "初级体力药水", "count": 2, "type": "消耗品", "effect": "恢复精力", "source": "随身行囊", "desc": "淡蓝色恢复药剂"}
                ]
                session.narrative_state.important_items = [
                    {"id": 1, "owner": "{{user}}", "name": "星辉罗盘", "desc": "指引平行世界命运分歧的神秘罗盘", "importance": "分支剧情信物"}
                ]
                session.narrative_state.skills = [
                    {"id": 1, "name": "命运洞察", "type": "被动感知", "level": "LV.1", "proficiency": "20%", "proficiencyCurrent": 20, "proficiencyMax": 100, "cost": "无", "cooldown": "无", "effect": "敏锐感知剧情中的关键抉择点", "source": "天生觉醒", "status": "已装备", "isEquipped": True}
                ]
                session.narrative_state.social_relations = [
                    {
                        "id": 1,
                        "name": char_name,
                        "relationTag": "初识",
                        "tagColor": "bg-[#F9C86D]",
                        "favorability": 50,
                        "favorBarColor": "bg-[#F9C86D]",
                        "relation": "初次结识的同行者",
                        "location": loc,
                        "attitude": (char.personality if char else "") or "友善",
                        "bodyFeature": (char.description if char else "") or "独特外表",
                        "personality": (char.personality if char else "") or "深邃内敛",
                        "job": "探索同伴",
                        "hobby": "收集回忆",
                        "favorite": "未知",
                        "residence": loc,
                        "otherInfo": (char.description if char else "") or ""
                    }
                ]
                session.narrative_state.tasks = [
                    {
                        "id": 1,
                        "role": "{{user}}",
                        "task": f"与 {char_name} 建立羁绊",
                        "typeTag": "主线",
                        "statusTag": "进行中",
                        "location": loc,
                        "duration": "当前幕",
                        "desc": f"通过深入交谈探寻 {char_name} 隐藏的过去与心愿",
                        "reward": "好感度提升"
                    }
                ]
                session.narrative_state.history_events = [
                    {
                        "id": "d1",
                        "dateText": "第一幕 · 初遇",
                        "eventCount": "1 个事件",
                        "events": [
                            {
                                "id": 1,
                                "time": "清晨",
                                "characters": f"{{user}}, {char_name}",
                                "location": loc,
                                "mood": "探索、期待",
                                "desc": f"在【{loc}】，你与 {char_name} 开启了最初的命运交织。"
                            }
                        ]
                    }
                ]
                await db.commit()
                await db.refresh(session)
            return session

        # 3. 初始化全新会话
        session_id = uuid.uuid4()
        main_branch_id = uuid.uuid4()

        # 创建默认主分支
        main_branch = StoryBranch(
            id=main_branch_id,
            session_id=session_id,
            name="🌿 主线剧情",
            is_main=True,
        )

        # 创建初始会话
        session = ChatSession(
            id=session_id,
            user_id=user_id,
            character_id=character_id,
            current_branch_id=main_branch_id,
            current_model_id=model_id,
            mode=mode,
        )

        # 查询当前用户的昵称（若有）
        user_name_val = "你"
        user_stmt = select(UserProfile).where(UserProfile.user_id == user_id)
        user_profile = (await db.execute(user_stmt)).scalar_one_or_none()
        if user_profile and user_profile.username and user_profile.username.strip():
            user_name_val = user_profile.username.strip()

        # 创建初始主控面板 (默认绑定当前用户真实昵称与角色卡初始 RPG 变量)
        char_ext = getattr(character, "extensions", None) or {}
        init_vars = char_ext.get("variables") or {}
        control_panel = ChatControlPanel(
            session_id=session_id,
            user_name=user_name_val,
            user_persona="",
            custom_prompt="",
            variables=dict(init_vars),
        )

        # 创建初始叙梦面板 (根据角色场景与身份初始化真实状态机)
        loc = (character.scenario.split("。")[0].split("\n")[0][:40] if character.scenario else "") or "木叶村残破废墟"
        narrative_state = ChatNarrativeState(
            session_id=session_id,
            date_text="第一幕 · 初始篇",
            time_text="清晨",
            location=loc,
            present_characters=[user_name_val, character.name],
            player_states=[
                {"id": 1, "type": "基础属性", "name": "精神状态", "currentVal": 100, "maxVal": "100", "desc": "当前意识清醒，处于最佳探索状态"},
                {"id": 2, "type": "环境感知", "name": "场景熟悉度", "currentVal": 15, "maxVal": "100", "desc": f"初抵【{loc}】，正在探索四周"}
            ],
            consumables=[
                {"id": 1, "name": "初级体力药水", "count": 2, "type": "消耗品", "effect": "恢复精力", "source": "随身行囊", "desc": "淡蓝色恢复药剂"}
            ],
            important_items=[
                {"id": 1, "owner": user_name_val, "name": "星辉罗盘", "desc": "指引平行世界命运分歧的神秘罗盘", "importance": "分支剧情信物"}
            ],
            skills=[
                {"id": 1, "name": "命运洞察", "type": "被动感知", "level": "LV.1", "proficiency": "20%", "proficiencyCurrent": 20, "proficiencyMax": 100, "cost": "无", "cooldown": "无", "effect": "敏锐感知剧情中的关键抉择点", "source": "天生觉醒", "status": "已装备", "isEquipped": True}
            ],
            social_relations=[
                {
                    "id": 1,
                    "name": character.name,
                    "relationTag": "初识",
                    "tagColor": "bg-[#F9C86D]",
                    "favorability": 50,
                    "favorBarColor": "bg-[#F9C86D]",
                    "relation": "初次结识的同行者",
                    "location": loc,
                    "attitude": character.personality or "友善",
                    "bodyFeature": character.description or "独特外表",
                    "personality": character.personality or "深邃内敛",
                    "job": "探索同伴",
                    "hobby": "收集回忆",
                    "favorite": "未知",
                    "residence": loc,
                    "otherInfo": character.description or ""
                }
            ],
            tasks=[
                {
                    "id": 1,
                    "role": "{{user}}",
                    "task": f"与 {character.name} 建立羁绊",
                    "typeTag": "主线",
                    "statusTag": "进行中",
                    "location": loc,
                    "duration": "当前幕",
                    "desc": f"通过深入交谈探寻 {character.name} 隐藏的过去与心愿",
                    "reward": "好感度提升"
                }
            ],
            history_events=[
                {
                    "id": "d1",
                    "dateText": "第一幕 · 初遇",
                    "eventCount": "1 个事件",
                    "events": [
                        {
                            "id": 1,
                            "time": "清晨",
                            "characters": f"{{user}}, {character.name}",
                            "location": loc,
                            "mood": "探索、期待",
                            "desc": f"在【{loc}】，你与 {character.name} 开启了最初的命运交织。"
                        }
                    ]
                }
            ],
        )

        db.add_all([session, main_branch, control_panel, narrative_state])

        # 4. 如果角色配置了 first_mes (开场白)，自动插入第一条 AI 问候消息 (经过酒馆与角色私有正则流水线清洗并展开宏)
        if character.first_mes and character.first_mes.strip():
            cleaned_greeting = await cls.clean_ai_text(
                text=character.first_mes.strip(),
                character=character,
                user_id=user_id,
                db=db,
            )
            cleaned_greeting = cleaned_greeting.replace("{{user}}", user_name_val).replace("{{char}}", character.name)
            greeting_msg = ChatMessage(
                id=uuid.uuid4(),
                session_id=session_id,
                branch_id=main_branch_id,
                sender="ai",
                character_name=character.name,
                avatar_url=character.avatar_url,
                content=cleaned_greeting,
                thinking_content="",
                input_tokens=0,
                output_tokens=0,
                parent_message_id=None,
            )
            db.add(greeting_msg)

        await db.commit()

        # 重新加载完整关联
        return await cls.get_session_by_id(db, user_id, session_id)

    @classmethod
    async def get_session_by_id(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> ChatSession:
        """获取指定会话实体（带权限校验与完整关联预加载）。"""
        stmt = (
            select(ChatSession)
            .where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
            )
            .options(
                selectinload(ChatSession.branches),
                selectinload(ChatSession.control_panel),
                selectinload(ChatSession.narrative_state),
                selectinload(ChatSession.character),
            )
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="对话会话不存在或无访问权限",
            )
        return session

    @classmethod
    async def get_session_response(
        cls,
        db: AsyncSession,
        session: ChatSession,
    ) -> ChatSessionResponse:
        """构建强类型的会话详情响应体 (包含当前激活分支的线性消息列表)。"""
        from app.services.tree_service import TreeService

        # 查询当前活跃分支的完整消息链路 (包含递归继承的父分支祖先消息)
        branch_id = session.current_branch_id
        if branch_id:
            messages = await TreeService.get_branch_active_messages(db, session.id, branch_id)
        else:
            msg_stmt = (
                select(ChatMessage)
                .where(ChatMessage.session_id == session.id)
                .order_by(ChatMessage.created_at.asc())
            )
            msg_res = await db.execute(msg_stmt)
            messages = list(msg_res.scalars().all())

        char = session.character
        all_alt_greetings: list[str] = []
        if char:
            if char.first_mes and char.first_mes.strip():
                all_alt_greetings.append(char.first_mes.strip())
            if char.alternate_greetings and isinstance(char.alternate_greetings, list):
                for g in char.alternate_greetings:
                    if isinstance(g, str) and g.strip():
                        all_alt_greetings.append(g.strip())
                    elif isinstance(g, dict) and g.get("greetingText"):
                        all_alt_greetings.append(g["greetingText"].strip())

        return ChatSessionResponse(
            id=session.id,
            character_id=session.character_id,
            character_name=char.name if char else "未知角色",
            character_avatar=char.avatar_url if char else "",
            character_banner=char.banner_url if char else None,
            character_author_note=char.creator_notes if char else "",
            character_prologue_title=char.prologue_title if char else "序幕",
            character_prologue_html=char.prologue_html if char else "",
            character_tags=char.tags if char else [],
            character_alternate_greetings=all_alt_greetings,
            character_extensions=getattr(char, "extensions", None) or {},
            current_branch_id=session.current_branch_id or uuid.uuid4(),
            current_model_id=session.current_model_id or "mimo-v2.5",
            mode=session.mode,  # type: ignore[arg-type]
            branches=[StoryBranchDTO.model_validate(b) for b in session.branches],
            messages=[ChatMessageDTO.model_validate(m) for m in messages],
            created_at=session.created_at,
            updated_at=session.updated_at,
        )

    @classmethod
    async def send_message_stream(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        payload: SendMessageRequest,
    ) -> AsyncGenerator[str, None]:
        """核心 SSE 流式问答生成与持久化引擎。

        流程：
        1. 检查钱包余额 (至少 1 星元)；
        2. 写入用户发言 ChatMessage；
        3. 组装 System Prompt 与上下文历史；
        4. 消费 LLM 流式输出并以 SSE 格式实时推送 (thinking / message)；
        5. 结束时原子扣费、持久化 AI 响应，并推送 usage 与 done 事件。
        """
        # 0. 查询当前大模型是否开启了深度思考 (Reasoning)
        from app.services.llm_service import LLMService
        supports_reasoning = await LLMService.check_model_supports_reasoning(db, payload.model_id)

        # 1. 权限与会话校验
        session = await cls.get_session_by_id(db, user_id, session_id)
        character = session.character
        if not character:
            yield f"event: error\ndata: {json.dumps({'message': '关联角色不存在'})}\n\n"
            return

        # 2. 检查钱包余额
        currency = "moon" if "claude" in payload.model_id.lower() or "o1" in payload.model_id.lower() else "star"
        cost = 1
        wallet_stmt = select(UserWallet).where(UserWallet.user_id == user_id)
        wallet = (await db.execute(wallet_stmt)).scalar_one_or_none()
        if not wallet:
            # 初始化默认钱包
            wallet = UserWallet(user_id=user_id, star_coins=100, moon_gems=50)
            db.add(wallet)
            await db.flush()

        current_balance = wallet.star_coins if currency == "star" else wallet.moon_gems
        if current_balance < cost:
            currency_name = "星元 ★" if currency == "star" else "月华 🌙"
            err_payload = {
                "code": "INSUFFICIENT_BALANCE",
                "message": f"{currency_name}余额不足，请充值后继续沉浸式对话",
            }
            yield f"event: error\ndata: {json.dumps(err_payload, ensure_ascii=False)}\n\n"
            return

        # 3. 写入用户消息 (优先使用客户端预分配的有效 UUID)
        user_msg_id = payload.client_message_id or uuid.uuid4()
        user_msg = ChatMessage(
            id=user_msg_id,
            session_id=session_id,
            branch_id=session.current_branch_id,
            sender="user",
            character_name="你",
            avatar_url=None,
            content=payload.content.strip(),
            thinking_content="",
            input_tokens=len(payload.content),
            output_tokens=0,
            parent_message_id=payload.parent_message_id,
        )
        db.add(user_msg)
        await db.flush()

        # 4. 加载历史上下文与组装 Prompt
        history_stmt = (
            select(ChatMessage)
            .where(
                ChatMessage.session_id == session_id,
                ChatMessage.branch_id == session.current_branch_id,
            )
            .order_by(ChatMessage.created_at.asc())
        )
        history_msgs = (await db.execute(history_stmt)).scalars().all()

        # 注入已激活 Mod 多锚点流水线 (Phase 7: Mod Pipeline)
        try:
            from app.services.mod_service import ModService
            mod_patches = await ModService.get_active_mod_prompt_patches(db, user_id)
        except Exception as mod_err:
            logger.warning("加载 Mod 插桩异常，自动跳过: %s", mod_err)
            from app.schemas.mod import ModPromptPatches
            mod_patches = ModPromptPatches()

        # 组装 System Prompt (多槽位插桩流水线)
        sys_prompt_parts: list[str] = []

        # 槽位 1: Mod 前置系统指令 (越狱/最高规则)
        if mod_patches.system_prefix:
            sys_prompt_parts.extend(mod_patches.system_prefix)

        # 槽位 2: 角色身份与固定执行框架
        sys_prompt_parts.append(f"你是 {character.name}。")
        sys_prompt_parts.append(FIXED_CHARACTER_SYSTEM_PROMPT)

        # 槽位 3: 角色前置插桩 (Mod 与角色自定义 before_char)
        char_ext = getattr(character, "extensions", None) or {}
        before_char_prompt = char_ext.get("before_char")
        if before_char_prompt:
            sys_prompt_parts.append(before_char_prompt)
        if mod_patches.before_char:
            sys_prompt_parts.extend(mod_patches.before_char)

        if character.description:
            sys_prompt_parts.append(f"【角色详细设定与身世背景】：\n{character.description}")
        if character.personality:
            sys_prompt_parts.append(f"【性格特征】：{character.personality}")
        if character.scenario:
            sys_prompt_parts.append(f"【当前场景背景】：{character.scenario}")
        if character.system_prompt:
            sys_prompt_parts.append(f"【核心系统指令】：{character.system_prompt}")
        if character.post_history_instructions:
            sys_prompt_parts.append(f"【输出要求】：{character.post_history_instructions}")
        if character.creator_notes:
            sys_prompt_parts.append(f"【创作者剧情指引与注意事项 (Author's Note)】：\n{character.creator_notes}")

        # 槽位 4: Mod 角色后置插桩
        if mod_patches.after_char:
            sys_prompt_parts.extend(mod_patches.after_char)

        # 槽位 5: Mod 作者注释与场景前缀
        if mod_patches.top_an:
            sys_prompt_parts.extend(mod_patches.top_an)

        # 计算生效的玩家称谓
        # 1. 优先使用当前会话主控面板中保存的 user_name (若非空且不为 "{{user}}")
        # 2. 否则读取当前用户 UserProfile.username
        # 3. 否则兜底为 "你"
        effective_user_name = "你"
        cp = session.control_panel
        if cp and cp.user_name and cp.user_name.strip() and cp.user_name.strip() != "{{user}}":
            effective_user_name = cp.user_name.strip()
        else:
            user_stmt = select(UserProfile).where(UserProfile.user_id == user_id)
            user_prof = (await db.execute(user_stmt)).scalar_one_or_none()
            if user_prof and user_prof.username and user_prof.username.strip():
                effective_user_name = user_prof.username.strip()

        # 注入主控面板 (RPG 变量、玩家人设与自定义指令)
        sys_prompt_parts.append(f"【玩家称谓】：{effective_user_name}")
        if cp:
            if cp.user_persona:
                sys_prompt_parts.append(f"【玩家人设设定】：{cp.user_persona}")
            if cp.custom_prompt:
                sys_prompt_parts.append(f"【用户自定义指令】：{cp.custom_prompt}")
            if cp.variables:
                active_vars = {k: v for k, v in cp.variables.items() if v}
                if active_vars:
                    sys_prompt_parts.append(f"【RPG数值与世界状态变量】：{json.dumps(active_vars, ensure_ascii=False)}")

        # 注入叙梦面板 6 大 Tab 状态机
        ns = session.narrative_state
        if ns:
            st_info = []
            if ns.date_text:
                st_info.append(f"日期: {ns.date_text}")
            if ns.time_text:
                st_info.append(f"时间: {ns.time_text}")
            if ns.location:
                st_info.append(f"地点: {ns.location}")
            if ns.present_characters:
                st_info.append(f"在场角色: {', '.join(ns.present_characters)}")
            if st_info:
                sys_prompt_parts.append(f"【当前时空与场景】：{' | '.join(st_info)}")
            if ns.player_states:
                sys_prompt_parts.append(f"【玩家当前状态】：{json.dumps(ns.player_states, ensure_ascii=False)}")
            if ns.important_items:
                sys_prompt_parts.append(f"【关键物品与背包】：{json.dumps(ns.important_items, ensure_ascii=False)}")
            if ns.social_relations:
                sys_prompt_parts.append(f"【NPC与社交关系】：{json.dumps(ns.social_relations, ensure_ascii=False)}")

        # 注入世界书 (World Book) Aho-Corasick + RAG 命中条目
        try:
            from app.services.world_book_service import WorldBookService

            recent_history_texts = [
                m.content
                for m in (history_msgs[-10:] if len(history_msgs) > 10 else history_msgs)
            ]
            wb_match = await WorldBookService.match_world_book_entries(
                db=db,
                character_id=session.character_id,
                user_id=user_id,
                user_text=payload.content,
                recent_history=recent_history_texts,
            )
            if wb_match.formatted_prompt:
                sys_prompt_parts.append(wb_match.formatted_prompt)
        except Exception as wb_err:
            logger.warning("世界书条目 RAG 扫描跳过: %s", wb_err)

        # 槽位 6: Mod 深度微表情与描写增强 (Bottom AN)
        if mod_patches.bottom_an:
            sys_prompt_parts.extend(mod_patches.bottom_an)

        # 槽位 8: 叙梦状态机与世界感知增量协议 (方案 A: Delta Tag 协议)
        delta_protocol_prompt = (
            "【叙梦状态机与世界感知增量协议】\n"
            "在推演剧情与对话时，如果本轮互动产生了时空推进、身心状态变动、变量增减、好感度升降、消耗品变动或新事件，"
            "请务必在回复文本的最末尾附带增量 JSON 标签 <narrative_delta>{...}</narrative_delta>。\n"
            "可包含字段（仅输出发生变动的字段，未变动的字段绝对不要输出）：\n"
            "- \"date_text\": \"推进后的日期\"\n"
            "- \"time_text\": \"推进后的时辰 (如 '正午'、'黄昏')\"\n"
            "- \"location\": \"转移后的当前地点\"\n"
            "- \"player_states\": [{\"name\": \"状态名\", \"currentVal\": 新数值, \"desc\": \"新状态描述\"}]\n"
            "- \"variables\": {\"变量名\": 新数值或状态}\n"
            "- \"social_relations\": [{\"name\": \"NPC名\", \"favorability\": 新好感度, \"relationTag\": \"新关系标签\"}]\n"
            "- \"consumables\": [{\"name\": \"物品名\", \"count\": 变动后数量}]\n"
            "- \"new_event\": {\"time\": \"此刻时辰\", \"location\": \"地点\", \"desc\": \"一句话概括刚才发生的新事件\"}\n"
            "注意：<narrative_delta> 必须位于输出内容的最末尾，且必须是合法的 JSON 对象。"
        )
        sys_prompt_parts.append(delta_protocol_prompt)

        # 检查是否激活了 SillyTavern 酒馆调音台流水线 (根据模型标识路由专属预设)
        try:
            from app.services.tavern_service import TavernService
            tavern_preset = await TavernService.get_user_preset(
                user_id=user_id,
                db=db,
                model_id=payload.model_id,
            )
            use_tavern = bool(tavern_preset and tavern_preset.is_active)
        except Exception as err:
            logger.warning("[SillyTavern] 获取酒馆调音台预设异常: %s", err)
            tavern_preset = None
            use_tavern = False

        sampling_kwargs: dict[str, Any] = {}
        if use_tavern and tavern_preset:
            world_info_text = (
                wb_match.formatted_prompt
                if ("wb_match" in locals() and wb_match and getattr(wb_match, "formatted_prompt", None))
                else ""
            )

            chat_examples = []
            example_dialogue = getattr(character, "mes_example", "") or getattr(character, "example_dialogue", "")
            if example_dialogue:
                chat_examples.append({"role": "system", "content": f"<对话样例>\n{example_dialogue}\n</对话样例>"})

            # 38 变量矩阵展开
            variables = {}
            if cp:
                variables.update({
                    "user_name": effective_user_name,
                    "user_persona": getattr(cp, "user_persona", "") or "",
                    "dialogue_style": getattr(cp, "dialogue_style", "") or "",
                })
            if ns:
                variables.update({
                    "time": getattr(ns, "time_of_day", "") or "",
                    "location": getattr(ns, "location", "") or "",
                    "plot_summary": getattr(ns, "plot_summary", "") or "",
                })
                player_states = getattr(ns, "player_states", None)
                if player_states and isinstance(player_states, dict):
                    variables.update(player_states)

            tavern_context = {
                "character_name": character.name,
                "character_desc": character.description or "",
                "character_personality": character.personality or "",
                "scenario": character.scenario or "",
                "user_name": effective_user_name,
                "user_persona": cp.user_persona if (cp and cp.user_persona) else "",
                "world_info_before": world_info_text,
                "world_info_after": delta_protocol_prompt,
                "chat_examples": chat_examples,
                "history_messages": [
                    {
                        "role": "user" if h.sender == "user" else "assistant",
                        "content": (
                            f"<think>{h.thinking_content}</think>\n{re.sub(r'```html[\s\S]*?```', '', h.content, flags=re.IGNORECASE).strip()}"
                            if (h.sender != "user" and getattr(h, "thinking_content", None) and supports_reasoning)
                            else re.sub(r"```html[\s\S]*?```", "", h.content, flags=re.IGNORECASE).strip()
                        ),
                    }
                    for h in (history_msgs[-10:] if len(history_msgs) > 10 else history_msgs)
                ],
                "mod_patches": mod_patches,
                "variables": variables,
            }
            messages_for_llm, sampling_kwargs = TavernService.assemble_tavern_messages_and_params(
                preset=tavern_preset,
                context=tavern_context,
            )
            # 若模型未开启深度思考，坚决切断 reasoning_effort 参数下发
            if not supports_reasoning:
                sampling_kwargs.pop("reasoning_effort", None)
            logger.info(
                f"[SillyTavern] 酒馆调音台接管聊天装配 | 模型: {payload.model_id} | 预设: {tavern_preset.preset_name} | "
                f"流水线消息数: {len(messages_for_llm)} | 采样参数: {sampling_kwargs}"
            )
        else:
            sys_prompt_joined = "\n".join(sys_prompt_parts)
            sys_prompt_joined = sys_prompt_joined.replace("{{char}}", character.name).replace("{{user}}", effective_user_name)
            messages_for_llm = [
                {"role": "system", "content": sys_prompt_joined}
            ]
            # 选取最近 10 条历史消息作为滑动窗口 (剔除纯前端挂件代码以节约 token)
            recent_history = history_msgs[-10:] if len(history_msgs) > 10 else history_msgs
            for h in recent_history:
                role = "user" if h.sender == "user" else "assistant"
                clean_h_content = re.sub(r"```html[\s\S]*?```", "", h.content, flags=re.IGNORECASE).strip()
                clean_h_content = clean_h_content.replace("{{char}}", character.name).replace("{{user}}", effective_user_name)
                messages_for_llm.append({"role": role, "content": clean_h_content})

        # 确保传递给大模型的所有消息中 {{user}} 宏均已展开替换
        for m_item in messages_for_llm:
            if isinstance(m_item.get("content"), str):
                m_item["content"] = m_item["content"].replace("{{char}}", character.name).replace("{{user}}", effective_user_name)

        # 5. 调用统一 LLM 网关消费流
        accumulated_thinking: list[str] = []
        accumulated_message: list[str] = []

        try:
            # 发送初始保活连接帧
            yield ": connected\n\n"

            reasoning_effort_param = sampling_kwargs.get("reasoning_effort") if supports_reasoning else None
            async for event_type, chunk in llm_gateway.stream_chat(
                messages=messages_for_llm,
                model=payload.model_id,
                temperature=sampling_kwargs.get("temperature", 0.8),
                top_p=sampling_kwargs.get("top_p", 1.0),
                frequency_penalty=sampling_kwargs.get("frequency_penalty", 0.0),
                presence_penalty=sampling_kwargs.get("presence_penalty", 0.0),
                seed=sampling_kwargs.get("seed"),
                max_tokens=sampling_kwargs.get("max_tokens", 2048),
                stop=sampling_kwargs.get("stop"),
                reasoning_effort=reasoning_effort_param,
                supports_reasoning=supports_reasoning,
            ):
                if event_type == "thinking":
                    if supports_reasoning:
                        accumulated_thinking.append(chunk)
                        data_json = json.dumps({"chunk": chunk}, ensure_ascii=False)
                        yield f"event: thinking\ndata: {data_json}\n\n"
                elif event_type == "message":
                    # 实时替换 chunk 中潜在的宏文本，确保打字机流绝不暴露 {{user}} / {{char}}
                    clean_chunk = chunk.replace("{{user}}", effective_user_name).replace("{{char}}", character.name)
                    accumulated_message.append(clean_chunk)
                    data_json = json.dumps({"chunk": clean_chunk}, ensure_ascii=False)
                    yield f"event: message\ndata: {data_json}\n\n"
                elif event_type == "error":
                    data_json = json.dumps({"message": chunk}, ensure_ascii=False)
                    yield f"event: error\ndata: {data_json}\n\n"
        except Exception as e:
            logger.exception("Chat generation failed: %s", e)
            err_data = json.dumps({"message": f"生成过程中断: {e}"}, ensure_ascii=False)
            yield f"event: error\ndata: {err_data}\n\n"
            return

        # 6. 生成完毕：提取状态增量、落库 AI 消息与扣费
        full_thinking = "".join(accumulated_thinking) if supports_reasoning else ""
        full_message = "".join(accumulated_message)

        # 提取并解析增量状态更新，并彻底从正文中切除所有 JSON/Tag 残留 (解决图 2 裸 JSON 泄漏问题)
        full_message, updated_delta_obj = cls.extract_and_strip_narrative_delta(full_message)

        # 执行酒馆与角色私有正则流水线及高级格式化清洗
        full_message = await cls.clean_ai_text(
            text=full_message,
            character=session.character,
            user_id=user_id,
            db=db,
            tavern_preset=tavern_preset,
            placement=2,
            model_id=payload.model_id,
        )

        # 再次执行切除以防二次拼接残留，并替换正文中可能的 {{user}}
        full_message, extra_delta = cls.extract_and_strip_narrative_delta(full_message)
        if extra_delta and not updated_delta_obj:
            updated_delta_obj = extra_delta

        full_message = full_message.replace("{{user}}", effective_user_name).strip()


        if tavern_preset and getattr(tavern_preset, "advanced_formatting", None):
            adv_fmt = tavern_preset.advanced_formatting
            if adv_fmt.reply_prefix.strip() and adv_fmt.show_reply_prefix:
                pref = adv_fmt.reply_prefix.strip()
                if not full_message.startswith(pref):
                    full_message = f"{pref} {full_message}" if not pref.endswith((" ", "*", "：", ":", "\n")) else f"{pref}{full_message}"

        # 状态增量合并入 ControlPanel 和 NarrativeState
        updated_cp_dto = None
        updated_ns_dto = None

        if updated_delta_obj and isinstance(updated_delta_obj, dict):
            try:
                # 1. 合并 RPG 角色变量到 ControlPanel
                if "variables" in updated_delta_obj and isinstance(updated_delta_obj["variables"], dict):
                    cp = session.control_panel
                    if cp:
                        cur_vars = dict(cp.variables or {})
                        cur_vars.update(updated_delta_obj["variables"])
                        cp.variables = cur_vars
                        flag_modified(cp, "variables")
                        updated_cp_dto = ControlPanelDTO.model_validate(cp)

                # 2. 合并 6 大 Tab 数据到 NarrativeState
                ns = session.narrative_state
                if ns:
                    if "date_text" in updated_delta_obj and updated_delta_obj["date_text"]:
                        ns.date_text = str(updated_delta_obj["date_text"]).strip()
                    if "time_text" in updated_delta_obj and updated_delta_obj["time_text"]:
                        ns.time_text = str(updated_delta_obj["time_text"]).strip()
                    if "location" in updated_delta_obj and updated_delta_obj["location"]:
                        ns.location = str(updated_delta_obj["location"]).strip()
                    if "present_characters" in updated_delta_obj and isinstance(updated_delta_obj["present_characters"], list):
                        ns.present_characters = updated_delta_obj["present_characters"]
                        flag_modified(ns, "present_characters")

                    # 玩家状态增量合并
                    if "player_states" in updated_delta_obj and isinstance(updated_delta_obj["player_states"], list):
                        cur_states = list(ns.player_states or [])
                        for delta_ps in updated_delta_obj["player_states"]:
                            if isinstance(delta_ps, dict) and "name" in delta_ps:
                                matched = next((s for s in cur_states if s.get("name") == delta_ps["name"]), None)
                                if matched:
                                    matched.update(delta_ps)
                                else:
                                    cur_states.append(delta_ps)
                        ns.player_states = cur_states
                        flag_modified(ns, "player_states")

                    # 社交好感度增量合并
                    if "social_relations" in updated_delta_obj and isinstance(updated_delta_obj["social_relations"], list):
                        cur_social = list(ns.social_relations or [])
                        for delta_sr in updated_delta_obj["social_relations"]:
                            if isinstance(delta_sr, dict) and "name" in delta_sr:
                                matched = next((s for s in cur_social if s.get("name") == delta_sr["name"]), None)
                                if matched:
                                    matched.update(delta_sr)
                                else:
                                    cur_social.append(delta_sr)
                        ns.social_relations = cur_social
                        flag_modified(ns, "social_relations")

                    # 背包消耗品增量合并
                    if "consumables" in updated_delta_obj and isinstance(updated_delta_obj["consumables"], list):
                        cur_cons = list(ns.consumables or [])
                        for delta_c in updated_delta_obj["consumables"]:
                            if isinstance(delta_c, dict) and "name" in delta_c:
                                matched = next((c for c in cur_cons if c.get("name") == delta_c["name"]), None)
                                if matched:
                                    matched.update(delta_c)
                                else:
                                    cur_cons.append(delta_c)
                        ns.consumables = cur_cons
                        flag_modified(ns, "consumables")

                    # 任务目标增量合并
                    if "tasks" in updated_delta_obj and isinstance(updated_delta_obj["tasks"], list):
                        cur_tasks = list(ns.tasks or [])
                        for delta_t in updated_delta_obj["tasks"]:
                            if isinstance(delta_t, dict) and "task" in delta_t:
                                matched = next((t for t in cur_tasks if t.get("task") == delta_t["task"]), None)
                                if matched:
                                    matched.update(delta_t)
                                else:
                                    cur_tasks.append(delta_t)
                        ns.tasks = cur_tasks
                        flag_modified(ns, "tasks")

                    # 新历史事件追加 (兼容 new_event 字典与 history_events 列表)
                    new_events_to_add: list[dict[str, Any]] = []
                    if "new_event" in updated_delta_obj and isinstance(updated_delta_obj["new_event"], dict):
                        new_events_to_add.append(updated_delta_obj["new_event"])
                    elif "history_events" in updated_delta_obj and isinstance(updated_delta_obj["history_events"], list):
                        for item in updated_delta_obj["history_events"]:
                            if isinstance(item, dict):
                                new_events_to_add.append(item)

                    if new_events_to_add:
                        cur_history = list(ns.history_events or [])
                        for ev in new_events_to_add:
                            raw_desc = ev.get("desc") or ev.get("summary") or "发生了剧情变动。"
                            ev_desc = raw_desc.replace("{{user}}", effective_user_name).replace("{{char}}", character.name)
                            ev_char = (ev.get("characters") or f"{effective_user_name}, {character.name}").replace("{{user}}", effective_user_name).replace("{{char}}", character.name)
                            ev_item = {
                                "id": int(datetime.now().timestamp() * 1000),
                                "time": ev.get("time") or ns.time_text or "此刻",
                                "characters": ev_char,
                                "location": (ev.get("location") or ns.location or "当前场景").replace("{{user}}", effective_user_name),
                                "mood": ev.get("mood") or "推进",
                                "desc": ev_desc,
                                "summary": ev_desc,
                            }
                            if cur_history and isinstance(cur_history[0], dict) and "events" in cur_history[0]:
                                cur_history[0]["events"] = [ev_item] + (cur_history[0]["events"] or [])
                            else:
                                cur_history.insert(0, {
                                    "id": f"d_{int(datetime.now().timestamp())}",
                                    "dateText": ns.date_text or "第一幕",
                                    "eventCount": "1 个事件",
                                    "events": [ev_item],
                                })
                        ns.history_events = cur_history
                        flag_modified(ns, "history_events")

                    updated_ns_dto = NarrativeStateDTO.model_validate(ns)
            except Exception as update_err:
                logger.warning("[Narrative Delta] 状态合并异常: %s", update_err)

        input_token_est = sum(len(m["content"]) for m in messages_for_llm)
        output_token_est = len(full_message) + len(full_thinking)

        ai_msg_id = uuid.uuid4()
        ai_msg = ChatMessage(
            id=ai_msg_id,
            session_id=session_id,
            branch_id=session.current_branch_id,
            sender="ai",
            character_name=character.name,
            avatar_url=character.avatar_url,
            content=full_message or "……",
            thinking_content=full_thinking,
            input_tokens=input_token_est,
            output_tokens=output_token_est,
            parent_message_id=user_msg_id,
        )
        db.add(ai_msg)

        # 7. 扣费事务
        try:
            await WalletService.deduct_balance(
                db=db,
                user_id=user_id,
                currency=currency,  # type: ignore[arg-type]
                amount=cost,
                model_id=payload.model_id,
                target_character_id=character.id,
                description=f"与角色「{character.name}」沉浸式对话消耗 {cost} {currency}",
            )
        except Exception as err:
            logger.warning("Auto-deduction warning (non-blocking for chat stream): %s", err)

        await db.commit()

        # 8. 发送状态机自动更新事件 (方案 A: Delta Tag 协议落地)
        if updated_ns_dto or updated_cp_dto:
            state_payload = {
                "narrative_state": updated_ns_dto.model_dump() if updated_ns_dto else None,
                "control_panel": updated_cp_dto.model_dump() if updated_cp_dto else None,
            }
            yield f"event: state_updated\ndata: {json.dumps(state_payload, ensure_ascii=False)}\n\n"

        # 9. 发送 usage 与 done 信号
        usage_payload = {
            "message_id": str(ai_msg_id),
            "user_message_id": str(user_msg_id),
            "input_tokens": input_token_est,
            "output_tokens": output_token_est,
            "cost": cost,
            "currency": currency,
            "cleaned_content": full_message,
        }
        yield f"event: usage\ndata: {json.dumps(usage_payload, ensure_ascii=False)}\n\n"
        yield f"event: done\ndata: {json.dumps({'status': 'completed', 'cleaned_content': full_message})}\n\n"

    @classmethod
    async def get_user_chat_sessions(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
    ) -> list[ChatSessionListItemDTO]:
        """获取当前用户的所有历史会话列表（按置顶与最近活跃时间倒序）。"""
        stmt = (
            select(ChatSession)
            .where(ChatSession.user_id == user_id)
            .options(
                selectinload(ChatSession.character),
                selectinload(ChatSession.messages),
            )
            .order_by(ChatSession.is_pinned.desc(), ChatSession.updated_at.desc())
        )
        result = await db.execute(stmt)
        sessions = result.scalars().all()

        item_list: list[ChatSessionListItemDTO] = []
        for s in sessions:
            char = s.character
            # 获取最后一条消息摘要
            last_msg_text = ""
            if s.messages:
                sorted_msgs = sorted(s.messages, key=lambda m: m.created_at, reverse=True)
                last_msg_text = sorted_msgs[0].content
            elif char and char.first_mes:
                last_msg_text = char.first_mes

            # 友好格式化时间
            now = datetime.now(s.updated_at.tzinfo) if s.updated_at.tzinfo else datetime.utcnow()
            diff = now - s.updated_at
            if diff.days == 0:
                if diff.seconds < 3600:
                    time_str = f"{max(1, diff.seconds // 60)} 分钟前"
                else:
                    time_str = f"{diff.seconds // 3600} 小时前"
            elif diff.days < 7:
                time_str = f"{diff.days} 天前"
            else:
                time_str = s.updated_at.strftime("%Y-%m-%d")

            item_list.append(
                ChatSessionListItemDTO(
                    id=s.id,
                    character_id=s.character_id,
                    title=char.name if char else "未知角色",
                    avatar=char.avatar_url if char else "",
                    banner_url=char.banner_url if char else (char.avatar_url if char else None),
                    last_message=last_msg_text[:100] if last_msg_text else "暂无对话记录",
                    last_message_time=time_str,
                    message_count=len(s.messages),
                    is_pinned=s.is_pinned,
                    remark=s.remark or "",
                    updated_at=s.updated_at,
                )
            )
        return item_list

    @classmethod
    async def toggle_pin_session(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> bool:
        """切换会话置顶状态。"""
        session = await cls.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
        session.is_pinned = not session.is_pinned
        await db.commit()
        return session.is_pinned

    @classmethod
    async def update_session_remark(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        remark: str,
    ) -> str:
        """更新会话备注。"""
        session = await cls.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
        session.remark = remark
        await db.commit()
        return session.remark

    @classmethod
    async def delete_session(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> bool:
        """删除指定会话及其全部级联数据。"""
        session = await cls.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
        await db.delete(session)
        await db.commit()
        return True

    @classmethod
    async def clear_session_messages(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> bool:
        """清空会话历史消息并恢复角色初始开场白。"""
        session = await cls.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
        from sqlalchemy import delete
        await db.execute(delete(ChatMessage).where(ChatMessage.session_id == session.id))

        if session.character and session.character.first_mes and session.current_branch_id:
            cleaned_greeting = await cls.clean_ai_text(
                text=session.character.first_mes.strip(),
                character=session.character,
                user_id=user_id,
                db=db,
            )
            cp = session.control_panel
            uname = (cp.user_name.strip() if cp and cp.user_name and cp.user_name.strip() != "{{user}}" else "") or "你"
            cleaned_greeting = cleaned_greeting.replace("{{user}}", uname).replace("{{char}}", session.character.name)
            greeting_msg = ChatMessage(
                session_id=session.id,
                branch_id=session.current_branch_id,
                sender="ai",
                character_name=session.character.name,
                avatar_url=session.character.avatar_url,
                content=cleaned_greeting,
                thinking_content="",
                input_tokens=0,
                output_tokens=0,
            )
            db.add(greeting_msg)
        await db.commit()
        return True

    @classmethod
    async def switch_session_greeting(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        greeting_index: int,
    ) -> ChatMessageDTO:
        """切换会话初始开场白 (支持在 first_mes 与 alternate_greetings 之间轮换)。"""
        session = await cls.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
        character = session.character
        if not character:
            raise HTTPException(status_code=404, detail="关联角色不存在")

        # 收集全部开场白列表: [first_mes, *alternate_greetings]
        all_greetings: list[str] = [character.first_mes] if character.first_mes else []
        if character.alternate_greetings and isinstance(character.alternate_greetings, list):
            for g in character.alternate_greetings:
                if isinstance(g, str) and g.strip():
                    all_greetings.append(g.strip())
                elif isinstance(g, dict) and g.get("greetingText"):
                    all_greetings.append(str(g["greetingText"]).strip())

        if not all_greetings:
            raise HTTPException(status_code=400, detail="该角色未配置任何开场白")

        idx = greeting_index % len(all_greetings)
        selected_text = all_greetings[idx]

        cleaned_text = await cls.clean_ai_text(
            text=selected_text,
            character=character,
            user_id=user_id,
            db=db,
        )
        cp = session.control_panel
        uname = (cp.user_name.strip() if cp and cp.user_name and cp.user_name.strip() != "{{user}}" else "") or "你"
        cleaned_text = cleaned_text.replace("{{user}}", uname).replace("{{char}}", character.name)

        # 查找当前分支下的第一条 AI 开场消息
        first_msg_stmt = (
            select(ChatMessage)
            .where(
                ChatMessage.session_id == session.id,
                ChatMessage.branch_id == session.current_branch_id,
            )
            .order_by(ChatMessage.created_at.asc())
            .limit(1)
        )
        first_msg = (await db.execute(first_msg_stmt)).scalar_one_or_none()
        if first_msg and first_msg.sender == "ai":
            first_msg.content = cleaned_text
            first_msg.output_tokens = 0
        else:
            first_msg = ChatMessage(
                id=uuid.uuid4(),
                session_id=session.id,
                branch_id=session.current_branch_id,
                sender="ai",
                character_name=character.name,
                avatar_url=character.avatar_url,
                content=cleaned_text,
                thinking_content="",
                input_tokens=0,
                output_tokens=0,
            )
            db.add(first_msg)

        await db.commit()
        await db.refresh(first_msg)
        return ChatMessageDTO.model_validate(first_msg)

    @classmethod
    async def fork_session_at_message(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        payload: ForkSessionRequest,
    ) -> ChatSessionResponse:
        """从指定消息分叉并创建全新独立的历史聊天会话。

        复制截至 fork_message_id 的所有时序对话记录到新会话中，形成独立历史记录。
        """
        source_session = await cls.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
        fork_msg = await db.get(ChatMessage, payload.fork_message_id)
        if not fork_msg or fork_msg.session_id != session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="分叉起点消息不存在",
            )

        # 1. 查找源会话中截至 fork_msg 的完整消息链
        from app.services.tree_service import TreeService

        active_msgs = await TreeService.get_branch_active_messages(
            db=db, session_id=session_id, branch_id=fork_msg.branch_id
        )

        # 截取截至 fork_msg 的部分
        copied_history: list[ChatMessage] = []
        for m in active_msgs:
            copied_history.append(m)
            if m.id == fork_msg.id:
                break

        # 2. 统计该角色已有会话数并生成备注
        stmt_count = select(func.count(ChatSession.id)).where(
            ChatSession.user_id == user_id,
            ChatSession.character_id == source_session.character_id,
        )
        count_res = await db.execute(stmt_count)
        session_count = count_res.scalar() or 1

        clean_snippet = fork_msg.content.replace("\n", " ").strip()[:14]
        remark = (
            payload.remark.strip()
            if payload.remark and payload.remark.strip()
            else f"分支 {session_count}：{clean_snippet}..."
        )

        # 3. 创建全新 ChatSession 记录
        new_session_id = uuid.uuid4()
        new_main_branch_id = uuid.uuid4()

        new_branch = StoryBranch(
            id=new_main_branch_id,
            session_id=new_session_id,
            name="🌿 主线剧情",
            is_main=True,
        )

        new_session = ChatSession(
            id=new_session_id,
            user_id=user_id,
            character_id=source_session.character_id,
            current_branch_id=new_main_branch_id,
            current_model_id=source_session.current_model_id,
            mode=source_session.mode,
            remark=remark,
            is_pinned=False,
        )

        # 复制主控与叙梦面板状态
        new_control = ChatControlPanel(
            session_id=new_session_id,
            variables=source_session.control_panel.variables if source_session.control_panel else {},
        )
        new_narrative = ChatNarrativeState(
            session_id=new_session_id,
            date_text=source_session.narrative_state.date_text if source_session.narrative_state else "",
            time_text=source_session.narrative_state.time_text if source_session.narrative_state else "",
            location=source_session.narrative_state.location if source_session.narrative_state else "",
        )

        db.add_all([new_session, new_branch, new_control, new_narrative])

        # 4. 复制历史消息
        prev_new_msg_id: uuid.UUID | None = None
        for old_m in copied_history:
            new_msg_id = uuid.uuid4()
            new_msg = ChatMessage(
                id=new_msg_id,
                session_id=new_session_id,
                branch_id=new_main_branch_id,
                sender=old_m.sender,
                character_name=old_m.character_name,
                avatar_url=old_m.avatar_url,
                content=old_m.content,
                thinking_content=old_m.thinking_content,
                input_tokens=old_m.input_tokens,
                output_tokens=old_m.output_tokens,
                parent_message_id=prev_new_msg_id,
                created_at=old_m.created_at,
            )
            db.add(new_msg)
            prev_new_msg_id = new_msg_id

        await db.commit()
        await db.refresh(new_session)

        loaded_new_session = await cls.get_session_by_id(
            db=db, user_id=user_id, session_id=new_session_id
        )
        logger.info(
            "Forked new independent ChatSession %s from message %s (session %s)",
            new_session_id,
            fork_msg.id,
            session_id,
        )
        return await cls.get_session_response(db=db, session=loaded_new_session)

    @classmethod
    async def get_control_panel(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> ControlPanelDTO:
        """获取指定会话的主控面板配置（支持自动初始化自愈）。

        Args:
            db: 异步数据库会话。
            user_id: 当前用户 ID。
            session_id: 目标会话 ID。

        Returns:
            ControlPanelDTO: 主控面板数据。
        """
        session = await cls.get_session_by_id(db=db, user_id=user_id, session_id=session_id)
        char_ext = getattr(session.character, "extensions", None) or {}
        init_vars = char_ext.get("variables") or {}

        stmt = select(ChatControlPanel).where(ChatControlPanel.session_id == session_id)
        result = await db.execute(stmt)
        control = result.scalar_one_or_none()

        if not control:
            # 自动初始化默认面板并继承角色卡初始 RPG 变量
            control = ChatControlPanel(
                session_id=session_id,
                user_name="{{user}}",
                user_persona="",
                custom_prompt="",
                variables=dict(init_vars),
                memory_blocks=[],
                text_replacements=[],
            )
            db.add(control)
            await db.commit()
            await db.refresh(control)
        elif not control.variables and init_vars:
            # 若历史会话变量为空但角色卡声明了初始变量，自动对齐初始状态
            control.variables = dict(init_vars)
            await db.commit()
            await db.refresh(control)

        return ControlPanelDTO.model_validate(control)

    @classmethod
    async def update_control_panel(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        payload: ControlPanelDTO,
    ) -> ControlPanelDTO:
        """更新指定会话的主控面板配置。

        Args:
            db: 异步数据库会话。
            user_id: 当前用户 ID。
            session_id: 目标会话 ID。
            payload: 更新数据体。

        Returns:
            ControlPanelDTO: 更新后的主控面板数据。
        """
        # 权限校验
        await cls.get_session_by_id(db=db, user_id=user_id, session_id=session_id)

        stmt = select(ChatControlPanel).where(ChatControlPanel.session_id == session_id)
        result = await db.execute(stmt)
        control = result.scalar_one_or_none()

        if not control:
            control = ChatControlPanel(
                session_id=session_id,
                user_name=payload.user_name,
                user_persona=payload.user_persona,
                custom_prompt=payload.custom_prompt,
                variables=payload.variables,
                memory_blocks=payload.memory_blocks,
                text_replacements=payload.text_replacements,
            )
            db.add(control)
        else:
            control.user_name = payload.user_name
            control.user_persona = payload.user_persona
            control.custom_prompt = payload.custom_prompt
            control.variables = payload.variables
            control.memory_blocks = payload.memory_blocks
            control.text_replacements = payload.text_replacements

        await db.commit()
        await db.refresh(control)
        logger.info("Updated ChatControlPanel for session %s by user %s", session_id, user_id)
        return ControlPanelDTO.model_validate(control)

    @classmethod
    async def get_narrative_state(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
    ) -> NarrativeStateDTO:
        """获取指定会话的叙梦 6 大 Tab 状态机数据（支持自动初始化自愈）。

        Args:
            db: 异步数据库会话。
            user_id: 当前用户 ID。
            session_id: 目标会话 ID。

        Returns:
            NarrativeStateDTO: 叙梦状态机数据。
        """
        # 权限校验
        session = await cls.get_session_by_id(db=db, user_id=user_id, session_id=session_id)

        stmt = select(ChatNarrativeState).where(ChatNarrativeState.session_id == session_id)
        result = await db.execute(stmt)
        narrative = result.scalar_one_or_none()

        if not narrative:
            char = session.character
            char_name = char.name if char else "神秘伙伴"
            loc = (char.scenario.split("。")[0].split("\n")[0][:40] if char and char.scenario else "") or "木叶村残破废墟"
            narrative = ChatNarrativeState(
                session_id=session_id,
                date_text="第一幕 · 初始篇",
                time_text="清晨",
                location=loc,
                present_characters=["{{user}}", char_name],
                player_states=[
                    {"id": 1, "type": "基础属性", "name": "精神状态", "currentVal": 100, "maxVal": "100", "desc": "当前意识清醒，处于最佳探索状态"},
                    {"id": 2, "type": "环境感知", "name": "场景熟悉度", "currentVal": 15, "maxVal": "100", "desc": f"初抵【{loc}】，正在探索四周"}
                ],
                consumables=[
                    {"id": 1, "name": "初级体力药水", "count": 2, "type": "消耗品", "effect": "恢复精力", "source": "随身行囊", "desc": "淡蓝色恢复药剂"}
                ],
                important_items=[
                    {"id": 1, "owner": "{{user}}", "name": "星辉罗盘", "desc": "指引平行世界命运分歧的神秘罗盘", "importance": "分支剧情信物"}
                ],
                skills=[
                    {"id": 1, "name": "命运洞察", "type": "被动感知", "level": "LV.1", "proficiency": "20%", "proficiencyCurrent": 20, "proficiencyMax": 100, "cost": "无", "cooldown": "无", "effect": "敏锐感知剧情中的关键抉择点", "source": "天生觉醒", "status": "已装备", "isEquipped": True}
                ],
                social_relations=[
                    {
                        "id": 1,
                        "name": char_name,
                        "relationTag": "初识",
                        "tagColor": "bg-[#F9C86D]",
                        "favorability": 50,
                        "favorBarColor": "bg-[#F9C86D]",
                        "relation": "初次结识的同行者",
                        "location": loc,
                        "attitude": (char.personality if char else "") or "友善",
                        "bodyFeature": (char.description if char else "") or "独特外表",
                        "personality": (char.personality if char else "") or "深邃内敛",
                        "job": "探索同伴",
                        "hobby": "收集回忆",
                        "favorite": "未知",
                        "residence": loc,
                        "otherInfo": (char.description if char else "") or ""
                    }
                ],
                tasks=[
                    {
                        "id": 1,
                        "role": "{{user}}",
                        "task": f"与 {char_name} 建立羁绊",
                        "typeTag": "主线",
                        "statusTag": "进行中",
                        "location": loc,
                        "duration": "当前幕",
                        "desc": f"通过深入交谈探寻 {char_name} 隐藏的过去与心愿",
                        "reward": "好感度提升"
                    }
                ],
                history_events=[
                    {
                        "id": "d1",
                        "dateText": "第一幕 · 初遇",
                        "eventCount": "1 个事件",
                        "events": [
                            {
                                "id": 1,
                                "time": "清晨",
                                "characters": f"{{user}}, {char_name}",
                                "location": loc,
                                "mood": "探索、期待",
                                "desc": f"在【{loc}】，你与 {char_name} 开启了最初的命运交织。"
                            }
                        ]
                    }
                ],
            )
            db.add(narrative)
            await db.commit()
            await db.refresh(narrative)
        elif (
            not narrative.player_states
            and not narrative.consumables
            and not narrative.important_items
            and not narrative.skills
            and not narrative.social_relations
            and not narrative.tasks
        ):
            char = session.character
            char_name = char.name if char else "神秘伙伴"
            loc = (char.scenario.split("。")[0].split("\n")[0][:40] if char and char.scenario else "") or "木叶村残破废墟"
            narrative.date_text = "第一幕 · 初始篇"
            narrative.time_text = "清晨"
            narrative.location = loc
            narrative.present_characters = ["{{user}}", char_name]
            narrative.player_states = [
                {"id": 1, "type": "基础属性", "name": "精神状态", "currentVal": 100, "maxVal": "100", "desc": "当前意识清醒，处于最佳探索状态"},
                {"id": 2, "type": "环境感知", "name": "场景熟悉度", "currentVal": 15, "maxVal": "100", "desc": f"初抵【{loc}】，正在探索四周"}
            ]
            narrative.consumables = [
                {"id": 1, "name": "初级体力药水", "count": 2, "type": "消耗品", "effect": "恢复精力", "source": "随身行囊", "desc": "淡蓝色恢复药剂"}
            ]
            narrative.important_items = [
                {"id": 1, "owner": "{{user}}", "name": "星辉罗盘", "desc": "指引平行世界命运分歧的神秘罗盘", "importance": "分支剧情信物"}
            ]
            narrative.skills = [
                {"id": 1, "name": "命运洞察", "type": "被动感知", "level": "LV.1", "proficiency": "20%", "proficiencyCurrent": 20, "proficiencyMax": 100, "cost": "无", "cooldown": "无", "effect": "敏锐感知剧情中的关键抉择点", "source": "天生觉醒", "status": "已装备", "isEquipped": True}
            ]
            narrative.social_relations = [
                {
                    "id": 1,
                    "name": char_name,
                    "relationTag": "初识",
                    "tagColor": "bg-[#F9C86D]",
                    "favorability": 50,
                    "favorBarColor": "bg-[#F9C86D]",
                    "relation": "初次结识的同行者",
                    "location": loc,
                    "attitude": (char.personality if char else "") or "友善",
                    "bodyFeature": (char.description if char else "") or "独特外表",
                    "personality": (char.personality if char else "") or "深邃内敛",
                    "job": "探索同伴",
                    "hobby": "收集回忆",
                    "favorite": "未知",
                    "residence": loc,
                    "otherInfo": (char.description if char else "") or ""
                }
            ]
            narrative.tasks = [
                {
                    "id": 1,
                    "role": "{{user}}",
                    "task": f"与 {char_name} 建立羁绊",
                    "typeTag": "主线",
                    "statusTag": "进行中",
                    "location": loc,
                    "duration": "当前幕",
                    "desc": f"通过深入交谈探寻 {char_name} 隐藏的过去与心愿",
                    "reward": "好感度提升"
                }
            ]
            narrative.history_events = [
                {
                    "id": "d1",
                    "dateText": "第一幕 · 初遇",
                    "eventCount": "1 个事件",
                    "events": [
                        {
                            "id": 1,
                            "time": "清晨",
                            "characters": f"{{user}}, {char_name}",
                            "location": loc,
                            "mood": "探索、期待",
                            "desc": f"在【{loc}】，你与 {char_name} 开启了最初的命运交织。"
                        }
                    ]
                }
            ]
            await db.commit()
            await db.refresh(narrative)

        return NarrativeStateDTO.model_validate(narrative)

    @classmethod
    async def update_narrative_state(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        payload: NarrativeStateDTO,
    ) -> NarrativeStateDTO:
        """更新指定会话的叙梦 6 大 Tab 状态机数据。

        Args:
            db: 异步数据库会话。
            user_id: 当前用户 ID。
            session_id: 目标会话 ID。
            payload: 更新数据体。

        Returns:
            NarrativeStateDTO: 更新后的叙梦状态机数据。
        """
        # 权限校验
        await cls.get_session_by_id(db=db, user_id=user_id, session_id=session_id)

        stmt = select(ChatNarrativeState).where(ChatNarrativeState.session_id == session_id)
        result = await db.execute(stmt)
        narrative = result.scalar_one_or_none()

        if not narrative:
            narrative = ChatNarrativeState(
                session_id=session_id,
                date_text=payload.date_text,
                time_text=payload.time_text,
                location=payload.location,
                present_characters=payload.present_characters,
                player_states=payload.player_states,
                consumables=payload.consumables,
                important_items=payload.important_items,
                skills=payload.skills,
                social_relations=payload.social_relations,
                tasks=payload.tasks,
                history_events=payload.history_events,
            )
            db.add(narrative)
        else:
            narrative.date_text = payload.date_text
            narrative.time_text = payload.time_text
            narrative.location = payload.location
            narrative.present_characters = payload.present_characters
            narrative.player_states = payload.player_states
            narrative.consumables = payload.consumables
            narrative.important_items = payload.important_items
            narrative.skills = payload.skills
            narrative.social_relations = payload.social_relations
            narrative.tasks = payload.tasks
            narrative.history_events = payload.history_events

        await db.commit()
        await db.refresh(narrative)
        logger.info("Updated ChatNarrativeState for session %s by user %s", session_id, user_id)
        return NarrativeStateDTO.model_validate(narrative)


