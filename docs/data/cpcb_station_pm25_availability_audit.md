# PM2.5 AVAILABILITY AUDIT
## Ahmedabad 9-Station CPCB/GPCB Dataset Verification

**Audit Date**: 2026-09-08
**Goal**: Determine definitively whether the 9 Ahmedabad station datasets contain PM2.5 concentration measurements.

---

## 1. FILES INSPECTED

All 9 station-level XLSX files found in workspace root:

| # | Station | File | SHA256 |
|---|---------|------|--------|
| 1 | Chandkheda | `aqi_hourly_station_level_chandkheda,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `5413b9f497e8a2c685b9295b449e401ed0614d2c12132220d75a9d1a2f5ade45` |
| 2 | Gyaspur | `aqi_hourly_station_level_gyaspur,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `b0b306634d209caaf69c7a7d6040fbcbe3d890397970ea45aad0cd0cb7c9334d` |
| 3 | Maninagar | `aqi_hourly_station_level_maninagar,_ahmedabad_-_gpcb_2025_January_ahmedabad_2025.xlsx` | `cc63cb2df2ab59f83325a073f61f8ffd80bd4102376f832fd64615b838540a2c` |
| 4 | Raikhad | `aqi_hourly_station_level_raikhad,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `af240bfe522888de71efb10de2fab32f5bf8dd4f345b51d14095df23c04266ec` |
| 5 | Rakhial | `aqi_hourly_station_level_rakhial,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `8a3345bf769358ef9e76f59b3d7a8bdc16c6423f0da592d02147a711291bec50` |
| 6 | SAC ISRO Bopal | `aqi_hourly_station_level_sac_isro_bopal,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `91c30dda2b4fe33c0e2fbcb21ade87607dfa1c50bd61516e9c02bc5a6c4b937f` |
| 7 | SAC ISRO Satellite | `aqi_hourly_station_level_sac_isro_satellite,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `7a9e35c2c0f2fc57f79591fbcc93d342052678f156ddffaf86730a8b7f1960c7` |
| 8 | SVPI Airport Hansol | `aqi_hourly_station_level_svpi_airport_hansol,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `8d37819d9a909a060270d34af3a1e920637ccc1312454489763e9748d80747d3` |
| 9 | SVP Stadium | `aqi_hourly_station_level_sardar_vallabhbhai_patel_stadium,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx` | `f37a845b9ab32f1392532b7a395ecacfd706397a1d6a67f5e47a81889d1673c1` |

---

## 2. SCHEMA INSPECTION (ALL 9 FILES IDENTICAL)

**Sheet names**: `['Sheet1']` (single sheet)

**Header row** (Row 0):
```
['Date', '00:00:00', '01:00:00', '02:00:00', '03:00:00', '04:00:00', '05:00:00', 
 '06:00:00', '07:00:00', '08:00:00', '09:00:00', '10:00:00', '11:00:00', '12:00:00', 
 '13:00:00', '14:00:00', '15:00:00', '16:00:00', '17:00:00', '18:00:00', '19:00:00', 
 '20:00:00', '21:00:00', '22:00:00', '23:00:00']
```

**Column names**: `Date` + 24 hourly timestamps (00:00:00 through 23:00:00)

**Data types**: `Date` = int64, hourly columns = float64/int64

**Units**: NONE PRESENT in any file

**Metadata/comments**: NONE

---

## 3. PM2.5 COLUMN SEARCH

Searched for patterns:
- `pm2.5`, `pm25`, `pm_2_5`, `pm2_5`
- `pm2.5 (µg/m³)`, `pm2.5 (ug/m3)`, `pm2.5 concentration`
- `particulate matter 2.5`
- `pm 2.5`, `pm 25`

**Result**: **NO PM2.5 COLUMN FOUND IN ANY FILE**

---

## 4. POLLUTANT COLUMN SEARCH

Searched for: PM10, NO2, SO2, CO, O3, NH3

**Result**: **NO POLLUTANT COLUMNS FOUND IN ANY FILE**

---

## 5. AQI vs PM2.5 DISTINCTION

The files contain only one unlabeled numeric series alongside timestamps.

**Evidence that these are AQI values (NOT PM2.5)**:
1. File names contain "aqi" prefix (`aqi_hourly_station_level_*`)
2. QC metadata file (`aqi_station_month_qc.csv`) has columns: `min_aqi`, `max_aqi`, `mean_aqi`
3. Value ranges (39-343) are consistent with CPCB AQI scale (0-500), NOT PM2.5 concentrations (0-500+ µg/m³)
4. City-level AQI files have identical structure and are explicitly labeled as AQI

**Classification**: These are **AQI values**, not PM2.5 concentrations.

---

## 6. UNITS

**No units present in any file.** The files contain bare numeric values with no unit header.

---

## 7. TEMPORAL RESOLUTION

| Attribute | Value |
|-----------|-------|
| Resolution | Hourly |
| Timezone | Not specified (assumed IST) |
| Start date | January 1, 2025 |
| End date | January 31, 2025 |
| Total days | 31 (January 2025) |

---

## 8. DATA AVAILABILITY (PER STATION)

| Station | Total Hours | Valid | Missing | Completeness | Min | Max | Mean | Negatives |
|---------|-------------|-------|---------|--------------|-----|-----|------|-----------|
| Chandkheda | 744 | 742 | 2 | 99.7% | 71.0 | 177.0 | 101.1 | 0 |
| Gyaspur | 744 | 689 | 55 | 92.6% | 39.0 | 308.0 | 138.3 | 0 |
| Maninagar | 744 | 627 | 117 | 84.3% | 57.0 | 255.0 | 108.0 | 0 |
| Raikhad | 744 | 690 | 54 | 92.7% | 75.0 | 282.0 | 128.8 | 0 |
| Rakhial | 744 | 659 | 85 | 88.6% | 83.0 | 284.0 | 151.9 | 0 |
| SAC ISRO Bopal | 744 | 659 | 85 | 88.6% | 64.0 | 215.0 | 114.3 | 0 |
| SAC ISRO Satellite | 744 | 742 | 2 | 99.7% | 66.0 | 193.0 | 102.2 | 0 |
| SVP Stadium | 720 | 712 | 8 | 98.9% | 88.0 | 343.0 | 154.2 | 0 |
| SVPI Airport | 744 | 604 | 140 | 81.2% | 60.0 | 216.0 | 109.0 | 0 |

**Note**: These are AQI values, NOT PM2.5 concentrations.

---

## 9. SOURCE VERIFICATION

| Station | File Schema | Workbook Metadata | CPCB Documentation | Classification |
|---------|-------------|-------------------|-------------------|----------------|
| Chandkheda | Unlabeled numeric | None | None | **NOT_PM25** |
| Gyaspur | Unlabeled numeric | None | None | **NOT_PM25** |
| Maninagar | Unlabeled numeric | None | None | **NOT_PM25** |
| Raikhad | Unlabeled numeric | None | None | **NOT_PM25** |
| Rakhial | Unlabeled numeric | None | None | **NOT_PM25** |
| SAC ISRO Bopal | Unlabeled numeric | None | None | **NOT_PM25** |
| SAC ISRO Satellite | Unlabeled numeric | None | None | **NOT_PM25** |
| SVP Stadium | Unlabeled numeric | None | None | **NOT_PM25** |
| SVPI Airport | Unlabeled numeric | None | None | **NOT_PM25** |

**Evidence type**: FILE_SCHEMA only (no official documentation confirms PM2.5)

---

## 10. STATION-BY-STATION TABLE

| station_name | station_id | agency | file | pm25_column | pm25_present | pm25_units | temporal_resolution | start_date | end_date | record_count | valid_pm25_records | completeness_pct | evidence_type | verification_status | notes |
|--------------|------------|--------|------|-------------|--------------|------------|---------------------|------------|----------|--------------|--------------------|--------------------|---------------|---------------------|-------|
| Chandkheda | site_5453 | IITM | aqi_hourly_station_level_chandkheda,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | None | NO | N/A | hourly | 2025-01-01 | 2025-01-31 | 744 | 0 | 0.0% | FILE_SCHEMA | NOT_PM25 | Unlabeled AQI values |
| Gyaspur | site_5450 | IITM | aqi_hourly_station_level_gyaspur,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | None | NO | N/A | hourly | 2025-01-01 | 2025-01-31 | 744 | 0 | 0.0% | FILE_SCHEMA | NOT_PM25 | Unlabeled AQI values |
| Maninagar | site_308 | GPCB | aqi_hourly_station_level_maninagar,_ahmedabad_-_gpcb_2025_January_ahmedabad_2025.xlsx | None | NO | N/A | hourly | 2025-01-01 | 2025-01-31 | 744 | 0 | 0.0% | FILE_SCHEMA | NOT_PM25 | Unlabeled AQI values |
| Raikhad | site_5452 | IITM | aqi_hourly_station_level_raikhad,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | None | NO | N/A | hourly | 2025-01-01 | 2025-01-31 | 744 | 0 | 0.0% | FILE_SCHEMA | NOT_PM25 | Unlabeled AQI values |
| Rakhial | site_5451 | IITM | aqi_hourly_station_level_rakhial,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | None | NO | N/A | hourly | 2025-01-01 | 2025-01-31 | 744 | 0 | 0.0% | FILE_SCHEMA | NOT_PM25 | Unlabeled AQI values |
| SAC ISRO Bopal | site_5454 | IITM | aqi_hourly_station_level_sac_isro_bopal,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | None | NO | N/A | hourly | 2025-01-01 | 2025-01-31 | 744 | 0 | 0.0% | FILE_SCHEMA | NOT_PM25 | Unlabeled AQI values |
| SAC ISRO Satellite | site_5455 | IITM | aqi_hourly_station_level_sac_isro_satellite,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | None | NO | N/A | hourly | 2025-01-01 | 2025-01-31 | 744 | 0 | 0.0% | FILE_SCHEMA | NOT_PM25 | Unlabeled AQI values |
| SVP Stadium | site_5449 | IITM | aqi_hourly_station_level_sardar_vallabhbhai_patel_stadium,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | None | NO | N/A | hourly | 2025-01-01 | 2025-01-30 | 720 | 0 | 0.0% | FILE_SCHEMA | NOT_PM25 | Unlabeled AQI values |
| SVPI Airport | site_5456 | IITM | aqi_hourly_station_level_svpi_airport_hansol,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx | None | NO | N/A | hourly | 2025-01-01 | 2025-01-31 | 744 | 0 | 0.0% | FILE_SCHEMA | NOT_PM25 | Unlabeled AQI values |

---

## 11. CRITICAL DECISION

### **C. NO_PM2.5_IN_CURRENT_FILES**

---

## 12. FINAL ANSWER

**"Current station workbooks do not contain verified PM2.5 concentration measurements. They cannot be used as PM2.5 ground truth."**

---

## ANSWER TO KEY QUESTION

**"Can these 9 currently available station datasets be used as PM2.5 ground truth for calibrating MAIAC AOD?"**

### **NO**

**Evidence**:
1. All 9 files contain **unlabeled numeric values** with no column header
2. No file contains a PM2.5 column, PM2.5 concentration data, or any labeled pollutant data
3. File names and QC metadata indicate these are **AQI values**, not PM2.5 concentrations (µg/m³)
4. No units are present in any file
5. No official documentation identifies these values as PM2.5
6. Per task requirement: "Do not infer PM2.5 from AQI"

---

## FILES CREATED

- `docs/data/cpcb_station_pm25_availability_audit.md` — This report
- `data/profiles/cpcb_station_pm25_availability.json` — Machine-readable results
