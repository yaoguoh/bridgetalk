"""主日志功能模块."""

from __future__ import annotations

import atexit
import logging
import os
import sys
from http import HTTPStatus
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TextIO

from core.logging.config import ColoredFormatter, LogConfig, MillisecondFormatter, SmartExceptionFormatter


__all__ = ["configure_logging", "get_logger", "get_startup_logger", "log_response"]
_LOGGING_STATE: dict[str, bool] = {"configured": False}


def _create_formatter(use_colors: bool = True, smart_exception: bool = False) -> logging.Formatter:
    """
    创建日志格式化器（工厂函数）

    Args:
        use_colors: 是否使用彩色输出
        smart_exception: 是否使用智能异常格式化（过滤第三方库堆栈）

    Returns:
        配置好的日志格式化器
    """
    if smart_exception and use_colors:
        return SmartExceptionFormatter(LogConfig.LOG_FORMAT, LogConfig.TIME_FORMAT, use_colors=True)
    if use_colors:
        return ColoredFormatter(LogConfig.LOG_FORMAT, LogConfig.TIME_FORMAT)
    return MillisecondFormatter(LogConfig.LOG_FORMAT, LogConfig.TIME_FORMAT)


def _create_file_handler(filename: str, level: int, max_bytes: int, backup_count: int) -> RotatingFileHandler:
    """创建文件handler（支持 multiprocessing）"""
    handler = RotatingFileHandler(filename=filename, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    handler.setLevel(level)
    handler.setFormatter(MillisecondFormatter(LogConfig.LOG_FORMAT, LogConfig.TIME_FORMAT))
    atexit.register(handler.flush)
    return handler


def _create_console_handler(level: int, colored: bool, stream: TextIO = sys.stdout) -> logging.StreamHandler[TextIO]:
    """创建控制台handler"""
    handler = logging.StreamHandler(stream)
    handler.setLevel(level)
    handler.setFormatter(_create_formatter(use_colors=colored, smart_exception=True))
    return handler


def _configure_logger(
    name: str,
    level: int,
    file_handler: logging.Handler | None = None,
    console_handler: logging.Handler | None = None,
    propagate: bool = False,
) -> logging.Logger:
    """配置指定logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = propagate
    logger.handlers.clear()
    if file_handler:
        logger.addHandler(file_handler)
    if console_handler:
        logger.addHandler(console_handler)
    return logger


def configure_logging(level: str = "INFO", console_output: bool = True, colored_output: bool = True) -> logging.Logger:
    """
    配置统一的日志系统（支持 multiprocessing 和 PyCharm 调试模式）

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: 是否输出到控制台
        colored_output: 控制台是否使用彩色输出

    Returns:
        配置好的根logger
    """
    if _LOGGING_STATE["configured"]:
        return logging.getLogger()
    env_level = os.getenv("LOG_LEVEL", level).upper()
    log_level = getattr(logging, env_level, logging.INFO)
    Path(LogConfig.LOG_DIR).mkdir(parents=True, exist_ok=True)
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(log_level)
    if console_output:
        stdout_handler = _create_console_handler(log_level, colored_output, stream=sys.stdout)
        root_logger.addHandler(stdout_handler)
    root_logger.addHandler(
        _create_file_handler(LogConfig.APP_LOG, log_level, LogConfig.MAX_BYTES, LogConfig.BACKUP_COUNT)
    )
    root_logger.addHandler(
        _create_file_handler(LogConfig.ERROR_LOG, logging.ERROR, LogConfig.MAX_BYTES, LogConfig.BACKUP_COUNT)
    )
    access_console = _create_console_handler(logging.INFO, colored_output) if console_output else None
    _configure_logger("uvicorn.access", logging.INFO, None, access_console, propagate=False)
    _configure_logger("uvicorn", logging.WARNING, propagate=True)
    sql_file = _create_file_handler(LogConfig.SQL_LOG, logging.INFO, LogConfig.MAX_BYTES, LogConfig.BACKUP_COUNT)
    sql_console = None
    if console_output:
        sql_console = logging.StreamHandler(sys.stdout)
        sql_console.setLevel(logging.WARNING)
        sql_console.setFormatter(_create_formatter(use_colors=colored_output, smart_exception=False))
    _configure_logger("sqlalchemy", logging.INFO, propagate=False)
    _configure_logger("sqlalchemy.engine", logging.INFO, sql_file, sql_console, propagate=False)
    for module_name, module_level in LogConfig.MODULE_LOG_LEVELS.items():
        if module_name not in ["uvicorn", "uvicorn.access", "sqlalchemy", "sqlalchemy.engine"]:
            logging.getLogger(module_name).setLevel(module_level)
    is_pycharm = bool(os.getenv("PYCHARM_HOSTED"))
    root_logger.info("日志系统已配置完成:")
    root_logger.info("- 环境: %s", ("PyCharm 调试模式" if is_pycharm else "标准模式"))
    root_logger.info(
        "- 全局日志级别: %s (来源: %s)", env_level, ("环境变量" if env_level != level.upper() else "默认值")
    )
    root_logger.info(
        "- 控制台日志: %s 级别%s",
        logging.getLevelName(log_level),
        " (彩色)" if colored_output else "",
    )
    root_logger.info("- 应用日志: %s (10MB x %s)", LogConfig.APP_LOG, LogConfig.BACKUP_COUNT)
    root_logger.info("- 错误日志: %s (10MB x %s)", LogConfig.ERROR_LOG, LogConfig.BACKUP_COUNT)
    root_logger.info("- SQL日志: %s (10MB x %s)", LogConfig.SQL_LOG, LogConfig.BACKUP_COUNT)
    _LOGGING_STATE["configured"] = True
    return root_logger


def get_logger(name: str, level: int | None = None) -> logging.Logger:
    """
    获取标准logger

    Args:
        name: logger名称（通常使用 __name__）
        level: 可选的日志级别

    Returns:
        配置好的logger
    """
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger


def get_startup_logger(name: str) -> logging.Logger:
    """
    获取启动阶段专用logger

    这是对 early logging 模块的补充，提供统一的启动日志接口。
    在 configure_logging() 调用后，启动日志将自动使用项目标准格式。

    Args:
        name: logger名称（默认 "startup"，可以是 "startup.imports"、"startup.bootstrap" 等）

    Returns:
        配置好的 startup logger

    Examples:
        >>> # 导入阶段（early logging）
        >>> from core.logging import get_import_logger
        >>> _import_logger = get_import_logger()  # startup.imports
        >>> _import_logger.info("Module importing...")

        >>> # 应用初始化阶段
        >>> from core.logging import get_startup_logger
        >>> _lifespan_logger = get_startup_logger("startup.lifespan")
        >>> _lifespan_logger.info("Stage 2/5: Initializing database engines...")
    """
    return logging.getLogger(name)


def log_response(logger: logging.Logger, method: str, path: str, status_code: int, duration_ms: float) -> None:
    """
    根据 HTTP 状态码自动选择日志级别记录响应

    日志级别选择规则：
    - 2xx (成功): INFO
    - 3xx (重定向): WARNING
    - 4xx/5xx (错误): WARNING

    Args:
        logger: Logger 实例
        method: HTTP 方法（GET, POST, PUT, DELETE 等）
        path: 请求路径
        status_code: HTTP 状态码
        duration_ms: 请求处理耗时（毫秒）

    Examples:
        >>> logger = get_logger(__name__)
        >>> log_response(logger, "GET", "/api/users", 200, 45.23)
        # 输出: [RESPONSE] GET /api/users - OK 200 (45.23ms)

        >>> log_response(logger, "POST", "/api/login", 422, 12.45)
        # 输出: [RESPONSE] POST /api/login - FAIL 422 (12.45ms)
    """
    if HTTPStatus.OK <= status_code < HTTPStatus.MULTIPLE_CHOICES:
        status_level = "OK"
        logger.info("[RESPONSE] %s %s - %s %s (%sms)", method, path, status_level, status_code, f"{duration_ms:.2f}")
    elif HTTPStatus.MULTIPLE_CHOICES <= status_code < HTTPStatus.BAD_REQUEST:
        status_level = "REDIRECT"
        logger.warning("[RESPONSE] %s %s - %s %s (%sms)", method, path, status_level, status_code, f"{duration_ms:.2f}")
    else:
        status_level = "FAIL"
        logger.warning("[RESPONSE] %s %s - %s %s (%sms)", method, path, status_level, status_code, f"{duration_ms:.2f}")
