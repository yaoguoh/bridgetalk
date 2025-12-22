"""翻译 API 路由"""

from __future__ import annotations

import logging
from typing import Annotated, Any
from uuid import UUID

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.api.response import CommonResponse, error_response, success_response
from core.database.session import db_session
from core.sse.events import sse_event
from domain.translate.schema.request import TranslateRequest
from domain.translate.schema.response import TranslateResponse, TranslationRecord
from domain.translate.service.translate_service import TranslateService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/translate", tags=["翻译"])


@router.post("", response_model=CommonResponse[TranslateResponse])
@inject
async def translate(
    request: TranslateRequest,
    session: Annotated[AsyncSession, Depends(db_session)],
    service: TranslateService = Depends(Provide["translate_service"]),
) -> CommonResponse[TranslateResponse] | CommonResponse[None]:
    """执行翻译（同步模式）"""
    if request.stream:
        return error_response("流式模式请使用 /api/translate/stream 端点", code=400)

    try:
        result = await service.translate(session, request.content, request.context)
        return success_response(result)
    except Exception as e:
        logger.exception("翻译失败")
        return error_response(f"翻译失败: {e!s}", code=500)


@router.post("/stream")
@inject
async def translate_stream(
    request: TranslateRequest,
    session: Annotated[AsyncSession, Depends(db_session)],
    service: TranslateService = Depends(Provide["translate_service"]),
) -> StreamingResponse:
    """执行翻译（流式模式）"""

    async def generate():
        try:
            async for event in service.translate_stream(session, request.content, request.context):
                yield sse_event(event["event"], event["data"])
        except Exception as e:
            logger.exception("流式翻译失败")
            yield sse_event("error", {"message": f"翻译失败: {e!s}"})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/history", response_model=CommonResponse[dict[str, Any]])
@inject
async def get_history(
    session: Annotated[AsyncSession, Depends(db_session)],
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    service: TranslateService = Depends(Provide["translate_service"]),
) -> CommonResponse[dict[str, Any]] | CommonResponse[None]:
    """获取翻译历史"""
    try:
        records, total = await service.get_history(session, page, size)
        return success_response(
            {
                "content": [r.model_dump() for r in records],
                "total": total,
                "page": page,
                "size": size,
                "total_pages": (total + size - 1) // size,
            }
        )
    except Exception as e:
        logger.exception("获取历史失败")
        return error_response(f"获取历史失败: {e!s}", code=500)


@router.get("/{translation_id}", response_model=CommonResponse[TranslationRecord])
@inject
async def get_translation(
    translation_id: UUID,
    session: Annotated[AsyncSession, Depends(db_session)],
    service: TranslateService = Depends(Provide["translate_service"]),
) -> CommonResponse[TranslationRecord] | CommonResponse[None]:
    """根据 ID 获取翻译记录"""
    try:
        record = await service.get_by_id(session, translation_id)
        if not record:
            return error_response("记录不存在", code=404)
        return success_response(record)
    except Exception as e:
        logger.exception("获取记录失败")
        return error_response(f"获取记录失败: {e!s}", code=500)
