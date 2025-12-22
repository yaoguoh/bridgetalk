"""翻译服务层"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any
from uuid import UUID

from langchain_core.language_models import BaseChatModel
from sqlalchemy.ext.asyncio import AsyncSession

from domain.translate.agent.translate_agent import TranslateAgent, TranslateResult
from domain.translate.repository.translate_repository import TranslateRepository
from domain.translate.schema.response import TranslateResponse, TranslationRecord


class TranslateService:
    """翻译服务"""

    def __init__(
        self,
        llm: BaseChatModel,
        repository: TranslateRepository,
    ) -> None:
        self.agent = TranslateAgent(llm)
        self.repository = repository

    async def translate(
        self,
        session: AsyncSession,
        content: str,
        context: str | None = None,
    ) -> TranslateResponse:
        """执行翻译（同步模式）"""
        # 调用 Agent 翻译
        result = await self.agent.translate(content, context)

        # 保存记录
        await self.repository.create(session, result)
        await session.commit()

        return TranslateResponse(
            translated_content=result.translated_content,
            original_content=result.original_content,
            direction=result.direction,
            detected_perspective=result.detected_perspective,
            gaps=result.gaps,
            suggestions=result.suggestions,
        )

    async def translate_stream(
        self,
        session: AsyncSession,
        content: str,
        context: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """执行翻译（流式模式）"""
        final_result: TranslateResult | None = None
        final_event_data: dict[str, Any] | None = None

        try:
            async for event in self.agent.translate_stream(content, context):
                # 捕获最终结果用于保存
                if event.get("event") == "message_done":
                    data = event.get("data", {})
                    final_result = TranslateResult(
                        original_content=content,
                        translated_content=data.get("translated_content", ""),
                        detected_perspective=data.get("detected_perspective", "unknown"),
                        direction=data.get("direction", "unknown"),
                        gaps=data.get("gaps", []),
                        suggestions=data.get("suggestions", []),
                    )
                    final_event_data = data
                    # 先不 yield message_done，等保存后再发送
                    continue
                yield event
        finally:
            # 保存记录并发送包含 ID 的 message_done
            if final_result and final_event_data:
                translation = await self.repository.create(session, final_result)
                await session.commit()
                # 在 message_done 中添加翻译 ID
                final_event_data["translation_id"] = str(translation.id)
                yield {
                    "event": "message_done",
                    "data": final_event_data,
                }

    async def get_history(
        self,
        session: AsyncSession,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[TranslationRecord], int]:
        """获取翻译历史"""
        offset = (page - 1) * size
        translations = await self.repository.list_recent(session, limit=size, offset=offset)
        total = await self.repository.count(session)

        records = [
            TranslationRecord(
                id=t.id,
                content=t.content,
                translated_content=t.translated_content,
                direction=t.direction,
                detected_perspective=t.detected_perspective,
                gaps=t.gaps_identified.get("gaps", []) if t.gaps_identified else [],
                created_at=t.created_at,
            )
            for t in translations
        ]

        return records, total

    async def get_by_id(
        self,
        session: AsyncSession,
        translation_id: UUID,
    ) -> TranslationRecord | None:
        """根据 ID 获取翻译记录"""
        translation = await self.repository.get_by_id(session, translation_id)
        if not translation:
            return None

        return TranslationRecord(
            id=translation.id,
            content=translation.content,
            translated_content=translation.translated_content,
            direction=translation.direction,
            detected_perspective=translation.detected_perspective,
            gaps=translation.gaps_identified.get("gaps", []) if translation.gaps_identified else [],
            created_at=translation.created_at,
        )
