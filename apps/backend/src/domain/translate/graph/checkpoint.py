from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator, Callable, Coroutine, Iterator, Sequence
from typing import Any, Protocol, cast, override, runtime_checkable

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from langgraph.checkpoint.redis.aio import AsyncRedisSaver
from langgraph.checkpoint.redis.jsonplus_redis import JsonPlusRedisSerializer

from core.cache.redis_service import redis_service
from core.context.request import current_realm
from core.logging import get_logger
from core.type.common import JSONDict


logger = get_logger(__name__)


class ProjectAwareRedisSerializer(JsonPlusRedisSerializer):
    """
    项目感知的 Redis Checkpoint 序列化器。

    允许反序列化项目内的 Pydantic 模型，避免恢复状态时被拒绝。
    """

    def __init__(self) -> None:
        super().__init__(allowed_json_modules=True)


@runtime_checkable
class CheckpointSaverProtocol(Protocol):
    """LangGraph Checkpoint Saver 协议。"""

    async def aget_tuple(self, config: RunnableConfig) -> CheckpointTuple | None: ...

    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None: ...

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig: ...

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig: ...

    async def aput_writes(
        self, config: RunnableConfig, writes: Sequence[tuple[str, object]], task_id: str, task_path: str = ""
    ) -> None: ...

    def put_writes(
        self, config: RunnableConfig, writes: Sequence[tuple[str, object]], task_id: str, task_path: str = ""
    ) -> None: ...

    def alist(
        self,
        config: RunnableConfig | None,
        *,
        filter: dict[str, object] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> AsyncIterator[CheckpointTuple]: ...

    def list(
        self,
        config: RunnableConfig | None,
        *,
        filter: dict[str, object] | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
    ) -> Iterator[CheckpointTuple]: ...

    async def adelete_thread(self, thread_id: str) -> None: ...

    def delete_thread(self, thread_id: str) -> None: ...


SetupFn = Callable[[], Coroutine[object, object, None]]


def _run_sync(coro: Coroutine[object, object, object]) -> object:
    """将异步协程安全地转换为同步调用。"""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    msg = "同步调用 LangGraph Checkpointer 接口必须在事件循环外执行，请使用异步接口。"
    raise RuntimeError(msg)


class TenantAwareRedisSaver(BaseCheckpointSaver[str]):
    """多租户感知的 Redis 检查点保存器。"""

    def __init__(self) -> None:
        super().__init__(serde=ProjectAwareRedisSerializer())
        self.savers: dict[str, CheckpointSaverProtocol] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._init_lock = asyncio.Lock()

    async def aget_checkpointer(self) -> CheckpointSaverProtocol:
        """异步获取当前租户的检查点处理器。"""
        realm = current_realm()
        if realm not in self._locks:
            async with self._init_lock:
                if realm not in self._locks:
                    self._locks[realm] = asyncio.Lock()
        async with self._locks[realm]:
            if realm not in self.savers:
                logger.info("为租户 %s 创建新的 AsyncRedisSaver 实例", realm)
                redis_client = redis_service().get_client()
                saver_kwargs: dict[str, Any] = {"redis_client": redis_client}
                saver = AsyncRedisSaver(**saver_kwargs)
                saver.serde = ProjectAwareRedisSerializer()
                setup_fn: SetupFn | None = getattr(saver, "asetup", None) or getattr(saver, "setup", None)
                if setup_fn:
                    await setup_fn()
                self.savers[realm] = cast(CheckpointSaverProtocol, cast(object, saver))
        return self.savers[realm]

    def _get_checkpointer_sync(self) -> CheckpointSaverProtocol:
        """同步场景下获取当前租户的保存器。"""
        if (realm := current_realm()) in self.savers:
            return self.savers[realm]
        return cast(CheckpointSaverProtocol, _run_sync(self.aget_checkpointer()))

    @override
    async def aget_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        checkpointer = await self.aget_checkpointer()
        return await checkpointer.aget_tuple(config)

    def get_tuple(self, config: RunnableConfig) -> CheckpointTuple | None:
        return self._get_checkpointer_sync().get_tuple(config)

    @override
    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        checkpointer = await self.aget_checkpointer()
        return await checkpointer.aput(config, checkpoint, metadata, new_versions)

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        return self._get_checkpointer_sync().put(config, checkpoint, metadata, new_versions)

    @override
    async def aput_writes(
        self, config: RunnableConfig, writes: Sequence[tuple[str, object]], task_id: str, task_path: str = ""
    ) -> None:
        checkpointer = await self.aget_checkpointer()
        await checkpointer.aput_writes(config, writes, task_id, task_path)

    def put_writes(
        self, config: RunnableConfig, writes: Sequence[tuple[str, object]], task_id: str, task_path: str = ""
    ) -> None:
        saver = self._get_checkpointer_sync()
        put_writes_fn = saver.put_writes
        put_writes_fn(config, writes, task_id, task_path)

    @override
    async def alist(
        self,
        config: RunnableConfig | None,
        *,
        filter_: JSONDict | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
        **kwargs: object,
    ) -> AsyncIterator[CheckpointTuple]:
        checkpointer = await self.aget_checkpointer()
        raw_filter = filter_ if filter_ is not None else kwargs.get("filter")
        filters = cast(dict[str, Any] | None, raw_filter)
        async for item in checkpointer.alist(config, filter=filters, before=before, limit=limit):
            yield item

    def list(
        self,
        config: RunnableConfig | None,
        *,
        filter_: JSONDict | None = None,
        before: RunnableConfig | None = None,
        limit: int | None = None,
        **kwargs: object,
    ) -> Iterator[CheckpointTuple]:
        raw_filter = filter_ if filter_ is not None else kwargs.get("filter")
        filters = cast(dict[str, Any] | None, raw_filter)
        return self._get_checkpointer_sync().list(config, filter=filters, before=before, limit=limit)

    async def adelete_thread(self, thread_id: str) -> None:
        saver = await self.aget_checkpointer()
        delete_fn = saver.adelete_thread
        await delete_fn(thread_id)

    def delete_thread(self, thread_id: str) -> None:
        saver = self._get_checkpointer_sync()
        delete_fn = saver.delete_thread
        delete_fn(thread_id)

    def get_next_version(self, current: str | None, channel: None) -> str:  # noqa: ARG002
        """生成下一个版本号。"""
        if current is None:
            current_v = 0
        elif isinstance(current, int):
            current_v = current
        else:
            current_v = int(current.split(".")[0])
        next_v = current_v + 1
        next_h = uuid.uuid4().hex[:16]
        return f"{next_v:032}.{next_h}"
