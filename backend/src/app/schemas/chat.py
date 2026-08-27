"""AI 对话、剧情分支树、主控与叙梦面板 Pydantic v2 DTO 契约。

包含 SSE 流式请求体、分支拓扑树、消息列表、主控 38 变量矩阵与叙梦 6 大 Tab 状态机。

Usage:
    >>> from app.schemas.chat import SendMessageRequest, ControlPanelDTO
    >>> req = SendMessageRequest(content="你好，艾莉丝", model_id="glm-5.2-o1")
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ChatMessageDTO(BaseModel):
    """消息列表项 DTO。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="消息 ID")
    session_id: uuid.UUID = Field(..., description="会话 ID")
    branch_id: uuid.UUID = Field(..., description="分支 ID")
    sender: Literal["user", "ai", "system"] = Field(..., description="发送方")
    character_name: str | None = Field(default=None, description="发言者姓名")
    avatar_url: str | None = Field(default=None, description="头像 URL")
    content: str = Field(..., description="正文内容")
    thinking_content: str = Field(default="", description="思维链内容")
    input_tokens: int = Field(default=0, description="输入 Token 数")
    output_tokens: int = Field(default=0, description="输出 Token 数")
    parent_message_id: uuid.UUID | None = Field(default=None, description="父消息 ID")
    created_at: datetime = Field(..., description="生成时间")


class StoryBranchDTO(BaseModel):
    """剧情分支 DTO。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="分支 ID")
    session_id: uuid.UUID = Field(..., description="会话 ID")
    name: str = Field(..., description="分支名称 (如 '🌿 主线剧情')")
    parent_branch_id: uuid.UUID | None = Field(default=None, description="父分支 ID")
    fork_message_id: uuid.UUID | None = Field(default=None, description="分叉节点消息 ID")
    is_main: bool = Field(default=False, description="是否为主线")
    created_at: datetime = Field(..., description="开辟时间")


class ChatSessionResponse(BaseModel):
    """会话详细状态响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="会话 ID")
    character_id: uuid.UUID = Field(..., description="角色 ID")
    character_name: str = Field(..., description="角色名称")
    character_avatar: str = Field(..., description="角色立绘")
    character_banner: str | None = Field(default=None, description="角色大背景/封面图")
    character_author_note: str = Field(default="", description="创作者留言/作者的话")
    character_prologue_title: str = Field(default="序幕", description="序幕标题")
    character_prologue_html: str = Field(default="", description="序幕富文本排版 HTML")
    character_tags: list[str] = Field(default_factory=list, description="角色标签列表")
    current_branch_id: uuid.UUID = Field(..., description="当前激活分支 ID")
    current_model_id: str = Field(default="mimo-v2.5", description="当前模型 ID")
    mode: Literal["story", "room"] = Field(default="story", description="对话模式")
    branches: list[StoryBranchDTO] = Field(default_factory=list, description="分支列表")
    messages: list[ChatMessageDTO] = Field(default_factory=list, description="当前分支线性消息链")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="活跃时间")


class ChatSessionCreateRequest(BaseModel):
    """初始化/恢复会话请求。"""

    character_id: uuid.UUID = Field(..., description="对话角色 ID")
    model_id: str = Field(default="glm-5.2-o1", description="初始选择模型")
    mode: Literal["story", "room"] = Field(default="story", description="模式")


class SendMessageRequest(BaseModel):
    """发送消息发起 SSE 生成请求体。"""

    content: str = Field(..., min_length=1, description="用户发言正文")
    model_id: str = Field(default="glm-5.2-o1", description="选用模型 ID")
    mode: Literal["story", "room"] = Field(default="story", description="模式")
    parent_message_id: uuid.UUID | None = Field(
        default=None,
        description="指定挂载的父消息 ID (回溯或重试时指定)",
    )


class StoryBranchCreateRequest(BaseModel):
    """开辟新分支请求体。"""

    from_message_id: uuid.UUID = Field(..., description="从哪条历史消息分叉")
    branch_name: str = Field(..., min_length=1, max_length=128, description="新分支名称")


class RollbackRequest(BaseModel):
    """回溯至历史节点请求体。"""

    target_message_id: uuid.UUID = Field(..., description="回溯的目标历史消息 ID")


class ControlPanelDTO(BaseModel):
    """主控面板数据 DTO。"""

    user_name: str = Field(default="{{user}}", description="用户代称")
    user_persona: str = Field(default="", description="用户人设")
    custom_prompt: str = Field(default="", description="前置/后置指令")
    variables: dict[str, Any] = Field(
        default_factory=dict,
        description="38 变量矩阵 (variable_1 ~ variable_38)",
    )
    memory_blocks: list[dict[str, Any]] = Field(default_factory=list, description="长期记忆区块")
    text_replacements: list[dict[str, Any]] = Field(default_factory=list, description="正则替换链")


class NarrativeStateDTO(BaseModel):
    """叙梦面板 6 大 Tab 状态机 DTO。"""

    date_text: str = Field(default="", description="当前剧情日期")
    time_text: str = Field(default="", description="当前剧情时间")
    location: str = Field(default="", description="当前地点")
    present_characters: list[str] = Field(default_factory=list, description="在场角色列表")
    player_states: list[dict[str, Any]] = Field(default_factory=list, description="玩家状态指标")
    consumables: list[dict[str, Any]] = Field(default_factory=list, description="消耗品")
    important_items: list[dict[str, Any]] = Field(default_factory=list, description="重要物品")
    skills: list[dict[str, Any]] = Field(default_factory=list, description="技能列表")
    social_relations: list[dict[str, Any]] = Field(default_factory=list, description="社交好感度")
    tasks: list[dict[str, Any]] = Field(default_factory=list, description="任务列表")
    history_events: list[dict[str, Any]] = Field(default_factory=list, description="历史事件时间轴")


class SSEMetricsDTO(BaseModel):
    """SSE 生成结束指标。"""

    input_tokens: int = Field(default=0, description="输入 Token 数")
    output_tokens: int = Field(default=0, description="输出 Token 数")
    cost_star: int = Field(default=0, description="扣除星元")
    cost_moon: int = Field(default=0, description="扣除月华")


class ChatSessionListItemDTO(BaseModel):
    """历史会话条目 DTO。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="会话 ID")
    character_id: uuid.UUID = Field(..., description="角色 ID")
    title: str = Field(..., description="角色/会话标题")
    avatar: str = Field(..., description="角色立绘头像 URL")
    banner_url: str | None = Field(default=None, description="角色大封面背景图 URL")
    last_message: str = Field(default="", description="最后一条消息摘要")
    last_message_time: str = Field(default="", description="最后发言时间友好展示")
    message_count: int = Field(default=0, description="当前总消息数")
    is_pinned: bool = Field(default=False, description="是否置顶")
    remark: str = Field(default="", description="用户自定义备注")
    updated_at: datetime = Field(..., description="最后活跃时间")


class UpdateRemarkRequest(BaseModel):
    """修改会话备注请求。"""

    remark: str = Field(default="", max_length=255, description="用户备注内容")
