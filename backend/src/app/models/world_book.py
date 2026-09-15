"""世界书 (World Book / Character Lorebook) 领域模型。

支持 SillyTavern V2/V3 规范的世界书与条目、Aho-Corasick 关键词扫描、
次级条件过滤 (Secondary Keys) 以及 pgvector 语义向量检索。

Usage:
    >>> from app.models.world_book import WorldBook, WorldBookEntry
    >>> wb = WorldBook(name="火影忍者疾风传世界观", user_id=user_id)
    >>> entry = WorldBookEntry(world_book_id=wb.id, keys=["草薙剑", "佐助"], content="佐助留给博人的佩剑...")
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.character import Character
    from app.models.user import User


class WorldBook(Base):
    """世界书元数据表。"""

    __tablename__ = "world_books"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="世界书全局唯一 ID",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="创建者用户 ID",
    )
    character_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="关联角色 ID (为空表示全局公共世界书)",
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        comment="世界书名称",
    )
    description: Mapped[str] = mapped_column(
        Text,
        default="",
        comment="世界书描述",
    )
    entry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="包含条目总数",
    )
    is_public: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否公开分享至世界书广场",
    )
    scan_depth: Mapped[int] = mapped_column(
        Integer,
        default=5,
        comment="扫描历史消息的深度 (轮数)",
    )
    token_budget: Mapped[int] = mapped_column(
        Integer,
        default=2048,
        comment="注入 Prompt 的最大 Token 预算上限",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # 关联关系
    entries: Mapped[list["WorldBookEntry"]] = relationship(
        "WorldBookEntry",
        back_populates="world_book",
        cascade="all, delete-orphan",
        order_by="WorldBookEntry.insertion_order.asc()",
    )

    __table_args__ = (
        Index("idx_world_books_user_char", "user_id", "character_id"),
    )


class WorldBookEntry(Base):
    """世界书具体设定条目表。"""

    __tablename__ = "world_book_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="条目全局唯一 ID",
    )
    world_book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("world_books.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属世界书 ID",
    )
    
    # 关键词匹配规则 (SillyTavern 协议兼容)
    keys: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        comment="主触发关键词列表",
    )
    secondary_keys: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        comment="次级关键词列表 (用于逻辑过滤)",
    )
    selective_logic: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="次级过滤逻辑: 0: AND ANY, 1: NOT ALL, 2: NOT ANY",
    )
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="注入 Prompt 的设定具体内容",
    )
    comment: Mapped[str] = mapped_column(
        String(256),
        default="",
        comment="条目备注说明 (如角色阵营/秘术分类)",
    )
    
    constant: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        comment="是否常驻生效 (忽略关键词扫描，永远注入)",
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        comment="是否启用此条目",
    )
    insertion_order: Mapped[int] = mapped_column(
        Integer,
        default=100,
        comment="插入优先级权重 (数字越小优先级越高)",
    )
    position: Mapped[str] = mapped_column(
        String(32),
        default="before_char",
        comment="Prompt 插入位置 (before_char / after_char / top_an)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # 关联关系
    world_book: Mapped["WorldBook"] = relationship(
        "WorldBook",
        back_populates="entries",
    )

    __table_args__ = (
        Index("idx_world_book_entries_wb_order", "world_book_id", "insertion_order"),
    )
