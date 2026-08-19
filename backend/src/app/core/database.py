"""异步数据库引擎与会话管理模块。

基于 SQLAlchemy 2.0 Async 与 asyncpg 实现高性能异步 PostgreSQL 连接池与依赖注入。

Usage:
    >>> from fastapi import Depends
    >>> from sqlalchemy.ext.asyncio import AsyncSession
    >>> from app.core.database import get_async_db
    >>>
    >>> async def sample_endpoint(db: AsyncSession = Depends(get_async_db)):
    >>>     ...
"""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# 创建异步数据库引擎
async_engine: AsyncEngine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,
)

# 创建异步会话工厂
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 声明式模型基类。"""


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖注入: 获取异步数据库会话。

    自动管理 Session 生命周期，在发生未捕获异常时自动回滚事务，
    请求结束时安全关闭连接并归还连接池。

    Yields:
        AsyncSession: 异步数据库会话对象。

    Raises:
        Exception: 捕获并记录数据库异常，向上抛出以保证错误可观测。

    Usage:
        >>> async def handler(db: AsyncSession = Depends(get_async_db)):
        >>>     result = await db.execute(...)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            logger.exception("数据库事务执行异常，正在回滚")
            await session.rollback()
            raise
        finally:
            await session.close()
