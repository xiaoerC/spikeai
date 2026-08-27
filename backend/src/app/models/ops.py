"""社区与运营支持领域数据模型。

包含平台公告 (Notice)、运营活动 (Activity) 与问卷调查 (Survey)。

Usage:
    >>> from app.models.ops import Notice, Activity, Survey
    >>> from sqlalchemy import select
    >>> stmt = select(Notice).order_by(Notice.created_at.desc())
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.core.database import Base


class Activity(Base):
    """运营活动表。"""

    __tablename__ = "activities"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="活动标题",
    )
    tag: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="活动标签 (如 '招募', '征集', '福利')",
    )
    reward_text: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="奖励描述 (如 '丰厚月华', '1000星元')",
    )
    date_range: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        doc="活动时间范围 (如 '长期有效', '2026.07.01 - 2026.08.31')",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
        doc="活动状态 (active / ended)",
    )
    rules: Mapped[list[str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="活动规则条目列表",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="发布时间",
    )


class Notice(Base):
    """系统公告与更新日志表。"""

    __tablename__ = "notices"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="公告标题",
    )
    category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="公告分类 (如 '系统公告', '更新日志', '活动公告')",
    )
    date_text: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="显示日期 (如 '2026-07-06')",
    )
    badge_type: Mapped[str] = mapped_column(
        String(32),
        default="notice",
        nullable=False,
        doc="徽章类型 (update: 更新 / notice: 重要 / event: 活动)",
    )
    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="摘要简介",
    )
    content_html: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
        doc="富文本详情 HTML",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="发布时间",
    )


class Survey(Base):
    """用户问卷调查表。"""

    __tablename__ = "surveys"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    title: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        doc="问卷标题",
    )
    reward_star: Mapped[int] = mapped_column(
        Integer,
        default=50,
        nullable=False,
        doc="完成问卷赠送星元数",
    )
    category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        doc="问卷分类 (如 '模型体验', '功能体验', 'Mod生态')",
    )
    duration_text: Mapped[str] = mapped_column(
        String(32),
        default="约3分钟",
        nullable=False,
        doc="预计用时描述",
    )
    status: Mapped[str] = mapped_column(
        String(32),
        default="active",
        nullable=False,
        doc="状态 (active / completed)",
    )
    questions: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        default=list,
        nullable=False,
        doc="问卷题目列表 (题干、选项、类型等)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        doc="发布时间",
    )
