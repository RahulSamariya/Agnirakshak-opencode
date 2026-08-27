"""Hazard assessment models."""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Float, DateTime, JSON, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class HazardAssessment(BaseModel):
    """Hazard assessment for a grid cell at a specific time."""

    __tablename__ = "hazard_assessments"

    model_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_runs.id"), nullable=False
    )
    grid_cell_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grid_cells.id"), nullable=False
    )
    valid_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    utci_value: Mapped[float] = mapped_column(Float, nullable=False)
    hazard_index: Mapped[float] = mapped_column(Float, nullable=False)
    hazard_category: Mapped[str] = mapped_column(String(50), nullable=False)
    air_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    relative_humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mean_radiant_temperature: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    calculation_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )

    __table_args__ = (
        Index("ix_hazard_assessments_grid_time", "grid_cell_id", "valid_time"),
        Index("ix_hazard_assessments_run", "model_run_id"),
        Index("ix_hazard_assessments_valid_time", "valid_time"),
    )
