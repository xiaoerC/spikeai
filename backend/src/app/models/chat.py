"""AI 对话、DAG 剧情分支树、主控与叙梦面板领域数据模型。

实现 Git 级别版本控制的剧情分支链（Parent-Pointer 模型）、双向消息与 Token 审计、
主控面板 38 变量矩阵以及叙梦 6 大 Tab 状态机持久化。

Usage:
    >>> from app.models.chat import ChatSession, StoryBranch, ChatMessage
    >>> from sqlalchemy import select
    >>> stmt = select(ChatSession).where(ChatSession.user_id == user_id)
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


class ChatSession(Base):
    """对话会话核心表。"""

    __tablename__ = "chat_sessions"
    __table_args__ = (
        Index("idx_chat_sessions_user_updated", "user_id", "updated_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        doc="会话全局唯一 UUID",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="用户 ID",
    )
    character_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="对话目标角色 ID",
    )
    current_branch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        doc="当前激活的剧情分支 ID",
    )
    current_model_id: Mapped[str] = mapped_column(
        String(64),
        default="glm-5.2-o1",
        nullable=False,
        doc="当前选中的模型标识 (如 glm-5.2-o1 / claude-3-5-sonnet)",
    )
    mode: Mapped[str] = mapped_column(
        String(32),
        default="story",
        nullable=False,
        doc="对话模式 (story: 剧情模式 / room: 聊天室模式)",
    )
    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="是否置顶会话",
    )
    remark: Mapped[str] = mapped_column(
        String(255),
        default="",
        nullable=False,
        doc="用户自定义备注",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="会话创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="会话最后活跃时间",
    )

    # 关联关系
    user: Mapped["User"] = relationship("User", back_populates="chat_sessions")
    character: Mapped["Character"] = relationship("Character", back_populates="chat_sessions")
    branches: Mapped[list["StoryBranch"]] = relationship(
        "StoryBranch",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
    )
    control_panel: Mapped["ChatControlPanel"] = relationship(
        "ChatControlPanel",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )
    narrative_state: Mapped["ChatNarrativeState"] = relationship(
        "ChatNarrativeState",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan",
    )


class StoryBranch(Base):
    """剧情平行分支表 (DAG 分支拓扑)。"""

    __tablename__ = "story_branches"
    __table_args__ = (
        Index("idx_story_branches_session", "session_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="分支 UUID",
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="关联会话 ID",
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="分支名称 (如 '🌿 主线剧情', '🔀 分支 1：独自探查')",
    )
    parent_branch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("story_branches.id", ondelete="SET NULL"),
        nullable=True,
        doc="父分支 ID (开辟新分支时的来源分支)",
    )
    fork_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        doc="分叉发生的历史消息节点 ID",
    )
    is_main: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        doc="是否为主线分支",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="分支开辟时间",
    )

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="branches")
    messages: Mapped[list["ChatMessage"]] = relationship(
        "ChatMessage",
        back_populates="branch",
        cascade="all, delete-orphan",
    )


class ChatMessage(Base):
    """消息表 (DAG 链式节点，包含 Parent-Pointer、Thinking 流与 Token 审计)。"""

    __tablename__ = "chat_messages"
    __table_args__ = (
        Index("idx_chat_messages_session_branch", "session_id", "branch_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="消息全局唯一 UUID",
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="关联会话 ID",
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("story_branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        doc="所属分支 ID",
    )
    sender: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        doc="发送者角色 (user / ai / system)",
    )
    character_name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        doc="显示发言者名称",
    )
    avatar_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="发言者头像 URL",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="消息正文 Markdown",
    )
    thinking_content: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="AI 深度思考思维链内容 (<thinking> 标签内容)",
    )
    input_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="本次生成输入 Token 数",
    )
    output_tokens: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="本次生成输出 Token 数",
    )
    parent_message_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_messages.id", ondelete="SET NULL"),
        nullable=True,
        doc="父消息指针，用于自底向上追溯线性对话历史",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="消息产生时间",
    )

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="messages")
    branch: Mapped["StoryBranch"] = relationship("StoryBranch", back_populates="messages")


class ChatControlPanel(Base):
    """主控面板状态表 (包含 38 变量矩阵、自定义人设、指令、记忆区块与正则替换链)。"""

    __tablename__ = "chat_control_panels"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        primary_key=True,
        doc="关联会话 ID",
    )
    user_name: Mapped[str] = mapped_column(
        String(64),
        default="{{user}}",
        nullable=False,
        doc="用户在对话中的代称",
    )
    user_persona: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="玩家人设与背景设定",
    )
    custom_prompt: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="自定义前置/后置指令 Prompt",
    )
    variables: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=dict,
        nullable=False,
        doc="38 个 RPG 角色数值变量矩阵 (variable_1 ~ variable_38)",
    )
    memory_blocks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="手动创建的长期记忆区块列表",
    )
    text_replacements: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="正则文本替换规则链 ([{from: '...', to: '...'}])",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="主控面板最后保存时间",
    )

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="control_panel")


class ChatNarrativeState(Base):
    """叙梦面板 6 大子 Tab 状态机持久化表。"""

    __tablename__ = "chat_narrative_states"

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("chat_sessions.id", ondelete="CASCADE"),
        primary_key=True,
        doc="关联会话 ID",
    )
    date_text: Mapped[str] = mapped_column(
        String(64),
        default="",
        nullable=False,
        doc="当前剧情日期 (如 '2026-07-06（周一）')",
    )
    time_text: Mapped[str] = mapped_column(
        String(32),
        default="",
        nullable=False,
        doc="当前剧情时间 (如 '15:20')",
    )
    location: Mapped[str] = mapped_column(
        String(128),
        default="",
        nullable=False,
        doc="当前剧情所在地点",
    )
    present_characters: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="当前在场角色列表",
    )
    player_states: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="玩家状态指标卡片与数值 (如家中名声、好感度等)",
    )
    consumables: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="背包消耗品列表",
    )
    important_items: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="背包重要物品列表",
    )
    skills: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="技能库与已装备技能列表",
    )
    social_relations: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="社交四宫格与 NPC 好感度列表",
    )
    tasks: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="进行中/已完成任务列表",
    )
    history_events: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="按星期分组的历史事件时间轴列表",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        doc="状态机最后刷新时间",
    )

    session: Mapped["ChatSession"] = relationship("ChatSession", back_populates="narrative_state")
