"""早期启动日志模块（最小依赖）.

在主日志系统加载之前提供基础日志功能。
用于应用启动阶段的日志记录（导入阶段、配置加载、lifespan 初始化等）。

Usage:
    from core.logging import get_import_logger, get_bootstrap_logger

    _import_logger = get_import_logger()
    _import_logger.info("Module importing...")

    _bootstrap_logger = get_bootstrap_logger()
    _bootstrap_logger.info("Container wiring...")
"""

from __future__ import annotations

import logging
import sys

from core.logging.config import LogConfig, MillisecondFormatter


__all__ = ["get_bootstrap_logger", "get_import_logger", "get_lifespan_logger"]
_EARLY_LOG_STATE: dict[str, bool] = {"configured": False}


def _configure_early_logging() -> None:
    """
    配置早期启动阶段的日志系统

    功能：
    1. 添加 StreamHandler 输出到 stderr（立即可见）
    2. 使用 Spring Boot 风格格式（与主日志系统一致）
    3. 设置 INFO 级别
    4. 幂等性保护（只运行一次）
    """
    if _EARLY_LOG_STATE["configured"]:
        return
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(MillisecondFormatter(LogConfig.LOG_FORMAT))
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)
    _EARLY_LOG_STATE["configured"] = True


def get_import_logger() -> logging.Logger:
    """
    获取导入阶段 logger

    Logger 名称: 'startup.imports'
    用于模块导入期间的日志记录（uvicorn 子进程启动后的空白期）

    Example:
        >>> _import_logger = get_import_logger()
        >>> _import_logger.info("FastAPI imported, loading application modules...")
    """
    _configure_early_logging()
    return logging.getLogger("startup.imports")


def get_bootstrap_logger() -> logging.Logger:
    """
    获取引导阶段 logger

    Logger 名称: 'startup.bootstrap'
    用于配置加载和容器连接期间的日志记录

    Example:
        >>> _bootstrap_logger = get_bootstrap_logger()
        >>> _bootstrap_logger.info("Loading configuration files...")
    """
    _configure_early_logging()
    return logging.getLogger("startup.bootstrap")


def get_lifespan_logger() -> logging.Logger:
    """
    获取 lifespan 初始化 logger

    Logger 名称: 'startup.lifespan'
    用于 FastAPI lifespan 启动阶段（数据库、存储、LLM 初始化）

    Example:
        >>> _lifespan_logger = get_lifespan_logger()
        >>> _lifespan_logger.info("Stage 2/5: Initializing database engines...")
    """
    _configure_early_logging()
    return logging.getLogger("startup.lifespan")


_configure_early_logging()
