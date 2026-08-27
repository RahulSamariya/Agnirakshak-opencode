"""Hazard schemas."""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


class HazardAssessmentResponse(BaseModel):
    id: uuid.UUID
    model_run_id: uuid.UUID
    grid_cell_id: uuid.UUID
    valid_time: datetime
    utci_value: float
    hazard_index: float = Field(ge=0.0, le=1.0)
    hazard_category: str
    air_temperature: Optional[float] = None
    relative_humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    mean_radiant_temperature: Optional[float] = None
    calculation_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HazardAssessmentBrief(BaseModel):
    id: uuid.UUID
    grid_cell_id: uuid.UUID
    valid_time: datetime
    hazard_index: float
    hazard_category: str

    class Config:
        from_attributes = True
