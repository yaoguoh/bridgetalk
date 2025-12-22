"""核心数据库模块：提供 ORM 基类与数据库注册表。"""

from __future__ import annotations

from sqlalchemy import MetaData

from .base import Base
from .state import DatabaseRegistry, database_registry


def get_metadata() -> MetaData:
    """返回 Base.metadata，供 Alembic 使用。"""
    return Base.metadata


__all__ = [
    "Base",
    "DatabaseRegistry",
    "database_registry",
    "get_metadata",
]
