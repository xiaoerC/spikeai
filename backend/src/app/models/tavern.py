"""SillyTavern (酒馆) 平台级全局预设与调音台数据模型。

用于 Admin 管理员统一配置、版本化管理及热发布全平台生效的 Transformer 提示词排版流水线与大模型物理采样超参数。

Usage:
    >>> from app.models.tavern import SystemTavernPreset
    >>> preset = SystemTavernPreset(preset_name="仓鼠之神V2", is_active=True, config={...})
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.core.database import Base


class SystemTavernPreset(Base):
    """平台级酒馆全局生效预设实体表。"""

    __tablename__ = "system_tavern_presets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="预设记录唯一主键 UUID",
    )
    preset_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="预设展示名称 (如 '仓鼠之神V2', '文学沉浸创作版')",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="是否为当前全平台大模型接管全局生效预设",
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="预设备注或变更说明",
    )
    config: Mapped[dict[str, Any]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        doc="完整的 TavernPresetConfig 序列化配置结构 (含 78 项流水线及采样参数)",
    )
    updated_by: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        doc="最后修改此预设的管理员账户或标识",
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
