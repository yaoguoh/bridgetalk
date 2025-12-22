"""日志配置和格式化器模块."""

from __future__ import annotations

import logging
import time
import traceback
from types import TracebackType
from typing import ClassVar, Literal


__all__ = [
    "AnsiColor",
    "ColoredFormatter",
    "LogConfig",
    "MillisecondFormatter",
    "SmartExceptionFormatter",
    "TqdmToLogger",
]


class TqdmToLogger:
    """将tqdm输出重定向到日志记录器."""

    def __init__(self, logger: logging.Logger, level: int = logging.INFO) -> None:
        self.logger = logger
        self.level = level
        self.buf = ""

    def write(self, buf: str) -> None:
        self.buf = buf.strip("\r\n\t ")

    def flush(self) -> None:
        if self.buf:
            self.logger.log(self.level, self.buf)
            self.buf = ""


class AnsiColor:
    """ANSI颜色常量类"""

    RESET: str = "\x1b[0m"
    BRIGHT_GREEN: str = "\x1b[92m"
    BRIGHT_YELLOW: str = "\x1b[93m"
    BRIGHT_RED: str = "\x1b[91m"
    BRIGHT_MAGENTA: str = "\x1b[95m"
    BRIGHT_CYAN: str = "\x1b[96m"
    DARK_GRAY: str = "\x1b[90m"
    BOLD: str = "\x1b[1m"

    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        """用指定颜色包装文本"""
        return f"{color}{text}{cls.RESET}"


class MillisecondFormatter(logging.Formatter):
    """支持毫秒的日志格式化器（Spring Boot 风格）"""

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        """格式化时间，使用 . 分隔毫秒"""
        ct = self.converter(record.created)
        if datefmt:
            t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
            msecs = int(record.msecs)
            return f"{t}.{msecs:03d}"
        t = time.strftime("%Y-%m-%d %H:%M:%S", ct)
        return f"{t}.{int(record.msecs):03d}"


class ColoredFormatter(MillisecondFormatter):
    """为不同日志级别提供颜色的格式化器"""

    COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: AnsiColor.BRIGHT_GREEN,
        logging.INFO: AnsiColor.BRIGHT_GREEN,
        logging.WARNING: AnsiColor.BRIGHT_YELLOW,
        logging.ERROR: AnsiColor.BRIGHT_RED,
        logging.CRITICAL: AnsiColor.BRIGHT_MAGENTA,
    }

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname
        color = self.COLORS.get(record.levelno, AnsiColor.RESET)
        record.levelname = AnsiColor.colorize(original_levelname, color)
        formatted_msg = super().format(record)
        record.levelname = original_levelname
        return formatted_msg


class SmartExceptionFormatter(ColoredFormatter):
    """
    智能异常格式化器 - 优化ERROR日志显示

    功能：
    1. 过滤第三方库堆栈（只显示项目代码）
    2. 添加红色错误摘要
    3. 高亮项目代码路径
    """

    FILTER_PATHS: ClassVar[list[str]] = [
        "site-packages/starlette",
        "site-packages/fastapi",
        "site-packages/pydantic",
        "site-packages/sqlalchemy",
        "site-packages/anyio",
        "site-packages/uvicorn",
        "site-packages/httpx",
    ]

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
        use_colors: bool = True,
    ) -> None:
        super().__init__(fmt, datefmt, style)
        self.use_colors = use_colors

    def formatException(self, ei: tuple[type[BaseException] | None, BaseException | None, TracebackType | None]) -> str:
        """格式化异常堆栈跟踪"""
        tb_lines = traceback.format_exception(*ei)
        error_type = ei[0].__name__ if ei[0] else "Unknown"
        error_msg = str(ei[1]) if ei[1] else "No message"
        separator = "=" * 80
        summary_parts = [
            "\n" + separator,
            self._colorize("[ERROR] ERROR SUMMARY", AnsiColor.BRIGHT_RED, bold=True),
            self._colorize(f"Type: {error_type}", AnsiColor.BRIGHT_RED),
            self._colorize(f"Message: {error_msg}", AnsiColor.BRIGHT_RED),
            separator + "\n",
        ]
        summary = "\n".join(summary_parts)
        filtered_lines: list[str] = []
        last_was_filtered = False
        for line in tb_lines[1:-1]:
            if any(path in line for path in self.FILTER_PATHS):
                if not last_was_filtered:
                    filtered_lines.append(self._colorize("  ... [第三方库代码已省略] ...", AnsiColor.DARK_GRAY))
                    last_was_filtered = True
            else:
                last_was_filtered = False
                if "File" in line and "/src/" in line:
                    filtered_lines.append(self._colorize(line.rstrip(), AnsiColor.BRIGHT_CYAN))
                else:
                    filtered_lines.append(line.rstrip())
        if tb_lines:
            final_error = tb_lines[-1].rstrip()
            filtered_lines.append(self._colorize(final_error, AnsiColor.BRIGHT_RED, bold=True))
        return summary + "\n" + "\n".join(filtered_lines)

    def _colorize(self, text: str, color: str, bold: bool = False) -> str:
        """添加颜色和样式"""
        if not self.use_colors:
            return text
        result = text
        if bold:
            result = AnsiColor.colorize(result, AnsiColor.BOLD)
        if color:
            result = AnsiColor.colorize(result, color)
        return result


class LogConfig:
    """日志配置常量"""

    LOG_DIR = "logs"
    LOG_FORMAT = "%(asctime)s  %(levelname)-5s %(process)d --- [%(threadName)-15s] %(name)-45s : %(message)s"
    TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
    APP_LOG = f"{LOG_DIR}/application.log"
    DAILY_LOG = f"{LOG_DIR}/logback.log"
    ERROR_LOG = f"{LOG_DIR}/error.log"
    DEBUG_LOG = f"{LOG_DIR}/debug.log"
    SQL_LOG = f"{LOG_DIR}/sql.log"
    ACCESS_LOG = f"{LOG_DIR}/access.log"
    MAX_BYTES = 10 * 1024 * 1024
    BACKUP_COUNT = 100
    DEBUG_BACKUP_COUNT = 20
    MODULE_LOG_LEVELS: ClassVar[dict[str, int]] = {
        "services": logging.DEBUG,
        "sqlalchemy": logging.INFO,
        "sqlalchemy.engine": logging.INFO,
        "uvicorn": logging.WARNING,
        "uvicorn.access": logging.INFO,
    }
