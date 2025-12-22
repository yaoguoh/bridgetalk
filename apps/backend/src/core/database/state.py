"""数据库引擎与 SessionFactory 注册表。

提供可注入的 `DatabaseRegistry`，统一管理多租户 AsyncEngine & SessionFactory。
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


def _empty_engines() -> dict[str, AsyncEngine]:
    return {}


def _empty_session_factories() -> dict[str, async_sessionmaker[AsyncSession]]:
    return {}


@dataclass
class DatabaseRegistry:
    """记录多租户数据库资源的注册表。"""

    _engines: dict[str, AsyncEngine] = field(default_factory=_empty_engines)
    _session_factories: dict[str, async_sessionmaker[AsyncSession]] = field(default_factory=_empty_session_factories)

    def register_engine(self, realm: str, engine: AsyncEngine) -> None:
        """注册或更新指定租户的 AsyncEngine。"""

        self._engines[realm] = engine

    def get_engine(self, realm: str) -> AsyncEngine | None:
        """获取指定租户的 AsyncEngine。"""

        return self._engines.get(realm)

    def register_session_factory(self, realm: str, factory: async_sessionmaker[AsyncSession]) -> None:
        """注册或更新指定租户的 SessionFactory。"""

        self._session_factories[realm] = factory

    def get_session_factory(self, realm: str) -> async_sessionmaker[AsyncSession] | None:
        """获取指定租户的 SessionFactory。"""

        return self._session_factories.get(realm)

    def engines(self) -> Mapping[str, AsyncEngine]:
        """返回所有已注册引擎的只读视图。"""

        return dict(self._engines)

    def session_factories(self) -> Mapping[str, async_sessionmaker[AsyncSession]]:
        """返回所有 SessionFactory 的只读视图。"""

        return dict(self._session_factories)

    def clear(self) -> None:
        """清空所有注册记录。"""

        self._engines.clear()
        self._session_factories.clear()


# 默认注册表实例，供未通过容器注入的模块使用。
database_registry = DatabaseRegistry()

__all__ = ["DatabaseRegistry", "database_registry"]
