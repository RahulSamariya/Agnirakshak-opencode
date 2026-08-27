"""Scientific model registry models."""
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class ScientificModel(BaseModel):
    """Registered scientific model metadata."""

    __tablename__ = "scientific_models"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    model_type: Mapped[str] = mapped_column(String(50), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    configuration_yaml: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    runs: Mapped[list["ModelRun"]] = relationship(back_populates="model")

    __table_args__ = (
        Index("ix_scientific_models_type", "model_type"),
        Index("ix_scientific_models_status", "status"),
    )


class ModelRun(BaseModel):
    """A specific execution of a scientific model."""

    __tablename__ = "model_runs"

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("scientific_models.id"), nullable=False
    )
    run_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    run_end: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="running"
    )
    input_parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    output_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(nullable=True)

    model: Mapped["ScientificModel"] = relationship(back_populates="runs")

    __table_args__ = (
        Index("ix_model_runs_model_id", "model_id"),
        Index("ix_model_runs_status", "status"),
        Index("ix_model_runs_start", "run_start"),
    )
