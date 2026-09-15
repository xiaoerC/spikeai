"""世界书 (World Book / Character Lorebook) 强类型 DTO 契约。

支持 SillyTavern V2/V3 规范世界书导入导出、关键词过滤规则与 RAG 检索命中结果。

Usage:
    >>> from app.schemas.world_book import WorldBookDTO, WorldBookEntryDTO
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorldBookEntryBase(BaseModel):
    """世界书条目基础属性。"""

    keys: list[str] = Field(default_factory=list, description="主触发关键词列表")
    secondary_keys: list[str] = Field(default_factory=list, description="次级过滤关键词列表")
    selective_logic: int = Field(0, description="次级过滤逻辑: 0: AND ANY, 1: NOT ALL, 2: NOT ANY")
    content: str = Field(..., min_length=1, description="注入设定内容")
    comment: str = Field("", description="条目备注说明")
    constant: bool = Field(False, description="是否常驻生效")
    enabled: bool = Field(True, description="是否启用")
    insertion_order: int = Field(100, description="插入优先级权重 (数字越小越靠前)")
    position: str = Field("before_char", description="插入位置: before_char / after_char / top_an")


class WorldBookEntryCreate(WorldBookEntryBase):
    """创建世界书条目请求。"""

    pass


class WorldBookEntryUpdate(BaseModel):
    """更新世界书条目请求。"""

    keys: list[str] | None = None
    secondary_keys: list[str] | None = None
    selective_logic: int | None = None
    content: str | None = None
    comment: str | None = None
    constant: bool | None = None
    enabled: bool | None = None
    insertion_order: int | None = None
    position: str | None = None


class WorldBookEntryDTO(WorldBookEntryBase):
    """世界书条目响应 DTO。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    world_book_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class WorldBookBase(BaseModel):
    """世界书基础属性。"""

    name: str = Field(..., min_length=1, max_length=128, description="世界书名称")
    description: str = Field("", description="世界书描述")
    is_public: bool = Field(False, description="是否公开")
    scan_depth: int = Field(5, ge=1, le=20, description="扫描历史消息轮数深度")
    token_budget: int = Field(2048, ge=256, le=8192, description="最大注入 Token 预算")


class WorldBookCreate(WorldBookBase):
    """创建世界书请求。"""

    character_id: uuid.UUID | None = Field(None, description="关联角色 ID")
    entries: list[WorldBookEntryCreate] = Field(default_factory=list, description="初始条目列表")


class WorldBookUpdate(BaseModel):
    """更新世界书请求。"""

    name: str | None = None
    description: str | None = None
    is_public: bool | None = None
    scan_depth: int | None = None
    token_budget: int | None = None
    character_id: uuid.UUID | None = None


class WorldBookDTO(WorldBookBase):
    """世界书简要响应 DTO。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    character_id: uuid.UUID | None = None
    entry_count: int = 0
    created_at: datetime
    updated_at: datetime


class WorldBookDetailDTO(WorldBookDTO):
    """世界书详情响应 DTO (包含条目列表)。"""

    entries: list[WorldBookEntryDTO] = Field(default_factory=list)


class SillyTavernWorldBookEntryItem(BaseModel):
    """SillyTavern 原生条目结构。"""

    keys: list[str] = Field(default_factory=list, alias="key")
    secondary_keys: list[str] = Field(default_factory=list, alias="keysecondary")
    selective_logic: int = Field(0, alias="selectiveLogic")
    content: str = ""
    comment: str = ""
    constant: bool = False
    enabled: bool = True
    order: int = 100
    position: int | str = 0


class SillyTavernWorldBookImportDTO(BaseModel):
    """导入 SillyTavern JSON 世界书数据体。"""

    name: str = Field("导入的世界书", description="世界书名称")
    description: str = Field("", description="世界书描述")
    character_id: uuid.UUID | None = None
    entries: dict[str, Any] | list[dict[str, Any]] = Field(
        ...,
        description="SillyTavern 原生 entries 字典或列表",
    )


class WorldBookMatchResultDTO(BaseModel):
    """世界书 RAG 检索命中结果。"""

    matched_entries: list[WorldBookEntryDTO] = Field(default_factory=list)
    formatted_prompt: str = Field("", description="组装渲染后的 Prompt 字符串")
    total_tokens: int = Field(0, description="消耗的总 Token 预估")
