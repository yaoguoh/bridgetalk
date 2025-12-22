"""Alembic 环境配置"""

from __future__ import annotations

import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# 添加 src 到 Python 路径
import sys
from pathlib import Path

src_path = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(src_path))

# 导入模型注册表和基类
from config import config_manager
from core.database.base import Base

# Alembic Config 对象
alembic_config = context.config

# 配置日志
if alembic_config.config_file_name is not None:
    fileConfig(alembic_config.config_file_name)

# 目标元数据
target_metadata = Base.metadata


def get_db_url() -> str:
    """获取数据库连接 URL"""
    # 优先使用环境变量
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # 从配置文件读取（ConfigLoader 会自动查找）
    config_manager.initialize()
    return config_manager.database.build_url()


def run_migrations_offline() -> None:
    """离线模式运行迁移（生成 SQL 脚本）"""
    url = get_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式运行迁移（直接执行）"""
    configuration = alembic_config.get_section(alembic_config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_db_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
