"""Operations domain models: alerts, action recommendations."""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Alert(BaseModel):
    """Heatwave alert for a geographic area."""

    __tablename__ = "alerts"

    risk_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("risk_runs.id"), nullable=True
    )
    ward_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wards.id"), nullable=True
    )
    alert_level: Mapped[str] = mapped_column(String(20), nullable=False)
    alert_type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    valid_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    valid_until: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    recommendations: Mapped[list["ActionRecommendation"]] = relationship(
        back_populates="alert"
    )

    __table_args__ = (
        Index("ix_alerts_level", "alert_level"),
        Index("ix_alerts_active", "is_active"),
        Index("ix_alerts_valid", "valid_from", "valid_until"),
        Index("ix_alerts_ward", "ward_id"),
    )


class ActionRecommendation(BaseModel):
    """Recommended action for an alert."""

    __tablename__ = "action_recommendations"

    alert_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("alerts.id"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    target_audience: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_acknowledged: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    alert: Mapped["Alert"] = relationship(back_populates="recommendations")

    __table_args__ = (
        Index("ix_action_recommendations_alert", "alert_id"),
        Index("ix_action_recommendations_category", "category"),
    )
