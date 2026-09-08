# AHMEDABAD PM2.5 MODELING READINESS
## Option A: Local CPCB + MAIAC Model

**Audit Date**: 2026-09-08
**Status**: BLOCKED — No PM2.5 concentration data available

---

## EXECUTIVE SUMMARY

**The Ahmedabad-specific PM2.5 modeling dataset CANNOT be built from currently available data.**

All 9 Ahmedabad CPCB/GPCB station files contain **composite AQI values**, not PM2.5 concentration measurements (µg/m³). Per the task requirement: "Only actual PM2.5 concentration fields with explicit units are ground truth."

---

## 1. CPCB PM2.5 INVENTORY

### Station Inventory (9 stations)

| station_id | station_name | agency | latitude | longitude | cpcb_code | verification_status |
|------------|--------------|--------|----------|-----------|-----------|---------------------|
| site_5453 | Chandkheda, Ahmedabad | IITM | 23.108 | 72.5746 | #5453 | VERIFIED CPCB |
| site_5450 | Gyaspur, Ahmedabad | IITM | 22.9771 | 72.553 | #5450 | VERIFIED CPCB |
| site_308 | Maninagar, Ahmedabad | GPCB | 23.0027 | 72.5919 | #308 | VERIFIED CPCB |
| site_5452 | Raikhad, Ahmedabad | IITM | 23.0205 | 72.5793 | #5452 | VERIFIED CPCB |
| site_5451 | Rakhial, Ahmedabad | IITM | 23.0168 | 72.6258 | #5451 | VERIFIED CPCB |
| site_5454 | SAC ISRO Bopal, Ahmedabad | IITM | 23.0411 | 72.4567 | #5454 | VERIFIED CPCB |
| site_5455 | SAC ISRO Satellite, Ahmedabad | IITM | 23.0234 | 72.5152 | #5455 | VERIFIED CPCB |
| site_5456 | SVPI Airport Hansol, Ahmedabad | IITM | 23.0768 | 72.6279 | #5456 | VERIFIED CPCB |
| site_5449 | Sardar Vallabhbhai Patel Stadium, Ahmedabad | IITM | 23.0431 | 72.563 | #5449 | VERIFIED CPCB |

### Data Availability (per metadata)

| station_id | month | hourly_available | aqi_available | pollutants_available | status |
|------------|-------|------------------|---------------|---------------------|--------|
| site_5453 | January-May 2025 | True | True | **False** | AVAILABLE |
| site_5450 | January-May 2025 | True | True | **False** | AVAILABLE |
| site_308 | January-May 2025 | True | True | **False** | AVAILABLE |
| site_5452 | January-May 2025 | True | True | **False** | AVAILABLE |
| site_5451 | January-May 2025 | True | True | **False** | AVAILABLE |
| site_5454 | January-May 2025 | True | True | **False** | AVAILABLE |
| site_5455 | January-May 2025 | True | True | **False** | AVAILABLE |
| site_5456 | January-May 2025 | True | True | **False** | AVAILABLE |
| site_5449 | January-May 2025 | True | True | **False** | AVAILABLE |

**Critical**: `pollutants_available=False` for ALL stations and ALL months.

### PM2.5 Availability Assessment

| station_id | station_name | valid_PM25_count | PM25_units | available_pollutants | source_file | sha256 |
|------------|--------------|------------------|------------|---------------------|-------------|--------|
| site_5453 | Chandkheda | **0** | N/A | None | aqi_hourly_station_level_chandkheda,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | 5413b9f4... |
| site_5450 | Gyaspur | **0** | N/A | None | aqi_hourly_station_level_gyaspur,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | b0b30663... |
| site_308 | Maninagar | **0** | N/A | None | aqi_hourly_station_level_maninagar,_ahmedabad_-_gpcb_2025_January_ahmedabad_2025.xlsx | cc63cb2d... |
| site_5452 | Raikhad | **0** | N/A | None | aqi_hourly_station_level_raikhad,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | af240bfe... |
| site_5451 | Rakhial | **0** | N/A | None | aqi_hourly_station_level_rakhial,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | 8a3345bf... |
| site_5454 | SAC ISRO Bopal | **0** | N/A | None | aqi_hourly_station_level_sac_isro_bopal,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | 91c30dda... |
| site_5455 | SAC ISRO Satellite | **0** | N/A | None | aqi_hourly_station_level_sac_isro_satellite,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | 7a9e35c2... |
| site_5449 | SVP Stadium | **0** | N/A | None | aqi_hourly_station_level_sardar_vallabhbhai_patel_stadium,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | f37a845b... |
| site_5456 | SVPI Airport | **0** | N/A | None | aqi_hourly_station_level_svpi_airport_hansol,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | 8d37819d... |

**Result**: 0 stations with actual PM2.5 concentration data.

---

## 2. COMMON MODELING PERIOD

### Data Availability Matrix

| Data Source | Period Available | Status |
|-------------|------------------|--------|
| CPCB PM2.5 concentrations | **NONE** | BLOCKED |
| CPCB AQI values | January-May 2025 | Available (but not PM2.5) |
| MAIAC MCD19A2.061 AOD | 2013-present (daily) | Available via GEE |
| ERA5 meteorology | 1979-present (hourly) | Available (March 2010 sample on disk) |
| ERA5-Land meteorology | 1981-present (hourly) | Available (March 2010 sample on disk) |

### Common Period Analysis

**A. Maximum possible common period**: CANNOT BE DETERMINED — PM2.5 data unavailable

**B. Months with sufficient station coverage**: NONE — no PM2.5 data

**C. Months with insufficient station coverage**: ALL — no PM2.5 data

### Recommendation

**No scientifically usable common period can be identified** because the ground truth variable (PM2.5 concentration) is not available in any file.

---

## 3. STATION BALANCE

### AQI Data Balance (not PM2.5)

For January 2025 (only month with station-level files):

| station | valid_aqi_observations | station_days | coverage_% | min | median | mean | p95 | max |
|---------|------------------------|--------------|------------|-----|--------|------|-----|-----|
| Chandkheda | 742 | 31 | 99.7% | 71.0 | 96.0 | 101.1 | 143.0 | 177.0 |
| Gyaspur | 689 | 31 | 92.6% | 39.0 | 121.0 | 138.3 | 250.0 | 308.0 |
| Maninagar | 627 | 31 | 84.3% | 57.0 | 104.0 | 108.0 | 153.4 | 255.0 |
| Raikhad | 690 | 31 | 92.7% | 75.0 | 108.0 | 128.8 | 237.0 | 282.0 |
| Rakhial | 659 | 31 | 88.6% | 83.0 | 138.0 | 151.9 | 250.0 | 284.0 |
| SAC ISRO Bopal | 659 | 31 | 88.6% | 64.0 | 108.0 | 114.3 | 170.2 | 215.0 |
| SAC ISRO Satellite | 742 | 31 | 99.7% | 66.0 | 96.0 | 102.2 | 157.9 | 193.0 |
| SVP Stadium | 712 | 30 | 98.9% | 88.0 | 128.0 | 154.2 | 323.4 | 343.0 |
| SVPI Airport | 604 | 31 | 81.2% | 60.0 | 106.0 | 109.0 | 146.9 | 216.0 |

**Note**: These are AQI values, NOT PM2.5 concentrations. Included for reference only.

### Extremely Sparse Stations

Based on AQI completeness (not PM2.5):
- SVPI Airport Hansol: 81.2% completeness (most sparse)
- Maninagar: 84.3% completeness

---

## 4. MAIAC DATA REQUIREMENT

### Dataset

- **Collection**: MODIS/061/MCD19A2_GRANULES
- **Resolution**: 1 km
- **Temporal**: Daily (multiple granules per day)
- **Product**: MAIAC Multi-Angle Implementation of Atmospheric Correction (MAIAC) AOD

### Availability

MAIAC MCD19A2.061 is available from 2013 to present via Google Earth Engine.

### Spatial Coverage

Ahmedabad bounding box: approximately lat [22.91, 23.14], lon [72.45, 72.70]

### Quality Filtering

Official AOD_QA bands:
- `AOD_QA`: Quality assurance
- `AOD05`: AOD at 550 nm
- `AOD05高昂`: AOD uncertainty

Quality mask should include:
- Cloud mask
- Cloud shadow mask
- Snow/ice mask
- Water mask
- Adjacent cloud mask

### Status

MAIAC data is **available** but cannot be matched to PM2.5 ground truth (which doesn't exist).

---

## 5. TEMPORAL MATCHING DESIGN

### Proposed Scheme

Since PM2.5 data is unavailable, this is a **design document** for when PM2.5 data is acquired.

**Daily aggregation**:
- Aggregate hourly CPCB observations to daily mean PM2.5
- Require minimum 18 hourly observations per day (75% completeness)
- Record: station, date, daily_PM25, hours_available

**Temporal alignment**:
- MAIAC AOD is from satellite overpass (typically 10:30-13:30 local time)
- CPCB PM2.5 is hourly (24 observations per day)
- Use daily mean PM2.5 as target (not hourly)

### Justification

Daily aggregation is appropriate because:
1. MAIAC provides daily composite AOD
2. Daily mean PM2.5 is standard in satellite-ground calibration literature
3. Reduces temporal mismatch between satellite overpass and surface measurements

---

## 6. SPATIAL AOD EXTRACTION

### Design (for when data is available)

**Pixel scale**: 1 km (MAIAC native resolution)

**Station point extraction**:
- Extract AOD at station lat/lon coordinates
- Use nearest pixel or sub-pixel averaging (3×3 window)

**Quality mask**:
- Apply AOD_QA quality flags
- Remove cloudy, snow, water pixels
- Require AOD uncertainty < 0.5

**Missing-day handling**:
- Do not interpolate missing AOD values
- Only use station-days with valid AOD observation

---

## 7. METEOROLOGICAL PREDICTORS

### Available from ERA5

| Variable | Short Name | Physical Rationale | Relevance |
|----------|------------|-------------------|-----------|
| 2m temperature | t2m | Affects chemical reaction rates, boundary layer | HIGH |
| 2m dewpoint | d2m | Proxy for moisture, hygroscopic growth | HIGH |
| 10m wind speed | u10, v10 | Dispersion, ventilation | HIGH |
| Surface pressure | sp | Atmospheric stability | MEDIUM |
| Total precipitation | tp | Washout, removal | MEDIUM |
| Surface solar radiation | ssrd | Photochemistry, boundary layer | MEDIUM |
| Surface thermal radiation | strd | Energy balance | LOW |
| Boundary layer height | blh | Mixing depth, accumulation | HIGH (if available) |

### Recommended Predictors

For initial model:
1. Temperature (t2m)
2. Relative humidity (derived from t2m, d2m)
3. Wind speed (sqrt(u10² + v10²))
4. Surface pressure (sp)
5. Precipitation (tp)

### Status

ERA5 data is **available** but cannot be matched to PM2.5 ground truth (which doesn't exist).

---

## 8. CALIBRATION TABLE STRUCTURE

### Canonical Table Design

```
station_id | station_name | date | latitude | longitude | daily_PM25 | AOD_550 | temperature | relative_humidity | wind_speed | surface_pressure | precipitation | pm25_hours_available | aod_valid | source_references
```

### Columns

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| station_id | string | CPCB | Unique station identifier |
| station_name | string | CPCB | Station name |
| date | date | Derived | YYYY-MM-DD |
| latitude | float | CPCB | Station latitude |
| longitude | float | CPCB | Station longitude |
| daily_PM25 | float | CPCB | Daily mean PM2.5 (µg/m³) |
| AOD_550 | float | MAIAC | AOD at 550 nm |
| temperature | float | ERA5 | 2m temperature (K) |
| relative_humidity | float | ERA5 | Relative humidity (%) |
| wind_speed | float | ERA5 | 10m wind speed (m/s) |
| surface_pressure | float | ERA5 | Surface pressure (Pa) |
| precipitation | float | ERA5 | Total precipitation (m) |
| pm25_hours_available | int | CPCB | Hours with valid PM2.5 |
| aod_valid | bool | MAIAC | Whether AOD is valid |
| source_references | string | Multiple | Traceability |

### Status

Table CANNOT be constructed — daily_PM25 column has no data source.

---

## 9. TRAIN/TEST DESIGN

### Primary Validation: Leave-One-Station-Out

For each station s:
1. Train model on all stations except s
2. Test on held-out station s
3. Repeat for all 9 stations

### Secondary Validation: Time-Based Holdout

Within training data:
- Use first 80% of time period for training
- Use last 20% for testing

### Why Not Random Split?

Random row splitting violates spatial autocorrelation and temporal autocorstructure in the data.

### Status

Validation framework CANNOT be implemented — no training data exists.

---

## 10. MODELING READINESS DECISION

### **INSUFFICIENT**

**Reason**: No PM2.5 concentration data available in any file. All 9 station files contain composite AQI values, not PM2.5 measurements (µg/m³).

### READY Requirements Assessment

| Requirement | Status | Evidence |
|-------------|--------|----------|
| Real PM2.5 target | **NOT MET** | 0 of 9 stations have PM2.5 columns |
| Sufficient common period | **CANNOT DETERMINE** | No PM2.5 data to establish overlap |
| Valid AOD overlap | **CANNOT DETERMINE** | No PM2.5 data to match against |
| Enough stations | **NOT MET for PM2.5** | 9 stations exist but none have PM2.5 |
| Documented predictors | **MET** | ERA5 variables identified |

---

## 11. OUTPUTS CREATED

### Files

| File | Description |
|------|-------------|
| `docs/data/ahmedabad_pm25_modeling_readiness.md` | This report |
| `data/metadata/ahmedabad_pm25_station_inventory.csv` | Station inventory (no PM2.5 data) |
| `data/metadata/ahmedabad_pm25_period_overlap.csv` | Period overlap (empty - no PM2.5) |

---

## 12. FINAL REPORT

### 1. How many Ahmedabad stations have actual PM2.5?

**ZERO (0) of 9 stations have actual PM2.5 concentration data.**

All 9 files contain unlabeled numeric values (AQI, not PM2.5 µg/m³).

### 2. How many have enough data?

**NONE** — data type is wrong (AQI, not PM2.5).

### 3. What is the longest common period?

**CANNOT BE DETERMINED** — no PM2.5 data exists to establish overlap with MAIAC or meteorological data.

### 4. How many station-days are usable?

**ZERO** — no PM2.5 observations available.

### 5. Is MAIAC available over that period?

**YES** — MAIAC MCD19A2.061 is available from 2013 to present via Google Earth Engine. However, it cannot be matched to PM2.5 ground truth (which doesn't exist).

### 6. What meteorological predictors are available?

ERA5 provides: temperature, dewpoint, wind components, surface pressure, precipitation, solar radiation. All are available but cannot be used without PM2.5 target variable.

### 7. What exact daily modeling table can we construct?

**NONE** — the required `daily_PM25` column has no data source.

### 8. Is Ahmedabad-specific PM2.5 modeling scientifically feasible?

**NOT WITH CURRENT DATA.**

Scientific feasibility requires:
1. Ground truth PM2.5 concentrations (µg/m³) — **MISSING**
2. Sufficient temporal overlap with MAIAC AOD — **CANNOT ASSESS**
3. Enough stations for spatial variation — **9 stations exist, but no PM2.5**

### 9. What should the first baseline model be?

**CANNOT RECOMMEND** — no training data exists.

When PM2.5 data is acquired, recommended baseline:
- Random forest or gradient boosting
- Predictors: AOD + temperature + RH + wind speed + pressure
- Validation: Leave-one-station-out

### 10. What validation strategy will be used?

**Leave-One-Station-Out** as primary validation:
- Train on 8 stations, test on 1
- Repeat for all 9 stations
- Report per-station and overall metrics (MAE, RMSE, R²)

---

## BLOCKER: REQUIRED DATA ACQUISITION

To proceed with Ahmedabad PM2.5 modeling, the following data must be acquired:

### Priority 1: PM2.5 Concentration Data

**Source**: CPCB CAAQMS API or manual download
**Required format**: Station-level hourly PM2.5 concentrations in µg/m³
**Required fields**: station_id, timestamp, PM2.5 (µg/m³), latitude, longitude
**Minimum period**: 3 months (ideally 12 months)

### Priority 2: Alternative Ground Truth

If PM2.5 concentrations are unavailable, consider:
1. **Back-calculate PM2.5 from AQI** using CPCB piecewise function (with documentation)
2. **Use Central Pollution Control Board monthly reports** for daily PM2.5
3. **Use Gujarat Pollution Control Board (GPCB) raw data** if available

### Priority 3: Literature-Based Approach

If no ground truth can be acquired:
1. Use published PM2.5/AOD relationships for Indian cities
2. Apply with high uncertainty flags
3. Validate against any available measurement

---

## FILES CREATED

| File | Description |
|------|-------------|
| `docs/data/ahmedabad_pm25_modeling_readiness.md` | This report |
| `data/metadata/ahmedabad_pm25_station_inventory.csv` | Station inventory |
| `data/metadata/ahmedabad_pm25_period_overlap.csv` | Period overlap (empty) |
