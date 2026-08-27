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
