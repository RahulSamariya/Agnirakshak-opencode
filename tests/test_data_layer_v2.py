"""Enhanced data layer tests using REAL Ahmedabad pilot files.

Tests verify:
- Census loading (BLOCKED — file not in repo)
- Census AMC filtering
- NetCDF loading and schema validation
- GIS loading and coordinate normalization
- Geometry validity
- AQI loading and timestamp normalization
- Duplicate detection
- Provenance metadata
"""
from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import xarray as xr

# ---------------------------------------------------------------------------
# ERA5-Land tests
# ---------------------------------------------------------------------------

class TestERA5Land:
    """Tests for real ERA5-Land NetCDF file."""

    NC_PATH = "data/raw/weather/data_0.nc"
    REQUIRED_VARS = ["t2m", "d2m", "u10", "v10", "sp", "ssrd", "strd"]

    def test_file_exists(self):
        assert Path(self.NC_PATH).exists(), f"File not found: {self.NC_PATH}"

    def test_loads_successfully(self):
        ds = xr.open_dataset(self.NC_PATH)
        assert ds is not None
        ds.close()

    def test_has_required_variables(self):
        ds = xr.open_dataset(self.NC_PATH)
        for var in self.REQUIRED_VARS:
            assert var in ds.data_vars, f"Missing variable: {var}"
        ds.close()

    def test_has_valid_dimensions(self):
        ds = xr.open_dataset(self.NC_PATH)
        assert "valid_time" in ds.dims
        assert "latitude" in ds.dims
        assert "longitude" in ds.dims
        ds.close()

    def test_no_missing_values(self):
        ds = xr.open_dataset(self.NC_PATH)
        for var in self.REQUIRED_VARS:
            missing = int(ds[var].isnull().sum().item())
            assert missing == 0, f"Missing values in {var}: {missing}"
        ds.close()

    def test_temperature_in_kelvin(self):
        """ERA5 t2m should be in Kelvin."""
        ds = xr.open_dataset(self.NC_PATH)
        t_min = float(ds["t2m"].min().item())
        t_max = float(ds["t2m"].max().item())
        ds.close()
        # Kelvin: 200-350 range is plausible
        assert 200 <= t_min <= 350, f"t2m min out of range: {t_min}"
        assert 200 <= t_max <= 350, f"t2m max out of range: {t_max}"

    def test_timestamp_count(self):
        ds = xr.open_dataset(self.NC_PATH)
        count = len(ds.valid_time.values)
        ds.close()
        assert count == 124, f"Expected 124 timestamps, got {count}"

    def test_no_duplicate_timestamps(self):
        ds = xr.open_dataset(self.NC_PATH)
        times = ds.valid_time.values
        unique_count = len(set(str(t) for t in times))
        ds.close()
        assert unique_count == len(times), "Duplicate timestamps found"

    def test_grid_dimensions(self):
        ds = xr.open_dataset(self.NC_PATH)
        assert len(ds.latitude) == 5
        assert len(ds.longitude) == 5
        ds.close()

    def test_covers_ahmedabad(self):
        ds = xr.open_dataset(self.NC_PATH)
        lat_min = float(ds.latitude.min().item())
        lat_max = float(ds.latitude.max().item())
        lon_min = float(ds.longitude.min().item())
        lon_max = float(ds.longitude.max().item())
        ds.close()
        # Ahmedabad: lat ~23, lon ~72.5
        assert lat_min <= 23.0 <= lat_max
        assert lon_min <= 72.5 <= lon_max


# ---------------------------------------------------------------------------
# GIS tests
# ---------------------------------------------------------------------------

class TestGIS:
    """Tests for real GIS GeoJSON file."""

    GEOJSON_PATH = "data/raw/gis/wards_ahmedabad.geojson"
    NORMALIZED_PATH = "data/staging/gis/wards_ahmedabad_epsg4326_normalized.geojson"

    def test_file_exists(self):
        assert Path(self.GEOJSON_PATH).exists()

    def test_loads_successfully(self):
        gdf = gpd.read_file(self.GEOJSON_PATH)
        assert gdf is not None

    def test_has_48_wards(self):
        gdf = gpd.read_file(self.GEOJSON_PATH)
        assert len(gdf) == 48

    def test_has_valid_crs(self):
        gdf = gpd.read_file(self.GEOJSON_PATH)
        assert gdf.crs.to_epsg() == 4326

    def test_has_valid_geometries(self):
        gdf = gpd.read_file(self.GEOJSON_PATH)
        assert gdf.geometry.is_valid.all()

    def test_no_duplicate_ids(self):
        gdf = gpd.read_file(self.GEOJSON_PATH)
        assert not gdf["ward_lgd_code"].duplicated().any()

    def test_has_required_columns(self):
        gdf = gpd.read_file(self.GEOJSON_PATH)
        assert "ward_lgd_code" in gdf.columns
        assert "ward_lgd_name" in gdf.columns

    def test_coordinate_order_lat_lon(self):
        """Verify raw GeoJSON uses lat/lon order."""
        gdf = gpd.read_file(self.GEOJSON_PATH)
        all_coords = []
        for geom in gdf.geometry:
            if geom is not None:
                coords = list(geom.exterior.coords)
                all_coords.extend(coords)
        xs = [c[0] for c in all_coords]
        # X should be latitude (~22.9-23.1), not longitude (~72.4-72.7)
        assert min(xs) > 22.0 and max(xs) < 24.0, f"X not lat: {min(xs)}-{max(xs)}"

    def test_normalized_copy_exists(self):
        assert Path(self.NORMALIZED_PATH).exists()

    def test_normalized_has_valid_geometries(self):
        gdf = gpd.read_file(self.NORMALIZED_PATH)
        assert gdf.geometry.is_valid.all()


# ---------------------------------------------------------------------------
# AQI tests
# ---------------------------------------------------------------------------

class TestAQI:
    """Tests for real AQI Excel files."""

    AQI_DIR = "data/raw/aqi"
    REQUIRED_FILES = [
        "aqi_hourly_city_level__2025_January_ahmedabad_2025.xlsx",
        "aqi_hourly_city_level__2025_February_ahmedabad_2025.xlsx",
        "aqi_hourly_city_level__2025_March_ahmedabad_2025.xlsx",
        "aqi_hourly_city_level__2025_April_ahmedabad_2025.xlsx",
        "aqi_hourly_city_level__2025_May_ahmedabad_2025.xlsx",
    ]

    def test_files_exist(self):
        for f in self.REQUIRED_FILES:
            assert Path(self.AQI_DIR, f).exists(), f"Missing: {f}"

    def test_files_load(self):
        for f in self.REQUIRED_FILES:
            df = pd.read_excel(Path(self.AQI_DIR, f))
            assert df is not None
            assert len(df) > 0

    def test_has_date_column(self):
        for f in self.REQUIRED_FILES:
            df = pd.read_excel(Path(self.AQI_DIR, f))
            assert "Date" in df.columns, f"No Date column in {f}"

    def test_has_24_hourly_columns(self):
        for f in self.REQUIRED_FILES:
            df = pd.read_excel(Path(self.AQI_DIR, f))
            hourly_cols = [c for c in df.columns if c != "Date"]
            assert len(hourly_cols) == 24, f"Expected 24 hourly cols in {f}, got {len(hourly_cols)}"

    def test_aqi_values_in_valid_range(self):
        for f in self.REQUIRED_FILES:
            df = pd.read_excel(Path(self.AQI_DIR, f))
            hourly_cols = [c for c in df.columns if c != "Date"]
            for col in hourly_cols:
                vals = df[col].dropna()
                if len(vals) > 0:
                    assert vals.min() >= 0, f"Negative AQI in {f}: {vals.min()}"
                    assert vals.max() <= 500, f"AQI > 500 in {f}: {vals.max()}"

    def test_no_duplicate_dates(self):
        for f in self.REQUIRED_FILES:
            df = pd.read_excel(Path(self.AQI_DIR, f))
            assert not df["Date"].duplicated().any(), f"Duplicate dates in {f}"

    def test_five_monthly_files(self):
        aqi_files = list(Path(self.AQI_DIR).glob("*.xlsx"))
        assert len(aqi_files) == 5


# ---------------------------------------------------------------------------
# Census tests
# ---------------------------------------------------------------------------

class TestCensus:
    """Tests for real Census 2011 file."""

    CENSUS_FILE = "data/raw/census/DDW_PCA2407_2011_MDDS with UI (1).xlsx"

    def test_file_exists(self):
        assert Path(self.CENSUS_FILE).exists()

    def test_loads_successfully(self):
        df = pd.read_excel(self.CENSUS_FILE)
        assert df is not None
        assert len(df) > 0

    def test_has_ward_column(self):
        df = pd.read_excel(self.CENSUS_FILE)
        assert "Ward" in df.columns

    def test_has_level_column(self):
        df = pd.read_excel(self.CENSUS_FILE)
        assert "Level" in df.columns

    def test_has_57_amc_wards(self):
        df = pd.read_excel(self.CENSUS_FILE)
        ward = df[(df["District"] == 474) & (df["Level"] == "WARD")]
        amc = ward[ward["Name"].str.contains("M Corp", case=False, na=False)]
        assert len(amc) == 57

    def test_has_population_columns(self):
        df = pd.read_excel(self.CENSUS_FILE)
        assert "TOT_P" in df.columns
        assert "TOT_M" in df.columns
        assert "TOT_F" in df.columns

    def test_amc_population_positive(self):
        df = pd.read_excel(self.CENSUS_FILE)
        ward = df[(df["District"] == 474) & (df["Level"] == "WARD")]
        amc = ward[ward["Name"].str.contains("M Corp", case=False, na=False)]
        assert amc["TOT_P"].sum() > 0

    def test_staging_csv_exists(self):
        assert Path("data/staging/census/wards_census_2011_amc.csv").exists()


# ---------------------------------------------------------------------------
# Provenance tests
# ---------------------------------------------------------------------------

class TestProvenance:
    """Tests for provenance metadata."""

    PROVENANCE_PATH = "data/metadata/provenance-manifest.json"

    def test_provenance_exists(self):
        assert Path(self.PROVENANCE_PATH).exists()

    def test_provenance_is_valid_json(self):
        with open(self.PROVENANCE_PATH) as f:
            data = json.load(f)
        assert data is not None

    def test_provenance_has_all_datasets(self):
        with open(self.PROVENANCE_PATH) as f:
            data = json.load(f)
        datasets = data.get("datasets", {})
        assert "era5land" in datasets
        assert "gis_raw" in datasets
        assert "gis_normalized" in datasets
        assert "aqi" in datasets
        assert "census" in datasets

    def test_provenance_uses_sha256(self):
        with open(self.PROVENANCE_PATH) as f:
            data = json.load(f)
        assert data.get("hash_algorithm") == "SHA256"

    def test_era5_has_sha256(self):
        with open(self.PROVENANCE_PATH) as f:
            data = json.load(f)
        sha = data["datasets"]["era5land"].get("source_sha256")
        assert sha is not None
        assert len(sha) == 64  # SHA256 hex length

    def test_gis_has_sha256(self):
        with open(self.PROVENANCE_PATH) as f:
            data = json.load(f)
        sha = data["datasets"]["gis_raw"].get("source_sha256")
        assert sha is not None
        assert len(sha) == 64


# ---------------------------------------------------------------------------
# Staging schema tests
# ---------------------------------------------------------------------------

class TestStagingSchemas:
    """Tests that staging schemas exist and are importable."""

    def test_staging_module_importable(self):
        import scientific.staging.schemas
        assert hasattr(scientific.staging.schemas, "WeatherRecord")
        assert hasattr(scientific.staging.schemas, "WardBoundary")
        assert hasattr(scientific.staging.schemas, "AQIRecord")

    def test_weather_record_fields(self):
        from scientific.staging.schemas import WeatherRecord
        fields = WeatherRecord.model_fields
        assert "air_temperature" in fields
        assert "relative_humidity" in fields
        assert "wind_speed" in fields
        assert "mean_radiant_temperature" in fields

    def test_ward_boundary_fields(self):
        from scientific.staging.schemas import WardBoundary
        fields = WardBoundary.model_fields
        assert "ward_id" in fields
        assert "ward_name" in fields
        assert "geometry" in fields
