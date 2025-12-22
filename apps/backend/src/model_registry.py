"""模型注册表

导入所有 SQLAlchemy 模型，触发 Base.metadata 注册。
Alembic 迁移脚本需要导入此模块。
"""

from domain.translate.model.translation import Translation


__all__ = ["Translation"]
