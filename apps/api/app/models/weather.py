"""Weather domain models: stations, observations, forecasts."""
import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class WeatherStation(BaseModel):
    """Meteorological observation station."""

    __tablename__ = "weather_stations"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    station_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    elevation: Mapped[float | None] = mapped_column(Float, nullable=True)
    geometry: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    observations: Mapped[list["WeatherObservation"]] = relationship(
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
    air_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    relative_humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_direction: Mapped[float | None] = mapped_column(Float, nullable=True)
    mean_radiant_temperature: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    precipitation: Mapped[float | None] = mapped_column(Float, nullable=True)

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
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resolution: Mapped[float | None] = mapped_column(Float, nullable=True)

    forecasts: Mapped[list["WeatherForecast"]] = relationship(
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
    air_temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    relative_humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    wind_direction: Mapped[float | None] = mapped_column(Float, nullable=True)
    mean_radiant_temperature: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    precipitation_probability: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )

    run: Mapped["WeatherForecastRun"] = relationship(back_populates="forecasts")

    __table_args__ = (
        Index("ix_weather_forecasts_run_grid", "run_id", "grid_cell_id"),
        Index("ix_weather_forecasts_valid_time", "valid_time"),
        Index("ix_weather_forecasts_grid_valid", "grid_cell_id", "valid_time"),
    )
