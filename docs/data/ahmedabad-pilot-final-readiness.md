# Ahmedabad Pilot Data — Final Readiness Report

**Generated**: 2026-08-30
**Branch**: Rahul
**Status**: PARTIAL READY

---

## 1. Dataset Inventory

| # | Dataset | Source | Files | Status | Notes |
|---|---------|--------|-------|--------|-------|
| 1 | ERA5-Land | CDS/Copernicus | 1 NetCDF | PASS | March 2010 sample only |
| 2 | GIS Wards | AMC | 1 GeoJSON | PASS | 48 wards, EPSG:4326 |
| 3 | AQI | CPCB | 5 Excel | PARTIAL | ~5% missing, city-level only |
| 4 | Census 2011 | Census of India | 0 | BLOCKED | File not in repository |
| 5 | Mortality | Health Dept | 0 | BLOCKED | Not available |
| 6 | Hospitalization | Health Dept | 0 | BLOCKED | Not available |

## 2. Data Quality Summary

### ERA5-Land (`data/raw/weather/data_0.nc`)
- **Variables**: t2m, d2m, u10, v10, sp, ssrd, strd (all 7 present)
- **Timesteps**: 124 (March 1-31, 2010, 6-hourly)
- **Grid**: 5x5 cells (22.8-23.2°N, 72.4-72.8°E)
- **Missing values**: 0%
- **QC status**: 20/20 checks passed

### GIS (`data/raw/gis/wards_ahmedabad.geojson`)
- **Features**: 48 wards
- **CRS**: EPSG:4326
- **Valid geometries**: 100%
- **No duplicates**: Yes
- **Normalized copy**: `data/staging/gis/wards_ahmedabad_normalized.geojson`
- **QC status**: 8/8 checks passed

### AQI (`data/raw/aqi/*.xlsx`)
- **Files**: 5 monthly (Jan, Feb, Mar, Apr, May 2025)
- **Format**: Wide (Date + 24 hourly columns)
- **AQI range**: 48-225
- **Missing values**: ~5% (17 of 360 daily-hours across files)
- **QC status**: 13/13 checks passed

### Census (`data/raw/census/`)
- **Status**: BLOCKED
- **Reason**: `DDW_PCA2407_2011_MDDS.xlsx` not found in repository

## 3. Temporal Compatibility

| Dataset | Period | Frequency |
|---------|--------|-----------|
| ERA5-Land | March 2010 | 6-hourly |
| Census 2011 | 2011 (static) | One-time |
| GIS | 2024 (static) | One-time |
| AQI | Jan-May 2025 | Hourly |

**Overlap**: NONE across all datasets. ERA5 (2010) ≠ Census (2011) ≠ AQI (2025).

## 4. Spatial Compatibility

| Dataset | Coverage | Resolution |
|---------|----------|------------|
| ERA5-Land | 22.8-23.2°N, 72.4-72.8°E | 0.1° grid |
| GIS | 22.9-23.1°N, 72.4-72.7°E | Ward polygons |
| AQI | City-level average | N/A |

**ERA5-GIS overlap**: ERA5 grid covers most of Ahmedabad city area.

## 5. Schema Alignment

| Field | ERA5 → WeatherRecord | GIS → WardBoundary | AQI → AQIRecord |
|-------|---------------------|--------------------|----|
| Identifier | station_id | ward_id | city |
| Timestamp | valid_time | N/A | valid_time |
| Temperature | air_temperature | N/A | N/A |
| Humidity | relative_humidity | N/A | N/A |
| Wind | wind_speed | N/A | N/A |
| MRT | mean_radiant_temperature | N/A | N/A |
| AQI | N/A | N/A | aqi_value |
| Geometry | N/A | geometry | N/A |

## 6. Known Blockers

| Blocker | Impact | Required Action |
|---------|--------|-----------------|
| Census file missing | Cannot compute V/E from demographics | Obtain DDW_PCA2407_2011_MDDS.xlsx |
| 57 vs 48 ward mismatch | Census data cannot be joined to GIS | Create crosswalk or obtain 2011 shapefile |
| No temporal overlap | Cannot correlate ERA5 weather with AQI/health | Acquire full-year ERA5 matching AQI period |
| No health data | Cannot train mortality model | Obtain mortality/hospitalization records |

## 7. Staging Schemas Created

| Schema | File | Purpose |
|--------|------|---------|
| WeatherRecord | `scientific/staging/schemas.py` | ERA5 data ingestion |
| WardBoundary | `scientific/staging/schemas.py` | GIS data ingestion |
| WardCensus | `scientific/staging/schemas.py` | Census data ingestion |
| AQIRecord | `scientific/staging/schemas.py` | AQI data ingestion |
| VulnerabilityWardInput | `scientific/staging/schemas.py` | V factor scores |
| ExposureWardInput | `scientific/staging/schemas.py` | E factor scores |
| RiskAssessment | `scientific/staging/schemas.py` | Risk results |
| WardRiskSummary | `scientific/staging/schemas.py` | Ward-level aggregation |
| HealthRecord | `scientific/staging/schemas.py` | Mortality/hospitalization |
| ProvenanceRecord | `scientific/staging/schemas.py` | Data lineage |

## 8. Quality Control

| Dataset | Checks | Passed | Status |
|---------|--------|--------|--------|
| ERA5-Land | 20 | 20 | PASS |
| GIS | 8 | 8 | PASS |
| AQI | 13 | 13 | PASS |

Full QC report: `data/profiles/qc_report.json`

## 9. Provenance

- Acquisition manifest: `data/metadata/acquisition-manifest.yaml`
- Provenance manifest: `data/metadata/provenance-manifest.json`
- All source file hashes (MD5) recorded
- Schema version: v1.0.0

## 10. Tests Added

| Test Suite | Tests | Status |
|------------|-------|--------|
| `tests/test_data_layer.py` | 19 | PASS |
| `tests/test_spatial_temporal.py` | 14 | PASS |

**Total project tests**: 292

## 11. GO/NO-GO Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| ERA5 available | GO | 7 variables, 0% missing |
| GIS available | GO | 48 wards, valid geometries |
| AQI available | PARTIAL | City-level, ~5% missing |
| Census available | BLOCKED | File missing |
| Temporal overlap | BLOCKED | No common period |
| Spatial overlap | GO | ERA5 covers Ahmedabad |
| Health data | BLOCKED | Not available |
| Schema alignment | GO | Staging schemas defined |
| QC passing | GO | All checks pass |
| Provenance tracked | GO | Hashes recorded |

**Overall: PARTIAL READY**

- Ready for: ERA5 → UTCI → H pipeline validation with real data
- Not ready for: V/E computation (no census/health data), ML training (no health targets)

## 12. Files Created in This Phase

```
scientific/staging/__init__.py
scientific/staging/schemas.py
scripts/quality_control.py
scripts/build_provenance.py
data/profiles/qc_report.json
data/metadata/provenance-manifest.json
tests/test_data_layer.py
tests/test_spatial_temporal.py
docs/data/era5land_ahmedabad.md
docs/data/ahmedabad-gis-profile-v2.md
docs/data/ahmedabad-temporal-availability-v2.md
docs/data/ahmedabad-spatial-reconciliation-v2.md
docs/data/ahmedabad-pilot-profile-v2.md
```
