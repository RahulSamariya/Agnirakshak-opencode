"""Wards schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str
    created_at: datetime
    updated_at: datetime


class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    state_id: uuid.UUID
    population: int | None = None
    created_at: datetime
    updated_at: datetime


class WardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    city_id: uuid.UUID
    ward_code: str | None = None
    population: int | None = None
    created_at: datetime
    updated_at: datetime


class WardWithRisk(WardResponse):
    current_risk_category: str | None = None
    current_hsri: float | None = None


class GridCellResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cell_code: str
    ward_id: uuid.UUID | None = None
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime
