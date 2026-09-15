"""用户与资产领域 Pydantic v2 DTO 契约。

定义注册、登录、Token 签发、用户资料、等级勋章、资产钱包与交易流水数据结构。

Usage:
    >>> from app.schemas.user import UserLoginRequest, TokenResponse
    >>> req = UserLoginRequest(email="user@test.com", password="secretpassword")
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    """用户注册请求体。"""

    email: EmailStr = Field(..., description="注册邮箱")
    password: str = Field(..., min_length=6, max_length=64, description="用户登录密码")
    code: str = Field(default="888888", description="邮箱验证码 (开发阶段支持测试码)")
    invite_code: str | None = Field(default=None, description="绑定的邀请码 (可选)")


class UserLoginRequest(BaseModel):
    """用户登录请求体。"""

    email: EmailStr = Field(..., description="账号邮箱")
    password: str = Field(..., description="登录密码")


class TokenResponse(BaseModel):
    """Token 签发响应。"""

    access_token: str = Field(..., description="JWT 访问令牌")
    token_type: str = Field(default="bearer", description="Token 类型")
    expires_in: int = Field(..., description="有效时间 (秒)")


class BadgeDTO(BaseModel):
    """勋章成就 DTO。"""

    id: str = Field(..., description="勋章 ID (如 star_sprout)")
    name: str = Field(..., description="勋章名称 (如 '星元萌动')")
    icon: str = Field(..., description="图标标识")
    description: str = Field(..., description="解锁条件与说明")
    unlocked_at: str | None = Field(default=None, description="解锁时间")


class UserWalletResponse(BaseModel):
    """用户资产钱包响应体。"""

    star_coins: int = Field(..., description="星元余额 ★")
    moon_gems: int = Field(..., description="月华余额 🌙")


class UserProfileResponse(BaseModel):
    """用户资料详细响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="用户 UID")
    email: str = Field(..., description="用户邮箱")
    username: str = Field(..., description="显示昵称")
    is_custom_username: bool = Field(default=False, description="是否已设置自定义用户名 (若为 False 则需在首次进入或登录时强制设置)")
    avatar_url: str = Field(default="", description="头像 URL")
    vip_level: int = Field(default=0, description="VIP 赞助等级")
    player_level: int = Field(default=1, description="玩家等级")
    player_xp: int = Field(default=0, description="玩家经验值")
    creator_level: int = Field(default=1, description="创作者等级")
    creator_xp: int = Field(default=0, description="创作者经验值")
    invite_code: str = Field(..., description="专属邀请码")
    badges: list[dict[str, Any]] = Field(default_factory=list, description="勋章列表")
    wallet: UserWalletResponse = Field(..., description="资产钱包")


class UserProfileUpdateRequest(BaseModel):
    """更新用户资料请求体。"""

    username: str = Field(..., min_length=2, max_length=20, description="用户自定义昵称 (2~20字符)")
    avatar_url: str | None = Field(default=None, description="自定义头像 URL (可选)")


class DailyRewardResponse(BaseModel):
    """每日签到领取奖励响应体。"""

    reward_star_coins: int = Field(..., description="本次领取的星元数")
    new_balance: int = Field(..., description="签到后星元总余额")
    consecutive_days: int = Field(default=1, description="连续签到天数")
    message: str = Field(default="签到成功", description="提示文案")


class WalletTransactionResponse(BaseModel):
    """钱包流水明细项响应体。"""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="流水 ID")
    type: str = Field(..., description="流水类型")
    currency: str = Field(..., description="币种 (star / moon)")
    amount: int = Field(..., description="变动数值")
    balance_after: int = Field(..., description="变动后余额")
    model_id: str | None = Field(default=None, description="模型 ID")
    target_character_id: uuid.UUID | None = Field(default=None, description="目标角色 ID")
    description: str | None = Field(default=None, description="流水备注")
    created_at: datetime = Field(..., description="发生时间")


class InviteInfoResponse(BaseModel):
    """邀请好友与福利信息响应。"""

    invite_code: str = Field(..., description="我的邀请码")
    invite_url: str = Field(..., description="完整邀请链接")
    invited_count: int = Field(default=0, description="成功邀请人数")
    reward_earned_star: int = Field(default=0, description="累计获得星元奖励")
