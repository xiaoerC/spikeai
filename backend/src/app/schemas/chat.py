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
    character_alternate_greetings: list[str] = Field(default_factory=list, description="备选开场白列表")
    character_extensions: dict[str, Any] = Field(default_factory=dict, description="角色扩展属性 (含 bgm_url, opening_replies 等)")
    current_branch_id: uuid.UUID = Field(..., description="当前激活分支 ID")
    current_model_id: str = Field(default="mimo-v2.5", description="当前模型 ID")
    mode: Literal["story", "room"] = Field(default="story", description="对话模式")
    branches: list[StoryBranchDTO] = Field(default_factory=list, description="分支列表")
    messages: list[ChatMessageDTO] = Field(default_factory=list, description="当前分支线性消息链")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="活跃时间")


class SwitchGreetingRequest(BaseModel):
    """切换开场白请求体。"""

    greeting_index: int = Field(default=0, ge=0, description="开场白索引")


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
    client_message_id: uuid.UUID | None = Field(
        default=None,
        description="客户端预生成的标准 UUID 消息 ID (用于乐观 UI 与即时编辑)",
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

    model_config = ConfigDict(from_attributes=True)

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

    model_config = ConfigDict(from_attributes=True)

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


class ForkSessionRequest(BaseModel):
    """从指定消息分叉并创建全新独立聊天会话请求 DTO。"""

    fork_message_id: uuid.UUID = Field(..., description="分叉起点的历史消息 UUID")
    remark: str | None = Field(default=None, max_length=255, description="新会话自定义备注/分支名")


class ForkBranchRequest(BaseModel):
    """剧情分叉请求 DTO。"""

    fork_message_id: uuid.UUID = Field(..., description="分叉发生的父消息节点 UUID")
    name: str | None = Field(default=None, max_length=128, description="自定义分支名称")
    switch_to: bool = Field(default=True, description="分叉后是否自动切换至新分支")


class RollbackRequest(BaseModel):
    """剧情节点回溯请求 DTO。"""

    target_message_id: uuid.UUID = Field(..., description="回溯目标消息节点 UUID")
    mode: str = Field(
        default="fork",
        description="回溯模式 (fork: 派生新分支保留旧历史 / truncate: 原地截断)",
    )
    branch_name: str | None = Field(default=None, max_length=128, description="派生分支时的名称")


class EditMessageRequest(BaseModel):
    """编辑消息请求 DTO。"""

    content: str = Field(..., min_length=1, description="修改后的消息正文内容")
    mode: str = Field(
        default="edit_only",
        description="编辑模式 (edit_only: 仅原位保存修改 / edit_and_fork: 保存并开辟新平行分支)",
    )
    branch_name: str | None = Field(default=None, max_length=128, description="派生分支时的名称")


class StoryBranchDetailDTO(BaseModel):
    """剧情分支详情 DTO。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="分支 UUID")
    session_id: uuid.UUID = Field(..., description="所属会话 UUID")
    name: str = Field(..., description="分支名称")
    parent_branch_id: uuid.UUID | None = Field(default=None, description="父分支 UUID")
    fork_message_id: uuid.UUID | None = Field(default=None, description="分叉起点消息 UUID")
    is_main: bool = Field(default=False, description="是否为主线分支")
    node_count: int = Field(default=0, description="当前分支独立消息节点数")
    total_path_count: int = Field(default=0, description="包含祖先节点的总消息数")
    created_at: datetime = Field(..., description="分支创建时间")


class DAGNodeDTO(BaseModel):
    """Vue Flow / DAG 剧情树节点 DTO。"""

    id: str = Field(..., description="节点前端唯一标识 (如 'node_xxx')")
    message_id: uuid.UUID = Field(..., description="对应消息 UUID")
    branch_id: uuid.UUID = Field(..., description="所属分支 UUID")
    branch_name: str = Field(..., description="所属分支名称")
    sender: str = Field(..., description="发言者 (user / ai / system)")
    character_name: str | None = Field(default=None, description="发言者名称")
    avatar_url: str | None = Field(default=None, description="发言者头像 URL")
    content: str = Field(..., description="消息完整正文")
    summary: str = Field(..., description="消息摘要 (前 60 字)")
    timestamp: str = Field(..., description="发言时间友好格式")
    is_current: bool = Field(default=False, description="是否为当前活跃主线的末端节点")
    is_main: bool = Field(default=False, description="是否属于主线分支")
    is_fork_point: bool = Field(default=False, description="是否为分叉起点")
    parent_message_id: uuid.UUID | None = Field(default=None, description="父消息节点 UUID")


class DAGEdgeDTO(BaseModel):
    """Vue Flow / DAG 剧情树连线 DTO。"""

    id: str = Field(..., description="边唯一标识 (如 'edge_xxx_yyy')")
    source: str = Field(..., description="源节点 ID")
    target: str = Field(..., description="目标节点 ID")
    is_main: bool = Field(default=False, description="是否属于主线分支连线")


class DAGGraphDTO(BaseModel):
    """Vue Flow / 全景剧情树完整图拓扑 DTO。"""

    nodes: list[DAGNodeDTO] = Field(default_factory=list, description="所有剧情节点")
    edges: list[DAGEdgeDTO] = Field(default_factory=list, description="所有拓扑连线")
    active_branch_id: uuid.UUID = Field(..., description="当前激活分支 UUID")
    active_message_id: uuid.UUID | None = Field(default=None, description="当前末端消息 UUID")
