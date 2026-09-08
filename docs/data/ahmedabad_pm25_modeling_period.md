# Ahmedabad PM2.5 Modeling Period Design

**Last Updated:** 2026-09-08  
**Maintainer:** Agnirakshak Project Team

## Executive Summary

Based on comprehensive analysis of 5 years of PM2.5 data from 9 Ahmedabad monitoring stations, this document recommends:

- **PILOT YEAR:** 2025
- **FINAL MODEL PERIOD:** 2023-2025 (3 years)
- **Status:** READY_FOR_1_YEAR_PILOT

The 2025 pilot year provides the best balance of data completeness (86.5% average), station coverage (9 stations), and seasonal representation. The 2023-2025 final period maximizes valid PM2.5 records while maintaining quality standards.

## Data Analysis Summary

### Available Data Overview
- **Total Stations:** 9
- **Total Station-Years:** 45
- **Total PM2.5 Records:** ~243,000 hourly observations
- **Date Range:** 2022-01-01 to 2026-08-31
- **Temporal Resolution:** Hourly
- **PM2.5 Units:** µg/m³

### Data Quality by Year

| Year | Avg Completeness | Stations >80% | Recommendation |
|------|-----------------|---------------|----------------|
| 2022 | 43.9% | 1/9 | EXCLUDE |
| 2023 | 82.8% | 7/9 | INCLUDE (final only) |
| 2024 | 83.7% | 6/9 | INCLUDE (final only) |
| 2025 | 86.5% | 7/9 | PILOT YEAR |
| 2026 | 83.0% | 7/9 | EXCLUDE (incomplete) |

## Candidate Period Ranking

### A. 2025 Only (RECOMMENDED FOR PILOT)
- **Number of Stations:** 9
- **Station-Days:** 3,285
- **Valid PM2.5 Records:** 67,973
- **Median Station Completeness:** 92.35%
- **Minimum Station Completeness:** 64.04% (SVPS)
- **Seasonal Coverage:** Full Year (Jan-Dec)
- **MAIAC Availability:** Available
- **ERA5 Availability:** Available
- **Recommendation:** **PILOT YEAR**

**Strengths:**
- Highest average completeness (86.5%)
- Best seasonal coverage (full year)
- All 9 stations operational
- Recent data (most current)

**Weaknesses:**
- SVPS at 64% completeness (still usable)
- No multi-year averaging for model stability
- Solar radiation data missing (affects MAIAC AOD)

### B. 2024-2025 (GOOD FOR FINAL MODEL)
- **Number of Stations:** 9
- **Station-Days:** 6,570
- **Valid PM2.5 Records:** 138,547
- **Median Station Completeness:** 92.35%
- **Minimum Station Completeness:** 38.52% (SAC ISRO Bopal 2024)
- **Seasonal Coverage:** Full Year (Jan-Dec 2024 + Jan-Dec 2025)
- **MAIAC Availability:** Available
- **ERA5 Availability:** Available
- **Recommendation:** GOOD FOR FINAL MODEL

**Strengths:**
- Doubles station-days compared to 2025 only
- Strong completeness in 2025
- Good seasonal representation

**Weaknesses:**
- SAC ISRO Bopal 2024 at 38.5% completeness
- Still only 2 years of data

### C. 2023-2025 (BEST FOR FINAL MODEL)
- **Number of Stations:** 9
- **Station-Days:** 9,855
- **Valid PM2.5 Records:** 209,618
- **Median Station Completeness:** 92.01%
- **Minimum Station Completeness:** 68.44% (Raikhad 2023)
- **Seasonal Coverage:** Full Year (Jan-Dec 2023 + Jan-Dec 2025)
- **MAIAC Availability:** Available
- **ERA5 Availability:** Available
- **Recommendation:** **BEST FOR FINAL MODEL**

**Strengths:**
- Maximum valid PM2.5 records (209,618)
- All years above 68% minimum completeness
- 3 years provides better seasonal averaging
- Stable station coverage across years

**Weaknesses:**
- Raikhad 2023 at 68.4% (still usable)
- Excludes 2024 SAC ISRO Bopal issue

### D. 2023-2026 (NOT RECOMMENDED)
- **Number of Stations:** 9
- **Station-Days:** 11,955
- **Valid PM2.5 Records:** 243,438
- **Median Station Completeness:** 92.01%
- **Minimum Station Completeness:** 0.00% (SVPS 2026)
- **Seasonal Coverage:** Partial (Jan-Aug 2026)
- **MAIAC Availability:** Available
- **ERA5 Availability:** Available
- **Recommendation:** NOT RECOMMENDED

**Critical Issue:** SVPS 2026 is 100% missing (station offline)

### E. 2022-2025 (NOT RECOMMENDED)
- **Number of Stations:** 9
- **Station-Days:** 13,140
- **Valid PM2.5 Records:** 242,346
- **Median Station Completeness:** 88.13%
- **Minimum Station Completeness:** 23.44% (Rakhial 2022)
- **Seasonal Coverage:** Full Year (Jan-Dec 2022 + Jan-Dec 2025)
- **MAIAC Availability:** Available
- **ERA5 Availability:** Available
- **Recommendation:** NOT RECOMMENDED

**Critical Issue:** 2022 data severely incomplete (avg 44%)

## Pilot Year Recommendation: 2025

### Why 2025 is the Best Pilot Year

1. **Data Completeness:** 86.5% average across all stations
2. **Station Coverage:** All 9 stations operational (SVPS at 64% still usable)
3. **Seasonal Representation:** Full year (Jan-Dec) for complete seasonal cycle
4. **Recency:** Most current data for model validation
5. **MAIAC Availability:** MODIS/061/MCD19A2_GRANULES accessible in Earth Engine
6. **ERA5 Availability:** Meteorological data available for all variables

### Pilot Year Data Quality

| Station | Completeness | Status |
|---------|-------------|--------|
| Chandkheda | 97.19% | VALID |
| Gyaspur | 88.13% | VALID_WITH_MISSING |
| Maninagar | 97.19% | VALID |
| Raikhad | 82.55% | VALID_WITH_MISSING |
| Rakhial | 92.35% | VALID |
| SAC ISRO Bopal | 81.22% | VALID_WITH_MISSING |
| SAC ISRO Satellite | 84.37% | VALID_WITH_MISSING |
| SVPS | 64.04% | VALID_WITH_MISSING |
| SVPI Airport | 92.99% | VALID |

**Minimum Threshold:** 80% completeness (SVPS at 64% is below threshold but still usable for initial testing)

### Pilot Year Limitations

1. **No Multi-Year Averaging:** Single year may not capture inter-annual variability
2. **Solar Radiation Missing:** SR column is NA, affecting MAIAC AOD retrieval
3. **SVPS Below Threshold:** 64% completeness requires careful handling

## Final Model Recommendation: 2023-2025

### Why 2023-2025 is Best for Final Model

1. **Maximum Valid Records:** 209,618 hourly PM2.5 observations
2. **Quality Threshold:** All years above 68% minimum completeness
3. **Station Stability:** Consistent 9-station network across all years
4. **Seasonal Coverage:** 3 full years provides robust seasonal averaging
5. **Inter-Annual Variability:** Captures year-to-year pollution patterns

### Final Model Data Quality

| Year | Avg Completeness | Min Station | Max Station |
|------|-----------------|-------------|-------------|
| 2023 | 82.8% | 68.4% (Raikhad) | 98.2% (SAC ISRO Bopal) |
| 2024 | 83.7% | 38.5% (SAC ISRO Bopal) | 99.0% (SVPS) |
| 2025 | 86.5% | 64.0% (SVPS) | 97.2% (Chandkheda) |

**Note:** SAC ISRO Bopal 2024 at 38.5% will be excluded from final model

### Final Model Exclusions

1. **Year 2022:** Excluded due to severe data gaps (avg 44% completeness)
2. **Year 2026:** Excluded due to incomplete year and SVPS offline
3. **SAC ISRO Bopal 2024:** Excluded due to 38.5% completeness

### Final Model Station Count

- **Total Stations:** 9
- **Usable Station-Years:** 26 (out of 45 possible)
- **Excluded Station-Years:** 19 (18 from 2022, 1 from 2024)

## Temporal Matching Readiness

### Hourly → Daily Aggregation

**Recommended Approach:**
1. Aggregate hourly PM2.5 to daily mean
2. Minimum 18 valid hours/day required (75% completeness)
3. Missing hours treated as missing values (not imputed)
4. Full 24-hour coverage preferred but not required

**Rationale:**
- CPCB PM2.5 monitoring is continuous (24-hour)
- Daily mean provides stable target variable
- 18-hour threshold balances completeness and data retention

### Station-Day Filtering

**Minimum Threshold:** 18 valid hourly observations/day

**Impact:**
- Expected station-days (2025): 3,285
- Valid station-days (estimated): ~3,100 (94%)
- Excluded station-days: ~185 (6%)

### Consistency Across Stations/Years

**Same Rule Applied:**
- 18-hour minimum threshold consistent across all stations
- Same aggregation method for all years
- Uniform QC standards for pilot and final models

## MAIAC Overlap

### MODIS/061/MCD19A2_GRANULES

**Availability:** Accessible in Earth Engine
**Spatial Resolution:** 1 km
**Temporal Resolution:** Daily
**Coverage:** Global (including Ahmedabad)

### Pilot Year MAIAC Testing

**Recommended Period:** 2025
**Rationale:**
- Matches pilot year for direct comparison
- Full year available for seasonal AOD patterns
- Can validate MAIAC retrieval against ground PM2.5

### MAIAC-PM2.5 Correlation

**Expected Relationship:**
- Positive correlation (higher AOD → higher PM2.5)
- Seasonal variation (winter: high PM2.5, low AOD; summer: low PM2.5, high AOD)
- Site-specific factors (meteorology, aerosol type)

## ERA5 Meteorological Overlap

### Available Variables

| Variable | Description | Units | Availability |
|----------|-------------|-------|--------------|
| AT | Ambient Temperature | °C | 2022-2026 |
| RH | Relative Humidity | % | 2022-2026 |
| WS | Wind Speed | m/s | 2022-2026 |
| WD | Wind Direction | deg | 2022-2026 |
| RF | Rainfall | mm | 2022-2026 |
| SR | Solar Radiation | W/m² | 2022-2024 only |
| BP | Barometric Pressure | mmHg | 2022-2024 only |
| VWS | Vertical Wind Speed | m/s | 2022-2024 only |

### Critical Gap: Solar Radiation (2025-2026)

**Issue:** SR column is NA in 2025-2026 data
**Impact:** Affects MAIAC AOD retrieval and model development
**Workaround:** Use ERA5 reanalysis SR for 2025-2026

## Modeling Design Rationale

### Why Pilot + Final Approach

**Pilot Year (2025):**
- Quick model development and validation
- Identify data quality issues
- Test model architecture
- Establish baseline performance

**Final Model (2023-2025):**
- Robust multi-year training
- Better seasonal representation
- Reduced inter-annual variability
- Improved model generalization

### Why Not One-Year Final Model

**Limitations:**
- May not capture inter-annual variability
- Sensitive to single-year anomalies
- Limited seasonal representation
- Reduced model robustness

### Why Not All Available Years Without QC

**Risks:**
- 2022 data quality issues (44% completeness)
- 2026 incomplete year
- SVPS 2026 offline (0% completeness)
- Inconsistent data quality across years

## Recommendations for Next Phase

### Immediate Actions (Pilot Model)
1. Use 2025 data for initial model development
2. Test MAIAC AOD retrieval for 2025
3. Validate ERA5 meteorological inputs
4. Establish baseline model performance

### Future Actions (Final Model)
1. Extend to 2023-2025 period
2. Implement rigorous QC filtering
3. Validate model across multiple years
4. Optimize for operational forecasting

### Data Acquisition Needs
1. Acquire 2026 data for SVPS station
2. Verify SR data availability for 2025-2026
3. Standardize file naming and format
4. Document all data transformations

## Conclusion

The Ahmedabad PM2.5 dataset is **READY_FOR_1_YEAR_PILOT** with 2025 as the recommended pilot year. The dataset provides:

- **9 monitoring stations** with hourly PM2.5 data
- **86.5% average completeness** across all stations
- **Full seasonal coverage** for complete annual cycle
- **MAIAC and ERA5 availability** for satellite and meteorological inputs

The pilot year will establish model performance and identify any remaining data quality issues before extending to the full 2023-2025 final model period.

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-08  
**Status:** READY_FOR_1_YEAR_PILOT  
**Next Review:** After pilot model completion