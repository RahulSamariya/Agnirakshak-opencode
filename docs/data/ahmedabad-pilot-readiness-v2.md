# Ahmedabad Pilot Data Readiness Report v2

**Generated**: 2026-08-30
**Branch**: Rahul
**Status**: PARTIAL READY

---

## GO / NO-GO Summary

| Data Layer | Status | Reason |
|------------|--------|--------|
| Weather data layer | **READY** | ERA5-Land profiled, all variables present |
| Population data layer | **BLOCKED** | Census file not in repository |
| GIS data layer | **READY** | 48 wards profiled, coordinate order verified, normalized copy created |
| AQI data layer | **PARTIAL** | City-level only, ~5% missing, no station breakdown |
| Mortality target | **BLOCKED** | Not available |
| Hospitalization target | **BLOCKED** | Not available |

## Detailed Assessment

### Weather Data Layer: READY

| Property | Value |
|----------|-------|
| Source | ERA5-Land (Copernicus) |
| File | `data/raw/weather/data_0.nc` |
| SHA256 | Verified |
| Variables | t2m, d2m, u10, v10, sp, ssrd, strd (all 7 present) |
| Missing values | 0% |
| Coverage | March 2010 (124 timesteps) |
| Grid | 5x5 cells (22.8-23.2N, 72.4-72.8E) |
| Staging schema | `WeatherRecord` in `scientific/staging/schemas.py` |

**Blocker**: None for weather processing.
**Limitation**: March 2010 sample only, not full year.

### Population Data Layer: BLOCKED

| Property | Value |
|----------|-------|
| Source | Census of India 2011 |
| File | `DDW_PCA2407_2011_MDDS with UI (1).xlsx` |
| Status | NOT FOUND in repository |
| `data/raw/census/` | Empty directory |

**Blocker**: Census file not available.
**Action required**: Obtain and place Census file in `data/raw/census/`.

### GIS Data Layer: READY

| Property | Value |
|----------|-------|
| Source | Ahmedabad Municipal Corporation |
| File | `data/raw/gis/wards_ahmedabad.geojson` |
| SHA256 | Verified |
| Features | 48 wards |
| CRS | EPSG:4326 |
| Coordinate order | Latitude/Longitude (raw) → Longitude/Latitude (normalized) |
| Valid geometries | 48/48 |
| Duplicate IDs | 0 |
| Normalized copy | `data/staging/gis/wards_ahmedabad_epsg4326_normalized.geojson` |
| Staging schema | `WardBoundary` in `scientific/staging/schemas.py` |

**Blocker**: None for GIS processing.
**Limitation**: 48 wards (2024) vs 57 Census 2011 wards — crosswalk required.

### AQI Data Layer: PARTIAL

| Property | Value |
|----------|-------|
| Source | Central Pollution Control Board (CPCB) |
| Files | 5 monthly Excel files (Jan-May 2025) |
| SHA256 | Verified per file |
| Records | 3624 hourly observations |
| Missing values | ~5% |
| AQI range | 48-225 |
| Coverage | City-level average only |
| Staging schema | `AQIRecord` in `scientific/staging/schemas.py` |
| Staging table | `data/staging/aqi/aqi_ahmedabad_2025_normalized.csv` |

**Blocker**: None for AQI processing.
**Limitations**: City-level only, no station breakdown, no pollutant columns.

### Mortality Target: BLOCKED

No mortality data available.

**Required fields** (when available):
- `location_id`
- `date`
- `all_cause_deaths`

### Hospitalization Target: BLOCKED

No hospitalization data available.

**Required fields** (when available):
- `location_id`
- `date`
- `hospitalization_count`

## Spatial Reconciliation

| Comparison | Status | Details |
|------------|--------|---------|
| Census 2011 vs Current GIS | CROSSWALK_REQUIRED | 57 vs 48 wards |
| ERA5 grid vs GIS | COMPATIBLE | ERA5 covers Ahmedabad area |
| ERA5-GIS intersection | MEASURED | See `ahmedabad-era5-gis-compatibility-v1.md` |

## Temporal Compatibility

| Comparison | Status | Details |
|------------|--------|---------|
| ERA5 vs AQI | NOT OVERLAPPING | 2010 vs 2025 |
| ERA5 vs Census | ADJACENT | 2010 vs 2011 |
| Census vs GIS | DIFFERENT PERIODS | 2011 vs 2024 |

**No common time period across all datasets.**

## Data Quality

| Dataset | Quality | Issues |
|---------|---------|--------|
| ERA5-Land | PASS | None |
| GIS | PASS | Coordinate order warning (normalized) |
| AQI | PARTIAL | ~5% missing, city-level only |
| Census | BLOCKED | File not in repo |
| Health data | BLOCKED | Not available |

## Provenance

All datasets have SHA256 hashes recorded in `data/metadata/provenance-manifest.json`.

## Files Created

```
data/profiles/census_ahmedabad_2011.json          (BLOCKED status)
data/profiles/census_ahmedabad_2011.md            (BLOCKED documentation)
data/profiles/era5land_ahmedabad_v2.json          (enhanced with SHA256)
data/profiles/gis_ahmedabad_v2.json               (enhanced with coordinate order)
data/profiles/aqi_ahmedabad_2025_v2.json          (enhanced with SHA256)
data/profiles/era5_gis_compatibility.json         (spatial intersection results)
data/staging/gis/wards_ahmedabad_epsg4326_normalized.geojson  (coordinate-normalized)
data/staging/aqi/aqi_ahmedabad_2025_normalized.csv            (AQI staging table)
data/metadata/provenance-manifest.json            (SHA256 hashes)
docs/data/era5land_ahmedabad_v2.md                (enhanced ERA5 profile)
docs/data/gis_ahmedabad_v2.md                     (enhanced GIS profile)
docs/data/aqi_ahmedabad_2025_v2.md                (enhanced AQI profile)
docs/data/ahmedabad-era5-gis-compatibility-v1.md  (spatial compatibility)
docs/data/ahmedabad-spatial-reconciliation-v3.md  (57 vs 48 ward analysis)
docs/data/ahmedabad-temporal-availability-v3.md   (temporal overlap matrix)
docs/data/ahmedabad-data-quality-v1.md            (quality matrix)
docs/data/data-dictionary.md                      (field definitions)
docs/data/ahmedabad-pilot-readiness-v2.md         (this document)
scripts/profile_census.py                         (ready when file available)
scripts/profile_era5_v3.py                        (enhanced ERA5 profiling)
scripts/profile_gis_v3.py                         (enhanced GIS profiling)
scripts/profile_aqi_v4.py                         (enhanced AQI profiling)
scripts/era5_gis_compatibility.py                 (spatial analysis)
scripts/build_provenance_v2.py                    (SHA256 provenance)
tests/test_data_layer_v2.py                       (36 tests using real files)
```

## Remaining Blockers

1. **Census 2011 file** — Not in repository. Required for V/E computation.
2. **Ward crosswalk** — 57 Census wards vs 48 GIS wards. Required for demographic-geographic join.
3. **Full-year ERA5** — Current sample is March 2010 only. Required for weather-AQI correlation.
4. **Health data** — Mortality/hospitalization not available. Required for ML training.

## ML Readiness

**NOT ML-READY**

- Mortality target: BLOCKED (data not available)
- Hospitalization target: BLOCKED (data not available)
- No synthetic health targets used
- No ML code introduced
