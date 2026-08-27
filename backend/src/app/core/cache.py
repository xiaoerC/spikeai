"""内存级微秒高速 TTL 缓存模块。

提供高性能进程内缓存与前缀失效机制，避免跨公网数据库频繁查询造成的毫秒/秒级网络延迟。

Usage:
    >>> from app.core.cache import local_cache
    >>> local_cache.set("key", value, ttl=30)
    >>> val = local_cache.get("key")
"""

import time
from typing import Any


class LocalTTLCache:
    """进程内内存微秒级 TTL 缓存。"""

    def __init__(self, default_ttl: int = 600) -> None:
        self._cache: dict[str, tuple[Any, float]] = {}
        self.default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        """获取缓存值，若已过期则自动清除并返回 None。"""
        if key in self._cache:
            val, expire_at = self._cache[key]
            if time.time() < expire_at:
                return val
            del self._cache[key]
        return None

    def set(self, key: str, val: Any, ttl: int | None = None) -> None:
        """写入缓存并设定过期秒数。"""
        effective_ttl = ttl if ttl is not None else self.default_ttl
        self._cache[key] = (val, time.time() + effective_ttl)

    def delete(self, key: str) -> None:
        """删除指定缓存键。"""
        self._cache.pop(key, None)

    def clear_prefix(self, prefix: str) -> None:
        """按前缀批量清除缓存。"""
        keys_to_del = [k for k in self._cache if k.startswith(prefix)]
        for k in keys_to_del:
            self._cache.pop(k, None)

    def clear(self) -> None:
        """清空全部缓存。"""
        self._cache.clear()


local_cache = LocalTTLCache(default_ttl=30)
