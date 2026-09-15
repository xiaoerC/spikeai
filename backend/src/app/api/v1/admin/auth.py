"""后台管理系统认证与个人资料 API 路由。

包含管理员登录 (JWT aud='admin')、获取动态菜单树与细粒度权限清单 (/me) 及安全注销。

Usage:
    POST /api/v1/admin/auth/login
    GET  /api/v1/admin/auth/me
    POST /api/v1/admin/auth/logout
"""

import logging
from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.core.database import get_async_db
from app.core.security import (
    add_token_to_blacklist,
    create_admin_access_token,
    get_current_admin_user,
    hash_password,
    http_bearer,
    verify_password,
)
from app.models.admin import AdminPermission, AdminRole, AdminUser
from app.schemas.admin import (
    AdminChangePasswordRequest,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminMeResponse,
    AdminMenuNode,
    AdminUserInfo,
)

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/auth", tags=["后台管理员认证"])


def build_menu_tree(
    permissions: list[AdminPermission],
    parent_id: Any = None,
) -> list[AdminMenuNode]:
    """将权限节点平铺列表递归转换为嵌套的菜单树。

    仅包含 directory 和 menu 类型的节点（排除 button 按钮权限）。
    """
    nodes: list[AdminMenuNode] = []
    # 筛选当前父级下的目录和菜单
    curr_items = [
        p for p in permissions
        if p.parent_id == parent_id and p.type in ("directory", "menu") and p.status == "active"
    ]
    # 按照 sort 字段升序排列
    curr_items.sort(key=lambda x: x.sort)

    for item in curr_items:
        node = AdminMenuNode(
            id=item.id,
            parent_id=item.parent_id,
            type=item.type,
            title=item.title,
            name=item.name,
            code=item.code,
            path=item.path,
            component=item.component,
            icon=item.icon,
            sort=item.sort,
            is_hidden=item.is_hidden,
            children=build_menu_tree(permissions, item.id),
        )
        nodes.append(node)
    return nodes


@router.post("/login", response_model=AdminLoginResponse, summary="后台管理员登录")
async def admin_login(
    req_body: AdminLoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
) -> AdminLoginResponse:
    """验证管理员用户名与密码，成功则签发后台专属 JWT (aud='admin')。"""
    stmt = (
        select(AdminUser)
        .where(AdminUser.username == req_body.username)
        .options(
            selectinload(AdminUser.department),
            selectinload(AdminUser.roles),
        )
    )
    result = await db.execute(stmt)
    admin_user = result.scalar_one_or_none()

    if not admin_user or not verify_password(req_body.password, admin_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )

    if admin_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该账号已被封禁或禁用，请联系超级管理员",
        )

    # 更新最后登录时间与 IP
    client_ip = request.client.host if request.client else "unknown"
    admin_user.last_login_at = datetime.now(UTC)
    admin_user.last_login_ip = client_ip
    await db.commit()

    # 签发专属 JWT
    token = create_admin_access_token(
        admin_id=admin_user.id,
        username=admin_user.username,
        is_super_admin=admin_user.is_super_admin,
    )

    logger.info("管理员登录成功: %s (IP: %s)", admin_user.username, client_ip)
    return AdminLoginResponse(
        access_token=token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/me", response_model=AdminMeResponse, summary="获取当前管理员资料与权限菜单树")
async def get_admin_me(
    current_admin: AdminUser = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db),
) -> AdminMeResponse:
    """拉取当前管理员个人资料、角色列表、拥有的全部权限编码及构建动态路由菜单树。"""
    role_keys = [r.role_key for r in current_admin.roles if r.status == "active"]

    if current_admin.is_super_admin:
        # 超级管理员获取系统全量激活权限与菜单
        stmt = select(AdminPermission).where(AdminPermission.status == "active")
        res = await db.execute(stmt)
        all_perms = list(res.scalars().all())

        perm_codes = [p.code for p in all_perms]
        menu_tree = build_menu_tree(all_perms, None)
    else:
        # 普通管理员按角色关联聚合去重
        perm_map: dict[str, AdminPermission] = {}
        for role in current_admin.roles:
            if role.status == "active":
                for perm in role.permissions:
                    if perm.status == "active":
                        perm_map[str(perm.id)] = perm

        user_perms = list(perm_map.values())
        perm_codes = [p.code for p in user_perms]
        menu_tree = build_menu_tree(user_perms, None)

    user_info = AdminUserInfo(
        id=current_admin.id,
        username=current_admin.username,
        email=current_admin.email,
        real_name=current_admin.real_name,
        avatar=current_admin.avatar,
        phone=current_admin.phone,
        job_number=current_admin.job_number,
        department_id=current_admin.department_id,
        department_name=current_admin.department.name if current_admin.department else None,
        is_super_admin=current_admin.is_super_admin,
        status=current_admin.status,
    )

    return AdminMeResponse(
        user_info=user_info,
        roles=role_keys,
        permissions=perm_codes,
        menus=menu_tree,
    )


@router.post("/logout", summary="安全注销并拉黑令牌")
async def admin_logout(
    auth: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    current_admin: AdminUser = Depends(get_current_admin_user),
) -> dict[str, Any]:
    """注销退出，将当前使用的 Token 存入 Redis 黑名单以销毁会话。"""
    if auth and auth.credentials:
        await add_token_to_blacklist(auth.credentials)
    logger.info("管理员安全注销: %s", current_admin.username)
    return {"message": "退出成功"}


@router.put("/change-password", summary="当前管理员修改登录密码")
async def admin_change_password(
    body: AdminChangePasswordRequest,
    db: AsyncSession = Depends(get_async_db),
    current_admin: AdminUser = Depends(get_current_admin_user),
) -> dict[str, Any]:
    """验证旧密码并更新为新密码。"""
    if not verify_password(body.old_password, current_admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前旧密码不正确",
        )

    current_admin.hashed_password = hash_password(body.new_password)
    await db.commit()
    logger.warning("管理员 %s 修改了自身登录密码", current_admin.username)
    return {"message": "密码修改成功，请使用新密码重新登录"}

