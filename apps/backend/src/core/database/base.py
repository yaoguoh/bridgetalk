"""SQLAlchemy Declarative Base 封装。"""

from __future__ import annotations

from typing import Any

from sqlalchemy import inspect
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有数据模型的声明性基类，提供通用构造和序列化能力。"""

    def __init__(self, **kwargs: object) -> None:
        """
        通用构造函数，只接受模型中定义的列作为参数。
        """
        super().__init__()
        column_keys = {c.key for c in inspect(self.__class__).columns}
        for key, value in kwargs.items():
            if key in column_keys:
                setattr(self, key, value)

    def to_dict(self) -> dict[str, Any]:
        """
        安全地将 SQLAlchemy 模型实例转换为字典。
        """
        mapper = inspect(self.__class__)
        obj_dict = {c.key: getattr(self, c.key) for c in mapper.columns.values()}
        obj_dict.pop("embedding", None)
        return obj_dict


__all__ = ["Base"]
