"""BridgeTalk 应用入口"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import config_manager
from container import AppContainer
from core.cache.redis_service import redis_service
from core.database.session import close_db_engines, initialize_db_engines, run_migrations
from core.logging import configure_logging, get_bootstrap_logger, get_startup_logger
from domain.translate.api.routes import router as translate_router


# 静态文件目录
STATIC_DIR = Path(__file__).parent.parent / "static"

bootstrap_logger = get_bootstrap_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """应用生命周期管理"""
    bootstrap_logger.info("加载配置文件...")
    config_manager.initialize()

    log_level = os.getenv("LOG_LEVEL", config_manager.logging.level)
    configure_logging(level=log_level)
    startup_logger = get_startup_logger("startup.lifespan")

    startup_logger.info("正在启动 BridgeTalk...")

    redis_service()
    startup_logger.info("Redis 连接初始化完成")

    await initialize_db_engines()
    startup_logger.info("数据库引擎初始化完成")

    await run_migrations()
    startup_logger.info("数据库迁移完成")

    container = AppContainer()
    container.wire(modules=["domain.translate.api.routes"])
    _app.state.container = container
    startup_logger.info("依赖注入容器已初始化")

    startup_logger.info("BridgeTalk 启动完成")

    yield

    startup_logger.info("正在关闭 BridgeTalk...")

    await redis_service().close()
    startup_logger.info("Redis 连接已关闭")

    await close_db_engines()
    startup_logger.info("BridgeTalk 已关闭")


async def health_check() -> dict[str, Any]:
    """健康检查端点"""
    return {"status": "ok", "service": "BridgeTalk"}


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    application = FastAPI(
        title="BridgeTalk",
        description="职能沟通翻译助手 - 帮助产品经理和开发工程师更好地理解彼此",
        version="1.0.0",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(translate_router)
    application.add_api_route("/health", health_check, methods=["GET"])

    if STATIC_DIR.exists():
        application.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return application


app = create_app()


if __name__ == "__main__":
    import uvicorn

    config_manager.initialize()
    server = config_manager.server
    uvicorn.run("main:app", host=server.host, port=server.port, reload=True)
