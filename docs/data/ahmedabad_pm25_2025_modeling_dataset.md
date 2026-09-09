# Ahmedabad PM2.5 2025 Modeling Dataset

**Generated:** 2026-09-09T10:43:46.583801  
**Status:** PARTIALLY_READY  
**Task:** Complete 2025 Ahmedabad PM2.5 modeling data pipeline

---

## Executive Summary

The 2025 Ahmedabad station-day modeling dataset has been constructed with daily PM2.5 target values for 9 CPCB monitoring stations. MAIAC AOD and ERA5 meteorological data columns have been created as placeholders pending data retrieval from Earth Engine.

**Key Metrics:**
- **Total Station-Days:** 3285
- **Eligible PM2.5 Station-Days:** 2737
- **AOD Matched:** 0 (0%)
- **ERA5 Matched:** 0 (0%)
- **Fully Matched:** 0 (0%)

---

## 1. Target Definition

**Target variable:** `daily_pm25_ug_m3`

**Definition:** Daily mean of valid hourly PM2.5 observations from CPCB/GPCB CAAQMS stations.

**Units:** µg/m³

**Daily eligibility rule:** Minimum 18 valid hourly observations per day (75% of 24 hours).

**Missing values:** Left as NaN (no imputation).

---

## 2. Station List

| Station ID | Station Name | Agency | Latitude | Longitude |
|------------|--------------|--------|----------|-----------|
| site_5453 | Chandkheda | IITM | 23.107969 | 72.574648 |
| site_5450 | Gyaspur | IITM | 22.977134 | 72.553024 |
| site_308 | Maninagar | GPCB | 23.002657 | 72.591912 |
| site_5452 | Raikhad | IITM | 23.020509 | 72.579261 |
| site_5451 | Rakhial | IITM | 23.016834 | 72.625775 |
| site_5454 | SAC ISRO Bopal | IITM | 23.041137 | 72.456691 |
| site_5455 | SAC ISRO Satellite | IITM | 23.023389 | 72.515201 |
| site_5449 | SVPS Stadium | IITM | 23.04307 | 72.562968 |
| site_5456 | SVPI Airport Hansol | IITM | 23.076793 | 72.627874 |

**Coordinate source:** CPCB CAAQMS All India station list

---

## 3. MAIAC AOD

**Dataset:** MODIS/061/MCD19A2_GRANULES  
**Variable:** Optical_Depth_055  
**Scale:** AOD_550 = stored_value x 0.001  
**Spatial resolution:** 1km  
**Temporal resolution:** Daily composite

**QA Filter:**
- Cloud mask bits 0-1 = 00 (clear)
- Heavy dust flag bit 2 = 0

**Extraction:** Nearest 1km pixel to station coordinates

---

## 4. ERA5 Meteorology

**Dataset:** ECMWF/ERA5/HOURLY  
**Spatial resolution:** 0.25deg x 0.25deg (~25km)

**Variables:**

| Variable | ERA5 Name | Original Unit | Final Unit | Conversion |
|----------|-----------|---------------|------------|------------|
| temperature | 2m_temperature (t2m) | K | degC | K - 273.15 |
| humidity | 2m_dewpoint_temperature (d2m) | K | % | Tetens formula |
| wind_speed | u10 + v10 | m/s | m/s | sqrt(u^2 + v^2) |
| surface_pressure | Surface pressure (sp) | Pa | hPa | Pa / 100 |
| precipitation | Total precipitation (tp) | m | mm | m x 1000 |

**Relative humidity calculation:**
```
es = 6.1078 x exp(17.27 x T / (T + 237.3))
RH = (es(Td) / es(T)) x 100
```
where T = temperature (degC), Td = dewpoint temperature (degC)

---

## 5. Earth Engine Extraction Design

**Memory-safe architecture:**
1. Load station-day driver table (small CSV)
2. Upload to Earth Engine as FeatureCollection
3. Process only dates in driver table
4. Extract at station POINTS, not full raster
5. Split into monthly batches if needed

**Driver table:** `data/staging/earth_engine/ahmedabad_pm25_station_days_2025.csv`

---

## 6. Missing-Value Rules

- **PM2.5:** Left as NaN if <18 valid hours
- **AOD:** Left as NaN if no valid retrieval
- **ERA5:** Left as NaN if data not available
- **No imputation** of any kind

---

## 7. Provenance

All source files have SHA-256 hashes recorded in:
- `data/metadata/cpcb_pm25_file_inventory.csv`
- `data/metadata/ahmedabad_pm25_station_day_2025_manifest.csv`
- `data/metadata/ahmedabad_pm25_predictor_match_qc.csv`

---

**Status:** PARTIALLY_READY  
**Next Step:** Retrieve MAIAC AOD and ERA5 data from Earth Engine, then populate dataset columns.
