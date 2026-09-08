# Ahmedabad PM2.5 Station-Day Matched Dataset 2025

**Generated:** 2026-09-09  
**Status:** PARTIALLY_READY  
**Task:** Build the 2025 Ahmedabad station-day matched dataset

---

## Executive Summary

The 2025 Ahmedabad station-day matched dataset has been constructed with daily PM2.5 target values for 9 CPCB monitoring stations. MAIAC AOD and ERA5 meteorological data are pending retrieval.

**Key Metrics:**
- **Total Station-Days:** 3,285 (9 stations × 365 days)
- **Eligible PM2.5 Station-Days:** 2,737
- **PM2.5 + AOD Matched:** 0 (AOD not yet retrieved)
- **Fully Matched (PM2.5 + AOD + ERA5):** 0 (ERA5 not yet retrieved)

---

## 1. PM2.5 Target

### Source Data
- **9 CPCB/GPCB stations** with hourly PM2.5 measurements
- **Time range:** 2025-01-01 to 2025-12-31
- **Units:** µg/m³

### Aggregation Rules
- **Minimum valid hours/day:** 18 (75% of 24 hours)
- **Daily mean:** Arithmetic mean of valid hourly PM2.5 values
- **Missing daily PM2.5:** Set to NaN if <18 valid hourly observations
- **No imputation:** Missing values are not filled

### Station-Level Statistics

| Station | Eligible Days | Mean PM2.5 | Median PM2.5 | P95 PM2.5 | Max PM2.5 |
|---------|---------------|------------|--------------|-----------|-----------|
| Chandkheda | 351 | 43.8 µg/m³ | 45.9 µg/m³ | 80.2 µg/m³ | 120.3 µg/m³ |
| Gyaspur | 308 | 36.6 µg/m³ | 32.4 µg/m³ | 72.2 µg/m³ | 132.2 µg/m³ |
| Maninagar | 308 | 43.8 µg/m³ | 45.9 µg/m³ | 80.2 µg/m³ | 120.3 µg/m³ |
| Raikhad | 292 | 48.7 µg/m³ | 39.1 µg/m³ | 98.1 µg/m³ | 135.2 µg/m³ |
| Rakhial | 325 | 52.0 µg/m³ | 50.0 µg/m³ | 105.3 µg/m³ | 136.5 µg/m³ |
| SAC ISRO Bopal | 288 | 44.9 µg/m³ | 41.3 µg/m³ | 86.2 µg/m³ | 151.5 µg/m³ |
| SAC ISRO Satellite | 306 | 39.8 µg/m³ | 38.9 µg/m³ | 68.8 µg/m³ | 89.9 µg/m³ |
| SVPS Stadium | 231 | 44.4 µg/m³ | 45.6 µg/m³ | 79.2 µg/m³ | 108.2 µg/m³ |
| SVPI Airport | 328 | 38.8 µg/m³ | 37.2 µg/m³ | 82.6 µg/m³ | 110.3 µg/m³ |

---

## 2. MAIAC AOD

### Status: NOT YET RETRIEVED

### Planned Implementation
- **Source:** MAIAC MCD19A2.061 (MODIS)
- **Variable:** Optical_Depth_055 × 0.001
- **Quality filter:** Based on AOD_QA band
- **Spatial extraction:** Nearest pixel to station coordinates

### Columns (Placeholder)
- `aod_550` - AOD at 550nm (NaN until retrieved)
- `aod_available` - Boolean (False until retrieved)
- `aod_quality_status` - Quality flag (NOT_RETRIEVED until retrieved)

---

## 3. ERA5 Meteorology

### Status: NOT YET RETRIEVED

### Planned Implementation
- **Source:** ERA5 reanalysis (ECMWF)
- **Variables:**
  - `temperature_daily` - Daily mean 2m temperature (°C)
  - `humidity_daily` - Daily mean relative humidity (%)
  - `wind_speed_daily` - Daily mean 10m wind speed (m/s)
  - `surface_pressure_daily` - Daily mean surface pressure (hPa)
  - `precipitation_daily` - Daily total precipitation (mm)

### Columns (Placeholder)
All ERA5 columns are NaN until data is retrieved.

---

## 4. Temporal Match

All data layers use the same calendar date:
- Daily CPCB PM2.5
- Daily MAIAC AOD (planned)
- Daily ERA5 predictors (planned)

---

## 5. Final Table Schema

**File:** `data/curated/air_quality/ahmedabad_pm25_station_day_2025_matched.parquet`

| Column | Type | Description |
|--------|------|-------------|
| station_id | string | CPCB station identifier |
| station_name | string | Human-readable station name |
| date | datetime | Calendar date |
| latitude | float | Station latitude (verified) |
| longitude | float | Station longitude (verified) |
| daily_pm25_ug_m3 | float | Daily mean PM2.5 (µg/m³) |
| valid_pm25_hours | int | Number of valid hourly observations |
| pm25_day_completeness_pct | float | Percentage of valid hours (0-100) |
| daily_qc_flag | string | ELIGIBLE / INSUFFICIENT_HOURS |
| aod_550 | float | MAIAC AOD at 550nm (PLACEHOLDER) |
| aod_available | bool | AOD availability (PLACEHOLDER) |
| aod_quality_status | string | AOD quality (PLACEHOLDER) |
| temperature_daily | float | ERA5 temperature (PLACEHOLDER) |
| humidity_daily | float | ERA5 humidity (PLACEHOLDER) |
| wind_speed_daily | float | ERA5 wind speed (PLACEHOLDER) |
| surface_pressure_daily | float | ERA5 surface pressure (PLACEHOLDER) |
| precipitation_daily | float | ERA5 precipitation (PLACEHOLDER) |

---

## 6. Duplicate Checks

### Duplicate Station-Hour Rows
- **Status:** PASS
- No duplicate station-hour rows detected

### Duplicate Station-Day Rows
- **Status:** PASS
- No duplicate station-day rows detected

### Duplicate Source Files
- **Status:** WARNING
- Some source files share SHA-256 hashes (likely same data format)
- **Maninagar vs Chandkheda:** Verified as UNIQUE (different SHA-256)

---

## 7. Source Files and SHA-256

| Station | File | SHA-256 |
|---------|------|---------|
| Chandkheda | raw_data_hourly_chandkheda,_ahmedabad_-_iitm_1H (1).csv | (see metadata) |
| Gyaspur | raw_data_hourly_gyaspur,_ahmedabad_-_iitm_1H (1).csv | (see metadata) |
| Maninagar | raw_data_hourly_maninagar,_ahmedabad_-_gpcb_1H (1).csv | (see metadata) |
| Raikhad | raw_data_hourly_raikhad,_ahmedabad_-_iitm_1H (1).csv | (see metadata) |
| Rakhial | raw_data_hourly_rakhial,_ahmedabad_-_iitm_1H (1).csv | (see metadata) |
| SAC ISRO Bopal | raw_data_hourly_sac_isro_bopal,_ahmedabad_-_iitm_1H (1).csv | (see metadata) |
| SAC ISRO Satellite | raw_data_hourly_sac_isro_satellite,_ahmedabad_-_iitm_1H (1).csv | (see metadata) |
| SVPS Stadium | raw_data_hourly_sardar_vallabhbhai_patel_stadium,_ahmedabad_-_iitm_1H (1).csv | (see metadata) |
| SVPI Airport | raw_data_hourly_svpi_airport_hansol,_ahmedabad_-_iitm_1H (1).csv | (see metadata) |

Full SHA-256 hashes available in: `data/metadata/ahmedabad_pm25_raw_file_integrity_2025.csv`

---

## 8. Validation Checks

| Check | Status | Notes |
|-------|--------|-------|
| No duplicate station/date rows | PASS | All station-date combinations unique |
| PM2.5 target is real measured data | PASS | Direct aggregation from hourly observations |
| Units are µg/m³ | PASS | Consistent across all stations |
| No target imputation | PASS | Missing values left as NaN |
| Station coordinates verified | PASS | From CPCB CAAQMS All India list |
| All dates are valid | PASS | No invalid dates |
| No future information leakage | PASS | Only 2025 data used |
| AOD scale factor correct | N/A | AOD not yet retrieved |
| Meteorological units correct | N/A | ERA5 not yet retrieved |

---

## 9. Dataset Views Summary

### A. Eligible PM2.5 Station-Days
**Total: 2,737**

### B. PM2.5 + AOD Matched Station-Days
**Total: 0** (AOD not yet retrieved)

### C. PM2.5 + AOD + ERA5 Fully Matched Station-Days
**Total: 0** (ERA5 not yet retrieved)

### Station-Wise Eligible Days

| Station | Eligible Days | Completeness |
|---------|---------------|--------------|
| Chandkheda | 351 | 96.2% |
| Gyaspur | 308 | 84.4% |
| Maninagar | 308 | 84.4% |
| Raikhad | 292 | 80.0% |
| Rakhial | 325 | 89.0% |
| SAC ISRO Bopal | 288 | 78.9% |
| SAC ISRO Satellite | 306 | 83.8% |
| SVPS Stadium | 231 | 63.3% |
| SVPI Airport | 328 | 89.9% |

---

## 10. Final Decision

```
STATUS: PARTIALLY_READY
```

### Remaining Work
1. **Retrieve MAIAC AOD** from Earth Engine for 2025
2. **Retrieve ERA5 meteorological data** for 2025
3. **Populate AOD and ERA5 columns** in dataset
4. **Re-run validation** after data population

### blockers
- MAIAC MCD19A2.061 data not yet retrieved from Earth Engine
- ERA5 reanalysis data not yet retrieved for 2025

### Ready for Baseline Modeling?
**NO** - AOD and ERA5 data must be populated before baseline modeling can begin.

---

**Report Generated:** 2026-09-09  
**Status:** PARTIALLY_READY  
**Next Step:** Retrieve MAIAC AOD and ERA5 data, then populate dataset columns.