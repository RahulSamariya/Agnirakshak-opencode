"""Hazard schemas."""
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HazardAssessmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model_run_id: uuid.UUID
    grid_cell_id: uuid.UUID
    valid_time: datetime
    utci_value: float
    hazard_index: float = Field(ge=0.0, le=1.0)
    hazard_category: str
    air_temperature: float | None = None
    relative_humidity: float | None = None
    wind_speed: float | None = None
    mean_radiant_temperature: float | None = None
    calculation_metadata: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class HazardAssessmentBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    grid_cell_id: uuid.UUID
    valid_time: datetime
    hazard_index: float
    hazard_category: str
