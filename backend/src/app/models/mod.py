"""Mod 模组生态与用户自定义中心领域数据模型。

包含 Mod 广场模组、用户激活 Mod 优先级矩阵 (带最高优先级逆序规则)、
Mod 精选/个人合集以及自定义（人设、快捷指令、画师串 Prompt、总结提示词、记忆增强模型）。

Usage:
    >>> from app.models.mod import ModItem, UserActiveMod, ModCollection, UserCustomItem
    >>> from sqlalchemy import select
    >>> stmt = select(ModItem).where(ModItem.status == "published")
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class ModItem(Base):
    """Mod 模组主表。"""

    __tablename__ = "mods"
    __table_args__ = (
        Index("idx_mods_category_status", "category_tag", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="Mod 全局唯一 UUID",
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="作者用户 ID",
    )
    title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        doc="Mod 标题",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Mod 详细说明",
    )
    category_tag: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="分类标签 (worldbook: 世界书 / system: 系统提示 / command: 指令 / regex: 正则 / artist: 画师)",
    )
    price: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="购买所需星元 (0 为免费)",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="published",
        nullable=False,
        doc="发布状态 (draft: 草稿 / published: 已发布)",
    )
    entries: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="Mod 包含的具体条目列表 (世界书/系统提示/正则词条等)",
    )
    downloads: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="下载/使用次数",
    )
    likes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="获赞数",
    )
    rating: Mapped[float] = mapped_column(
        Float,
        default=5.0,
        nullable=False,
        doc="平均评分 (1.0~5.0)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="最后更新时间",
    )

    author: Mapped["User"] = relationship("User", back_populates="mods")
    active_records: Mapped[list["UserActiveMod"]] = relationship(
        "UserActiveMod",
        back_populates="mod",
        cascade="all, delete-orphan",
    )


class UserActiveMod(Base):
    """用户已激活 Mod 优先级矩阵表。

    priority_order 越大，在组装 Prompt 时排在越靠后（更靠近最新输入，Transformer 注意力权重最高）。
    """

    __tablename__ = "user_active_mods"
    __table_args__ = (
        UniqueConstraint("user_id", "mod_id", name="uq_user_mod"),
        Index("idx_user_active_mods_order", "user_id", "priority_order"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="用户 ID",
    )
    mod_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mods.id", ondelete="CASCADE"),
        nullable=False,
        doc="Mod ID",
    )
    priority_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="优先级排序号 (数字越大优先级越高)",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        doc="是否当前激活生效",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="添加时间",
    )

    user: Mapped["User"] = relationship("User", back_populates="active_mods")
    mod: Mapped["ModItem"] = relationship("ModItem", back_populates="active_records")


class ModCollection(Base):
    """Mod 合集表 (用户打包收藏或官方精选)。"""

    __tablename__ = "mod_collections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="合集 UUID",
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="创建者 ID",
    )
    title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="合集标题",
    )
    description: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="合集描述",
    )
    cover_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="合集封面图 URL",
    )
    mod_ids: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="包含的 Mod ID 列表",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="创建时间",
    )

    author: Mapped["User"] = relationship("User")


class UserCustomItem(Base):
    """用户自定义配置项表 (人设、指令、画师串、总结词、记忆模型)。"""

    __tablename__ = "user_custom_items"
    __table_args__ = (
        Index("idx_user_custom_type", "user_id", "type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="配置项 UUID",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="所属用户 ID",
    )
    type: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="自定义类型 (persona / command / artist / summary_prompt / memory_model)",
    )
    title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="名称/标题",
    )
    content: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=dict,
        nullable=False,
        doc="详细配置数据 (正文、Prompt、正负向词条、模型参数等)",
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="是否设为默认生效项",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="更新时间",
    )

    user: Mapped["User"] = relationship("User")
