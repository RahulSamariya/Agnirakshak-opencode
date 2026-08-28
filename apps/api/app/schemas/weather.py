"""Weather schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WeatherStationBase(BaseModel):
    name: str
    station_code: str
    latitude: float
    longitude: float
    elevation: float | None = None


class WeatherStationResponse(WeatherStationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class WeatherObservationBase(BaseModel):
    station_id: uuid.UUID
    observation_time: datetime
    air_temperature: float | None = None
    relative_humidity: float | None = None
    wind_speed: float | None = None
    wind_direction: float | None = None
    mean_radiant_temperature: float | None = None
    pressure: float | None = None
    precipitation: float | None = None


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
    source: str | None = None
    resolution: float | None = None
    created_at: datetime
    updated_at: datetime


class WeatherForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    run_id: uuid.UUID
    grid_cell_id: uuid.UUID
    valid_time: datetime
    lead_time_hours: int
    air_temperature: float | None = None
    relative_humidity: float | None = None
    wind_speed: float | None = None
    wind_direction: float | None = None
    mean_radiant_temperature: float | None = None
    pressure: float | None = None
    precipitation_probability: float | None = None
    created_at: datetime
    updated_at: datetime
