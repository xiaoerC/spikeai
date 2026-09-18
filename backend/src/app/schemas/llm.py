"""大模型 (LLM) 渠道连接与客户端模型上架配置 Pydantic DTO 契约。

包含管理端多渠道管理、在线连通性测试、/v1/models 远端拉取以及客户端 C 端安全公开模型模型。

Usage:
    >>> from app.schemas.llm import LLMProviderCreate, LLMModelItem
    >>> item = LLMModelItem(id="deepseek-chat", display_name="DeepSeek-V3")
"""

import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class LLMModelItem(BaseModel):
    """单个模型纳管配置项。"""

    id: str = Field(description="上游真实模型标识 (如 'deepseek-chat', 'gpt-4o')")
    display_name: str = Field(default="", description="客户端展示名称 (如 'DeepSeek-V3 旗舰大模型')")
    is_enabled: bool = Field(default=True, description="是否在平台开启使用")
    is_public: bool = Field(default=True, description="是否上架推送至客户端 (C端) 供用户选择")
    is_default: bool = Field(default=False, description="是否为全平台默认首选模型")
    supports_streaming: bool = Field(default=True, description="是否支持 SSE 流式生成")
    supports_reasoning: bool = Field(default=False, description="是否为深度思考/推理模型 (如 R1, 输出 reasoning_content)")
    cost: int = Field(default=1, ge=0, description="调用单次消耗点数 (金星/月亮)")
    family: str = Field(default="deepseek", description="模型所属家族 ('deepseek', 'gpt', 'claude', 'gemini', 'other')")
    context_limit: int = Field(default=64000, description="上下文窗口大小 (Tokens)")
    sort_order: int = Field(default=0, description="排序权重 (越大越靠前)")
    preset_id: str | None = Field(default=None, description="绑定的专属酒馆调音预设唯一ID (若为空则跟随全局默认激活预设)")
    preset_name: str | None = Field(default=None, description="绑定的专属预设展示名称 (冗余字段方便快速展示与排查)")


class LLMProviderCreate(BaseModel):
    """创建新渠道请求入参。"""

    name: str = Field(min_length=1, max_length=64, description="渠道展示名称")
    provider_type: str = Field(default="openai", description="协议类型 ('openai', 'anthropic', 'gemini', 'ollama')")
    base_url: str = Field(min_length=1, max_length=255, description="基础 API 端点 Base URL")
    api_key: str = Field(default="", max_length=512, description="API 密钥 Bearer Token")
    is_active: bool = Field(default=True, description="是否激活启用")
    timeout_seconds: int = Field(default=60, ge=5, le=300, description="超时时间 (秒)")
    custom_headers: dict[str, str] = Field(default_factory=dict, description="自定义 HTTP 请求头字典")
    models: list[LLMModelItem] = Field(default_factory=list, description="纳管的模型清单")
    description: str | None = Field(default=None, max_length=255, description="备注说明")
    sort_order: int = Field(default=0, description="排序权重")


class LLMProviderUpdate(BaseModel):
    """更新渠道配置请求入参。"""

    name: str | None = None
    provider_type: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    is_active: bool | None = None
    timeout_seconds: int | None = None
    custom_headers: dict[str, str] | None = None
    models: list[LLMModelItem] | None = None
    description: str | None = None
    sort_order: int | None = None


class LLMProviderResponse(BaseModel):
    """渠道详细信息响应 (含 API Key 脱敏)。"""

    id: uuid.UUID = Field(description="渠道唯一主键 UUID")
    name: str = Field(description="渠道展示名称")
    provider_type: str = Field(description="协议类型")
    base_url: str = Field(description="基础 API 端点 Base URL")
    api_key: str = Field(description="脱敏后的 API Key (如 'sk-****abcd')")
    has_api_key: bool = Field(description="是否已配置 API 密钥")
    is_active: bool = Field(description="是否激活")
    timeout_seconds: int = Field(description="请求超时时间")
    custom_headers: dict[str, str] = Field(description="自定义请求头")
    models: list[LLMModelItem] = Field(description="模型清单")
    models_count: int = Field(default=0, description="总纳管模型数")
    public_models_count: int = Field(default=0, description="已上架客户端模型数")
    description: str | None = Field(default=None, description="备注说明")
    sort_order: int = Field(default=0, description="排序权重")
    created_at: datetime = Field(description="创建时间")
    updated_at: datetime = Field(description="最后更新时间")


class LLMTestConnectionRequest(BaseModel):
    """连通性 Ping 测试请求。"""

    base_url: str = Field(description="待测试 Base URL")
    api_key: str = Field(default="", description="待测试 API Key (若传空且带 provider_id 则读取数据库已有真实 Key)")
    provider_type: str = Field(default="openai", description="协议类型")
    custom_headers: dict[str, str] = Field(default_factory=dict, description="自定义请求头")
    provider_id: uuid.UUID | None = Field(default=None, description="若为已有渠道，可指定渠道 ID")


class LLMTestConnectionResponse(BaseModel):
    """连通性 Ping 测试响应。"""

    success: bool = Field(description="是否测试成功")
    latency_ms: int = Field(description="往返延迟 (毫秒)")
    message: str = Field(description="结果详情或错误说明")
    status_code: int | None = Field(default=None, description="上游返回的 HTTP 状态码")
    discovered_models_count: int = Field(default=0, description="上游探测到的模型数量")


class LLMFetchModelsRequest(BaseModel):
    """在线拉取上游模型列表请求。"""

    base_url: str = Field(description="Base URL")
    api_key: str = Field(default="", description="API Key")
    custom_headers: dict[str, str] = Field(default_factory=dict, description="自定义请求头")
    provider_id: uuid.UUID | None = Field(default=None, description="渠道 ID (可选)")


class LLMFetchModelsResponse(BaseModel):
    """在线拉取上游模型列表响应。"""

    success: bool = Field(description="是否拉取成功")
    models: list[str] = Field(default_factory=list, description="拉取到的可用模型标识列表")
    message: str = Field(description="提示信息")


class ClientModelItem(BaseModel):
    """C 端客户端公开模型展示项 (完全脱敏，不含敏感 BaseURL / Key)。"""

    id: str = Field(description="模型调用唯一标识符")
    name: str = Field(description="客户端展示名称")
    familyId: str = Field(description="家族归属 ('deepseek', 'gpt', 'claude', 'gemini', 'other')")
    category: str = Field(default="normal", description="模型分类档位 ('normal'=普通, 'advanced'=高级, 'infinite'=无限)")
    health: int = Field(default=99, description="健康度评分 (0-100)")
    cost: int = Field(default=1, description="单次消耗展示点数")
    starCost: int = Field(default=1, description="金星单次消耗")
    moonCost: int = Field(default=1, description="橙月单次消耗")
    freeCountText: str = Field(default="★ 1 / 次", description="客户端角标提示")
    isStreaming: bool = Field(default=True, description="是否支持流式")
    supportsReasoning: bool = Field(default=False, description="是否支持深度思考链")
    isFavorite: bool = Field(default=False, description="是否收藏")
    isDefault: bool = Field(default=False, description="是否默认模型")
