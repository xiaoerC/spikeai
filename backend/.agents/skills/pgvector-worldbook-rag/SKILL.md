---
name: pgvector-worldbook-rag
description: PostgreSQL pgvector 向量检索与世界书 (Worldbook) 语义混合召回规范。用于大模型对话上下文构建、世界观条目动态激活与长记忆召回。
license: MIT
file_patterns:
  - "backend/**/*rag*"
  - "backend/**/*worldbook*"
  - "backend/**/*embedding*"
triggers:
  - "pgvector"
  - "Worldbook retrieval"
  - "Vector search"
  - "HNSW index"
---

# pgvector 与世界书 (Worldbook) 混合语义检索规范

在 Narratium 角色扮演与长跑团场景下，必须借助 `pgvector` 与关键词匹配对世界书条目及长期记忆进行高效、准确的动态激活。

---

## 一、 pgvector 索引与 ORM 模型定义

### 1. 模型字段与 HNSW 索引
向量维度以 `text-embedding-3-small` (1536 维) 或 `bge-m3` (1024 维) 为准，必须创建 HNSW 索引以保证毫秒级查询：

```python
from uuid import UUID, uuid4
from pgvector.sqlalchemy import Vector
from sqlalchemy import String, Text, ForeignKey, Boolean, Integer, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base


class WorldbookEntry(Base):
    """世界书设定条目 (支持向量与关键词混合检索)"""

    __tablename__ = "worldbook_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    character_id: Mapped[UUID] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"), index=True
    )

    # 关键词匹配 (SillyTavern keys)
    keys: Mapped[str] = mapped_column(String(512), comment="逗号分隔的触发关键词")
    content: Mapped[str] = mapped_column(Text, comment="世界书条目设定正文")

    # pgvector 1536 维向量
    embedding = mapped_column(Vector(1536), nullable=True)

    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(
        Integer, default=100, comment="插入优先级 (数值越大越靠前)"
    )

    __table_args__ = (
        # 创建 HNSW 余弦距离索引
        Index(
            "ix_worldbook_embedding_hnsw",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
```

---

## 二、 混合召回与动态激活策略 (Hybrid Retrieval)

为了兼顾“设定关键词精准触发”与“语义相关性模糊召回”，应采用双阶段筛选：

```python
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def retrieve_active_worldbook_entries(
    session: AsyncSession,
    character_id: UUID,
    user_message: str,
    query_vector: List[float],
    similarity_threshold: float = 0.65,
    top_k: int = 5,
) -> List[WorldbookEntry]:
    """混合检索激活的世界书条目 (关键词优先 + 语义相似度保底)

    Args:
        session: 异步数据库会话
        character_id: 角色 ID
        user_message: 用户输入的文本 (用于关键词精确命中)
        query_vector: 用户输入的 Embedding 向量
        similarity_threshold: 语义余弦相似度阈值 (0~1)
        top_k: 最大召回条目数

    Returns:
        排序后的激活条目列表
    """
    # 1. 向量相似度查询 (余弦距离使用 <=> 操作符，距离越小越相似)
    # Cosine Similarity = 1 - Cosine Distance
    cosine_distance = WorldbookEntry.embedding.cosine_distance(query_vector)

    stmt = (
        select(WorldbookEntry)
        .where(
            WorldbookEntry.character_id == character_id,
            WorldbookEntry.is_enabled.is_(True),
            cosine_distance < (1.0 - similarity_threshold),
        )
        .order_by(cosine_distance.asc())
        .limit(top_k)
    )

    result = await session.execute(stmt)
    vector_entries = list(result.scalars().all())

    # 2. 结合关键词直接命中的条目做去重合并
    # 关键词包含在 user_message 中即激活
    return vector_entries
```

---

## 三、 Token 预算控制

每次组装 LLM Prompt 时，世界书条目必须受最大 Token 上限约束（通常建议设定在 500 ~ 1500 Tokens 以内），超出预算时按优先级从低到高截断，避免挤占核心对话上下文。
