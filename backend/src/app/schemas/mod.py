"""Mod 模组生态与自定义中心 Pydantic v2 DTO 契约。

包含 Mod 广场、已激活 Mod 优先级拖拽调序、合集以及自定义人设/指令/画师串。

Usage:
    >>> from app.schemas.mod import ModCreateRequest, ModPriorityUpdateRequest
    >>> req = ModCreateRequest(title="赛博朋克世界观扩展", category_tag="worldbook", description="...")
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ModItemResponse(BaseModel):
    """Mod 模组响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Mod ID")
    author_id: uuid.UUID = Field(..., description="作者 UID")
    title: str = Field(..., description="Mod 标题")
    description: str = Field(..., description="说明")
    category_tag: str = Field(..., description="分类标签")
    price: int = Field(default=0, description="价格 (星元)")
    status: str = Field(default="published", description="状态")
    entries: list[dict[str, Any]] = Field(default_factory=list, description="词条列表")
    downloads: int = Field(default=0, description="下载量")
    likes: int = Field(default=0, description="点赞量")
    rating: float = Field(default=5.0, description="评分")
    created_at: datetime = Field(..., description="创建时间")


class ModCreateRequest(BaseModel):
    """创建/编辑 Mod 请求体。"""

    title: str = Field(..., min_length=1, max_length=128, description="Mod 标题")
    description: str = Field(..., description="Mod 说明")
    category_tag: Literal["worldbook", "system", "command", "regex", "artist"] = Field(
        ..., description="分类标签"
    )
    price: int = Field(default=0, ge=0, description="价格")
    status: Literal["draft", "published"] = Field(default="published", description="发布状态")
    entries: list[dict[str, Any]] = Field(default_factory=list, description="词条内容")


class ModUpdateRequest(BaseModel):
    """更新 Mod 请求体。"""

    title: str | None = Field(default=None, min_length=1, max_length=128, description="Mod 标题")
    description: str | None = Field(default=None, description="Mod 说明")
    category_tag: Literal["worldbook", "system", "command", "regex", "artist"] | None = Field(
        default=None, description="分类标签"
    )
    price: int | None = Field(default=None, ge=0, description="价格")
    status: Literal["draft", "published"] | None = Field(default=None, description="发布状态")
    entries: list[dict[str, Any]] | None = Field(default=None, description="词条内容")


class ModPromptPatches(BaseModel):
    """多锚点合并后的提示词插桩结果。"""

    system_prefix: list[str] = Field(default_factory=list, description="前置系统指令 (越狱/最高规则)")
    before_char: list[str] = Field(default_factory=list, description="角色人设前置 (画师串/基调)")
    after_char: list[str] = Field(default_factory=list, description="角色人设后置")
    top_an: list[str] = Field(default_factory=list, description="作者注释与场景前缀")
    bottom_an: list[str] = Field(default_factory=list, description="深度描写与微表情增强")
    user_suffix: list[str] = Field(default_factory=list, description="用户最新输入后置增强")



class ModSquareFilterParams(BaseModel):
    """Mod 广场筛选参数。"""

    category: str | None = Field(default=None, description="分类标签")
    sort: Literal["heat", "rating", "newest"] = Field(default="heat", description="排序")
    keyword: str | None = Field(default=None, description="搜索关键词")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=50, description="每页条数")


class UserActiveModResponse(BaseModel):
    """用户已激活 Mod 优先级项。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="记录 ID")
    mod_id: uuid.UUID = Field(..., description="Mod ID")
    mod_title: str = Field(..., description="Mod 标题")
    category_tag: str = Field(..., description="分类")
    priority_order: int = Field(..., description="优先级序号 (越大越排在后面/权重最高)")
    is_active: bool = Field(default=True, description="是否启用")
    is_highest_priority: bool = Field(default=False, description="是否为最高优先级 (金色高光)")
    entries_count: int = Field(default=0, description="包含词条数")


class ModPriorityUpdateRequest(BaseModel):
    """更新 Mod 激活与优先级排序请求体。"""

    active_mods: list[dict[str, Any]] = Field(
        ...,
        description="排序后的 Mod 列表 (格式: [{mod_id: UUID, priority_order: int, is_active: bool}])",
    )


class ModPrioritySummaryResponse(BaseModel):
    """Mod 注入统计横幅数据。"""

    active_count: int = Field(default=0, description="已激活 Mod 数量")
    worldbook_entries_count: int = Field(default=0, description="注入世界书条目数")
    worldbook_words_count: int = Field(default=0, description="注入世界书总字数")
    system_prompt_entries_count: int = Field(default=0, description="注入系统提示条目数")
    system_prompt_words_count: int = Field(default=0, description="注入系统提示总字数")
    has_performance_warning: bool = Field(default=False, description="是否触发性能警告黄色横幅")


class ModCollectionResponse(BaseModel):
    """Mod 合集响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="合集 ID")
    title: str = Field(..., description="合集标题")
    description: str = Field(default="", description="合集描述")
    cover_url: str | None = Field(default=None, description="封面图")
    mod_count: int = Field(default=0, description="包含 Mod 数")
    created_at: datetime = Field(..., description="创建时间")


class ModCollectionCreateRequest(BaseModel):
    """创建 Mod 合集请求体。"""

    title: str = Field(..., min_length=1, max_length=128, description="合集标题")
    description: str = Field(default="", description="合集描述")
    cover_url: str | None = Field(default=None, description="封面图 URL")
    mod_ids: list[str] = Field(default_factory=list, description="选中的 Mod ID 列表")


class UserCustomItemResponse(BaseModel):
    """用户自定义项响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="配置 ID")
    type: str = Field(..., description="类型 (persona / command / artist / summary_prompt / memory_model)")
    title: str = Field(..., description="标题")
    content: dict[str, Any] = Field(default_factory=dict, description="配置内容")
    is_default: bool = Field(default=False, description="是否默认")
    created_at: datetime = Field(..., description="创建时间")


class UserCustomItemCreateRequest(BaseModel):
    """创建/更新用户自定义项请求体。"""

    type: Literal["persona", "command", "artist", "summary_prompt", "memory_model"] = Field(
        ..., description="类型"
    )
    title: str = Field(..., min_length=1, max_length=128, description="标题")
    content: dict[str, Any] = Field(default_factory=dict, description="配置内容详情")
    is_default: bool = Field(default=False, description="是否设为默认")
