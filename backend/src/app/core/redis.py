"""异步 Redis 客户端与连接池管理模块。

提供 Redis 异步客户端单例、连接生命周期管理与健康探针。

Usage:
    >>> from app.core.redis import get_redis_client, close_redis_connection
    >>> redis = get_redis_client()
    >>> await redis.set("key", "val", ex=60)
"""

import logging

from redis.asyncio import ConnectionPool, Redis

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_redis_pool: ConnectionPool | None = None
_redis_client: Redis | None = None


def get_redis_pool() -> ConnectionPool:
    """获取或初始化 Redis 异步连接池。

    Returns:
        ConnectionPool: Redis 异步连接池单例。
    """
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = ConnectionPool.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            max_connections=50,
        )
    return _redis_pool


def get_redis_client() -> Redis:
    """获取 Redis 异步客户端实例。

    Returns:
        Redis: Redis 异步客户端。

    Usage:
        >>> redis = get_redis_client()
        >>> await redis.ping()
        True
    """
    global _redis_client
    if _redis_client is None:
        pool = get_redis_pool()
        _redis_client = Redis(connection_pool=pool)
    return _redis_client


async def close_redis_connection() -> None:
    """优雅关闭 Redis 连接池。

    在 FastAPI 应用关闭钩子 (Lifespan) 中调用。
    """
    global _redis_client, _redis_pool
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
    if _redis_pool is not None:
        await _redis_pool.disconnect()
        _redis_pool = None
    logger.info("Redis 异步连接池已安全释放")
