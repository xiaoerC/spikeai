"""后台管理系统 RBAC 鉴权与组织架构 Pydantic Schemas 数据模型契约。

定义管理员认证、用户信息、角色管理、权限菜单树以及部门组织架构的输入输出规范。

Usage:
    >>> from app.schemas.admin import AdminLoginRequest, AdminMeResponse
"""

import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------- 认证登录契约 ----------------
class AdminLoginRequest(BaseModel):
    """管理员登录凭据。"""

    username: str = Field(..., min_length=2, max_length=64, description="管理员登录名")
    password: str = Field(..., min_length=6, max_length=128, description="登录密码")


class AdminLoginResponse(BaseModel):
    """管理员登录成功响应。"""

    token_type: str = Field(default="Bearer", description="令牌类型")
    access_token: str = Field(..., description="JWT 访问令牌 (aud='admin')")
    expires_in: int = Field(..., description="有效时间(秒)")


class AdminChangePasswordRequest(BaseModel):
    """管理员自行修改密码请求。"""

    old_password: str = Field(..., min_length=1, description="当前旧密码")
    new_password: str = Field(..., min_length=6, max_length=128, description="新密码 (不少于6位)")


class AdminMenuNode(BaseModel):
    """前端动态菜单节点树。"""

    id: uuid.UUID
    parent_id: uuid.UUID | None = None
    type: str = Field(..., description="directory / menu / button")
    title: str = Field(..., description="显示标题")
    name: str | None = Field(None, description="路由名称")
    code: str = Field(..., description="权限代码")
    path: str | None = Field(None, description="路由路径")
    component: str | None = Field(None, description="前端 SFC 路径")
    icon: str | None = Field(None, description="图标名")
    sort: int = 0
    is_hidden: bool = False
    children: list["AdminMenuNode"] = Field(default_factory=list, description="子节点")

    model_config = ConfigDict(from_attributes=True)


class AdminUserInfo(BaseModel):
    """当前登录管理员个人信息。"""

    id: uuid.UUID
    username: str
    email: str
    real_name: str
    avatar: str | None = None
    phone: str | None = None
    job_number: str | None = None
    department_id: uuid.UUID | None = None
    department_name: str | None = None
    is_super_admin: bool = False
    status: str

    model_config = ConfigDict(from_attributes=True)


class AdminMeResponse(BaseModel):
    """管理员资料与动态权限清单。"""

    user_info: AdminUserInfo
    roles: list[str] = Field(default_factory=list, description="角色 key 列表")
    permissions: list[str] = Field(default_factory=list, description="拥有的权限 code 列表")
    menus: list[AdminMenuNode] = Field(default_factory=list, description="动态可访问菜单树")


# ---------------- 部门组织契约 ----------------
class AdminDepartmentCreate(BaseModel):
    """创建部门参数。"""

    parent_id: uuid.UUID | None = None
    name: str = Field(..., min_length=2, max_length=64, description="部门名称")
    leader: str | None = None
    phone: str | None = None
    sort: int = 0
    status: str = "active"


class AdminDepartmentUpdate(BaseModel):
    """更新部门参数。"""

    parent_id: uuid.UUID | None = None
    name: str | None = None
    leader: str | None = None
    phone: str | None = None
    sort: int | None = None
    status: str | None = None


class AdminDepartmentNode(BaseModel):
    """部门架构树节点。"""

    id: uuid.UUID
    parent_id: uuid.UUID | None = None
    name: str
    leader: str | None = None
    phone: str | None = None
    sort: int = 0
    status: str = "active"
    created_at: datetime
    children: list["AdminDepartmentNode"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ---------------- 角色权限契约 ----------------
class AdminRoleCreate(BaseModel):
    """创建角色参数。"""

    role_key: str = Field(..., min_length=2, max_length=64, description="角色英文标识")
    name: str = Field(..., min_length=2, max_length=64, description="角色显示名称")
    description: str | None = None
    sort: int = 0
    status: str = "active"
    permission_ids: list[uuid.UUID] = Field(default_factory=list, description="关联权限 ID 列表")


class AdminRoleUpdate(BaseModel):
    """更新角色参数。"""

    name: str | None = None
    description: str | None = None
    sort: int | None = None
    status: str | None = None
    permission_ids: list[uuid.UUID] | None = None


class AdminRoleItem(BaseModel):
    """角色详情。"""

    id: uuid.UUID
    role_key: str
    name: str
    description: str | None = None
    sort: int = 0
    status: str = "active"
    created_at: datetime
    permission_ids: list[uuid.UUID] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# ---------------- 后台用户管理契约 ----------------
class AdminUserCreate(BaseModel):
    """新建后台管理员。"""

    username: str = Field(..., min_length=2, max_length=64)
    email: EmailStr
    real_name: str = Field(..., min_length=2, max_length=64)
    password: str = Field(..., min_length=6, max_length=128)
    phone: str | None = None
    job_number: str | None = None
    department_id: uuid.UUID | None = None
    role_ids: list[uuid.UUID] = Field(default_factory=list)
    status: str = "active"


class AdminUserUpdate(BaseModel):
    """更新后台管理员。"""

    email: EmailStr | None = None
    real_name: str | None = None
    phone: str | None = None
    job_number: str | None = None
    department_id: uuid.UUID | None = None
    role_ids: list[uuid.UUID] | None = None
    status: str | None = None


class AdminUserResetPwd(BaseModel):
    """管理员重置密码。"""

    new_password: str = Field(..., min_length=6, max_length=128)


class AdminUserItem(BaseModel):
    """管理员列表项。"""

    id: uuid.UUID
    username: str
    email: str
    real_name: str
    avatar: str | None = None
    phone: str | None = None
    job_number: str | None = None
    department_id: uuid.UUID | None = None
    department_name: str | None = None
    is_super_admin: bool = False
    status: str
    roles: list[AdminRoleItem] = Field(default_factory=list)
    role_names: str | None = None
    created_at: datetime
    last_login_at: datetime | None = None
    last_login_ip: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AdminUserPageResult(BaseModel):
    """用户分页结果。"""

    total: int
    page: int
    size: int
    list: list[AdminUserItem]


# ---------------- C 端用户治理与资产中心契约 ----------------

class CUserItem(BaseModel):
    """C 端用户列表/画像数据项。"""

    id: uuid.UUID
    email: str
    username: str
    avatar_url: str = ""
    status: str = Field("active", description="active / banned / suspended")
    invite_code: str
    vip_level: int = 0
    player_level: int = 1
    player_xp: int = 0
    creator_level: int = 1
    creator_xp: int = 0
    star_coins: int = 0
    moon_gems: int = 0
    character_count: int = 0
    chat_session_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CUserPageResult(BaseModel):
    """C 端用户分页响应。"""

    total: int
    page: int
    size: int
    list: list[CUserItem]


class CUserStatusUpdate(BaseModel):
    """C 端用户状态变更请求。"""

    status: str = Field(..., description="active / banned / suspended")
    reason: str | None = Field(None, max_length=255, description="封禁或处置理由")


class WalletAdjustRequest(BaseModel):
    """管理员人工调账请求。"""

    currency: str = Field(..., description="star (星元) / moon (月华)")
    action: str = Field(..., description="add (增加) / sub (扣减)")
    amount: int = Field(..., gt=0, le=1000000, description="变动数值（正整数）")
    reason: str = Field(..., min_length=2, max_length=255, description="调账审核原因备注")


class WalletTransactionItem(BaseModel):
    """钱包资金流水记录项。"""

    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    currency: str
    amount: int
    balance_after: int
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WalletTransactionPageResult(BaseModel):
    """钱包资金流水分页响应。"""

    total: int
    page: int
    size: int
    list: list[WalletTransactionItem]


# ---------------- AI 角色卡与设定集治理中心契约 ----------------

class WorldBookEntryItem(BaseModel):
    """世界书词条条目简要。"""

    id: uuid.UUID
    keys: list[str] = Field(default_factory=list)
    content: str
    constant: bool = False
    position: str = "after_char"

    model_config = ConfigDict(from_attributes=True)


class AdminCharacterItem(BaseModel):
    """角色卡列表治理项。"""

    id: uuid.UUID
    name: str
    avatar_url: str
    banner_url: str | None = None
    category: str
    description: str
    status: str = Field("published", description="published / draft / private / banned")
    tags: list[str] = Field(default_factory=list)
    settings_word_count: int = 0
    version: str = "1.0.0"
    author_id: uuid.UUID
    author_name: str
    author_email: str
    chat_count: int = 0
    like_count: int = 0
    favorite_count: int = 0
    rating: float = 5.0
    worldbook_entry_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminCharacterPageResult(BaseModel):
    """角色卡分页响应。"""

    total: int
    page: int
    size: int
    list: list[AdminCharacterItem]


class AdminCharacterStatusUpdate(BaseModel):
    """角色卡审核与上下架状态变更。"""

    status: str = Field(..., description="published (上架) / private (私密) / banned (违规下架)")
    reason: str | None = Field(None, max_length=255, description="下架或处置原因说明")


class AdminCharacterDetail(AdminCharacterItem):
    """角色卡全景画像与提示词档案详情。"""

    personality: str = ""
    scenario: str = ""
    first_mes: str = ""
    system_prompt: str = ""
    post_history_instructions: str = ""
    prologue_title: str = "序幕"
    creator_notes: str = ""
    alternate_greetings: list[str] = Field(default_factory=list)
    worldbook_entries: list[WorldBookEntryItem] = Field(default_factory=list)


class AdminBatchCharacterIds(BaseModel):
    """批量角色卡操作 ID 列表。"""

    character_ids: list[uuid.UUID] = Field(..., min_length=1, description="角色卡 UUID 列表")



# ---------------- AI 对话会话与推理审计中心契约 ----------------

class AdminChatSessionItem(BaseModel):
    """会话大盘列表项。"""

    id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    user_email: str
    user_avatar: str
    character_id: uuid.UUID
    character_name: str
    character_avatar: str
    current_model_id: str
    mode: str
    remark: str
    is_pinned: bool = False
    message_count: int = 0
    total_tokens: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminChatSessionPageResult(BaseModel):
    """会话大盘分页响应。"""

    total: int
    page: int
    size: int
    list: list[AdminChatSessionItem]


class AdminChatMessageItem(BaseModel):
    """单条消息审计记录项。"""

    id: uuid.UUID
    sender: str  # user / ai / system
    character_name: str | None = None
    avatar_url: str | None = None
    content: str
    thinking_content: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminChatTranscriptResult(BaseModel):
    """会话全景历史回溯响应。"""

    session: AdminChatSessionItem
    messages: list[AdminChatMessageItem]


# ---------------- 平台财务与订单结算中心契约 ----------------

class AdminFinanceSummary(BaseModel):
    """财务大盘宏观指标。"""

    total_star_recharged: int = 0
    total_moon_recharged: int = 0
    total_transactions_count: int = 0
    today_transactions_count: int = 0


class AdminOrderTransactionItem(BaseModel):
    """订单与流水治理项。"""

    id: uuid.UUID
    user_id: uuid.UUID
    user_name: str
    user_email: str
    user_avatar: str
    type: str
    currency: str
    amount: int
    balance_after: int
    description: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminOrderPageResult(BaseModel):
    """订单流水分页响应 (包含宏观指标汇总)。"""

    total: int
    page: int
    size: int
    list: list[AdminOrderTransactionItem]
    summary: AdminFinanceSummary


class AdminOrderRefundRequest(BaseModel):
    """退款冲正处置请求。"""

    reason: str = Field(..., min_length=2, max_length=255, description="退款或冲正原因说明")


# ---------------- 系统公告与运营活动管理中心契约 ----------------

class AdminNoticeItem(BaseModel):
    """系统公告项。"""

    id: uuid.UUID
    title: str
    category: str
    date_text: str
    badge_type: str
    summary: str
    content_html: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminNoticePageResult(BaseModel):
    """公告分页响应。"""

    total: int
    page: int
    size: int
    list: list[AdminNoticeItem]


class AdminNoticeCreate(BaseModel):
    """创建公告请求。"""

    title: str = Field(..., min_length=2, max_length=128, description="公告标题")
    category: str = Field(..., min_length=2, max_length=32, description="分类 (系统公告/更新日志/活动公告)")
    date_text: str = Field(..., min_length=2, max_length=32, description="展示日期文本")
    badge_type: str = Field(default="notice", description="徽章类型 (notice/update/event)")
    summary: str = Field(..., min_length=2, max_length=500, description="摘要简介")
    content_html: str = Field(default="", description="富文本详情 HTML")


class AdminNoticeUpdate(BaseModel):
    """更新公告请求。"""

    title: str | None = Field(None, min_length=2, max_length=128)
    category: str | None = Field(None, min_length=2, max_length=32)
    date_text: str | None = Field(None, min_length=2, max_length=32)
    badge_type: str | None = None
    summary: str | None = Field(None, min_length=2, max_length=500)
    content_html: str | None = None


class AdminActivityItem(BaseModel):
    """运营活动项。"""

    id: uuid.UUID
    title: str
    tag: str
    reward_text: str
    date_range: str
    status: str
    rules: list[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminActivityPageResult(BaseModel):
    """运营活动分页响应。"""

    total: int
    page: int
    size: int
    list: list[AdminActivityItem]


class AdminActivityCreate(BaseModel):
    """创建运营活动请求。"""

    title: str = Field(..., min_length=2, max_length=128, description="活动标题")
    tag: str = Field(..., min_length=1, max_length=32, description="标签 (福利/招募/征集)")
    reward_text: str = Field(..., min_length=1, max_length=64, description="奖励描述")
    date_range: str = Field(..., min_length=2, max_length=64, description="时间范围")
    status: str = Field(default="active", description="状态 (active/ended)")
    rules: list[str] = Field(default_factory=list, description="规则条目列表")


class AdminActivityUpdate(BaseModel):
    """更新运营活动请求。"""

    title: str | None = Field(None, min_length=2, max_length=128)
    tag: str | None = Field(None, min_length=1, max_length=32)
    reward_text: str | None = Field(None, min_length=1, max_length=64)
    date_range: str | None = Field(None, min_length=2, max_length=64)
    status: str | None = None
    rules: list[str] | None = None





