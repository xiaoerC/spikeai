"""大模型 (LLM) API 连接渠道与模型上架配置数据模型。

用于 Admin 管理员统一管理上游大模型 API 提供商 (如 OpenAI, DeepSeek, SiliconFlow, Ollama 等)、
多渠道密钥轮询/管理、连通性探测以及配置哪些模型上架推送给客户端 (C 端) 用户选择使用。

Usage:
    >>> from app.models.llm import SystemLLMProvider
    >>> provider = SystemLLMProvider(
    ...     name="DeepSeek 官方 API",
    ...     provider_type="openai",
    ...     base_url="https://api.deepseek.com/v1",
    ...     api_key="sk-xxxxxx",
    ...     models=[{
    ...         "id": "deepseek-chat",
    ...         "display_name": "DeepSeek-V3 旗舰大模型",
    ...         "is_enabled": True,
    ...         "is_public": True,
    ...         "cost": 1,
    ...     }]
    ... )
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from app.core.database import Base


class SystemLLMProvider(Base):
    """平台级大模型 API 提供商与连接配置实体表。"""

    __tablename__ = "system_llm_providers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="渠道唯一标识符 UUID",
    )
    name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        doc="渠道展示名称 (例如 'DeepSeek 官方 API', '硅基流动 SiliconFlow', '自建 OneAPI 中转')",
    )
    provider_type: Mapped[str] = mapped_column(
        String(32),
        default="openai",
        nullable=False,
        doc="协议类型 ('openai'=兼容协议, 'anthropic'=Claude 原生, 'gemini'=谷歌原生, 'ollama'=本地)",
    )
    base_url: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="基础 API 端点 Base URL (如 'https://api.deepseek.com/v1')",
    )
    api_key: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
        default="",
        doc="API 密钥 Bearer Token",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        doc="是否启用该渠道",
    )
    timeout_seconds: Mapped[int] = mapped_column(
        Integer,
        default=60,
        nullable=False,
        doc="接口请求超时时间 (秒)",
    )
    custom_headers: Mapped[dict[str, str]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=dict,
        doc="自定义 HTTP Headers 键值对字典",
    )
    models: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB().with_variant(JSON(), "sqlite"),
        nullable=False,
        default=list,
        doc="该渠道下纳管的模型列表 (包含 id, display_name, is_enabled, is_public, cost 等)",
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="渠道备注说明",
    )
    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="排序权重 (越大越靠前)",
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
