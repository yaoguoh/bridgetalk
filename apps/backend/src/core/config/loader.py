"""
配置加载器 - 参考 Spring Boot 的配置加载机制

加载优先级:
1. 环境变量 CONFIG_PATH
2. 当前工作目录
3. apps/backend/ 目录（从项目根目录启动）
4. 代码所在目录的上级目录
"""

import os
from pathlib import Path
from typing import Any

import yaml

from core.logging import get_logger


logger = get_logger(__name__)


class ConfigLoader:
    """配置加载器，在应用最早期执行"""

    @staticmethod
    def load() -> dict[str, Any]:
        """
        加载配置

        Returns:
            配置字典
        """
        return ConfigLoader._load_yaml_config()

    @staticmethod
    def _load_yaml_config() -> dict[str, Any]:
        """加载 YAML 配置文件"""
        config_path = Path(ConfigLoader._resolve_config_path("config.yaml"))
        with config_path.open(encoding="utf-8") as f:
            return yaml.safe_load(f)

    @staticmethod
    def _resolve_config_path(default_path: str) -> str:
        """
        智能解析配置文件路径，支持多种启动方式

        查找优先级:
        1. 环境变量 CONFIG_PATH
        2. 当前工作目录（Working Directory）
        3. apps/backend/ 目录（从项目根目录启动）
        4. 代码所在目录的上级目录（从 src/ 启动）

        Args:
            default_path: 默认配置文件路径（如 "config.yaml"）

        Returns:
            解析后的配置文件绝对路径
        """
        if env_path := os.getenv("CONFIG_PATH"):
            if Path(env_path).exists():
                logger.info("Using config from CONFIG_PATH env: %s", env_path)
                return env_path
            logger.warning("CONFIG_PATH specified but file not found: %s", env_path)

        cwd_path = Path(default_path)
        if cwd_path.exists():
            resolved = cwd_path.resolve()
            logger.info("Using config from current directory: %s", resolved)
            return str(resolved)

        backend_path = Path("apps/backend") / default_path
        if backend_path.exists():
            resolved = backend_path.resolve()
            logger.info("Using config from apps/backend: %s", resolved)
            return str(resolved)

        code_dir = Path(__file__).parent.parent.parent
        config_in_backend = code_dir / default_path
        if config_in_backend.exists():
            resolved = config_in_backend.resolve()
            logger.info("Using config from backend directory: %s", resolved)
            return str(resolved)

        logger.warning(
            "Config file '%s' not found in any standard location. Tried: cwd, apps/backend, %s",
            default_path,
            code_dir,
        )
        return default_path

    @staticmethod
    def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """
        深度合并两个字典

        Args:
            base: 基础字典
            override: 覆盖字典

        Returns:
            合并后的字典
        """
        result = base.copy()
        for key, value in override.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = ConfigLoader._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
