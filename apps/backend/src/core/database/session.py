"""数据库基础设施：Session 依赖、引擎初始化与迁移工具。"""

from __future__ import annotations

import asyncio
import subprocess
import sys
from collections.abc import AsyncGenerator
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from config import config_manager
from core.database import database_registry
from core.logging import get_logger


logger = get_logger(__name__)
_DEFAULT_REALM = "default"
_MIGRATION_CMD = [sys.executable, "-m", "alembic", "upgrade", "head"]


async def db_session() -> AsyncGenerator[AsyncSession]:
    """
    提供标准的 AsyncSession 依赖。

    - 每次调用创建一个新的 AsyncSession
    - 请求结束时自动关闭 Session, 连接归还到连接池
    """
    session_factory = database_registry.get_session_factory(_DEFAULT_REALM)
    if session_factory is None:
        msg = "数据库 SessionFactory 未初始化"
        raise RuntimeError(msg)
    async with session_factory() as session:
        yield session


async def initialize_db_engines() -> AsyncEngine:
    """
    初始化数据库引擎（单租户模式）。

    应在应用启动时调用 (lifespan startup)。
    """
    if (engine := database_registry.get_engine(_DEFAULT_REALM)) is not None:
        logger.info("Database engine already initialized")
        return engine

    db_config = config_manager.database
    db_url = db_config.build_url()

    engine = create_async_engine(
        db_url,
        pool_size=db_config.pool_size,
        max_overflow=db_config.max_overflow,
        pool_timeout=db_config.pool_timeout,
        pool_recycle=db_config.pool_recycle,
        pool_pre_ping=db_config.pool_pre_ping,
        echo=False,
    )

    database_registry.register_engine(_DEFAULT_REALM, engine)
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    database_registry.register_session_factory(_DEFAULT_REALM, session_factory)

    logger.info("Database engine initialized")
    return engine


async def close_db_engines() -> None:
    """关闭数据库引擎。"""
    engine = database_registry.get_engine(_DEFAULT_REALM)
    if engine is not None:
        await engine.dispose()
        logger.info("Database engine disposed")
    database_registry.clear()


async def run_migrations() -> None:
    """执行数据库迁移（alembic upgrade head）。"""
    backend_root = Path(__file__).resolve().parents[3]
    try:
        result = await asyncio.to_thread(
            subprocess.run,
            _MIGRATION_CMD,
            capture_output=True,
            text=True,
            cwd=str(backend_root),
            check=True,
        )
        if result.stdout:
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    logger.debug("%s", line)
        logger.info("Database migration completed")
    except subprocess.CalledProcessError as exc:
        logger.exception("Migration failed")
        msg = f"Database migration failed: {exc.stderr or str(exc)}"
        raise RuntimeError(msg) from exc
