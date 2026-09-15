"""世界书 (World Book) 双模 RAG 检索引擎与业务服务层。

实现 Aho-Corasick 高性能关键词极速扫描、次级逻辑过滤 (Secondary Keys)、
Token 预算动态截断、SillyTavern JSON 互转及 System Prompt 插桩组装。

Usage:
    >>> from app.services.world_book_service import WorldBookService
    >>> result = await WorldBookService.match_world_book_entries(db, session_id, user_text, history_texts)
"""

import json
import logging
import uuid
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import AppException
from app.models.character import Character
from app.models.world_book import WorldBook, WorldBookEntry
from app.schemas.world_book import (
    SillyTavernWorldBookImportDTO,
    WorldBookCreate,
    WorldBookDetailDTO,
    WorldBookDTO,
    WorldBookEntryCreate,
    WorldBookEntryDTO,
    WorldBookEntryUpdate,
    WorldBookMatchResultDTO,
    WorldBookUpdate,
)

logger = logging.getLogger("spikeai.world_book")

# 尝试加载 C 扩展 pyahocorasick
try:
    import ahocorasick

    HAS_AHOCORASICK = True
except ImportError:
    HAS_AHOCORASICK = False
    logger.warning("pyahocorasick 未检测到，启用纯 Python 多模式扫描引擎。")


class WorldBookScanner:
    """Aho-Corasick 多模式多关键词极速扫描器。"""

    @classmethod
    def scan_keywords(cls, text: str, keyword_map: dict[str, list[uuid.UUID]]) -> set[uuid.UUID]:
        """在文本中极速扫描所有关键词并返回命中的条目 ID 集合。

        Args:
            text: 待扫描文本 (用户输入 + 历史对话)。
            keyword_map: 关键词 -> [Entry ID 列表] 的映射字典。

        Returns:
            set[uuid.UUID]: 命中的所有 Entry ID 集合。
        """
        if not text or not keyword_map:
            return set()

        text_lower = text.lower()
        matched_ids: set[uuid.UUID] = set()

        if HAS_AHOCORASICK:
            A = ahocorasick.Automaton()
            for kw, entry_ids in keyword_map.items():
                kw_clean = kw.strip().lower()
                if kw_clean:
                    A.add_word(kw_clean, (kw_clean, entry_ids))
            try:
                A.make_automaton()
                for _, (_, entry_ids) in A.iter(text_lower):
                    matched_ids.update(entry_ids)
                return matched_ids
            except Exception as e:
                logger.warning("Aho-Corasick 扫描异常，回退至 Python 遍历: %s", e)

        # 纯 Python 兜底扫描
        for kw, entry_ids in keyword_map.items():
            kw_clean = kw.strip().lower()
            if kw_clean and kw_clean in text_lower:
                matched_ids.update(entry_ids)

        return matched_ids

    @classmethod
    def filter_secondary_keys(
        cls,
        text: str,
        secondary_keys: list[str],
        selective_logic: int,
    ) -> bool:
        """根据 SillyTavern 规范过滤次级关键词。

        Args:
            text: 待扫描文本。
            secondary_keys: 次级关键词列表。
            selective_logic: 0: AND ANY (包含任意一个即可), 1: NOT ALL (不能全包含), 2: NOT ANY (严禁包含任何一个)

        Returns:
            bool: True 表示条目符合条件，保留；False 表示被次级逻辑过滤。
        """
        if not secondary_keys:
            return True

        text_lower = text.lower()
        sec_hits = [k.strip().lower() in text_lower for k in secondary_keys if k.strip()]
        if not sec_hits:
            return True

        if selective_logic == 0:  # AND ANY
            return any(sec_hits)
        elif selective_logic == 1:  # NOT ALL
            return not all(sec_hits)
        elif selective_logic == 2:  # NOT ANY
            return not any(sec_hits)

        return True


class WorldBookService:
    """世界书领域业务服务。"""

    # 估算每个字符折算的 Token 系数
    TOKEN_FACTOR = 0.65

    @classmethod
    async def create_world_book(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        payload: WorldBookCreate,
    ) -> WorldBookDetailDTO:
        """创建新世界书及其初始条目。"""
        wb = WorldBook(
            user_id=user_id,
            character_id=payload.character_id,
            name=payload.name,
            description=payload.description,
            is_public=payload.is_public,
            scan_depth=payload.scan_depth,
            token_budget=payload.token_budget,
            entry_count=len(payload.entries),
        )
        db.add(wb)
        await db.flush()

        for idx, entry_in in enumerate(payload.entries):
            entry = WorldBookEntry(
                world_book_id=wb.id,
                keys=entry_in.keys,
                secondary_keys=entry_in.secondary_keys,
                selective_logic=entry_in.selective_logic,
                content=entry_in.content,
                comment=entry_in.comment,
                constant=entry_in.constant,
                enabled=entry_in.enabled,
                insertion_order=entry_in.insertion_order or (idx + 1) * 10,
                position=entry_in.position,
            )
            db.add(entry)

        await db.commit()
        await db.refresh(wb)
        return await cls.get_world_book_detail(db, user_id=user_id, world_book_id=wb.id)

    @classmethod
    async def list_world_books(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        character_id: uuid.UUID | None = None,
    ) -> list[WorldBookDTO]:
        """获取世界书列表。"""
        stmt = select(WorldBook).where(
            (WorldBook.user_id == user_id) | (WorldBook.is_public.is_(True))
        )
        if character_id:
            stmt = stmt.where(
                (WorldBook.character_id == character_id) | (WorldBook.character_id.is_(None))
            )
        stmt = stmt.order_by(WorldBook.updated_at.desc())
        result = await db.execute(stmt)
        books = result.scalars().all()
        return [WorldBookDTO.model_validate(b) for b in books]

    @classmethod
    async def get_world_book_detail(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        world_book_id: uuid.UUID,
    ) -> WorldBookDetailDTO:
        """获取世界书详情及全部条目。"""
        stmt = (
            select(WorldBook)
            .where(WorldBook.id == world_book_id)
            .options(selectinload(WorldBook.entries))
        )
        result = await db.execute(stmt)
        wb = result.scalar_one_or_none()
        if not wb:
            raise AppException(status_code=404, message="目标世界书不存在")
        if not wb.is_public and wb.user_id != user_id:
            raise AppException(status_code=403, message="无权访问该私有世界书")

        return WorldBookDetailDTO.model_validate(wb)

    @classmethod
    async def update_world_book(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        world_book_id: uuid.UUID,
        payload: WorldBookUpdate,
    ) -> WorldBookDTO:
        """更新世界书元数据。"""
        stmt = select(WorldBook).where(WorldBook.id == world_book_id, WorldBook.user_id == user_id)
        result = await db.execute(stmt)
        wb = result.scalar_one_or_none()
        if not wb:
            raise AppException(status_code=404, message="世界书不存在或无权修改")

        if payload.name is not None:
            wb.name = payload.name
        if payload.description is not None:
            wb.description = payload.description
        if payload.is_public is not None:
            wb.is_public = payload.is_public
        if payload.scan_depth is not None:
            wb.scan_depth = payload.scan_depth
        if payload.token_budget is not None:
            wb.token_budget = payload.token_budget
        if payload.character_id is not None:
            wb.character_id = payload.character_id

        await db.commit()
        await db.refresh(wb)
        return WorldBookDTO.model_validate(wb)

    @classmethod
    async def delete_world_book(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        world_book_id: uuid.UUID,
    ) -> None:
        """删除世界书。"""
        stmt = select(WorldBook).where(WorldBook.id == world_book_id, WorldBook.user_id == user_id)
        result = await db.execute(stmt)
        wb = result.scalar_one_or_none()
        if not wb:
            raise AppException(status_code=404, message="世界书不存在或无权删除")
        await db.delete(wb)
        await db.commit()

    @classmethod
    async def add_entry(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        world_book_id: uuid.UUID,
        payload: WorldBookEntryCreate,
    ) -> WorldBookEntryDTO:
        """向指定世界书添加新条目。"""
        stmt = select(WorldBook).where(WorldBook.id == world_book_id, WorldBook.user_id == user_id)
        result = await db.execute(stmt)
        wb = result.scalar_one_or_none()
        if not wb:
            raise AppException(status_code=404, message="世界书不存在或无权操作")

        entry = WorldBookEntry(
            world_book_id=world_book_id,
            keys=payload.keys,
            secondary_keys=payload.secondary_keys,
            selective_logic=payload.selective_logic,
            content=payload.content,
            comment=payload.comment,
            constant=payload.constant,
            enabled=payload.enabled,
            insertion_order=payload.insertion_order,
            position=payload.position,
        )
        db.add(entry)
        wb.entry_count += 1
        await db.commit()
        await db.refresh(entry)
        return WorldBookEntryDTO.model_validate(entry)

    @classmethod
    async def update_entry(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        entry_id: uuid.UUID,
        payload: WorldBookEntryUpdate,
    ) -> WorldBookEntryDTO:
        """更新世界书条目。"""
        stmt = (
            select(WorldBookEntry)
            .join(WorldBook)
            .where(WorldBookEntry.id == entry_id, WorldBook.user_id == user_id)
        )
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        if not entry:
            raise AppException(status_code=404, message="条目不存在或无权修改")

        if payload.keys is not None:
            entry.keys = payload.keys
        if payload.secondary_keys is not None:
            entry.secondary_keys = payload.secondary_keys
        if payload.selective_logic is not None:
            entry.selective_logic = payload.selective_logic
        if payload.content is not None:
            entry.content = payload.content
        if payload.comment is not None:
            entry.comment = payload.comment
        if payload.constant is not None:
            entry.constant = payload.constant
        if payload.enabled is not None:
            entry.enabled = payload.enabled
        if payload.insertion_order is not None:
            entry.insertion_order = payload.insertion_order
        if payload.position is not None:
            entry.position = payload.position

        await db.commit()
        await db.refresh(entry)
        return WorldBookEntryDTO.model_validate(entry)

    @classmethod
    async def delete_entry(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        entry_id: uuid.UUID,
    ) -> None:
        """删除条目。"""
        stmt = (
            select(WorldBookEntry)
            .join(WorldBook)
            .where(WorldBookEntry.id == entry_id, WorldBook.user_id == user_id)
            .options(selectinload(WorldBookEntry.world_book))
        )
        result = await db.execute(stmt)
        entry = result.scalar_one_or_none()
        if not entry:
            raise AppException(status_code=404, message="条目不存在或无权删除")

        wb = entry.world_book
        if wb and wb.entry_count > 0:
            wb.entry_count -= 1

        await db.delete(entry)
        await db.commit()

    @classmethod
    async def match_world_book_entries(
        cls,
        db: AsyncSession,
        character_id: uuid.UUID | None,
        user_id: uuid.UUID,
        user_text: str,
        recent_history: list[str] | None = None,
        token_budget_override: int | None = None,
    ) -> WorldBookMatchResultDTO:
        """执行世界书 RAG 混合扫描，匹配当前上下文所需的世界设定。

        1. 加载当前角色关联的世界书及公共世界书的所有启用条目；
        2. 将常驻条目 (constant=True) 强制纳入匹配列表；
        3. 构建 Aho-Corasick 关键词映射并在 (user_text + 最近历史) 中扫描；
        4. 经过次级关键词 Secondary Keys 逻辑过滤；
        5. 按 insertion_order 升序排序；
        6. 在 Token 预算限制下截断并组装为 Markdown Prompt。

        Args:
            db: 异步数据库 Session。
            character_id: 当前对话角色 ID。
            user_id: 当前用户 ID。
            user_text: 用户当前输入的文本。
            recent_history: 最近 N 轮历史消息文本。
            token_budget_override: 覆盖 Token 预算。

        Returns:
            WorldBookMatchResultDTO: 命中条目列表及组装后的 Prompt。
        """
        # 1. 查找关联的世界书 (支持当前用户、公共世界书以及绑定当前角色的世界书)
        from sqlalchemy import or_

        conditions = [
            (WorldBook.user_id == user_id),
            (WorldBook.is_public.is_(True)),
        ]
        if character_id:
            conditions.append(WorldBook.character_id == character_id)

        stmt = select(WorldBook).where(or_(*conditions))
        if character_id:
            stmt = stmt.where(
                (WorldBook.character_id == character_id) | (WorldBook.character_id.is_(None))
            )
        stmt = stmt.options(selectinload(WorldBook.entries))
        result = await db.execute(stmt)
        world_books = result.scalars().all()

        if not world_books:
            return WorldBookMatchResultDTO(matched_entries=[], formatted_prompt="", total_tokens=0)

        # 聚合所有启用的条目并进行内容指纹去重，防止重复导入导致 Token 爆炸
        seen_fingerprints: set[str] = set()
        all_entries: list[WorldBookEntry] = []
        max_budget = token_budget_override or 4096
        scan_depth = 5

        for wb in world_books:
            if wb.token_budget and wb.token_budget > max_budget:
                max_budget = wb.token_budget
            if wb.scan_depth:
                scan_depth = max(scan_depth, wb.scan_depth)
            for e in wb.entries:
                if not e.enabled:
                    continue
                # 基于标题 + 正文做指纹去重
                fp = f"{e.comment.strip()}:{e.content.strip()}"
                if fp in seen_fingerprints:
                    continue
                seen_fingerprints.add(fp)
                all_entries.append(e)

        if not all_entries:
            return WorldBookMatchResultDTO(matched_entries=[], formatted_prompt="", total_tokens=0)

        # 组装扫描文本 (用户最新输入 + 最近 scan_depth 轮历史)
        history_slice = (recent_history or [])[-scan_depth:]
        full_scan_text = f"{user_text}\n" + "\n".join(history_slice)

        matched_entries_map: dict[uuid.UUID, WorldBookEntry] = {}
        keyword_map: dict[str, list[uuid.UUID]] = {}

        # 区分常驻条目与关键词条目，同时将条目标题/备注也作为隐式触发词
        for entry in all_entries:
            if entry.constant:
                matched_entries_map[entry.id] = entry
            else:
                for k in entry.keys:
                    k_str = str(k).strip()
                    if k_str:
                        keyword_map.setdefault(k_str, []).append(entry.id)
                # 如果备注中有明确名词 (如 "阿黑颜" / "草薙剑")，也纳入扫描字典
                clean_comment = entry.comment.replace("_", "").replace("姿势/表情：", "").replace("技能–才艺:", "").strip()
                if len(clean_comment) >= 2:
                    keyword_map.setdefault(clean_comment, []).append(entry.id)

        # 3. Aho-Corasick 扫描关键词 (同时区分用户最新单条发言的直接命中)
        direct_hit_entry_ids = set(WorldBookScanner.scan_keywords(user_text, keyword_map))
        full_hit_entry_ids = WorldBookScanner.scan_keywords(full_scan_text, keyword_map)

        for entry in all_entries:
            if entry.id in full_hit_entry_ids or entry.id in direct_hit_entry_ids:
                # 4. 次级关键词过滤 (Secondary Keys)
                if WorldBookScanner.filter_secondary_keys(
                    full_scan_text, entry.secondary_keys, entry.selective_logic
                ):
                    matched_entries_map[entry.id] = entry

        if not matched_entries_map:
            return WorldBookMatchResultDTO(matched_entries=[], formatted_prompt="", total_tokens=0)

        # 5. 超级优先级排序:
        # 层级 0: 用户最新发言显式直接命中 (Explicit Hit) 绝对置顶
        # 层级 1: 常驻生效条目 (Constant) 按 insertion_order 排序
        # 层级 2: 上下文多轮历史命中条目 按 insertion_order 排序
        def calculate_entry_rank(e: WorldBookEntry) -> tuple[int, int]:
            if e.id in direct_hit_entry_ids or any(k in user_text for k in (e.keys or [])):
                return (0, e.insertion_order)
            if e.constant:
                return (1, e.insertion_order)
            return (2, e.insertion_order)

        sorted_entries = sorted(
            matched_entries_map.values(),
            key=calculate_entry_rank,
        )

        # 6. Token 预算动态截断与结构化 Markdown Prompt 组装
        selected_entries: list[WorldBookEntry] = []
        accumulated_tokens = 0
        prompt_lines: list[str] = [
            "【核心世界观与设定集 (World Book / Lorebook)】：",
            "以下是当前场景生效的最高设定准则，当剧情、动作或用户互动涉及对应设定时，你必须在神态描写、心理活动与台词中深入体现对应的具体表现与特征：",
        ]

        for entry in sorted_entries:
            entry_token_est = int(len(entry.content) * cls.TOKEN_FACTOR) + 12
            if accumulated_tokens + entry_token_est > max_budget:
                logger.info("世界书条目超过 Token 预算 (%d/%d)，跳过条目: %s", accumulated_tokens, max_budget, entry.comment)
                continue

            selected_entries.append(entry)
            accumulated_tokens += entry_token_est

            title = entry.comment or (entry.keys[0] if entry.keys else "设定")
            prompt_lines.append(f"- 【{title}】：{entry.content}")

        formatted_prompt = "\n".join(prompt_lines) if selected_entries else ""

        return WorldBookMatchResultDTO(
            matched_entries=[WorldBookEntryDTO.model_validate(e) for e in selected_entries],
            formatted_prompt=formatted_prompt,
            total_tokens=accumulated_tokens,
        )

    @classmethod
    async def import_sillytavern_json(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        payload: SillyTavernWorldBookImportDTO,
    ) -> WorldBookDetailDTO:
        """导入 SillyTavern V2/V3 格式的世界书 JSON。"""
        # 校验关联角色是否存在，避免外键异常
        character_id = payload.character_id
        if character_id:
            char_exists = await db.scalar(
                select(Character.id).where(Character.id == character_id)
            )
            if not char_exists:
                character_id = None

        wb = WorldBook(
            user_id=user_id,
            character_id=character_id,
            name=str(payload.name or "导入的世界书"),
            description=str(payload.description or "从 SillyTavern 导入"),
            is_public=False,
        )
        db.add(wb)
        await db.flush()

        raw_entries = payload.entries
        entry_list: list[dict[str, Any]] = []
        if isinstance(raw_entries, dict):
            entry_list = list(raw_entries.values())
        elif isinstance(raw_entries, list):
            entry_list = raw_entries

        pos_map: dict[Any, str] = {
            0: "before_char",
            1: "after_char",
            2: "top_an",
            3: "bottom_an",
            4: "at_depth",
            "0": "before_char",
            "1": "after_char",
            "2": "top_an",
            "3": "bottom_an",
            "4": "at_depth",
            "before_char": "before_char",
            "after_char": "after_char",
            "top_an": "top_an",
            "bottom_an": "bottom_an",
            "at_depth": "at_depth",
        }

        count = 0
        for idx, item in enumerate(entry_list):
            if not isinstance(item, dict):
                continue

            # 解析主关键词
            keys = item.get("key") or item.get("keys") or []
            if isinstance(keys, str):
                keys = [k.strip() for k in keys.split(",") if k.strip()]
            elif isinstance(keys, list):
                keys = [str(k).strip() for k in keys if str(k).strip()]
            else:
                keys = []

            # 解析次级关键词
            sec_keys = item.get("keysecondary") or item.get("secondary_keys") or []
            if isinstance(sec_keys, str):
                sec_keys = [k.strip() for k in sec_keys.split(",") if k.strip()]
            elif isinstance(sec_keys, list):
                sec_keys = [str(k).strip() for k in sec_keys if str(k).strip()]
            else:
                sec_keys = []

            # 设定内容
            content = str(item.get("content") or "").strip()
            if not content:
                continue

            # 插入位置规范化为 string
            raw_pos = item.get("position", "before_char")
            pos_str = pos_map.get(raw_pos, str(raw_pos) if raw_pos is not None else "before_char")

            # 优先级权重规范化为 int
            raw_order = item.get("order")
            try:
                insertion_order = int(raw_order) if raw_order is not None else (idx + 1) * 10
            except (ValueError, TypeError):
                insertion_order = (idx + 1) * 10

            # 次级逻辑规范化为 int
            raw_logic = item.get("selectiveLogic", item.get("selective_logic", 0))
            try:
                selective_logic = int(raw_logic) if raw_logic is not None else 0
            except (ValueError, TypeError):
                selective_logic = 0

            # 启用状态 (兼容 disable 与 enabled)
            if "disable" in item:
                enabled = not bool(item.get("disable"))
            elif "enabled" in item:
                enabled = bool(item.get("enabled"))
            else:
                enabled = True

            # 条目备注
            comment = str(item.get("comment") or f"条目 {idx + 1}")[:255]

            # 常驻开关
            constant = bool(item.get("constant", False))

            entry = WorldBookEntry(
                world_book_id=wb.id,
                keys=keys,
                secondary_keys=sec_keys,
                selective_logic=selective_logic,
                content=content,
                comment=comment,
                constant=constant,
                enabled=enabled,
                insertion_order=insertion_order,
                position=pos_str,
            )
            db.add(entry)
            count += 1

        wb.entry_count = count
        await db.commit()
        await db.refresh(wb)
        return await cls.get_world_book_detail(db, user_id=user_id, world_book_id=wb.id)

    @classmethod
    async def export_sillytavern_json(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        world_book_id: uuid.UUID,
    ) -> dict[str, Any]:
        """将世界书导出为 100% 兼容 SillyTavern 的 JSON 字典结构。"""
        detail = await cls.get_world_book_detail(db, user_id=user_id, world_book_id=world_book_id)

        entries_dict: dict[str, Any] = {}
        for idx, e in enumerate(detail.entries):
            entries_dict[str(idx)] = {
                "uid": idx,
                "key": e.keys,
                "keysecondary": e.secondary_keys,
                "selectiveLogic": e.selective_logic,
                "content": e.content,
                "comment": e.comment,
                "constant": e.constant,
                "enabled": e.enabled,
                "order": e.insertion_order,
                "position": e.position,
            }

        return {
            "name": detail.name,
            "description": detail.description,
            "scan_depth": detail.scan_depth,
            "token_budget": detail.token_budget,
            "entries": entries_dict,
        }
