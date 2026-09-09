# Ahmedabad PM2.5 Predictor Extraction — Earth Engine Pipeline

**Generated**: 2026-09-09  
**Status**: Scripts created, requires Earth Engine authentication + CDS API  
**Project**: `agniraksha-508013`

## Overview

This pipeline extracts MAIAC AOD and ERA5 meteorological data for the 2025 Ahmedabad PM2.5 station-day dataset.

## Files

| File | Purpose |
|------|---------|
| `scripts/earth_engine/extract_ahmedabad_pm25_maiac_2025.py` | Extract MAIAC AOD at 9 station coordinates |
| `scripts/earth_engine/extract_ahmedabad_pm25_era5_2025.py` | Extract ERA5 meteorology at 9 station coordinates |
| `scripts/join_predictors_to_cpcb.py` | Join CPCB PM2.5 with MAIAC AOD + ERA5 |
| `data/staging/earth_engine/ahmedabad_pm25_station_days_2025.csv` | Driver table (2,737 station-days) |
| `data/staging/earth_engine/ahmedabad_pm25_maiac_station_day_2025.csv` | MAIAC AOD output |
| `data/staging/earth_engine/ahmedabad_pm25_era5_station_day_2025.csv` | ERA5 output |
| `data/curated/air_quality/ahmedabad_pm25_station_day_2025_matched.parquet` | Final matched dataset |

## Prerequisites

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

## Execution Order

1. **Extract MAIAC AOD**
   ```bash
   python scripts/earth_engine/extract_ahmedabad_pm25_maiac_2025.py
   ```
   - Source: `MODIS/061/MCD19A2_GRANULES`
   - Variable: `Optical_Depth_055` (×0.001)
   - QA filtering: cloud mask bits 0-1 = 00, dust flag bit 2 = 0
   - Quarterly chunks for memory safety

2. **Extract ERA5 Meteorology**
   ```bash
   python scripts/earth_engine/extract_ahmedabad_pm25_era5_2025.py
   ```
   - Source: `ECMWF/ERA5/HOURLY`
   - Variables: t2m, d2m, u10, v10, sp, tp
   - RH derived using Tetens formula

3. **Join Predictors**
   ```bash
   python scripts/join_predictors_to_cpcb.py
   ```
   - Joins CPCB target with MAIAC AOD + ERA5
   - Outputs matched parquet + QC CSV

## MAIAC AOD Extraction

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

## ERA5 Meteorology Extraction

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

## Driver Table

The driver table `ahmedabad_pm25_station_days_2025.csv` contains:

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

**Statistics**: 2,737 station-days across 9 stations, date range 2025-01-01 to 2025-12-31

## Strict Matching Rules

1. **One row = one station + one date** (no duplicates)
2. **Never alter PM2.5 target** during joining
3. **Predictor missingness is allowed** and must be explicit
4. **Do not drop rows** merely because predictors are missing
5. **fully_matched** column indicates rows with both AOD and ERA5

## Quality Control

The join script outputs:
- `ahmedabad_pm25_predictor_match_qc.csv`: Per-station matching statistics
- Console output: Matching rates, predictor statistics, readiness status

### Readiness Thresholds
- **READY_FOR_BASELINE_MODEL**: Full match rate > 50%
- **PARTIALLY_READY**: Full match rate 0-50%
- **INSUFFICIENT**: Full match rate = 0%

## Memory Safety

Both extraction scripts process data in quarterly chunks:
- Q1: 2025-01-01 to 2025-03-31
- Q2: 2025-04-01 to 2025-06-30
- Q3: 2025-07-01 to 2025-09-30
- Q4: 2025-10-01 to 2025-12-31

This avoids memory limits when processing large Earth Engine collections.

## Troubleshooting

### Earth Engine Authentication Failed
```bash
pip install earthengine-api
earthengine authenticate
earthengine set_project agniraksha-508013
```

### ModuleNotFoundError: No module named 'ee'
```bash
pip install earthengine-api
```

### Empty MAIAC/ERA5 Output
- Check date range in driver table
- Verify Earth Engine project is set correctly
- Check if data exists for Ahmedabad region

### Low Match Rates
- MAIAC: Cloud cover may reduce AOD availability
- ERA5: 0.25° resolution may not capture local variations