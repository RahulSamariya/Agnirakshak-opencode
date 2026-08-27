"""Geography domain models: states, cities, wards, grid_cells."""
import uuid
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
from app.models.base import BaseModel


class State(BaseModel):
    """Indian state entity."""

    __tablename__ = "states"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    geometry: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True
    )

    cities: Mapped[List["City"]] = relationship(back_populates="state")


class City(BaseModel):
    """City entity within a state."""

    __tablename__ = "cities"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    state_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("states.id"), nullable=False
    )
    population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    geometry: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True
    )

    state: Mapped["State"] = relationship(back_populates="cities")
    wards: Mapped[List["Ward"]] = relationship(back_populates="city")

    __table_args__ = (
        Index("ix_cities_state_id", "state_id"),
    )


class Ward(BaseModel):
    """Ward entity within a city."""

    __tablename__ = "wards"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    city_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cities.id"), nullable=False
    )
    ward_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    geometry: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True
    )

    city: Mapped["City"] = relationship(back_populates="wards")
    grid_cells: Mapped[List["GridCell"]] = relationship(back_populates="ward")

    __table_args__ = (
        Index("ix_wards_city_id", "city_id"),
    )


class GridCell(BaseModel):
    """Computational grid cell (~333m resolution)."""

    __tablename__ = "grid_cells"

    cell_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    ward_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wards.id"), nullable=True
    )
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    geometry: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326), nullable=True
    )
    centroid: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    ward: Mapped[Optional["Ward"]] = relationship(back_populates="grid_cells")

    __table_args__ = (
        Index("ix_grid_cells_ward_id", "ward_id"),
        Index("ix_grid_cells_lat_lon", "latitude", "longitude"),
    )
