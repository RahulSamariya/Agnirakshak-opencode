# Ahmedabad PM2.5 Data Inventory

**Last Updated:** 2026-09-08  
**Maintainer:** Agnirakshak Project Team

## Executive Summary

The Agnirakshak repository contains **5 years of hourly PM2.5 concentration data** (2022-2026) from **9 continuous ambient air quality monitoring stations** in Ahmedabad, Gujarat, India. The data is sourced from CPCB CAAQMS (Central Pollution Control Board Continuous Ambient Air Quality Monitoring System) via the airquality.cpcb.gov.in portal.

**Key Metrics:**
- **Total Stations:** 9
- **Total Station-Years:** 45
- **Total PM2.5 Records:** ~243,000 hourly observations
- **Date Range:** 2022-01-01 to 2026-08-31
- **Temporal Resolution:** Hourly
- **PM2.5 Units:** µg/m³

## Station Inventory

### 1. Chandkheda (site_5453)
- **Agency:** IITM (Indian Institute of Tropical Meteorology)
- **Location:** Chandkheda, Ahmedabad
- **Data Quality:** Excellent (2023-2025: 87-97% completeness)
- **Best Year:** 2024 (97.29%)
- **Worst Year:** 2022 (49.22% - excluded from modeling)

### 2. Gyaspur (site_5450)
- **Agency:** IITM
- **Location:** Gyaspur, Ahmedabad
- **Data Quality:** Excellent (2022-2026: 88-96% completeness)
- **Best Year:** 2022 (96.27%)
- **Worst Year:** 2025 (88.13% - still acceptable)

### 3. Maninagar (site_308)
- **Agency:** GPCB (Gujarat Pollution Control Board)
- **Location:** Maninagar, Ahmedabad
- **Data Quality:** Excellent (2023-2025: 87-97% completeness)
- **Best Year:** 2024 (97.29%)
- **Worst Year:** 2022 (49.22% - excluded from modeling)

### 4. Raikhad (site_5452)
- **Agency:** IITM
- **Location:** Raikhad, Ahmedabad
- **Data Quality:** Good (2023-2025: 68-88% completeness)
- **Best Year:** 2024 (88.60%)
- **Worst Year:** 2022 (39.86% - excluded from modeling)

### 5. Rakhial (site_5451)
- **Agency:** IITM
- **Location:** Rakhial, Ahmedabad
- **Data Quality:** Excellent (2023-2026: 92-94% completeness)
- **Best Year:** 2024 (93.34%)
- **Worst Year:** 2022 (23.44% - excluded from modeling)

### 6. SAC ISRO Bopal (site_5454)
- **Agency:** IITM
- **Location:** Space Applications Centre (SAC), ISRO, Bopal
- **Data Quality:** Variable (2023: 98%, 2024: 39%, 2025: 81%)
- **Best Year:** 2023 (98.17%)
- **Worst Year:** 2024 (38.52% - excluded from modeling)

### 7. SAC ISRO Satellite (site_5455)
- **Agency:** IITM
- **Location:** SAC ISRO Satellite Centre
- **Data Quality:** Good (2023-2026: 71-97% completeness)
- **Best Year:** 2026 (96.76%)
- **Worst Year:** 2022 (51.36% - excluded from modeling)

### 8. Sardar Vallabhbhai Patel Stadium (site_5449)
- **Agency:** IITM
- **Location:** Sardar Vallabhbhai Patel Stadium
- **Data Quality:** Variable (2023: 91%, 2024: 99%, 2025: 64%, 2026: 0%)
- **Best Year:** 2024 (98.95%)
- **Critical Issue:** 2026 data is 100% missing (station offline)
- **Note:** Only station with complete data loss in 2026

### 9. SVPI Airport Hansol (site_5456)
- **Agency:** IITM
- **Location:** Sardar Vallabhbhai Patel International Airport, Hansol
- **Data Quality:** Improving (2023: 64%, 2024: 89%, 2025: 93%, 2026: 92%)
- **Best Year:** 2025 (92.99%)
- **Worst Year:** 2022 (50.41% - excluded from modeling)

## Data Quality by Year

### 2022 (EXCLUDED)
- **Average Completeness:** 43.9%
- **Stations with >80% completeness:** 1/9 (Gyaspur only)
- **Recommendation:** EXCLUDE from modeling due to severe data gaps

### 2023 (EXCLUDED for most stations)
- **Average Completeness:** 82.8%
- **Stations with >80% completeness:** 7/9
- **Recommendation:** EXCLUDE for pilot, INCLUDE for final model with careful QC

### 2024 (RECOMMENDED)
- **Average Completeness:** 83.7%
- **Stations with >80% completeness:** 6/9
- **Recommendation:** EXCLUDE for pilot due to SAC ISRO Bopal (39% completeness)

### 2025 (RECOMMENDED - PILOT YEAR)
- **Average Completeness:** 86.5%
- **Stations with >80% completeness:** 7/9
- **Recommendation:** PILOT YEAR - Best balance of completeness and station coverage

### 2026 (EXCLUDED for final model)
- **Average Completeness:** 83.0%
- **Stations with >80% completeness:** 7/9 (SVPS at 0%)
- **Recommendation:** EXCLUDE from final model due to incomplete year and SVPS offline

## Meteorological Variables

All stations include the following meteorological variables:
- **AT** (°C) - Ambient Temperature
- **RH** (%) - Relative Humidity
- **WS** (m/s) - Wind Speed
- **WD** (deg) - Wind Direction
- **RF** (mm) - Rainfall
- **SR** (W/m²) - Solar Radiation (available 2022-2024, NA from 2025)
- **BP** (mmHg) - Barometric Pressure (available 2022-2024, NA from 2025)
- **VWS** (m/s) - Vertical Wind Speed (available 2022-2024, NA from 2025)

**Note:** Solar radiation data is critical for MAIAC AOD retrieval and model development. SR is available for 2022-2024 but missing from 2025-2026 data.

## Other Pollutants

All stations include the following pollutant measurements:
- PM10 (µg/m³)
- NO (µg/m³)
- NO2 (µg/m³)
- NOx (ppb)
- NH3 (µg/m³)
- SO2 (µg/m³)
- CO (mg/m³)
- Ozone (µg/m³)
- Benzene (µg/m³) - available 2022-2024, NA from 2025
- Toluene (µg/m³) - available 2022-2024, NA from 2025
- Xylene (µg/m³) - available 2022-2024, NA from 2025

## Data Files Location

### Primary Data (PM2.5 Concentration)
```
data/PM2.5 data/
├── Chandkheda/          (5 files: 2022-2026)
├── gyaspur/             (5 files: 2022-2026)
├── Maninagar/           (5 files: 2022-2026)
├── raikhad/             (5 files: 2022-2026)
├── rakhial/             (5 files: 2022-2026)
├── sac_isro_bopal/      (5 files: 2022-2026)
├── sac_isro_satellite/  (5 files: 2022-2026)
├── sardar_vallabhbhai_patel_stadium/ (5 files: 2022-2026)
└── svpi_airport_hansol/ (5 files: 2022-2026)
```

### Metadata Files
- `data/metadata/ahmedabad_pm25_station_year_inventory.csv` - Station-year inventory
- `data/metadata/ahmedabad_pm25_period_comparison.csv` - Period comparison analysis
- `data/metadata/ahmedabad_cpcb_current_station_inventory.csv` - Current station metadata

### AQI Data (City-Level)
- `data/raw/aqi/` - City-level AQI data (Jan-May 2025)
- `aqi_hourly_station_level_*.xlsx` - Station-level AQI (Jan 2025 only)

## Data Quality Issues

### Critical Issues
1. **Sardar Vallabhbhai Patel Stadium 2026:** 100% missing - station appears offline
2. **2022 Data Quality:** Severe data gaps across all stations (avg 44% completeness)
3. **Solar Radiation Missing (2025-2026):** SR column is NA, affecting MAIAC AOD retrieval

### Moderate Issues
1. **SAC ISRO Bopal 2024:** Only 38.5% completeness
2. **Raikhad 2023:** Only 68.4% completeness
3. **SVPI Airport 2023:** Only 64.4% completeness

### Minor Issues
1. **File Naming Inconsistencies:** Double dots (`..csv`), mixed numbering schemes
2. **Empty Value Representation:** Mix of `NA` and empty strings
3. **Duplicate Files:** Root CSV is duplicate of Chandkheda 2026

## Recommendations

### For Pilot Model
- **Year:** 2025
- **Stations:** All 9 stations
- **Minimum Completeness Threshold:** 80%
- **Excluded Stations:** None (SVPS 2025 at 64% still usable)

### For Final Model
- **Period:** 2023-2025 (3 years)
- **Stations:** All 9 stations
- **Minimum Completeness Threshold:** 80%
- **Excluded Years:** 2022 (poor quality), 2026 (incomplete)

### For Future Data Acquisition
1. Acquire 2026 data for SVPS station (currently offline)
2. Verify SR data availability for 2025-2026
3. Standardize file naming conventions
4. Normalize empty value representation

## Data Provenance

**Source:** CPCB CAAQMS (Central Pollution Control Board)
**Portal:** https://airquality.cpcb.gov.in
**Data Type:** Hourly PM2.5 concentration measurements
**Quality Assurance:** CPCB automated QC + manual verification
**Access Method:** Browser session download from CPCB portal

## Contact

**Data Issues:** Report to Agnirakshak project team
**CPCB Data Requests:** Contact CPCB through official channels

---

**Inventory Version:** 1.0  
**Last Updated:** 2026-09-08  
**Next Review:** After 2026 data completion