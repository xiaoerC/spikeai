"""角色卡与世界书领域数据模型。

包含角色基础设定、10项指标统计、世界书语义条目、角色评论与用户互动（点赞/收藏/评分）。

Usage:
    >>> from app.models.character import Character, CharacterMetrics, CharacterWorldBook
    >>> from sqlalchemy import select
    >>> stmt = select(Character).where(Character.status == "published")
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
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
    from app.models.chat import ChatSession
    from app.models.user import User


class Character(Base):
    """角色卡主表。"""

    __tablename__ = "characters"
    __table_args__ = (
        Index("idx_characters_category_status", "category", "status"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="角色卡全局唯一 UUID",
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="创作者用户 ID",
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        index=True,
        doc="角色/故事名称",
    )
    avatar_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="角色立绘头像 URL",
    )
    banner_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="角色卡大封面背景图 URL",
    )
    category: Mapped[str] = mapped_column(
        String(32),
        default="story",
        nullable=False,
        doc="大分类 (story: 剧情卡 / nsfw: 绅士卡 / rpg: 跑团数值卡)",
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="角色简介与背景描述",
    )
    personality: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="角色性格特征描述",
    )
    scenario: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="故事发生情境与时空背景",
    )
    first_mes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="首次对话开场白问候语",
    )
    alternate_greetings: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="备选开场白列表",
    )
    system_prompt: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="专属系统前置提示词 (System Prompt)",
    )
    post_history_instructions: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="对话历史后置注入指令",
    )
    prologue_title: Mapped[str] = mapped_column(
        String(128),
        default="序幕",
        nullable=False,
        doc="序幕卡片标题 (如 Dolce Notte)",
    )
    prologue_html: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="序幕富文本排版 HTML (叙梦专属扩展)",
    )
    creator_notes: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="创作者留言/作者的话 (Markdown 格式)",
    )
    tags: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="角色标签列表",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="published",
        nullable=False,
        doc="发布状态 (draft: 草稿 / published: 已上架 / private: 私有)",
    )
    settings_word_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="设定总字数",
    )
    version: Mapped[str] = mapped_column(
        String(32),
        default="1.0.0",
        nullable=False,
        doc="角色卡版本号",
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

    # 关联关系
    author: Mapped["User"] = relationship("User", back_populates="characters")
    metrics: Mapped["CharacterMetrics"] = relationship(
        "CharacterMetrics",
        back_populates="character",
        uselist=False,
        cascade="all, delete-orphan",
    )
    worldbooks: Mapped[list["CharacterWorldBook"]] = relationship(
        "CharacterWorldBook",
        back_populates="character",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list["CharacterComment"]] = relationship(
        "CharacterComment",
        back_populates="character",
        cascade="all, delete-orphan",
        order_by="desc(CharacterComment.created_at)",
    )
    interactions: Mapped[list["CharacterInteraction"]] = relationship(
        "CharacterInteraction",
        back_populates="character",
        cascade="all, delete-orphan",
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="character",
        cascade="all, delete-orphan",
    )


class CharacterMetrics(Base):
    """角色卡 10 项核心数据指标统计表。"""

    __tablename__ = "character_metrics"
    __table_args__ = (
        Index("idx_character_metrics_hotness", "hotness"),
        Index("idx_character_metrics_trend", "trend_score"),
    )

    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        primary_key=True,
        doc="关联角色 ID",
    )
    hotness: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="综合热度分数",
    )
    trend_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="趋势增长分 (如 5.41)",
    )
    chat_count: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        doc="累计对话消息数",
    )
    like_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="点赞数",
    )
    favorite_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="收藏数",
    )
    import_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="导入/下载次数",
    )
    rating: Mapped[float] = mapped_column(
        Float,
        default=5.0,
        nullable=False,
        doc="用户平均评分 (1.0~5.0)",
    )
    rating_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="评分人数",
    )
    total_tokens: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        doc="累计消耗 Token 数",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="统计最后刷新时间",
    )

    character: Mapped["Character"] = relationship("Character", back_populates="metrics")


class CharacterWorldBook(Base):
    """世界书条目表 (支持关键词匹配与 pgvector HNSW 语义检索)。"""

    __tablename__ = "character_worldbooks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="条目 UUID",
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="关联角色 ID",
    )
    keys: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="触发关键词列表 (如 ['镜花水月', '斩魄刀'])",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="世界书设定正文",
    )
    constant: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="是否为常驻条目 (True 时无条件注入)",
    )
    position: Mapped[str] = mapped_column(
        String(32),
        default="after_char",
        nullable=False,
        doc="注入位置 (before_char / after_char / system_top)",
    )
    embedding: Mapped[list[float] | None] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=True,
        doc="语义嵌入向量 (1536维，pgvector/JSON)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="条目创建时间",
    )

    character: Mapped["Character"] = relationship("Character", back_populates="worldbooks")


class CharacterComment(Base):
    """角色卡用户评论表。"""

    __tablename__ = "character_comments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="评论 UUID",
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="关联角色 ID",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="发表评论用户 ID",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="评论内容",
    )
    likes: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="评论获赞数",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="评论发表时间",
    )

    character: Mapped["Character"] = relationship("Character", back_populates="comments")
    user: Mapped["User"] = relationship("User")


class CharacterInteraction(Base):
    """用户与角色卡互动状态表 (点赞、收藏、评分)。"""

    __tablename__ = "character_interactions"
    __table_args__ = (
        Index("idx_character_user_interaction", "character_id", "user_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        doc="角色 ID",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        doc="用户 ID",
    )
    is_liked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="是否已点赞",
    )
    is_favorited: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="是否已收藏",
    )
    user_rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="用户给出的评分 (1~5 星)",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="互动更新时间",
    )

    character: Mapped["Character"] = relationship("Character", back_populates="interactions")
    user: Mapped["User"] = relationship("User")
