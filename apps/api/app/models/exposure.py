"""Exposure domain models."""
import uuid
from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class ExposureProfile(BaseModel):
    """Exposure profile for a ward."""

    __tablename__ = "exposure_profiles"

    ward_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wards.id"), nullable=False
    )
    model_run_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("model_runs.id"), nullable=True
    )
    exposure_index: Mapped[float] = mapped_column(Float, nullable=False)
    score_details: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    factors: Mapped[list["ExposureFactor"]] = relationship(back_populates="profile")

    __table_args__ = (
        Index("ix_exposure_profiles_ward", "ward_id"),
    )


class ExposureFactor(BaseModel):
    """Individual exposure factor score."""

    __tablename__ = "exposure_factors"

    profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("exposure_profiles.id"), nullable=False
    )
    factor_name: Mapped[str] = mapped_column(String(50), nullable=False)
    raw_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    factor_score: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    weighted_score: Mapped[float] = mapped_column(Float, nullable=False)
    sub_factors: Mapped[dict[str, Any] | None] = mapped_column(
        JSON, nullable=True
    )

    profile: Mapped["ExposureProfile"] = relationship(back_populates="factors")

    __table_args__ = (
        Index("ix_exposure_factors_profile", "profile_id"),
        Index("ix_exposure_factors_name", "factor_name"),
    )
