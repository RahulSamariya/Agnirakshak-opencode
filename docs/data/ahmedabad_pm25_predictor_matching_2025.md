# Ahmedabad PM2.5 Predictor Matching 2025

**Generated:** 2026-09-09  
**Status:** PARTIALLY_READY  
**Task:** Populate and validate MAIAC AOD + ERA5 for the 2025 Ahmedabad PM2.5 pilot dataset

---

## Executive Summary

The 2025 Ahmedabad station-day matched dataset has been constructed with daily PM2.5 target values for 9 CPCB monitoring stations. MAIAC AOD and ERA5 meteorological data columns have been created as placeholders pending data retrieval from Earth Engine and CDS API.

**Key Metrics:**
- **Total Station-Days:** 3,285 (9 stations × 365 days)
- **Eligible PM2.5 Station-Days:** 2,737
- **AOD Matched Station-Days:** 0 (not yet retrieved)
- **ERA5 Matched Station-Days:** 0 (not yet retrieved)
- **Fully Matched Station-Days:** 0 (not yet retrieved)

---

## 1. MAIAC AOD Methodology

### Source Dataset
- **Dataset:** MODIS/061/MCD19A2_GRANULES
- **Variable:** Optical_Depth_055
- **Spatial Resolution:** 1km
- **Temporal Resolution:** Daily composite

### Extraction Method
- **Scale Factor:** AOD = stored_value × 0.001
- **Spatial Extraction:** Nearest pixel to station coordinates
- **Interpolation:** None - missing values left as NaN

### Quality Filter
- **QA Band:** AOD_QA
- **Filter:** Cloud mask bits 0-1 = 00 (clear), Heavy dust flag bit 2 = 0

### Columns
- `aod_550` - AOD at 550nm (unitless)
- `aod_available` - Boolean indicating valid AOD exists
- `aod_quality_status` - Quality flag from AOD_QA band
- `aod_source_date` - Date of AOD observation

### Status: NOT YET RETRIEVED
Earth Engine Python API is not installed. To retrieve:
```bash
pip install earthengine-api
earthengine authenticate
```

---

## 2. ERA5 Meteorology Methodology

### Source Dataset
- **Dataset:** ERA5 hourly data on single levels (0.25° × 0.25°)
- **Dataset ID:** reanalysis-era5-single-levels
- **Spatial Resolution:** 0.25° × 0.25° (~25km)

### Extraction Method
- **Spatial Extraction:** Nearest grid cell to station coordinates
- **Temporal Aggregation:** Daily mean (24 hourly values) for all variables except precipitation

### Variables

| Variable | ERA5 Name | Original Unit | Final Unit | Conversion | Aggregation |
|----------|-----------|---------------|------------|------------|-------------|
| temperature | 2m_temperature (t2m) | K | °C | K - 273.15 | Daily mean |
| humidity | 2m_dewpoint_temperature (d2m) | K | % | Calculate RH from T and Td using Tetens formula | Daily mean |
| wind_speed | 10m_u_component_of_wind (u10) + 10m_v_component_of_wind (v10) | m/s | m/s | sqrt(u10² + v10²) | Daily mean |
| surface_pressure | Surface pressure (sp) | Pa | hPa | Pa / 100 | Daily mean |
| precipitation | Total precipitation (tp) | m | mm | m × 1000 | Daily sum |

### Columns
- `temperature_daily` - Daily mean 2m temperature (°C)
- `humidity_daily` - Daily mean relative humidity (%)
- `wind_speed_daily` - Daily mean 10m wind speed (m/s)
- `surface_pressure_daily` - Daily mean surface pressure (hPa)
- `precipitation_daily` - Daily total precipitation (mm)

### Status: NOT YET RETRIEVED
CDS API is not installed. To retrieve:
```bash
pip install cdsapi
# Configure CDS API key in ~/.cdsapirc
```

---

## 3. Temporal Matching

All data layers use the same calendar date:
- Daily CPCB PM2.5
- Daily MAIAC AOD (composite)
- Daily ERA5 predictors

**Rules:**
- Do not use future data
- Do not use monthly values for daily observations
- Do not treat MAIAC as hourly

---

## 4. Station Spatial Extraction

### Verified Station Coordinates
| Station | ID | Latitude | Longitude | Source |
|---------|-----|----------|-----------|--------|
| Chandkheda | site_5453 | 23.107969 | 72.574648 | CPCB CAAQMS |
| Gyaspur | site_5450 | 22.977134 | 72.553024 | CPCB CAAQMS |
| Maninagar | site_308 | 23.002657 | 72.591912 | CPCB CAAQMS |
| Raikhad | site_5452 | 23.020509 | 72.579261 | CPCB CAAQMS |
| Rakhial | site_5451 | 23.016834 | 72.625775 | CPCB CAAQMS |
| SAC ISRO Bopal | site_5454 | 23.041137 | 72.456691 | CPCB CAAQMS |
| SAC ISRO Satellite | site_5455 | 23.023389 | 72.515201 | CPCB CAAQMS |
| SVPS Stadium | site_5449 | 23.04307 | 72.562968 | CPCB CAAQMS |
| SVPI Airport | site_5456 | 23.076793 | 72.627874 | CPCB CAAQMS |

### Extraction Method
- **MAIAC:** Nearest 1km pixel to station coordinates
- **ERA5:** Nearest 0.25° grid cell to station coordinates

---

## 5. Missingness Report

### PM2.5 Target
- **Available:** 2,737 station-days (83.3%)
- **Missing:** 548 station-days (16.7%)
- **Reason:** Insufficient hourly observations (<18 hours)

### MAIAC AOD
- **Available:** 0 station-days (0.0%)
- **Missing:** 2,737 station-days (100.0%)
- **Reason:** Data not yet retrieved from Earth Engine

### ERA5 Meteorology
- **Available:** 0 station-days (0.0%)
- **Missing:** 2,737 station-days (100.0%)
- **Reason:** Data not yet retrieved from CDS API

---

## 6. Quality Checks

| Check | Status | Notes |
|-------|--------|-------|
| No duplicate station/date | PASS | 0 duplicates |
| No duplicate station/hour in source | PASS | Verified |
| PM2.5 remains real measured data | PASS | Direct aggregation from hourly |
| No PM2.5 imputation | PASS | Missing values left as NaN |
| AOD scale factor = 0.001 | N/A | AOD not yet retrieved |
| Meteorological units verified | N/A | ERA5 not yet retrieved |
| Timestamps aligned correctly | PASS | Same calendar date |
| No future leakage | PASS | Only 2025 data used |
| Coordinates verified | PASS | From CPCB CAAQMS |
| Dates fall within 2025 | PASS | All dates in 2025 |
| Source provenance preserved | PASS | SHA-256 hashes recorded |

---

## 7. Final Matching Counts

### By Station

| Station | Eligible Days | AOD Matched | ERA5 Matched | Fully Matched |
|---------|---------------|-------------|--------------|---------------|
| Chandkheda | 351 | 0 | 0 | 0 |
| Gyaspur | 308 | 0 | 0 | 0 |
| Maninagar | 308 | 0 | 0 | 0 |
| Raikhad | 292 | 0 | 0 | 0 |
| Rakhial | 325 | 0 | 0 | 0 |
| SAC ISRO Bopal | 288 | 0 | 0 | 0 |
| SAC ISRO Satellite | 306 | 0 | 0 | 0 |
| SVPS Stadium | 231 | 0 | 0 | 0 |
| SVPI Airport | 328 | 0 | 0 | 0 |
| **Total** | **2,737** | **0** | **0** | **0** |

### Percentages
- **AOD Match Percentage:** 0.0%
- **ERA5 Match Percentage:** 0.0%
- **Full Match Percentage:** 0.0%

---

## 8. Predictor Coverage

### PM2.5 (Available)
| Statistic | Value |
|-----------|-------|
| Count | 2,737 |
| Missing | 0 |
| Missing% | 0.0% |
| Min | 0.91 µg/m³ |
| Median | 38.95 µg/m³ |
| Mean | 42.79 µg/m³ |
| P95 | 86.17 µg/m³ |
| Max | 151.54 µg/m³ |

### AOD (Not Available)
All values are NaN (not yet retrieved).

### ERA5 Variables (Not Available)
All values are NaN (not yet retrieved).

---

## 9. Sanity Checks

### PM2.5 Values
- **Physically plausible:** YES (0.91 - 151.54 µg/m³)
- **Within India AQI scale:** YES (<500 µg/m³)
- **No extreme outliers:** YES

### AOD Values
- **Status:** NOT YET RETRIEVED
- **Expected range:** 0.0 - 3.0 (unitless)

### ERA5 Values
- **Status:** NOT YET RETRIEVED
- **Expected temperature:** -10°C to 50°C
- **Expected humidity:** 0% to 100%
- **Expected wind speed:** 0 to 50 m/s
- **Expected surface pressure:** 900 to 1100 hPa
- **Expected precipitation:** ≥0 mm

---

## 10. Final Decision

```
STATUS: PARTIALLY_READY
```

### Requirements for READY_FOR_BASELINE_MODEL
- [x] Real PM2.5 target
- [x] Sufficient matched station-days (2,737 eligible)
- [ ] Verified AOD values for a meaningful fraction
- [ ] Verified ERA5 predictors
- [x] No target imputation
- [x] No coordinate errors
- [x] No temporal leakage

### Blockers
1. **MAIAC MCD19A2.061** not retrieved from Earth Engine
2. **ERA5 reanalysis** not retrieved from CDS API

### Next Steps
1. Install Earth Engine Python API: `pip install earthengine-api`
2. Authenticate: `earthengine authenticate`
3. Install CDS API: `pip install cdsapi`
4. Configure CDS API key
5. Run data retrieval scripts
6. Re-run this script to populate predictors

---

**Report Generated:** 2026-09-09  
**Status:** PARTIALLY_READY  
**Next Step:** Retrieve MAIAC AOD and ERA5 data, then populate dataset columns.