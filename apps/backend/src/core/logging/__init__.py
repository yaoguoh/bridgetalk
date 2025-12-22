"""统一日志模块.

提供完整的日志记录功能，包括：
- 主日志系统（configure_logging, get_logger, log_response）
- 早期启动日志（get_import_logger, get_bootstrap_logger, get_lifespan_logger）
- 辅助工具（TqdmToLogger）

Usage:
    # 主日志功能
    from core.logging import configure_logging, get_logger

    configure_logging(level="INFO", console_output=True, colored_output=True)
    logger = get_logger(__name__)
    logger.info("Application started")

    # 早期启动日志
    from core.logging import get_import_logger

    _import_logger = get_import_logger()
    _import_logger.info("Loading modules...")

    # 辅助工具
    from core.logging import TqdmToLogger

    tqdm_logger = TqdmToLogger(logger)
"""

from __future__ import annotations

from core.logging.config import TqdmToLogger
from core.logging.core import configure_logging, get_logger, get_startup_logger, log_response
from core.logging.early import get_bootstrap_logger, get_import_logger, get_lifespan_logger


__all__ = [
    "TqdmToLogger",
    "configure_logging",
    "get_bootstrap_logger",
    "get_import_logger",
    "get_lifespan_logger",
    "get_logger",
    "get_startup_logger",
    "log_response",
]
