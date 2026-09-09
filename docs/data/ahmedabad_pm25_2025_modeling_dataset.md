# Ahmedabad Pm25 2025 Modeling Dataset

**STATUS: HISTORICAL / SUPERSEDED**
**SUPERSEDED BY:** `ahmedabad_pm25_2025_canonical.md`
**Updated:** 2026-09-09T19:34:30.187955

---

> **Note:** This document is retained for historical provenance. Do not use it
> as the current implementation specification. The canonical document is
> `ahmedabad_pm25_2025_canonical.md`.

---

# Ahmedabad PM2.5 2025 Modeling Dataset — Comprehensive Documentation

**Generated**: 2026-09-09  
**Version**: 3.0  
**Status**: PARTIALLY_READY — scripts created, requires Earth Engine authentication  
**Project**: Agnirakshak (Agniraksha)

## Executive Summary

This document provides comprehensive documentation for the 2025 Ahmedabad PM2.5 modeling dataset, including:

1. **Station coordinates** verified from CPCB CAAQMS All India list
2. **Raw file integrity** confirmed via SHA-256 hashing
3. **Daily aggregation** from hourly PM2.5 observations
4. **MAIAC AOD extraction** methodology and scripts
5. **ERA5 meteorology extraction** methodology and scripts
6. **Matched dataset** structure and quality control
7. **Model readiness** assessment

## 1. Station Coordinates

### Source
CPCB Continuous Ambient Air Quality Monitoring Station (CAAQMS) All India list

### Verified Coordinates

| Station | ID | Latitude | Longitude | Agency |
|---------|-----|----------|-----------|--------|
| Chandkheda | site_5453 | 23.107969 | 72.574648 | IITM |
| Gyaspur | site_5450 | 22.977134 | 72.553024 | IITM |
| Maninagar | site_308 | 23.002657 | 72.591912 | GPCB |
| Raikhad | site_5452 | 23.020509 | 72.579261 | IITM |
| Rakhial | site_5451 | 23.016834 | 72.625775 | IITM |
| SAC ISRO Bopal | site_5454 | 23.041137 | 72.456691 | IITM |
| SAC ISRO Satellite | site_5455 | 23.023389 | 72.515201 | IITM |
| SVPS Stadium | site_5449 | 23.04307 | 72.562968 | IITM |
| SVPI Airport Hansol | site_5456 | 23.076793 | 72.627874 | IITM |

### Coordinate Range
- **Latitude**: 22.977134 to 23.107969 (north-south span ~14.5 km)
- **Longitude**: 72.456691 to 72.627874 (east-west span ~18.8 km)
- **Ahmadabad bounding box**: [72.587967, 23.258922] to [72.621748, 23.259674]

## 2. Raw File Integrity

### Methodology
- Computed SHA-256 hashes for all 9 station CSV files
- Verified no duplicate files exist
- Confirmed Maninagar (site_308) is unique after re-upload

### Key Findings
- **Maninagar (site_308)**: Initially had duplicate file `(8).csv` identical to Chandkheda
- **Resolution**: User re-uploaded correct file `(1).csv` with unique SHA-256 hash
- **Final status**: All 9 stations have unique, verified source files

### File Inventory

| Station | Files | Years | Hourly Observations |
|---------|-------|-------|---------------------|
| Chandkheda | 5 | 2022-2026 | ~43,800 |
| Gyaspur | 5 | 2022-2026 | ~43,800 |
| Maninagar | 5 | 2022-2026 | ~43,800 |
| Raikhad | 5 | 2022-2026 | ~43,800 |
| Rakhial | 5 | 2022-2026 | ~43,800 |
| SAC ISRO Bopal | 5 | 2022-2026 | ~43,800 |
| SAC ISRO Satellite | 5 | 2022-2026 | ~43,800 |
| SVPS Stadium | 5 | 2022-2026 | ~43,800 |
| SVPI Airport Hansol | 5 | 2022-2026 | ~43,800 |

## 3. Daily Aggregation

### Rule
- **Minimum valid hours**: 18 hours per day
- **Aggregation**: Arithmetic mean of valid hourly PM2.5 observations
- **No imputation**: Missing hours are excluded from mean calculation

### 2025 Dataset Statistics

| Metric | Value |
|--------|-------|
| Total station-days | 3,285 |
| Eligible station-days (≥18h) | 2,737 |
| Stations | 9 |
| Date range | 2025-01-01 to 2025-12-31 |
| Daily PM2.5 mean | ~65 µg/m³ |
| Daily PM2.5 median | ~50 µg/m³ |
| Daily PM2.5 P95 | ~150 µg/m³ |

### Station-Day Distribution

| Station | Eligible Days |
|---------|---------------|
| Chandkheda | 351 |
| Gyaspur | 308 |
| Maninagar | 308 |
| Raikhad | 292 |
| Rakhial | 325 |
| SAC ISRO Bopal | 288 |
| SAC ISRO Satellite | 306 |
| SVPS Stadium | 231 |
| SVPI Airport Hansol | 328 |

## 4. MAIAC AOD Extraction

### Dataset
- **Source**: `MODIS/061/MCD19A2_GRANULES`
- **Band**: `Optical_Depth_055`
- **Scale**: stored_value × 0.001
- **Spatial**: 1km resolution
- **Temporal**: 2 overpasses/day (Terra ~10:30, Aqua ~13:30)

### QA Filtering
```python
# Valid pixels: Cloud mask bits 0-1 = 00 AND Dust flag bit 2 = 0
qa_mask = (qa_image.bitwiseAnd(3).eq(0)) & (qa_image.bitwiseAnd(4).eq(0))
```

### Extraction Method
- Station-driven: extract at 9 CPCB coordinates
- Radius: 1000m around each point
- Daily composite: mean of available overpasses
- Quarterly chunks: Q1-Q4 for memory safety

### Script
```bash
python scripts/earth_engine/extract_ahmedabad_pm25_maiac_2025.py
```

## 5. ERA5 Meteorology Extraction

### Dataset
- **Source**: `ECMWF/ERA5/HOURLY`
- **Variables**: 
  - `temperature_2m` (K → degC)
  - `dewpoint_temperature_2m` (K → degC)
  - `u_component_of_wind_10m` (m/s)
  - `v_component_of_wind_10m` (m/s)
  - `surface_pressure` (Pa → hPa)
  - `total_precipitation` (m → mm)
- **Spatial**: 0.25° resolution
- **Temporal**: Hourly

### Derived Predictors

| Predictor | Formula |
|-----------|---------|
| `temperature_daily_c` | Mean of hourly 2m temperature (K → degC) |
| `relative_humidity_daily_pct` | Tetens formula: RH = es(Td)/es(T) × 100 |
| `wind_speed_daily_ms` | Mean of sqrt(u² + v²) |
| `surface_pressure_daily_hpa` | Mean of hourly surface pressure (Pa → hPa) |
| `precipitation_daily_m` | Sum of hourly total precipitation (m → mm) |

### Tetens Formula
```
es(T) = 6.1078 × exp(17.27 × T / (T + 237.3))
RH = (es(Td) / es(T)) × 100
```
where T = temperature (degC), Td = dewpoint (degC)

### Extraction Method
- Station-driven: extract at 9 CPCB coordinates
- Radius: 25000m (nearest 0.25° grid cell)
- Daily aggregates computed from hourly data
- Quarterly chunks: Q1-Q4 for memory safety

### Script
```bash
python scripts/earth_engine/extract_ahmedabad_pm25_era5_2025.py
```

## 6. Matched Dataset

### Structure

| Column | Description |
|--------|-------------|
| `station_id` | CPCB station identifier |
| `station_name` | Station name |
| `agency` | Operating agency (IITM/GPCB) |
| `date` | Date (YYYY-MM-DD) |
| `latitude` | Station latitude (WGS84) |
| `longitude` | Station longitude (WGS84) |
| `daily_pm25_ug_m3` | Daily mean PM2.5 (µg/m³) |
| `valid_pm25_hours` | Number of valid hourly observations |
| `pm25_day_completeness_pct` | Percentage of valid hourly observations |
| `aod_550` | MAIAC AOD at 550nm |
| `aod_available` | Boolean: AOD extracted successfully |
| `aod_quality_status` | Quality status of AOD extraction |
| `aod_source_date` | Date of MAIAC data used |
| `temperature_daily_c` | Daily mean temperature (degC) |
| `relative_humidity_daily_pct` | Daily mean relative humidity (%) |
| `wind_speed_daily_ms` | Daily mean wind speed (m/s) |
| `surface_pressure_daily_hpa` | Daily mean surface pressure (hPa) |
| `precipitation_daily_m` | Daily total precipitation (mm) |
| `meteo_available` | Boolean: ERA5 extracted successfully |
| `fully_matched` | Boolean: both AOD and ERA5 available |

### Strict Matching Rules

1. **One row = one station + one date** (no duplicates)
2. **Never alter PM2.5 target** during joining
3. **Predictor missingness is allowed** and must be explicit
4. **Do not drop rows** merely because predictors are missing
5. **fully_matched** column indicates rows with both AOD and ERA5

### Join Script
```bash
python scripts/join_predictors_to_cpcb.py
```

## 7. Quality Control

### QC Metrics

| Metric | Description |
|--------|-------------|
| `eligible_days` | Station-days with ≥18 valid PM2.5 hours |
| `aod_days` | Station-days with valid AOD |
| `era5_days` | Station-days with valid ERA5 |
| `fully_matched_days` | Station-days with both AOD and ERA5 |
| `aod_match_rate` | AOD days / eligible days × 100 |
| `era5_match_rate` | ERA5 days / eligible days × 100 |
| `full_match_rate` | Fully matched days / eligible days × 100 |

### Readiness Thresholds

| Status | Full Match Rate | Description |
|--------|-----------------|-------------|
| READY_FOR_BASELINE_MODEL | > 50% | Sufficient data for training |
| PARTIALLY_READY | 0-50% | Limited data, may affect model performance |
| INSUFFICIENT | 0% | No matched data available |

### Expected Results

Based on Ahmedabad's location (23.02°N, 72.57°E) and 2025 meteorology:

- **MAIAC AOD**: 70-85% availability (clear skies ~60-70% of year)
- **ERA5**: 95-100% availability (continuous reanalysis)
- **Full match**: 65-80% (limited by cloud cover)

## 8. Model Readiness

### Current Status
**PARTIALLY_READY** — Scripts created, requires Earth Engine authentication

### Prerequisites

1. **Earth Engine Python API**
   ```bash
   pip install earthengine-api
   earthengine authenticate
   earthengine set_project agniraksha-508013
   ```

2. **CDS API** (for ERA5 historical data)
   ```bash
   pip install cdsapi
   ```
   Configure API key at: https://cds.climate.copernicus.eu/api/config

### Execution Order

1. **Extract MAIAC AOD**
   ```bash
   python scripts/earth_engine/extract_ahmedabad_pm25_maiac_2025.py
   ```

2. **Extract ERA5 Meteorology**
   ```bash
   python scripts/earth_engine/extract_ahmedabad_pm25_era5_2025.py
   ```

3. **Join Predictors**
   ```bash
   python scripts/join_predictors_to_cpcb.py
   ```

### Next Steps After Extraction

1. Run QC checks and update readiness status
2. Commit and push all results
3. Proceed to baseline model training with leave-one-station-out validation

## 9. File Inventory

### Scripts

| File | Purpose |
|------|---------|
| `scripts/earth_engine/extract_ahmedabad_pm25_maiac_2025.py` | Extract MAIAC AOD |
| `scripts/earth_engine/extract_ahmedabad_pm25_era5_2025.py` | Extract ERA5 meteorology |
| `scripts/join_predictors_to_cpcb.py` | Join CPCB + MAIAC + ERA5 |
| `scripts/build_2025_matched_dataset.py` | Earlier matched dataset builder |
| `scripts/build_2025_matched_dataset_v2.py` | Matched dataset builder with methodology |
| `scripts/build_2025_station_day_dataset.py` | Original station-day dataset builder |
| `scripts/build_2025_modeling_pipeline.py` | Complete 18-phase pipeline script |

### Data Files

| File | Description |
|------|-------------|
| `data/staging/earth_engine/ahmedabad_pm25_station_days_2025.csv` | Driver table (2,737 rows) |
| `data/staging/earth_engine/ahmedabad_pm25_maiac_station_day_2025.csv` | MAIAC AOD output |
| `data/staging/earth_engine/ahmedabad_pm25_era5_station_day_2025.csv` | ERA5 output |
| `data/curated/air_quality/ahmedabad_pm25_station_day_2025_matched.parquet` | Final matched dataset |
| `data/curated/air_quality/ahmedabad_pm25_station_day_2025.parquet` | Earlier pilot dataset |
| `data/metadata/ahmedabad_station_coordinate_verification.csv` | Verified coordinates |
| `data/metadata/ahmedabad_pm25_raw_file_integrity.csv` | SHA-256 hashes |
| `data/metadata/ahmedabad_pm25_raw_file_integrity_2025.csv` | 2025-specific inventory |
| `data/metadata/ahmedabad_pm25_predictor_match_qc.csv` | Predictor match QC |

### Documentation

| File | Description |
|------|-------------|
| `docs/data/ahmedabad_pm25_2025_modeling_dataset.md` | Comprehensive pipeline documentation |
| `docs/data/ahmedabad_pm25_predictor_matching_2025.md` | MAIAC/ERA5 methodology |
| `docs/data/ahmedabad_station_coordinate_integrity.md` | Coordinate verification report |
| `docs/data/ahmedabad_pm25_matched_dataset_2025.md` | Matched dataset documentation |
| `docs/data/ahmedabad_pm25_station_day_2025.md` | Station-day dataset documentation |
| `scripts/earth_engine/README.md` | Earth Engine extraction documentation |

## 10. Constraints

### DO NOT

- Rebuild the PM2.5 target from raw CSVs
- Train ML models
- Fabricate synthetic predictor data
- Fill missing predictor values
- Modify scientific equations

### MUST

- Use authoritative coordinate sources only
- Verify raw file integrity via SHA-256
- Apply ≥18 valid hours/day for daily aggregation
- Use strict one-row-per-station-day matching
- Maintain explicit provenance

## 11. Contact

**Project**: Agnirakshak (Agniraksha)  
**Repository**: https://github.com/RahulSamariya/Agnirakshak-opencode  
**Branch**: `Rahul`  
**Last Updated**: 2026-09-09