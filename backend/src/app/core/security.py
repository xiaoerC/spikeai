"""用户认证安全与 JWT 令牌管理模块。

实现基于 Passlib Bcrypt 的密码安全哈希/验证、JWT 双令牌签发/解析与 Redis 令牌黑名单撤销机制。

Usage:
    >>> from app.core.security import hash_password, verify_password, create_access_token
    >>> hashed = hash_password("secret123")
    >>> assert verify_password("secret123", hashed) is True
"""

import logging
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.core.database import get_async_db
from app.core.redis import get_redis_client
from app.models.admin import AdminPermission, AdminRole, AdminUser
from app.models.user import User


logger = logging.getLogger(__name__)
settings = get_settings()

http_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """对明文密码执行 Bcrypt 安全哈希。

    Args:
        password: 用户原始明文密码。

    Returns:
        str: Bcrypt 加盐哈希密文。
    """
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """比对明文密码与哈希密文是否一致。

    Args:
        plain_password: 明文密码。
        hashed_password: 数据库存储的哈希密文。

    Returns:
        bool: 密码匹配返回 True，否则返回 False。
    """
    password_bytes = plain_password.encode("utf-8")[:72]
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(
    user_id: uuid.UUID,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    """生成 JWT 访问令牌 (Access Token)。

    Args:
        user_id: 用户唯一 UUID。
        email: 用户邮箱。
        expires_delta: 自定义过期时间段。

    Returns:
        str: 编码后的 JWT Token 字符串。
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "aud": "client",
        "exp": expire,
        "iat": datetime.now(UTC),
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_admin_access_token(
    admin_id: uuid.UUID,
    username: str,
    is_super_admin: bool = False,
    expires_delta: timedelta | None = None,
) -> str:
    """生成后台专属 JWT 访问令牌 (Access Token, aud='admin')。

    Args:
        admin_id: 管理员唯一 UUID。
        username: 管理员登录名。
        is_super_admin: 是否超级管理员。
        expires_delta: 自定义过期时间段。

    Returns:
        str: 编码后的后台专用 JWT Token 字符串。
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: dict[str, Any] = {
        "sub": str(admin_id),
        "username": username,
        "aud": "admin",
        "is_super": is_super_admin,
        "exp": expire,
        "iat": datetime.now(UTC),
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)



def decode_access_token(token: str) -> dict[str, Any] | None:
    """解码并校验 JWT Token 载荷。

    Args:
        token: JWT 字符串。

    Returns:
        dict[str, Any] | None: 成功返回 payload 字典，失败返回 None。
    """
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None


async def add_token_to_blacklist(token: str, expire_seconds: int = 3600 * 24 * 7) -> None:
    """将已注销的 Token 加入 Redis 黑名单。

    Args:
        token: JWT Token 字符串。
        expire_seconds: 黑名单键在 Redis 中的 TTL 过期时间。
    """
    redis = get_redis_client()
    if redis:
        try:
            await redis.setex(f"token_blacklist:{token}", expire_seconds, "revoked")
        except Exception as e:
            logger.warning("写入 Redis Token 黑名单失败: %s", e)


async def is_token_blacklisted(token: str) -> bool:
    """校验 Token 是否存在于 Redis 黑名单中。

    Args:
        token: JWT Token 字符串。

    Returns:
        bool: 若已拉黑返回 True，否则返回 False。
    """
    redis = get_redis_client()
    if redis:
        try:
            val = await redis.get(f"token_blacklist:{token}")
            return val is not None
        except Exception as e:
            logger.warning("查询 Redis Token 黑名单失败: %s", e)
    return False


async def get_current_user(
    auth: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    """FastAPI 依赖注入: 从请求 Header Authorization 获取并验证当前登录用户。

    Args:
        auth: HTTP Bearer 认证凭据。
        db: 异步数据库会话。

    Returns:
        User: 当前有效登录用户模型实体。

    Raises:
        HTTPException: 未提供 Token、Token 已过期/失效或已被拉黑时抛出 401 异常。
    """
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录后再进行操作",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth.credentials

    # 1. 检查 Redis 黑名单
    if await is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录状态已失效，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 解析 JWT 载荷
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )

        user_id_str: str | None = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的登录凭证",
            )
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError) as e:
        logger.warning("JWT 解析失败: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录凭证已过期或无效",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # 3. 查库获取用户及其关联资料与钱包
    stmt = (
        select(User)
        .where(User.id == user_id, User.status == "active")
        .options(
            selectinload(User.profile),
            selectinload(User.wallet),
        )
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在或已被封禁",
        )

    return user


async def get_current_admin_user(
    auth: HTTPAuthorizationCredentials | None = Depends(http_bearer),
    db: AsyncSession = Depends(get_async_db),
) -> AdminUser:
    """FastAPI 依赖注入: 从请求 Header Authorization 获取并验证当前后台管理用户。

    严格校验 Token 的 aud 字段必须为 'admin'，从根源杜绝前台 C 端用户越权穿透。

    Args:
        auth: HTTP Bearer 认证凭据。
        db: 异步数据库会话。

    Returns:
        AdminUser: 当前有效后台管理员实体 (预加载 roles 及其 permissions)。

    Raises:
        HTTPException: 未认证、Token 已拉黑、受众非 admin 或账号已被禁用时抛出对应异常。
    """
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="请先登录管理后台",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth.credentials

    # 1. 检查 Redis 黑名单
    if await is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="管理员登录状态已失效，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. 解析 JWT 载荷并强制校验 aud='admin'
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False},
        )
        aud: str | None = payload.get("aud")

        if aud != "admin":
            logger.warning("非法访问后台接口: Token aud 不匹配 (%s)", aud)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="非法凭证：非后台管理有效令牌，拒绝访问",
            )

        admin_id_str: str | None = payload.get("sub")
        if not admin_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的管理员凭证",
            )
        admin_id = uuid.UUID(admin_id_str)
    except (JWTError, ValueError) as e:
        logger.warning("后台 JWT 解析失败: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录凭据已过期或无效",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

    # 3. 查库获取管理员实体并预加载角色与部门
    stmt = (
        select(AdminUser)
        .where(AdminUser.id == admin_id)
        .options(
            selectinload(AdminUser.department),
            selectinload(AdminUser.roles).selectinload(AdminRole.permissions),
        )
    )
    result = await db.execute(stmt)
    admin_user = result.scalar_one_or_none()

    if not admin_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="管理员账号不存在",
        )

    if admin_user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="管理员账号已被禁用，请联系超级管理员",
        )

    return admin_user


class RequirePermission:
    """声明式细粒度权限守卫依赖项。

    超级管理员直接无条件放行；普通管理员根据其拥有的角色关联的 permissions code 进行校验。

    Usage:
        >>> @router.post("/users", dependencies=[Depends(RequirePermission("system:user:create"))])
        >>> async def create_admin_user(...):
        >>>     ...
    """

    def __init__(self, *permission_codes: str, require_all: bool = False) -> None:
        """初始化权限守卫。

        Args:
            *permission_codes: 所需权限唯一编码列表 (如 'system:user:create')。
            require_all: 是否需要同时满足所有权限编码，默认 False (满足其一即可)。
        """
        self.permission_codes = set(permission_codes)
        self.require_all = require_all

    async def __call__(
        self,
        current_admin: AdminUser = Depends(get_current_admin_user),
    ) -> AdminUser:
        # 1. 超级管理员拥有全系统最高无限制权限
        if current_admin.is_super_admin:
            return current_admin

        # 2. 收集该管理员所有激活角色下的所有激活权限编码
        user_perm_codes: set[str] = set()
        for role in current_admin.roles:
            if role.status == "active":
                for perm in role.permissions:
                    if perm.status == "active":
                        user_perm_codes.add(perm.code)

        # 3. 校验权限匹配
        if self.require_all:
            has_permission = self.permission_codes.issubset(user_perm_codes)
        else:
            has_permission = bool(self.permission_codes & user_perm_codes)

        if not has_permission:
            logger.warning(
                "管理员 %s(ID:%s) 尝试越权访问，缺少权限: %s，当前持有: %s",
                current_admin.username,
                current_admin.id,
                self.permission_codes,
                user_perm_codes,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"无权限执行此操作，缺少必要权限代码: {list(self.permission_codes)}",
            )

        return current_admin

