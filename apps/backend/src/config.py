"""配置管理器"""

from __future__ import annotations

import os
from typing import Any, cast

from pydantic import BaseModel, Field

from core.config.loader import ConfigLoader
from core.logging import get_logger


logger = get_logger(__name__)


class DatabaseConfig(BaseModel):
    """数据库配置"""

    host: str = "127.0.0.1"
    port: int = 5432
    username: str = "postgres"
    password: str = "password"
    name: str = "bridgetalk"
    pool_size: int = 10
    max_overflow: int = 5
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True

    def build_url(self) -> str:
        """构建数据库连接 URL"""
        return f"postgresql+psycopg://{self.username}:{self.password}@{self.host}:{self.port}/{self.name}"


class DashScopeConfig(BaseModel):
    """DashScope LLM 配置"""

    api_key: str = ""
    model_name: str = "qwen-max"
    temperature: float = 0.7
    max_tokens: int = 4096
    request_timeout: int = 60


class LLMConfig(BaseModel):
    """LLM 配置"""

    dashscope: DashScopeConfig = Field(default_factory=DashScopeConfig)


class RedisConfig(BaseModel):
    """Redis 配置"""

    host: str = "127.0.0.1"
    port: int = 6379
    password: str = ""
    database: int = 0
    key_prefix: str = "bridgetalk"
    max_connections: int = 20
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 2.0
    health_check_interval: int = 15


class LoggingConfig(BaseModel):
    """日志配置"""

    level: str = "INFO"
    format: str = "text"  # text | json
    include_timestamp: bool = True


class ServerConfig(BaseModel):
    """服务器配置"""

    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])


class AppConfig(BaseModel):
    """应用配置"""

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)


class ConfigManager:
    """配置管理器（单例）"""

    _instance: ConfigManager | None = None
    _config: AppConfig | None = None

    def __new__(cls) -> ConfigManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self) -> None:
        """初始化配置"""
        if self._config is not None:
            return

        config_data = ConfigLoader.load()
        config_data = self._resolve_env_vars(config_data)
        self._config = AppConfig.model_validate(config_data)
        self._validate_config()

    def _resolve_env_vars(self, data: dict[str, Any]) -> dict[str, Any]:
        """解析环境变量引用 ${VAR_NAME}"""
        return self._resolve_value(data)

    def _resolve_value(self, value: dict[str, Any]) -> dict[str, Any]:
        """递归解析字典中的环境变量"""
        result: dict[str, Any] = {}
        for key, val in value.items():
            result[key] = self._resolve_single(val)
        return result

    def _resolve_single(self, value: Any) -> Any:
        """解析单个值中的环境变量"""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, "")
        if isinstance(value, dict):
            return self._resolve_value(cast(dict[str, Any], value))
        if isinstance(value, list):
            resolved_list: list[Any] = []
            for item in cast(list[Any], value):
                resolved_list.append(self._resolve_single(item))
            return resolved_list
        return value

    def _validate_config(self) -> None:
        """验证关键配置"""
        if self._config is None:
            return

        if not self._config.llm.dashscope.api_key:
            logger.warning("DashScope API Key 未配置，LLM 功能将不可用")

    @property
    def config(self) -> AppConfig:
        """获取配置"""
        if self._config is None:
            msg = "配置未初始化，请先调用 initialize()"
            raise RuntimeError(msg)
        return self._config

    @property
    def database(self) -> DatabaseConfig:
        """获取数据库配置"""
        return self.config.database

    @property
    def llm(self) -> LLMConfig:
        """获取 LLM 配置"""
        return self.config.llm

    @property
    def server(self) -> ServerConfig:
        """获取服务器配置"""
        return self.config.server

    @property
    def logging(self) -> LoggingConfig:
        """获取日志配置"""
        return self.config.logging

    @property
    def redis(self) -> RedisConfig:
        """获取 Redis 配置"""
        return self.config.redis


# 全局单例
config_manager = ConfigManager()
