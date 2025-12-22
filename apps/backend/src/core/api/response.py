"""统一响应格式"""

from __future__ import annotations

from pydantic import BaseModel


class CommonResponse[T](BaseModel):
    """通用响应格式"""

    code: int = 200
    message: str = "success"
    data: T | None = None


def success_response[T](
    data: T | None = None,
    message: str = "success",
) -> CommonResponse[T]:
    """构建成功响应"""
    return CommonResponse(code=200, message=message, data=data)


def error_response(
    message: str = "error",
    code: int = 500,
) -> CommonResponse[None]:
    """构建错误响应"""
    return CommonResponse(code=code, message=message, data=None)


class PageParams(BaseModel):
    """分页参数"""

    page: int = 1
    size: int = 20


class PageResult[T](BaseModel):
    """分页结果"""

    content: list[T]
    total: int
    page: int
    size: int
    total_pages: int
