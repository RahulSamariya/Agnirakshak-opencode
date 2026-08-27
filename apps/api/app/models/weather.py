"""Weather domain models: stations, observations, forecasts."""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.models.base import BaseModel


class WeatherStation(BaseModel):
    """Meteorological observation station."""

    __tablename__ = "weather_stations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    station_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    elevation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geometry: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    observations: Mapped[List["WeatherObservation"]] = relationship(
        back_populates="station"
    )

    __table_args__ = (
        Index("ix_weather_stations_code", "station_code"),
    )


class WeatherObservation(BaseModel):
    """Historical weather observation from a station."""

    __tablename__ = "weather_observations"

    station_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("weather_stations.id"), nullable=False
    )
    observation_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    air_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    relative_humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_direction: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mean_radiant_temperature: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    pressure: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precipitation: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    station: Mapped["WeatherStation"] = relationship(back_populates="observations")

    __table_args__ = (
        Index("ix_weather_observations_station_time", "station_id", "observation_time"),
        Index("ix_weather_observations_time", "observation_time"),
    )


class WeatherForecastRun(BaseModel):
    """A forecast model run / initialization."""

    __tablename__ = "weather_forecast_runs"

    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    run_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    resolution: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    forecasts: Mapped[List["WeatherForecast"]] = relationship(
        back_populates="run"
    )

    __table_args__ = (
        Index("ix_forecast_runs_model_time", "model_name", "run_time"),
    )


class WeatherForecast(BaseModel):
    """Forecast data for a grid cell at a specific valid time."""

    __tablename__ = "weather_forecasts"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("weather_forecast_runs.id"), nullable=False
    )
    grid_cell_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grid_cells.id"), nullable=False
    )
    valid_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    lead_time_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    air_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    relative_humidity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wind_direction: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mean_radiant_temperature: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )
    pressure: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    precipitation_probability: Mapped[Optional[float]] = mapped_column(
        Float, nullable=True
    )

    run: Mapped["WeatherForecastRun"] = relationship(back_populates="forecasts")

    __table_args__ = (
        Index("ix_weather_forecasts_run_grid", "run_id", "grid_cell_id"),
        Index("ix_weather_forecasts_valid_time", "valid_time"),
        Index("ix_weather_forecasts_grid_valid", "grid_cell_id", "valid_time"),
    )
