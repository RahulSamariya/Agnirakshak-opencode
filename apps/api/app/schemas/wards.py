"""Wards schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
import uuid


class StateResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CityResponse(BaseModel):
    id: uuid.UUID
    name: str
    state_id: uuid.UUID
    population: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WardResponse(BaseModel):
    id: uuid.UUID
    name: str
    city_id: uuid.UUID
    ward_code: Optional[str] = None
    population: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WardWithRisk(WardResponse):
    current_risk_category: Optional[str] = None
    current_hsri: Optional[float] = None


class GridCellResponse(BaseModel):
    id: uuid.UUID
    cell_code: str
    ward_id: Optional[uuid.UUID] = None
    latitude: float
    longitude: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
