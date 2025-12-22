"""Redis 连接管理，提供缓存服务统一接口。"""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import lru_cache
from typing import cast

import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import RedisError

from config import config_manager
from core.logging import get_logger


logger = get_logger(__name__)
_DEFAULT_PREFIX = "bridgetalk"


class RedisService:
    """Redis 服务（单实例）"""

    def __init__(self) -> None:
        self._client: Redis | None = None
        self._key_prefix = _DEFAULT_PREFIX
        self._initialize_client()

    def _initialize_client(self) -> None:
        """初始化全局 Redis 客户端"""
        redis_config = config_manager.redis
        if redis_config.key_prefix:
            self._key_prefix = redis_config.key_prefix
        pool = ConnectionPool(
            host=redis_config.host,
            port=redis_config.port,
            password=redis_config.password or None,
            db=redis_config.database,
            max_connections=redis_config.max_connections,
            socket_timeout=redis_config.socket_timeout,
            socket_connect_timeout=redis_config.socket_connect_timeout,
            decode_responses=True,
            health_check_interval=redis_config.health_check_interval,
        )
        self._client = redis.Redis(connection_pool=pool)
        logger.info("Redis 连接初始化成功")

    def _build_key(self, key: str) -> str:
        """构建带前缀的 key"""
        return f"{self._key_prefix}:{key}"

    def get_client(self) -> Redis:
        """获取 Redis 客户端（直接操作 Redis 的场景）"""
        if self._client is None:
            msg = "Redis 客户端未初始化"
            raise RuntimeError(msg)
        return self._client

    async def set(self, key: str, value: str | bytes, ex: int | None = None) -> bool:
        """SET 操作（自动添加前缀）"""
        if self._client is None:
            logger.error("Redis 客户端未初始化")
            return False
        prefixed_key = self._build_key(key)
        try:
            await self._client.set(prefixed_key, value, ex=ex)
        except (RedisError, ValueError):
            logger.exception("Redis SET 失败: %s", prefixed_key)
            return False
        else:
            return True

    async def get(self, key: str) -> str | bytes | None:
        """GET 操作（自动添加前缀）"""
        if self._client is None:
            logger.error("Redis 客户端未初始化")
            return None
        prefixed_key = self._build_key(key)
        try:
            return await self._client.get(prefixed_key)
        except (RedisError, ValueError):
            logger.exception("Redis GET 失败: %s", prefixed_key)
            return None

    async def delete(self, *keys: str) -> int:
        """DELETE 操作（自动添加前缀）"""
        if not keys or self._client is None:
            return 0
        prefixed_keys = [self._build_key(key) for key in keys]
        try:
            return await self._client.delete(*prefixed_keys)
        except (RedisError, ValueError):
            logger.exception("Redis DELETE 失败")
            return 0

    async def expire(self, key: str, time: int) -> bool:
        """EXPIRE 操作（自动添加前缀）"""
        if self._client is None:
            logger.error("Redis 客户端未初始化")
            return False
        prefixed_key = self._build_key(key)
        try:
            return await self._client.expire(prefixed_key, time)
        except (RedisError, ValueError):
            logger.exception("Redis EXPIRE 失败: %s", prefixed_key)
            return False

    async def scan_iter(self, match: str) -> AsyncIterator[str]:
        """SCAN 迭代器（自动添加前缀到 match 模式）"""
        if self._client is None:
            logger.error("Redis 客户端未初始化")
            return
        prefixed_match = self._build_key(match)
        try:
            async for raw_key in self._client.scan_iter(match=prefixed_match):
                yield cast(str, raw_key)
        except (RedisError, ValueError):
            logger.exception("Redis SCAN 失败: %s", prefixed_match)

    async def delete_by_pattern(self, pattern: str) -> int:
        """根据模式删除 key（自动添加前缀）"""
        if self._client is None:
            logger.error("Redis 客户端未初始化")
            return 0
        deleted_count = 0
        try:
            async for key in self.scan_iter(pattern):
                await self._client.delete(key)
                deleted_count += 1
        except (RedisError, ValueError):
            logger.exception("Redis 按模式删除失败: %s", pattern)
            return 0
        else:
            return deleted_count

    async def close(self) -> None:
        """关闭连接"""
        if self._client is not None:
            try:
                await self._client.close()
                logger.info("Redis 连接已关闭")
            except Exception:
                logger.exception("关闭 Redis 连接失败")


@lru_cache(maxsize=1)
def redis_service() -> RedisService:
    """RedisService 单例访问入口"""
    return RedisService()
