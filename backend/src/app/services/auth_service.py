"""用户认证与个人资料领域服务。

实现注册、登录、密码校验、专属邀请码生成以及资料聚合组装。

Usage:
    >>> from app.services.auth_service import AuthService
    >>> user, token = await AuthService.login(db, req)
"""

import logging
import secrets
import string
import uuid
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserProfile, UserWallet
from app.schemas.user import (
    UserLoginRequest,
    UserProfileResponse,
    UserProfileUpdateRequest,
    UserRegisterRequest,
    UserWalletResponse,
)

logger = logging.getLogger(__name__)


class AuthService:
    """用户认证与资产初始化业务服务。"""

    @classmethod
    def generate_unique_invite_code(cls) -> str:
        """生成 6 位大写字母/数字的专属邀请码 (如 NAR-5CWSPD)。"""
        charset = string.ascii_uppercase + string.digits
        random_suffix = "".join(secrets.choice(charset) for _ in range(6))
        return f"NAR-{random_suffix}"

    @classmethod
    async def register(
        cls,
        db: AsyncSession,
        req: UserRegisterRequest,
    ) -> tuple[User, str]:
        """用户注册逻辑。

        校验邮箱唯一性、绑定邀请人、初始化双代币钱包与默认新手成就勋章。

        Args:
            db: 异步数据库会话。
            req: 用户注册请求体。

        Returns:
            tuple[User, str]: 创建的用户实体与 JWT 访问令牌。

        Raises:
            HTTPException: 邮箱已存在或邀请码无效时抛出。
        """
        # 1. 检查邮箱唯一性
        stmt = select(User).where(User.email == req.email.lower().strip())
        existing_user = (await db.execute(stmt)).scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="该邮箱已被注册，请直接登录",
            )

        # 2. 查询邀请人
        inviter_id: uuid.UUID | None = None
        if req.invite_code:
            inviter_stmt = select(User).where(User.invite_code == req.invite_code.strip())
            inviter = (await db.execute(inviter_stmt)).scalar_one_or_none()
            if inviter:
                inviter_id = inviter.id

        # 3. 生成新用户专属邀请码
        invite_code = cls.generate_unique_invite_code()

        # 4. 创建用户与关联实体
        new_user = User(
            email=req.email.lower().strip(),
            hashed_password=hash_password(req.password),
            invite_code=invite_code,
            invited_by=inviter_id,
            status="active",
        )

        username = req.email.split("@")[0]
        default_avatar = f"https://api.dicebear.com/7.x/bottts/svg?seed={username}"

        initial_badges: list[dict[str, Any]] = [
            {"id": "1", "name": "星元萌动", "color": "#FDE68A", "description": "初次踏入叙梦世界的旅人"},
        ]

        new_profile = UserProfile(
            user=new_user,
            username=username,
            avatar_url=default_avatar,
            vip_level=0,
            player_level=1,
            player_xp=0,
            creator_level=1,
            creator_xp=0,
            badges=initial_badges,
        )

        # 新人赠送 100 星元与 50 月华
        new_wallet = UserWallet(
            user=new_user,
            star_coins=100,
            moon_gems=50,
            version=0,
        )

        db.add_all([new_user, new_profile, new_wallet])
        await db.flush()
        await db.commit()

        # 重新预加载关联
        refreshed_user = await cls.get_user_by_id(db, new_user.id)
        if not refreshed_user:
            raise HTTPException(status_code=500, detail="用户创建失败")

        token = create_access_token(user_id=refreshed_user.id, email=refreshed_user.email)
        return refreshed_user, token

    @classmethod
    async def login(
        cls,
        db: AsyncSession,
        req: UserLoginRequest,
    ) -> tuple[User, str]:
        """用户密码登录校验。

        Args:
            db: 异步数据库会话。
            req: 登录请求参数。

        Returns:
            tuple[User, str]: 登录成功的用户实体与 JWT 令牌。

        Raises:
            HTTPException: 用户不存在、密码错误或账号被封禁时抛出。
        """
        user = await cls.get_user_by_email(db, req.email.lower().strip())
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账号或密码错误，请检查后重试",
            )

        if not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="账号或密码错误，请检查后重试",
            )

        if user.status != "active":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="该账号已被冻结或封禁，请联系客服",
            )

        token = create_access_token(user_id=user.id, email=user.email)
        return user, token

    @classmethod
    async def get_user_by_id(cls, db: AsyncSession, user_id: uuid.UUID) -> User | None:
        """根据 ID 查询用户及其资料与钱包。"""
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.profile),
                selectinload(User.wallet),
            )
        )
        return (await db.execute(stmt)).scalar_one_or_none()

    @classmethod
    async def get_user_by_email(cls, db: AsyncSession, email: str) -> User | None:
        """根据邮箱查询用户。"""
        stmt = (
            select(User)
            .where(User.email == email)
            .options(
                selectinload(User.profile),
                selectinload(User.wallet),
            )
        )
        return (await db.execute(stmt)).scalar_one_or_none()

    @classmethod
    def to_profile_response(cls, user: User) -> UserProfileResponse:
        """将用户 ORM 模型映射为与前端 100% 兼容的响应 DTO。"""
        profile = user.profile
        wallet = user.wallet

        return UserProfileResponse(
            id=user.id,
            email=user.email,
            username=profile.username if profile else user.email.split("@")[0],
            is_custom_username=bool(getattr(profile, "is_custom_username", False)) if profile else False,
            avatar_url=profile.avatar_url if profile else "",
            vip_level=profile.vip_level if profile else 0,
            player_level=profile.player_level if profile else 1,
            player_xp=profile.player_xp if profile else 0,
            creator_level=profile.creator_level if profile else 1,
            creator_xp=profile.creator_xp if profile else 0,
            invite_code=user.invite_code,
            badges=profile.badges if profile and isinstance(profile.badges, list) else [],
            wallet=UserWalletResponse(
                star_coins=wallet.star_coins if wallet else 0,
                moon_gems=wallet.moon_gems if wallet else 0,
            ),
        )

    @classmethod
    async def update_profile(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        req: UserProfileUpdateRequest,
    ) -> UserProfileResponse:
        """更新当前用户的昵称或头像，并将 is_custom_username 标为已设置。

        Args:
            db: 异步数据库会话。
            user_id: 当前登录用户 ID。
            req: 资料更新请求体。

        Returns:
            UserProfileResponse: 更新后的用户资料 DTO。

        Raises:
            HTTPException: 用户不存在或昵称不合规。
        """
        trimmed_name = req.username.strip()
        if len(trimmed_name) < 2 or len(trimmed_name) > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户昵称长度必须在 2 到 20 个字符之间",
            )

        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.profile),
                selectinload(User.wallet),
            )
        )
        user = (await db.execute(stmt)).scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在",
            )

        profile = user.profile
        if not profile:
            profile = UserProfile(
                user=user,
                username=trimmed_name,
                is_custom_username=True,
                avatar_url=req.avatar_url.strip() if req.avatar_url else f"https://api.dicebear.com/7.x/bottts/svg?seed={trimmed_name}",
            )
            db.add(profile)
        else:
            profile.username = trimmed_name
            profile.is_custom_username = True
            if req.avatar_url is not None:
                profile.avatar_url = req.avatar_url.strip()

        await db.commit()

        refreshed_user = await cls.get_user_by_id(db, user_id)
        if not refreshed_user:
            raise HTTPException(status_code=500, detail="用户资料更新异常")

        return cls.to_profile_response(refreshed_user)

