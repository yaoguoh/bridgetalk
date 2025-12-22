"""翻译请求模型"""

from __future__ import annotations

from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    """翻译请求

    注意：不需要指定翻译方向，Agent 会自动识别视角并选择翻译方向
    """

    content: str = Field(..., min_length=1, max_length=10000, description="待翻译内容")
    stream: bool = Field(default=True, description="是否流式输出")
    context: str | None = Field(default=None, max_length=2000, description="补充上下文")
