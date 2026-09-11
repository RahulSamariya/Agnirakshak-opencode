# Ahmedabad PM2.5 2025 Canonical Data

**Status:** CANONICAL
**Version:** 1.0
**Generated:** 2026-09-09T19:34:30.135743
**Updated:** 2026-09-09T19:34:30.135754
**Supersedes:** All previous PM2.5 data documents

---

## 1. Canonical Target Dataset

**File:** `data/curated/air_quality/ahmedabad_pm25_station_day_2025.parquet`

**Canonical row count:** 2780 eligible station-days

**Historical row count:** 2737 (old driver CSV)

**Difference:** 43 Maninagar station-days (data update, not error)

---

## 2. Daily PM2.5 Aggregation

**Definition:**
```
daily_pm25_ug_m3 = mean(valid hourly PM2.5 observations)
```

**Daily eligibility rule:**
- Minimum 18 valid hourly observations per day
- = 75% of 24 hourly observations

**No target imputation.** Missing values left as NaN.

---

## 3. Nine Stations

| Station ID | Station Name | Latitude | Longitude |
|------------|--------------|----------|-----------|
| site_5453 | Chandkheda | 23.107969 | 72.574648 |
| site_5450 | Gyaspur | 22.977134 | 72.553024 |
| site_308 | Maninagar | 23.002657 | 72.591912 |
| site_5452 | Raikhad | 23.020509 | 72.579261 |
| site_5451 | Rakhial | 23.016834 | 72.625775 |
| site_5454 | SAC ISRO Bopal | 23.041137 | 72.456691 |
| site_5455 | SAC ISRO Satellite | 23.023389 | 72.515201 |
| site_5449 | SVPS Stadium | 23.043070 | 72.562968 |
| site_5456 | SVPI Airport Hansol | 23.076793 | 72.627874 |

**Coordinate source:** CPCB CAAQMS All India station list
**Verification:** `data/metadata/ahmedabad_station_coordinate_verification.csv`

---

## 4. Canonical Station/Date Keys

The canonical station/date keys are defined by the eligible rows in:
`data/curated/air_quality/ahmedabad_pm25_station_day_2025.parquet`

---

## 5. Target Version

**Current version:** 2780 eligible station-days

**Historical version:** 2737 eligible station-days

**Reason for difference:** Maninagar (site_308) received updated CPCB data
with 43 additional eligible station-days.

**Version metadata:** `data/metadata/canonical_2025_target_version.md`

**Old files preserved for provenance:**
- `data/staging/earth_engine/ahmedabad_pm25_station_days_2025_old.csv`

---

## 6. MAIAC Dataset

**File:** `data/curated/air_quality/ahmedabad_pm25_maiac_station_day_2025.parquet`

**Total rows:** 2737

**Strict AOD available:** 596 (21.8% coverage)

**Strict AOD rule:**
- cloud_mask = 1
- land_mask = 0
- AOD_QA = 0
- glint_mask = 0

**AOD:** Optical_Depth_055 x 0.001

**AOD uncertainty:** AOD_Uncertainty x 0.0001

**Multiple valid candidates:** Select lowest valid AOD_Uncertainty.

---

## 7. ERA5 Dataset

**File:** `data/staging/earth_engine/ahmedabad_pm25_era5_pilot_500.csv`

**Total rows:** 1728 (192 dates x 9 stations)

**ERA5-complete for pilot:** 500/500

**Variables:**
- temperature_daily_c
- relative_humidity_daily_pct
- wind_speed_daily_ms
- surface_pressure_daily_hpa
- precipitation_daily_m

---

## 8. Pilot Subset

**File:** `data/curated/air_quality/ahmedabad_pm25_station_day_2025_pilot_500.parquet`

**Total rows:** 500

**ERA5-complete:** 500

**AOD-complete:** 92 (18.4%)

**Fully complete:** 92

---

## 9. Data Provenance

All source files have SHA-256 hashes recorded in:
- `data/metadata/cpcb_pm25_file_inventory.csv`

---

## 10. Missing-Value Rules

- **PM2.5:** Left as NaN if <18 valid hours
- **AOD:** Left as NaN if no valid retrieval
- **ERA5:** Left as NaN if data not available
- **No imputation** of any kind

---

## 11. Scientific Rules

- **No synthetic targets**
- **No target imputation**
- **No fabricate PM2.5**
- **No infer PM2.5 from AQI**
- **No silently impute AOD**
- **No use unmasked MAIAC AOD**
- **No use QA-invalid AOD**
- **No use future information**
- **No use held-out station data during training**

---

**Status:** CANONICAL - This is the primary source of truth for 2025 PM2.5 data.

---

## 15. Git Version History

| Commit | Stage | Description |
|--------|-------|-------------|
| 6be4027 | Stage 1 | Build 2025 Ahmedabad PM2.5 station-day modeling dataset |
| fb7fbeb | Stage 1 | Verify station coordinates and raw PM2.5 file integrity |
| 7fd6999 | Stage 1 | Build 2025 Ahmedabad station-day matched dataset |
| faefc28 | Stage 1 | Build 2025 Ahmedabad station-day matched dataset with predictor methodology |
| 43b1e6d | Stage 1 | Add raw PM2.5 hourly data files for 9 Ahmedabad stations |
| 12cc2a1 | Stage 1 | Complete 2025 Ahmedabad PM2.5 modeling data pipeline |
| 179a074 | Stage 6 | Freeze baseline and resolve data version discrepancy |

**Current canonical version:** 2780 eligible station-days
**Historical version:** 2737 eligible station-days
**Version change commit:** 179a074
