"""Tests for Ahmedabad data layer."""
import json
from pathlib import Path
import pytest
import xarray as xr
import geopandas as gpd
import pandas as pd


class TestERA5Land:
    """Tests for ERA5-Land data."""

    def test_file_exists(self):
        """Verify ERA5-Land file exists."""
        assert Path("data/raw/weather/data_0.nc").exists()

    def test_loads_successfully(self):
        """Verify ERA5-Land file loads."""
        ds = xr.open_dataset("data/raw/weather/data_0.nc")
        assert ds is not None
        ds.close()

    def test_has_required_variables(self):
        """Verify all required variables are present."""
        ds = xr.open_dataset("data/raw/weather/data_0.nc")
        required = ["t2m", "d2m", "u10", "v10", "sp", "ssrd", "strd"]
        for var in required:
            assert var in ds.data_vars, f"Missing variable: {var}"
        ds.close()

    def test_has_valid_dimensions(self):
        """Verify dimensions are valid."""
        ds = xr.open_dataset("data/raw/weather/data_0.nc")
        assert "valid_time" in ds.dims
        assert "latitude" in ds.dims
        assert "longitude" in ds.dims
        ds.close()

    def test_no_missing_values(self):
        """Verify no missing values."""
        ds = xr.open_dataset("data/raw/weather/data_0.nc")
        for var in ds.data_vars:
            missing = ds[var].isnull().sum().item()
            assert missing == 0, f"Missing values in {var}: {missing}"
        ds.close()


class TestGIS:
    """Tests for GIS data."""

    def test_file_exists(self):
        """Verify GIS file exists."""
        assert Path("data/raw/gis/wards_ahmedabad.geojson").exists()

    def test_loads_successfully(self):
        """Verify GIS file loads."""
        gdf = gpd.read_file("data/raw/gis/wards_ahmedabad.geojson")
        assert gdf is not None

    def test_has_48_wards(self):
        """Verify 48 wards are present."""
        gdf = gpd.read_file("data/raw/gis/wards_ahmedabad.geojson")
        assert len(gdf) == 48

    def test_has_valid_crs(self):
        """Verify CRS is EPSG:4326."""
        gdf = gpd.read_file("data/raw/gis/wards_ahmedabad.geojson")
        assert gdf.crs.to_epsg() == 4326

    def test_has_valid_geometries(self):
        """Verify all geometries are valid."""
        gdf = gpd.read_file("data/raw/gis/wards_ahmedabad.geojson")
        assert gdf.geometry.is_valid.all()

    def test_no_duplicate_ids(self):
        """Verify no duplicate ward IDs."""
        gdf = gpd.read_file("data/raw/gis/wards_ahmedabad.geojson")
        assert not gdf["ward_lgd_code"].duplicated().any()

    def test_normalized_copy_exists(self):
        """Verify normalized copy exists."""
        assert Path("data/staging/gis/wards_ahmedabad_normalized.geojson").exists()


class TestAQI:
    """Tests for AQI data."""

    def test_files_exist(self):
        """Verify AQI files exist."""
        aqi_files = list(Path("data/raw/aqi").glob("*.xlsx"))
        assert len(aqi_files) == 5

    def test_files_load(self):
        """Verify AQI files load."""
        aqi_files = list(Path("data/raw/aqi").glob("*.xlsx"))
        for file in aqi_files:
            df = pd.read_excel(file)
            assert df is not None
            assert len(df) > 0

    def test_has_date_column(self):
        """Verify AQI files have Date column."""
        aqi_files = list(Path("data/raw/aqi").glob("*.xlsx"))
        for file in aqi_files:
            df = pd.read_excel(file)
            assert "Date" in df.columns


class TestProfiles:
    """Tests for data profiles."""

    def test_era5_profile_exists(self):
        """Verify ERA5 profile exists."""
        assert Path("data/profiles/era5land_ahmedabad.json").exists()

    def test_gis_profile_exists(self):
        """Verify GIS profile exists."""
        assert Path("data/profiles/gis_ahmedabad.json").exists()

    def test_aqi_profile_exists(self):
        """Verify AQI profile exists."""
        assert Path("data/profiles/aqi_ahmedabad_2025.json").exists()

    def test_profiles_are_valid_json(self):
        """Verify profiles are valid JSON."""
        for profile in [
            "data/profiles/era5land_ahmedabad.json",
            "data/profiles/gis_ahmedabad.json",
            "data/profiles/aqi_ahmedabad_2025.json",
        ]:
            with open(profile) as f:
                data = json.load(f)
                assert data is not None
