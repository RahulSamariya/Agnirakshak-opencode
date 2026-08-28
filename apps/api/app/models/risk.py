"""Risk assessment models."""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class RiskRun(BaseModel):
    """A risk calculation run encompassing multiple assessments."""

    __tablename__ = "risk_runs"

    hazard_model_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_runs.id"), nullable=False
    )
    run_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    run_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="running"
    )
    total_assessments: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_assessments: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    assessments: Mapped[list["RiskAssessment"]] = relationship(
        back_populates="risk_run"
    )
    ward_summaries: Mapped[list["WardRiskSummary"]] = relationship(
        back_populates="risk_run"
    )

    __table_args__ = (
        Index("ix_risk_runs_status", "status"),
        Index("ix_risk_runs_start", "run_start"),
    )


class RiskAssessment(BaseModel):
    """Risk assessment for a grid cell at a specific time."""

    __tablename__ = "risk_assessments"

    risk_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("risk_runs.id"), nullable=False
    )
    grid_cell_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grid_cells.id"), nullable=False
    )
    hazard_assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hazard_assessments.id"), nullable=False
    )
    vulnerability_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vulnerability_profiles.id"), nullable=False
    )
    exposure_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exposure_profiles.id"), nullable=False
    )
    valid_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    hazard: Mapped[float] = mapped_column(Float, nullable=False)
    vulnerability: Mapped[float] = mapped_column(Float, nullable=False)
    exposure: Mapped[float] = mapped_column(Float, nullable=False)
    hsri: Mapped[float] = mapped_column(Float, nullable=False)
    risk_category: Mapped[str] = mapped_column(String(20), nullable=False)
    calculation_metadata: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    risk_run: Mapped["RiskRun"] = relationship(back_populates="assessments")

    __table_args__ = (
        Index("ix_risk_assessments_run_grid", "risk_run_id", "grid_cell_id"),
        Index("ix_risk_assessments_valid_time", "valid_time"),
        Index("ix_risk_assessments_category", "risk_category"),
    )


class RiskAssessmentComponent(BaseModel):
    """Detailed component breakdown for a risk assessment."""

    __tablename__ = "risk_assessment_components"

    risk_assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("risk_assessments.id"), nullable=False
    )
    component_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # hazard, vulnerability, exposure
    factor_name: Mapped[str] = mapped_column(String(50), nullable=False)
    factor_value: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    weighted_value: Mapped[float] = mapped_column(Float, nullable=False)
    rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    __table_args__ = (
        Index("ix_risk_components_assessment", "risk_assessment_id"),
        Index("ix_risk_components_type", "component_type"),
    )


class WardRiskSummary(BaseModel):
    """Aggregated risk summary for a ward."""

    __tablename__ = "ward_risk_summaries"

    risk_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("risk_runs.id"), nullable=False
    )
    ward_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wards.id"), nullable=False
    )
    valid_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    mean_hazard: Mapped[float] = mapped_column(Float, nullable=False)
    mean_vulnerability: Mapped[float] = mapped_column(Float, nullable=False)
    mean_exposure: Mapped[float] = mapped_column(Float, nullable=False)
    mean_hsri: Mapped[float] = mapped_column(Float, nullable=False)
    max_hsri: Mapped[float] = mapped_column(Float, nullable=False)
    min_hsri: Mapped[float] = mapped_column(Float, nullable=False)
    risk_category: Mapped[str] = mapped_column(String(20), nullable=False)
    cell_count: Mapped[int] = mapped_column(Integer, nullable=False)
    high_risk_cell_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )

    risk_run: Mapped["RiskRun"] = relationship(back_populates="ward_summaries")

    __table_args__ = (
        Index("ix_ward_risk_summaries_run_ward", "risk_run_id", "ward_id"),
        Index("ix_ward_risk_summaries_ward", "ward_id"),
        Index("ix_ward_risk_summaries_valid_time", "valid_time"),
    )
