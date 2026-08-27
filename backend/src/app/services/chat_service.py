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
import uuid
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from datetime import datetime
from app.models.character import Character
from app.models.chat import (
    ChatControlPanel,
    ChatMessage,
    ChatNarrativeState,
    ChatSession,
    StoryBranch,
)
from app.models.user import UserWallet
from app.schemas.chat import (
    ChatMessageDTO,
    ChatSessionListItemDTO,
    ChatSessionResponse,
    SendMessageRequest,
    StoryBranchDTO,
)
from app.services.llm_gateway import llm_gateway
from app.services.wallet_service import WalletService

logger = logging.getLogger(__name__)


class ChatService:
    """AI 对话与剧情树核心服务。"""

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

        # 创建初始主控面板
        control_panel = ChatControlPanel(
            session_id=session_id,
            user_name="{{user}}",
            user_persona="",
            custom_prompt="",
            variables={},
        )

        # 创建初始叙梦面板
        narrative_state = ChatNarrativeState(
            session_id=session_id,
            date_text="第一幕",
            time_text="清晨",
            location="起始之境",
            present_characters=[character.name],
        )

        db.add_all([session, main_branch, control_panel, narrative_state])

        # 4. 如果角色配置了 first_mes (开场白)，自动插入第一条 AI 问候消息
        if character.first_mes and character.first_mes.strip():
            greeting_msg = ChatMessage(
                id=uuid.uuid4(),
                session_id=session_id,
                branch_id=main_branch_id,
                sender="ai",
                character_name=character.name,
                avatar_url=character.avatar_url,
                content=character.first_mes.strip(),
                thinking_content="",
                input_tokens=0,
                output_tokens=len(character.first_mes),
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
        # 查询当前活跃分支下的消息列表 (按时间正序)
        msg_stmt = (
            select(ChatMessage)
            .where(
                ChatMessage.session_id == session.id,
                ChatMessage.branch_id == session.current_branch_id,
            )
            .order_by(ChatMessage.created_at.asc())
        )
        msg_res = await db.execute(msg_stmt)
        messages = msg_res.scalars().all()

        char = session.character
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

        # 3. 写入用户消息
        user_msg_id = uuid.uuid4()
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

        # 组装 System Prompt
        sys_prompt_parts = [
            f"你是 {character.name}。",
        ]
        if character.personality:
            sys_prompt_parts.append(f"【性格特征】：{character.personality}")
        if character.scenario:
            sys_prompt_parts.append(f"【当前场景背景】：{character.scenario}")
        if character.system_prompt:
            sys_prompt_parts.append(f"【核心系统指令】：{character.system_prompt}")
        if character.post_history_instructions:
            sys_prompt_parts.append(f"【输出要求】：{character.post_history_instructions}")

        sys_prompt_parts.append(
            "请遵循角色设定进行极具沉浸感和情感张力的角色扮演，可使用括号包裹神态、动作描写。"
        )

        messages_for_llm: list[dict[str, str]] = [
            {"role": "system", "content": "\n".join(sys_prompt_parts)}
        ]

        # 选取最近 10 条历史消息作为滑动窗口
        recent_history = history_msgs[-10:] if len(history_msgs) > 10 else history_msgs
        for h in recent_history:
            role = "user" if h.sender == "user" else "assistant"
            messages_for_llm.append({"role": role, "content": h.content})

        # 5. 调用统一 LLM 网关消费流
        accumulated_thinking: list[str] = []
        accumulated_message: list[str] = []

        try:
            async for event_type, chunk in llm_gateway.stream_chat(
                messages=messages_for_llm,
                model=payload.model_id,
            ):
                if event_type == "thinking":
                    accumulated_thinking.append(chunk)
                    data_json = json.dumps({"chunk": chunk}, ensure_ascii=False)
                    yield f"event: thinking\ndata: {data_json}\n\n"
                elif event_type == "message":
                    accumulated_message.append(chunk)
                    data_json = json.dumps({"chunk": chunk}, ensure_ascii=False)
                    yield f"event: message\ndata: {data_json}\n\n"
                elif event_type == "error":
                    data_json = json.dumps({"message": chunk}, ensure_ascii=False)
                    yield f"event: error\ndata: {data_json}\n\n"
        except Exception as e:
            logger.exception("Chat generation failed: %s", e)
            err_data = json.dumps({"message": f"生成过程中断: {e}"}, ensure_ascii=False)
            yield f"event: error\ndata: {err_data}\n\n"
            return

        # 6. 生成完毕：落库 AI 消息与扣费
        full_thinking = "".join(accumulated_thinking)
        full_message = "".join(accumulated_message)
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

        # 8. 发送 usage 与 done 信号
        usage_payload = {
            "message_id": str(ai_msg_id),
            "input_tokens": input_token_est,
            "output_tokens": output_token_est,
            "cost": cost,
            "currency": currency,
        }
        yield f"event: usage\ndata: {json.dumps(usage_payload, ensure_ascii=False)}\n\n"
        yield f"event: done\ndata: {json.dumps({'status': 'completed'})}\n\n"

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
            greeting_msg = ChatMessage(
                session_id=session.id,
                branch_id=session.current_branch_id,
                sender="ai",
                character_name=session.character.name,
                avatar_url=session.character.avatar_url,
                content=session.character.first_mes,
                thinking_content="",
                input_tokens=0,
                output_tokens=len(session.character.first_mes),
            )
            db.add(greeting_msg)
        await db.commit()
        return True
