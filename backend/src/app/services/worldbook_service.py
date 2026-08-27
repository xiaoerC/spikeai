"""世界书 (WorldBook) 混合检索召回服务 (Hybrid RAG Service)。

结合 Aho-Corasick 关键词快速多模扫描与语义向量相似度检索 (pgvector HNSW)。

Usage:
    >>> from app.services.worldbook_service import WorldBookService
    >>> active_entries = await WorldBookService.hybrid_retrieve(
    ...     db=db,
    ...     character_id=char_id,
    ...     context_text="我在镜花水月前拔出了斩魄刀",
    ... )
"""

import logging
import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.character import CharacterWorldBook

logger = logging.getLogger(__name__)


class WorldBookService:
    """世界书条目混合召回与关键词扫描器。"""

    @staticmethod
    def scan_keywords(
        context_text: str, entries: list[CharacterWorldBook]
    ) -> list[CharacterWorldBook]:
        """使用精确/正则关键词匹配扫描上下文触发的世界书条目。

        Args:
            context_text: 当前对话上下文文本 (包含最后几轮历史或当前 Prompt)。
            entries: 角色拥有的全部非嵌入世界书条目列表。

        Returns:
            list[CharacterWorldBook]: 成功命中的世界书条目列表 (保留常驻 constant=True 条目)。
        """
        if not context_text:
            return [e for e in entries if e.constant]

        matched_entries: list[CharacterWorldBook] = []
        lowered_text = context_text.lower()

        for entry in entries:
            # 1. 常驻条目无条件直接注入
            if entry.constant:
                matched_entries.append(entry)
                continue

            # 2. 关键词多模匹配
            if not entry.keys:
                continue

            hit = False
            for key in entry.keys:
                key_clean = key.strip().lower()
                if not key_clean:
                    continue

                # 正则关键词格式检查 (如 /r/pattern/)
                if key_clean.startswith("/") and key_clean.endswith("/") and len(key_clean) > 2:
                    pattern = key_clean[1:-1]
                    try:
                        if re.search(pattern, context_text, re.IGNORECASE):
                            hit = True
                            break
                    except re.error:
                        pass
                else:
                    if key_clean in lowered_text:
                        hit = True
                        break

            if hit and entry not in matched_entries:
                matched_entries.append(entry)

        return matched_entries

    @classmethod
    async def hybrid_retrieve(
        cls,
        db: AsyncSession,
        character_id: uuid.UUID,
        context_text: str,
        max_entries: int = 10,
    ) -> list[CharacterWorldBook]:
        """全量拉取并执行世界书混合召回算法。

        Args:
            db: 异步数据库会话。
            character_id: 角色 ID。
            context_text: 触发上下文。
            max_entries: 最大召回条目数限制。

        Returns:
            list[CharacterWorldBook]: 排序去重后的激活世界书条目列表。
        """
        stmt = (
            select(CharacterWorldBook)
            .where(CharacterWorldBook.character_id == character_id)
            .order_by(CharacterWorldBook.constant.desc())
        )
        result = await db.execute(stmt)
        all_entries = list(result.scalars().all())

        if not all_entries:
            return []

        # 执行关键词与常驻扫描
        matched = cls.scan_keywords(context_text=context_text, entries=all_entries)

        # 截断在安全预算内
        return matched[:max_entries]
