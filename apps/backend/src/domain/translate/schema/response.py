"""翻译响应模型"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


def _empty_gaps() -> list[dict[str, Any]]:
    return []


def _empty_suggestions() -> list[str]:
    return []


class TranslateResponse(BaseModel):
    """翻译响应（同步模式）"""

    translated_content: str = Field(description="翻译结果")
    original_content: str = Field(description="原始内容")
    direction: str = Field(description="翻译方向")
    detected_perspective: str = Field(description="识别的视角")
    gaps: list[dict[str, Any]] = Field(default_factory=_empty_gaps, description="识别的缺失信息")
    suggestions: list[str] = Field(default_factory=_empty_suggestions, description="补充建议")


class TranslationRecord(BaseModel):
    """翻译历史记录"""

    id: UUID
    content: str = Field(description="原始内容")
    translated_content: str = Field(description="翻译结果")
    direction: str = Field(description="翻译方向")
    detected_perspective: str | None = Field(default=None, description="识别的视角")
    gaps: list[dict[str, Any]] = Field(default_factory=_empty_gaps, description="识别的缺失信息")
    created_at: datetime = Field(description="创建时间")

    class Config:
        from_attributes = True
