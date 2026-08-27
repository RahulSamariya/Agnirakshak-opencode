"""Exposure schemas."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field
import uuid


class ExposureFactorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    factor_name: str
    raw_value: Optional[str] = None
    factor_score: float = Field(ge=0.0, le=1.0)
    weight: float = Field(ge=0.0, le=1.0)
    weighted_score: float = Field(ge=0.0, le=1.0)
    sub_factors: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class ExposureProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ward_id: uuid.UUID
    model_run_id: Optional[uuid.UUID] = None
    exposure_index: float = Field(ge=0.0, le=1.0)
    score_details: Optional[Dict[str, Any]] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime


class ExposureProfileWithFactors(ExposureProfileResponse):
    factors: List[ExposureFactorResponse] = []
