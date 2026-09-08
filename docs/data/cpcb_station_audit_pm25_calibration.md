# CPCB/GPCB STATION AUDIT: PM2.5 CALIBRATION FEASIBILITY
## Ahmedabad 9-Station Assessment

**Audit Date**: 2026-09-08
**Task**: Determine whether 9 Ahmedabad monitoring stations contain sufficient real PM2.5 observations to calibrate/validate MAIAC 1-km AOD product

---

## A. Which stations have actual PM2.5 observations?

**NONE.**

All 9 station files contain **UNLABELED numeric values** with no column header indicating the variable type. The files have structure:
- Column 1: `Date` (1-31, day of month)
- Columns 2-25: `00:00:00` through `23:00:00` (hourly timestamps)
- Values: Numeric (range 39-343 across all stations)

**No file contains a PM2.5 column, PM2.5 concentration data, or any labeled pollutant data.**

Based on QC metadata (`aqi_station_month_qc.csv`), these values appear to be **AQI (Air Quality Index)** values, not PM2.5 concentrations (μg/m³).

## B. What months are actually available?

| Data Type | Months Available |
|-----------|------------------|
| Station-level files | January 2025 only (9 files) |
| City-level files | January, February, March, April, May 2025 (5 files) |
| MAIAC AOD | January 2025 (31 daily dates) |

**Station-level data is available for January 2025 only.**

## C. What temporal resolution?

**Hourly** (24 values per day, 31 days for January 2025 = 744 potential observations per station)

## D. What units?

**UNKNOWN.** The xlsx files have no unit header. Based on value ranges and QC metadata:
- Station values: 39-343 (consistent with AQI scale 0-500)
- City-level AQI: 48-225 (CPCB NAQI scale)
- **These are NOT PM2.5 concentrations (μg/m³)**

## E. How many usable PM2.5 observations?

**ZERO.**

No PM2.5 concentration data exists in any file. Per task requirement: "Do not infer PM2.5 from AQI."

| Station | Valid Values | Completeness | PM2.5 Status |
|---------|-------------|--------------|--------------|
| Chandkheda | 742 | 99.7% | NOT PM2.5 |
| Gyaspur | 689 | 92.6% | NOT PM2.5 |
| Maninagar | 627 | 84.3% | NOT PM2.5 |
| Raikhad | 690 | 92.7% | NOT PM2.5 |
| Rakhial | 659 | 88.6% | NOT PM2.5 |
| SAC ISRO Bopal | 659 | 88.6% | NOT PM2.5 |
| SAC ISRO Satellite | 742 | 99.7% | NOT PM2.5 |
| SVP Stadium | 712 | 98.9% | NOT PM2.5 |
| SVPI Airport | 604 | 81.2% | NOT PM2.5 |

## F. Which stations have sufficient data?

**NONE for PM2.5 calibration.**

All 9 stations have data files, but the data is not PM2.5 concentrations.

## G. Which stations are too sparse?

**All stations are unsuitable** — not because of sparsity, but because the data type is wrong (AQI, not PM2.5).

## H. Is there enough data for an Ahmedabad-specific AOD→PM2.5 model?

**NO.**

**Critical blocker**: We have zero PM2.5 concentration measurements. The available data is:
1. AQI values (unlabeled, inferred from QC metadata)
2. City-level AQI only (no station-level PM2.5 breakdown)

Without direct PM2.5 measurements (μg/m³), we cannot:
- Calibrate MAIAC AOD against ground truth
- Build an AOD→PM2.5 regression model
- Validate satellite-derived PM2.5 estimates

## I. If yes, what should the next modeling step be?

**N/A** — Data not available.

## J. If no, what is the best fallback?

**Fallback options (in order of preference)**:

1. **Re-acquire station data with PM2.5 concentrations**
   - Download raw CPCB/GPCB data with pollutant-specific columns
   - Ensure files contain: station_id, timestamp, PM2.5 (μg/m³), latitude, longitude
   - Required period: January 2025 (minimum) for MAIAC overlap

2. **Use city-level AQI as proxy** (with caveats)
   - City-level AQI available Jan-May 2025
   - PM2.5 sub-index can be back-calculated from AQI using CPCB formula
   - **Limitation**: Single city-wide value, no spatial variation for 48-ward model

3. **Use literature PM2.5/AOD ratios**
   - Published relationships for Indian cities (e.g., Kumar et al. 2019)
   - **Limitation**: Not Ahmedabad-specific, high uncertainty

4. **Proceed without calibration**
   - Use MAIAC AOD as qualitative indicator only
   - No quantitative PM2.5 estimation

---

## CLASSIFICATION

### **INSUFFICIENT**

**Reason**: No PM2.5 concentration data available in any of the 9 station files. All files contain unlabeled numeric values (likely AQI, not PM2.5 μg/m³). Per task requirement, we cannot infer PM2.5 from AQI.

---

## FILES INSPECTED

| Station | File | SHA256 |
|---------|------|--------|
| Chandkheda | `aqi_hourly_station_level_chandkheda,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `5413b9f4...` |
| Gyaspur | `aqi_hourly_station_level_gyaspur,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `b0b30663...` |
| Maninagar | `aqi_hourly_station_level_maninagar,_ahmedabad_-_gpcb_2025_January_ahmedabad_2025.xlsx` | `cc63cb2d...` |
| Raikhad | `aqi_hourly_station_level_raikhad,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `af240bfe...` |
| Rakhial | `aqi_hourly_station_level_rakhial,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `8a3345bf...` |
| SAC ISRO Bopal | `aqi_hourly_station_level_sac_isro_bopal,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `91c30dda...` |
| SAC ISRO Satellite | `aqi_hourly_station_level_sac_isro_satellite,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `7a9e35c2...` |
| SVP Stadium | `aqi_hourly_station_level_sardar_vallabhbhai_patel_stadium,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `f37a845b...` |
| SVPI Airport | `aqi_hourly_station_level_svpi_airport_hansol,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `8d37819d...` |

## STATION INVENTORY (from `ahmedabad_cpcb_station_inventory.csv`)

| Station | Station ID | Agency | Lat | Lon | CPCB Code |
|---------|-----------|--------|-----|-----|-----------|
| Chandkheda | site_5453 | IITM | 23.108 | 72.5746 | #5453 |
| Gyaspur | site_5450 | IITM | 22.9771 | 72.553 | #5450 |
| Maninagar | site_308 | GPCB | 23.0027 | 72.5919 | #308 |
| Raikhad | site_5452 | IITM | 23.0205 | 72.5793 | #5452 |
| Rakhial | site_5451 | IITM | 23.0168 | 72.6258 | #5451 |
| SAC ISRO Bopal | site_5454 | IITM | 23.0411 | 72.4567 | #5454 |
| SAC ISRO Satellite | site_5455 | IITM | 23.0234 | 72.5152 | #5455 |
| SVPI Airport Hansol | site_5456 | IITM | 23.0768 | 72.6279 | #5456 |
| SVP Stadium | site_5449 | IITM | 23.0431 | 72.563 | #5449 |

## KEY FINDINGS

1. **No PM2.5 data**: All 9 station files contain unlabeled numeric values, not PM2.5 concentrations
2. **AQI values only**: QC metadata indicates these are AQI values (min_aqi, max_aqi columns)
3. **January 2025 only**: Station-level data covers only January 2025
4. **Cannot infer PM2.5**: Task explicitly prohibits inferring PM2.5 from AQI
5. **Calibration infeasible**: Without ground truth PM2.5, AOD→PM2.5 model cannot be built
