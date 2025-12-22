"""翻译记录仓储层"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.translate.model.translation import Translation


if TYPE_CHECKING:
    from domain.translate.agent.translate_agent import TranslateResult


class TranslateRepository:
    """翻译记录仓储"""

    async def create(
        self,
        session: AsyncSession,
        result: TranslateResult,
    ) -> Translation:
        """保存翻译记录"""
        translation = Translation(
            content=result.original_content,
            translated_content=result.translated_content,
            direction=result.direction,
            detected_perspective=result.detected_perspective,
            gaps_identified={
                "gaps": result.gaps,
                "suggestions": result.suggestions,
            }
            if result.gaps
            else None,
        )
        session.add(translation)
        await session.flush()
        return translation

    async def get_by_id(
        self,
        session: AsyncSession,
        translation_id: UUID,
    ) -> Translation | None:
        """根据 ID 获取翻译记录"""
        stmt = select(Translation).where(Translation.id == translation_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_recent(
        self,
        session: AsyncSession,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Translation]:
        """获取最近的翻译记录"""
        stmt = select(Translation).order_by(desc(Translation.created_at)).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, session: AsyncSession) -> int:
        """统计翻译记录总数"""
        stmt = select(func.count()).select_from(Translation)
        result = await session.execute(stmt)
        return result.scalar_one()
