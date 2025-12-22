"""翻译记录模型"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from core.database.base import Base


class TranslateDirection(str, Enum):
    """翻译方向"""

    PM_TO_DEV = "pm_to_dev"  # 产品 -> 开发
    DEV_TO_PM = "dev_to_pm"  # 开发 -> 产品


class Translation(Base):
    """翻译记录表"""

    __tablename__ = "translations"
    __table_args__ = (
        Index("ix_translations_created_at", "created_at"),
        Index("ix_translations_direction", "direction"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False, comment="原始内容")
    translated_content: Mapped[str] = mapped_column(Text, nullable=False, comment="翻译结果")
    direction: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="翻译方向: pm_to_dev / dev_to_pm",
    )
    detected_perspective: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="识别的视角: pm / dev / unknown",
    )
    gaps_identified: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="识别的缺失信息",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
