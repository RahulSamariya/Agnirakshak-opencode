"""Geography domain models: states, cities, wards, grid_cells."""
import uuid
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class State(BaseModel):
    """Indian state entity."""

    __tablename__ = "states"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    geometry: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True
    )

    cities: Mapped[list["City"]] = relationship(back_populates="state")


class City(BaseModel):
    """City entity within a state."""

    __tablename__ = "cities"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    state_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("states.id"), nullable=False
    )
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    geometry: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True
    )

    state: Mapped["State"] = relationship(back_populates="cities")
    wards: Mapped[list["Ward"]] = relationship(back_populates="city")

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
    ward_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    population: Mapped[int | None] = mapped_column(Integer, nullable=True)
    geometry: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="MULTIPOLYGON", srid=4326), nullable=True
    )

    city: Mapped["City"] = relationship(back_populates="wards")
    grid_cells: Mapped[list["GridCell"]] = relationship(back_populates="ward")
    intersections: Mapped[list["GridWardIntersection"]] = relationship(
        back_populates="ward"
    )

    __table_args__ = (
        Index("ix_wards_city_id", "city_id"),
    )


class GridCell(BaseModel):
    """Computational grid cell (~333m resolution)."""

    __tablename__ = "grid_cells"

    cell_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    ward_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wards.id"), nullable=True
    )
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    geometry: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326), nullable=True
    )
    centroid: Mapped[str | None] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=True
    )

    ward: Mapped[Optional["Ward"]] = relationship(back_populates="grid_cells")
    intersections: Mapped[list["GridWardIntersection"]] = relationship(
        back_populates="grid_cell"
    )

    __table_args__ = (
        Index("ix_grid_cells_ward_id", "ward_id"),
        Index("ix_grid_cells_lat_lon", "latitude", "longitude"),
    )


class GridWardIntersection(BaseModel):
    """Spatial intersection between grid cells and wards.

    Supports accurate ward aggregation when grid cells cross administrative boundaries.
    """

    __tablename__ = "grid_ward_intersections"

    grid_cell_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("grid_cells.id"), nullable=False
    )
    ward_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("wards.id"), nullable=False
    )
    intersection_area: Mapped[float] = mapped_column(nullable=False)
    coverage_fraction: Mapped[float] = mapped_column(nullable=False)

    grid_cell: Mapped["GridCell"] = relationship(back_populates="intersections")
    ward: Mapped["Ward"] = relationship(back_populates="intersections")

    __table_args__ = (
        Index("ix_grid_ward_intersections_grid", "grid_cell_id"),
        Index("ix_grid_ward_intersections_ward", "ward_id"),
        Index("ix_grid_ward_intersections_unique", "grid_cell_id", "ward_id", unique=True),
    )
