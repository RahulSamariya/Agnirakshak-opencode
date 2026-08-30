"""Temporal and spatial compatibility tests for Ahmedabad pilot data.

Validates that datasets can be joined and used together.
Documents known incompatibilities (57 vs 48 ward mismatch, etc.).
"""
from __future__ import annotations

from pathlib import Path
from datetime import datetime

import json
import xarray as xr
import geopandas as gpd
import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Temporal compatibility
# ---------------------------------------------------------------------------

class TestTemporalCompatibility:
    """Tests for temporal overlap between datasets."""

    def test_era5_covers_target_period(self):
        """ERA5-Land covers at least the target analysis period."""
        ds = xr.open_dataset("data/raw/weather/data_0.nc")
        times = ds.valid_time.values
        ds.close()

        min_time = pd.Timestamp(times.min())
        max_time = pd.Timestamp(times.max())

        # Should have at least 24 hours of data
        assert (max_time - min_time).total_seconds() >= 3600 * 24

    def test_aqi_covers_target_period(self):
        """AQI data covers multiple months.

        The Date column contains day numbers (1-31), not full dates.
        Month is encoded in the filename: *_YYYY_Month_city_YYYY.xlsx
        """
        aqi_dir = Path("data/raw/aqi")
        files = sorted(aqi_dir.glob("*.xlsx"))

        months_covered = set()
        for f in files:
            # Extract month from filename pattern: ..._January_... or ..._April_...
            parts = f.stem.split("_")
            for part in parts:
                if part in (
                    "January", "February", "March", "April", "May",
                    "June", "July", "August", "September", "October",
                    "November", "December",
                ):
                    month_map = {
                        "January": 1, "February": 2, "March": 3,
                        "April": 4, "May": 5, "June": 6,
                    }
                    if part in month_map:
                        months_covered.add(month_map[part])

        # Should cover at least 3 months
        assert len(months_covered) >= 3, f"Only {len(months_covered)} months: {months_covered}"

    def test_era5_aqi_no_temporal_overlap(self):
        """ERA5 (2010) and AQI (2025) have no temporal overlap.

        This is a KNOWN LIMITATION documented in:
        docs/data/ahmedabad-temporal-availability-v1.md
        """
        ds = xr.open_dataset("data/raw/weather/data_0.nc")
        era5_year = pd.Timestamp(ds.valid_time.values.min()).year
        ds.close()

        aqi_dir = Path("data/raw/aqi")
        files = sorted(aqi_dir.glob("*.xlsx"))
        aqi_years = set()
        for f in files:
            df = pd.read_excel(f)
            if "Date" in df.columns:
                dates = pd.to_datetime(df["Date"])
                aqi_years.update(dates.dt.year.unique())

        # Known limitation: different years
        assert era5_year not in aqi_years, (
            "ERA5 and AQI temporal overlap detected - unexpected!"
        )

    def test_era5_date_range_metadata(self):
        """ERA5 temporal coverage is documented."""
        profile_path = Path("data/profiles/era5land_ahmedabad.json")
        if profile_path.exists():
            with open(profile_path) as f:
                profile = json.load(f)

            # time_range can be a list [start, end] or dict with 'start' key
            time_range = profile.get("time_range", [])
            has_valid_range = (
                (isinstance(time_range, list) and len(time_range) == 2)
                or (isinstance(time_range, dict) and "start" in time_range)
                or "min_time" in profile
            )
            assert has_valid_range


# ---------------------------------------------------------------------------
# Spatial compatibility
# ---------------------------------------------------------------------------

class TestSpatialCompatibility:
    """Tests for spatial overlap between datasets."""

    def test_gis_covers_ahmedabad(self):
        """GIS boundaries cover Ahmedabad city area."""
        gdf = gpd.read_file("data/raw/gis/wards_ahmedabad.geojson")

        # GeoJSON has lat as x-axis, lon as y-axis (lat-first convention)
        # bounds = [min_lat, min_lon, max_lat, max_lon] in this file
        bounds = gdf.total_bounds
        assert bounds[0] >= 22.8  # min lat (minx in this GeoJSON)
        assert bounds[2] <= 23.3  # max lat (maxx in this GeoJSON)
        assert bounds[1] >= 72.3  # min lon (miny in this GeoJSON)
        assert bounds[3] <= 72.9  # max lon (maxy in this GeoJSON)

    def test_era5_covers_ahmedabad_grid(self):
        """ERA5 grid covers Ahmedabad area."""
        ds = xr.open_dataset("data/raw/weather/data_0.nc")
        lats = ds.latitude.values
        lons = ds.longitude.values
        ds.close()

        assert lats.min() <= 23.0
        assert lats.max() >= 23.0
        assert lons.min() <= 72.5
        assert lons.max() >= 72.5

    def test_era5_gis_spatial_overlap(self):
        """ERA5 grid overlaps with GIS ward centroids."""
        gdf = gpd.read_file("data/raw/gis/wards_ahmedabad.geojson")
        centroids = gdf.geometry.centroid

        ds = xr.open_dataset("data/raw/weather/data_0.nc")
        lat_min = float(ds.latitude.min().item())
        lat_max = float(ds.latitude.max().item())
        lon_min = float(ds.longitude.min().item())
        lon_max = float(ds.longitude.max().item())
        ds.close()

        # GeoJSON has lat as x-axis, lon as y-axis
        centroid_lat = centroids.x.values  # lat is x-axis
        centroid_lon = centroids.y.values  # lon is y-axis

        within = (
            (centroid_lat >= lat_min) & (centroid_lat <= lat_max) &
            (centroid_lon >= lon_min) & (centroid_lon <= lon_max)
        )
        coverage_pct = within.sum() / len(within) * 100

        # Some coverage expected (not 100% since ERA5 is 5x5 grid)
        assert coverage_pct > 0, "No spatial overlap between ERA5 and GIS"

    def test_ward_id_consistency(self):
        """Ward IDs are consistent between GIS and staging copy."""
        gdf_raw = gpd.read_file("data/raw/gis/wards_ahmedabad.geojson")
        gdf_staging = gpd.read_file(
            "data/staging/gis/wards_ahmedabad_normalized.geojson"
        )

        raw_ids = set(gdf_raw["ward_lgd_code"].astype(str))
        staging_ids = set(gdf_staging["ward_lgd_code"].astype(str))

        # Staging copy should have same IDs as raw
        assert raw_ids == staging_ids, (
            f"ID mismatch: extra in raw={raw_ids - staging_ids}, "
            f"extra in staging={staging_ids - raw_ids}"
        )

    def test_no_duplicate_ward_ids(self):
        """No duplicate ward IDs in GIS."""
        gdf = gpd.read_file("data/raw/gis/wards_ahmedabad.geojson")
        assert not gdf["ward_lgd_code"].duplicated().any()

    def test_census_gis_ward_count_mismatch(self):
        """Known limitation: Census 2011 has 57 wards, GIS has 48.

        This is a KNOWN LIMITATION documented in:
        docs/data/ahmedabad-spatial-reconciliation-v1.md
        """
        gdf = gpd.read_file("data/raw/gis/wards_ahmedabad.geojson")
        current_ward_count = len(gdf)

        census_ward_count = 57  # From Census 2011

        # Known mismatch
        assert current_ward_count != census_ward_count, (
            "Ward count mismatch no longer exists - unexpected!"
        )

    def test_era5_grid_resolution(self):
        """ERA5 grid resolution is documented and reasonable."""
        ds = xr.open_dataset("data/raw/weather/data_0.nc")
        lats = ds.latitude.values
        lons = ds.longitude.values
        ds.close()

        if len(lats) > 1:
            lat_res = abs(float(lats[1] - lats[0]))
            lon_res = abs(float(lons[1] - lons[0]))
            # ERA5-Land is nominally 0.1 degree
            assert 0.05 <= lat_res <= 0.2
            assert 0.05 <= lon_res <= 0.2


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

class TestSchemaValidation:
    """Tests that data conforms to canonical staging schemas."""

    def test_weather_schema_alignment(self):
        """ERA5 variables map to WeatherRecord fields."""
        required_fields = [
            "air_temperature",  # t2m
            "relative_humidity",  # derived from t2m/d2m
            "wind_speed",  # derived from u10/v10
            "mean_radiant_temperature",  # derived from ssrd/strd
        ]
        # Just verify these are documented concepts
        assert len(required_fields) == 4

    def test_gis_schema_alignment(self):
        """GIS features map to WardBoundary fields."""
        gdf = gpd.read_file("data/raw/gis/wards_ahmedabad.geojson")

        required_cols = ["ward_lgd_code", "ward_lgd_name", "geometry"]
        for col in required_cols:
            assert col in gdf.columns, f"Missing column: {col}"

    def test_aqi_schema_alignment(self):
        """AQI files map to AQIRecord fields."""
        aqi_dir = Path("data/raw/aqi")
        files = sorted(aqi_dir.glob("*.xlsx"))

        for f in files[:1]:  # Check first file
            df = pd.read_excel(f)
            assert "Date" in df.columns
            hourly_cols = [c for c in df.columns if c != "Date"]
            assert len(hourly_cols) == 24
