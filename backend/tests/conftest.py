"""Pytest 全局 Fixture 与异步测试环境配置。"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.core.cache import local_cache
from app.core.database import Base, get_async_db
from app.core.redis import close_redis_connection
from app.main import app as fastapi_app

get_settings().APP_ENV = "test"

# 导入所有 ORM 模型以确保 Base.metadata 注册完全
import app.models.character  # noqa: F401
import app.models.chat  # noqa: F401
import app.models.mod  # noqa: F401
import app.models.ops  # noqa: F401
import app.models.user  # noqa: F401

# 全局共享测试用 SQLite 内存引擎
test_async_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    echo=False,
)
TestAsyncSessionLocal = async_sessionmaker(
    bind=test_async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """测试用数据库会话注入。"""
    async with TestAsyncSessionLocal() as session:
        yield session


fastapi_app.dependency_overrides[get_async_db] = override_get_async_db


@pytest_asyncio.fixture(autouse=True)
async def setup_test_db() -> AsyncGenerator[None, None]:
    """在每个测试用例前初始化数据库表结构，测试后清理。"""
    local_cache.clear()
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    local_cache.clear()
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def cleanup_redis_fixture() -> AsyncGenerator[None, None]:
    """在每个异步测试运行前后重置 Redis 连接池，避免跨事件循环复用关闭的 Loop。"""
    yield
    await close_redis_connection()
