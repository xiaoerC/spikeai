"""用户认证与登录路由控制层。

提供注册、账号密码登录与登出拉黑 Token 功能。

Usage:
    POST /api/v1/auth/register
    POST /api/v1/auth/login
    POST /api/v1/auth/logout
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import add_token_to_blacklist
from app.schemas.common import ApiResponse
from app.schemas.user import (
    UserLoginRequest,
    UserRegisterRequest,
)
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["认证与权限 (Auth)"])


@router.post(
    "/register",
    response_model=ApiResponse[dict[str, Any]],
    summary="用户注册",
    description="支持邮箱、密码与邀请码注册，自动赠送新人初始资产 (100星元+50月华)。",
)
async def register(
    req: UserRegisterRequest,
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[dict[str, Any]]:
    """处理用户注册请求。"""
    user, token = await AuthService.register(db, req)
    profile_dto = AuthService.to_profile_response(user)

    return ApiResponse(
        code=0,
        message="注册成功，欢迎加入叙梦！",
        show_message=True,
        data={
            "access_token": token,
            "token_type": "bearer",
            "user": profile_dto.model_dump(),
        },
    )


@router.post(
    "/login",
    response_model=ApiResponse[dict[str, Any]],
    summary="账号密码登录",
    description="校验邮箱与密码，返回 JWT 访问凭证及用户资料。",
)
async def login(
    req: UserLoginRequest,
    db: AsyncSession = Depends(get_async_db),
) -> ApiResponse[dict[str, Any]]:
    """处理用户登录请求。"""
    user, token = await AuthService.login(db, req)
    profile_dto = AuthService.to_profile_response(user)

    return ApiResponse(
        code=0,
        message="登录成功，欢迎回来！",
        show_message=True,
        data={
            "access_token": token,
            "token_type": "bearer",
            "user": profile_dto.model_dump(),
        },
    )


@router.post(
    "/logout",
    response_model=ApiResponse[None],
    summary="退出登录",
    description="注销登录状态并将当前 JWT 令牌加入 Redis 黑名单。",
)
async def logout(
    authorization: str | None = Header(default=None),
) -> ApiResponse[None]:
    """处理用户退出登录请求。"""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "").strip()
        await add_token_to_blacklist(token)

    return ApiResponse(code=0, message="已成功退出登录", show_message=True)
