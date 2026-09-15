"""角色卡与世界书领域 Pydantic v2 DTO 契约。

包含角色创建/更新、10 项指标响应、市场列表卡片、SillyTavern V2/V3 标准协议卡片模型。

Usage:
    >>> from app.schemas.character import CharacterCreateRequest, STV2Card
    >>> card = STV2Card(data={"name": "艾莉丝", "description": "魔法少女", "first_mes": "你好"})
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorldBookEntryDTO(BaseModel):
    """世界书单条目 DTO。"""

    id: uuid.UUID | None = Field(default=None, description="条目 ID")
    keys: list[str] = Field(default_factory=list, description="触发关键词")
    content: str = Field(default="", description="设定正文")
    constant: bool = Field(default=False, description="是否常驻")
    position: str = Field(default="after_char", description="注入位置 (before_char / after_char / system_top)")

    @field_validator("position", mode="before")
    @classmethod
    def normalize_position(cls, v: Any) -> str:
        """规范化世界书插入位置。兼容酒馆数字枚举 (0, 1, 2, 3, 4) 与字符串。"""
        if v is None:
            return "after_char"
        pos_map = {
            0: "before_char",
            1: "after_char",
            2: "top_an",
            3: "bottom_an",
            4: "at_depth",
            "0": "before_char",
            "1": "after_char",
            "2": "top_an",
            "3": "bottom_an",
            "4": "at_depth",
        }
        if v in pos_map:
            return pos_map[v]
        v_str = str(v).strip().lower()
        if not v_str:
            return "after_char"
        return v_str

    @field_validator("content", mode="before")
    @classmethod
    def normalize_content(cls, v: Any) -> str:
        """确保世界书内容始终为安全字符串。"""
        if v is None:
            return ""
        return str(v)

    @field_validator("keys", mode="before")
    @classmethod
    def normalize_keys(cls, v: Any) -> list[str]:
        """兼容逗号分隔字符串或非列表输入。"""
        if v is None:
            return []
        if isinstance(v, str):
            return [k.strip() for k in v.split(",") if k.strip()]
        if isinstance(v, list):
            return [str(k) for k in v if k is not None]
        return []


class CharacterMetricsDTO(BaseModel):
    """角色卡 10 项数据指标 DTO。"""

    model_config = ConfigDict(from_attributes=True)

    hotness: float = Field(default=0.0, description="综合热度")
    trend_score: float = Field(default=0.0, description="趋势增长分")
    chat_count: int = Field(default=0, description="对话总消息数")
    like_count: int = Field(default=0, description="点赞数")
    favorite_count: int = Field(default=0, description="收藏数")
    import_count: int = Field(default=0, description="导入量")
    rating: float = Field(default=5.0, description="平均评分")
    rating_count: int = Field(default=0, description="评分人数")
    total_tokens: int = Field(default=0, description="总消耗 Token")


class CharacterAuthorDTO(BaseModel):
    """角色创作者简要信息。"""

    id: uuid.UUID = Field(..., description="创作者 UID")
    username: str = Field(..., description="创作者昵称")
    avatar_url: str = Field(default="", description="创作者头像")
    creator_level: int = Field(default=1, description="创作者等级")
    followers_count: int = Field(default=0, description="粉丝数")
    is_following: bool = Field(default=False, description="当前用户是否已关注")


class CharacterListItemResponse(BaseModel):
    """角色市场双列瀑布流卡片响应项。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="角色卡 ID")
    name: str = Field(..., description="角色名称")
    avatar_url: str = Field(..., description="角色立绘头像")
    banner_url: str | None = Field(default=None, description="背景封面")
    category: str = Field(..., description="分类 (story / nsfw / rpg)")
    description: str = Field(..., description="简介描述")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    author: CharacterAuthorDTO = Field(..., description="创作者信息")
    metrics: CharacterMetricsDTO = Field(..., description="核心指标")
    created_at: datetime = Field(..., description="发布时间")


class CharacterDetailResponse(BaseModel):
    """角色卡全量详情响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="角色卡 ID")
    name: str = Field(..., description="角色名称")
    avatar_url: str = Field(..., description="角色立绘头像")
    banner_url: str | None = Field(default=None, description="大封面背景")
    category: str = Field(..., description="分类")
    description: str = Field(..., description="描述")
    personality: str = Field(default="", description="性格")
    scenario: str = Field(default="", description="情境")
    first_mes: str = Field(..., description="首次问候语")
    alternate_greetings: list[str] = Field(default_factory=list, description="备选开场白列表")
    system_prompt: str = Field(default="", description="系统前置提示词")
    post_history_instructions: str = Field(default="", description="历史后置指令")
    prologue_title: str = Field(default="序幕", description="序幕标题")
    prologue_html: str = Field(default="", description="序幕富文本 HTML")
    creator_notes: str = Field(default="", description="创作者留言/作者的话 (Markdown)")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    status: str = Field(default="published", description="发布状态")
    settings_word_count: int = Field(default=0, description="设定字数")
    version: str = Field(default="1.0.0", description="版本号")
    extensions: dict[str, Any] = Field(default_factory=dict, description="SillyTavern 与叙梦扩展配置 (variables, regex_scripts, opening_replies 等)")
    created_at: datetime = Field(..., description="创建时间")
    author: CharacterAuthorDTO = Field(..., description="创作者信息")
    metrics: CharacterMetricsDTO = Field(..., description="10项数据指标")
    worldbooks: list[WorldBookEntryDTO] = Field(default_factory=list, description="世界书条目")
    is_liked: bool = Field(default=False, description="当前用户是否点赞")
    is_favorited: bool = Field(default=False, description="当前用户是否收藏")
    user_rating: int | None = Field(default=None, description="当前用户评分")


class CharacterCreateRequest(BaseModel):
    """创建/上传角色卡请求体。"""

    name: str = Field(..., min_length=1, max_length=128, description="角色名称")
    avatar_url: str = Field(..., description="立绘头像 URL")
    banner_url: str | None = Field(default=None, description="封面背景 URL")
    category: Literal["story", "nsfw", "rpg"] = Field(default="story", description="大分类")
    description: str = Field(..., min_length=1, description="描述")
    personality: str = Field(default="", description="性格设定")
    scenario: str = Field(default="", description="情境设定")
    first_mes: str = Field(..., min_length=1, description="第一句问候语")
    alternate_greetings: list[str] = Field(default_factory=list, description="备选问候语")
    system_prompt: str = Field(default="", description="系统提示词")
    post_history_instructions: str = Field(default="", description="历史后置指令")
    prologue_title: str = Field(default="序幕", description="序幕标题")
    prologue_html: str = Field(default="", description="序幕富文本 HTML")
    creator_notes: str = Field(default="", description="创作者留言/作者的话 (Markdown)")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    status: Literal["draft", "published", "private"] = Field(default="published", description="发布状态")
    version: str = Field(default="1.0.0", description="角色卡版本号")
    extensions: dict[str, Any] = Field(default_factory=dict, description="SillyTavern 与叙梦扩展配置")
    worldbooks: list[WorldBookEntryDTO] = Field(default_factory=list, description="包含的世界书条目")

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, v: Any) -> str:
        """分类容错清洗。"""
        if v not in ("story", "nsfw", "rpg"):
            return "story"
        return str(v)

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, v: Any) -> str:
        """描述非空兜底。"""
        if not v or not str(v).strip():
            return "暂无描述"
        return str(v)

    @field_validator("first_mes", mode="before")
    @classmethod
    def normalize_first_mes(cls, v: Any) -> str:
        """首次问候语非空兜底。"""
        if not v or not str(v).strip():
            return "你好！"
        return str(v)

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: Any) -> str:
        """发布状态容错。"""
        if v not in ("draft", "published", "private"):
            return "published"
        return str(v)


class CharacterUpdateRequest(BaseModel):
    """更新角色卡请求体。"""

    name: str | None = Field(default=None, max_length=128, description="角色名称")
    avatar_url: str | None = Field(default=None, description="立绘头像 URL")
    banner_url: str | None = Field(default=None, description="封面背景 URL")
    category: Literal["story", "nsfw", "rpg"] | None = Field(default=None, description="大分类")
    description: str | None = Field(default=None, description="描述")
    personality: str | None = Field(default=None, description="性格设定")
    scenario: str | None = Field(default=None, description="情境设定")
    first_mes: str | None = Field(default=None, description="第一句问候语")
    alternate_greetings: list[str] | None = Field(default=None, description="备选问候语")
    system_prompt: str | None = Field(default=None, description="系统提示词")
    post_history_instructions: str | None = Field(default=None, description="历史后置指令")
    prologue_title: str | None = Field(default=None, description="序幕标题")
    prologue_html: str | None = Field(default=None, description="序幕富文本 HTML")
    creator_notes: str | None = Field(default=None, description="创作者留言/作者的话 (Markdown)")
    tags: list[str] | None = Field(default=None, description="标签列表")
    status: Literal["draft", "published", "private"] | None = Field(default=None, description="发布状态")
    version: str | None = Field(default=None, description="角色卡版本号")
    extensions: dict[str, Any] | None = Field(default=None, description="SillyTavern 与叙梦扩展配置")
    worldbooks: list[WorldBookEntryDTO] | None = Field(default=None, description="包含的世界书条目")

    @field_validator("category", mode="before")
    @classmethod
    def normalize_category(cls, v: Any) -> str | None:
        """分类容错清洗。"""
        if v is None:
            return None
        if v not in ("story", "nsfw", "rpg"):
            return "story"
        return str(v)

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v: Any) -> str | None:
        """发布状态容错。"""
        if v is None:
            return None
        if v not in ("draft", "published", "private"):
            return "published"
        return str(v)


class CharacterStatusUpdateRequest(BaseModel):
    """更新角色卡发布状态请求体。"""

    status: Literal["draft", "published", "private"] = Field(..., description="发布状态")


class CharacterFilterParams(BaseModel):
    """角色市场多维复合筛选参数。"""

    mode: Literal["story", "nsfw"] = Field(default="story", description="剧情/绅士模式")
    sort: Literal["heat", "recommend", "trend", "random", "favorite"] = Field(
        default="heat", description="排序方式"
    )
    time_span: Literal["day", "week", "month"] = Field(default="day", description="趋势时间跨度")
    tag: str | None = Field(default=None, description="标签精确过滤")
    keyword: str | None = Field(default=None, description="搜索关键词")
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=50, description="每页数量")


class CharacterCommentResponse(BaseModel):
    """角色卡评论响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="评论 ID")
    character_id: uuid.UUID = Field(..., description="角色卡 ID")
    user_id: uuid.UUID = Field(..., description="评论者 UID")
    username: str = Field(..., description="评论者昵称")
    avatar_url: str = Field(default="", description="评论者头像")
    content: str = Field(..., description="评论内容")
    likes: int = Field(default=0, description="获赞数")
    created_at: datetime = Field(..., description="发表时间")


class CharacterCommentCreateRequest(BaseModel):
    """发表评论请求体。"""

    content: str = Field(..., min_length=1, max_length=1000, description="评论正文")


class RewardRequest(BaseModel):
    """打赏角色卡/创作者请求体。"""

    currency: Literal["star", "moon"] = Field(default="star", description="打赏币种 (star / moon)")
    amount: int = Field(..., gt=0, description="打赏金额")


# ============================================================================
# SillyTavern V2 / V3 角色卡标准协议 DTO
# ============================================================================


class STV2Data(BaseModel):
    """SillyTavern V2 核心数据段。"""

    name: str = Field(default="", description="角色名称")
    description: str = Field(default="", description="角色描述")
    personality: str = Field(default="", description="角色性格")
    scenario: str = Field(default="", description="故事场景")
    first_mes: str = Field(default="", description="首条问候语")
    mes_example: str = Field(default="", description="对话样例")
    creator_notes: str = Field(default="", description="创作者寄语")
    system_prompt: str = Field(default="", description="系统提示词")
    post_history_instructions: str = Field(default="", description="历史后置提示词")
    alternate_greetings: list[str] = Field(default_factory=list, description="备选问候语")
    tags: list[str] = Field(default_factory=list, description="标签列表")
    creator: str = Field(default="", description="作者名称")
    character_version: str = Field(default="1.0.0", description="版本号")
    character_book: dict[str, Any] | None = Field(default=None, description="内嵌世界书设定")
    extensions: dict[str, Any] = Field(
        default_factory=dict,
        description="第三方扩展数据 (存放 naro_prologue_html 等)",
    )


class STV2Card(BaseModel):
    """SillyTavern V2 标准角色卡模型。"""

    spec: str = Field(default="chara_card_v2", description="协议标识")
    spec_version: str = Field(default="2.0", description="协议版本号")
    data: STV2Data = Field(default_factory=STV2Data, description="核心数据段")


class STV3Data(STV2Data):
    """SillyTavern V3 核心数据段 (继承 V2 并扩展 assets 与 group)。"""

    assets: list[dict[str, Any]] = Field(default_factory=list, description="静态多媒体资源列表")
    group_only_greetings: list[str] = Field(default_factory=list, description="群聊专用问候语")


class STV3Card(BaseModel):
    """SillyTavern V3 标准角色卡模型。"""

    spec: str = Field(default="chara_card_v3", description="协议标识")
    spec_version: str = Field(default="3.0", description="协议版本号")
    data: STV3Data = Field(default_factory=STV3Data, description="核心数据段")


class PrologueGenerateRequest(BaseModel):
    """请求基于角色设定生成 HTML 序幕。"""

    name: str = Field(..., description="角色/故事名称")
    description: str = Field(default="", description="描述")
    personality: str = Field(default="", description="性格特征")
    scenario: str = Field(default="", description="背景情境")
    first_mes: str = Field(default="", description="首句问候")


class PrologueGenerateResponse(BaseModel):
    """生成的 HTML 序幕响应。"""

    prologue_html: str = Field(..., description="生成的富文本序幕 HTML")

