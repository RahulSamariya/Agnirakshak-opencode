"""Weather schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
import uuid


class WeatherStationBase(BaseModel):
    name: str
    station_code: str
    latitude: float
    longitude: float
    elevation: Optional[float] = None


class WeatherStationResponse(WeatherStationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class WeatherObservationBase(BaseModel):
    station_id: uuid.UUID
    observation_time: datetime
    air_temperature: Optional[float] = None
    relative_humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    mean_radiant_temperature: Optional[float] = None
    pressure: Optional[float] = None
    precipitation: Optional[float] = None


class WeatherObservationResponse(WeatherObservationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class WeatherForecastRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    model_name: str
    run_time: datetime
    status: str
    source: Optional[str] = None
    resolution: Optional[float] = None
    created_at: datetime
    updated_at: datetime


class WeatherForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    grid_cell_id: uuid.UUID
    valid_time: datetime
    lead_time_hours: int
    air_temperature: Optional[float] = None
    relative_humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[float] = None
    mean_radiant_temperature: Optional[float] = None
    pressure: Optional[float] = None
    precipitation_probability: Optional[float] = None
    created_at: datetime
    updated_at: datetime
