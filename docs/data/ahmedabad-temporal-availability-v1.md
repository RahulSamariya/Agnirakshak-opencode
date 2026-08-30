# Ahmedabad Temporal Availability Matrix

## Dataset Coverage

| Dataset | Start | End | Frequency | Geography | Status | Main Issue |
|---------|-------|-----|-----------|-----------|--------|------------|
| ERA5-Land | 2010-03-01 | 2010-03-31 | Hourly | 5x5 grid (22.8-23.2°N, 72.4-72.8°E) | PASS | Sample only - not full year |
| Census 2011 | 2011-03-01 | 2011-03-31 | Static | 57 AMC wards | PASS | Historical - 13 years old |
| GIS (current) | 2024-01-01 | 2024-12-31 | Static | 48 wards | PASS | Current configuration |
| AQI (CPCB) | 2025-01-01 | 2025-05-31 | Hourly | City-level | PARTIAL | Missing April data partially |
| Mortality | N/A | N/A | N/A | N/A | BLOCKED | Not available |
| Hospitalization | N/A | N/A | N/A | N/A | BLOCKED | Not available |
| IMDAA | N/A | N/A | N/A | N/A | UNKNOWN | Not provided |

## Temporal Overlap Analysis

### ERA5-Land vs AQI
- **ERA5-Land**: March 2010 only
- **AQI**: January-May 2025
- **Overlap**: NONE (different years)

### ERA5-Land vs Census
- **ERA5-Land**: March 2010
- **Census**: 2011 (static)
- **Overlap**: Partial (2010 vs 2011)

### Census vs GIS
- **Census**: 2011 (57 wards)
- **GIS**: 2024 (48 wards)
- **Overlap**: Spatial only (different time periods)

## Critical Issues

1. **No common time period**: ERA5-Land (2010), Census (2011), AQI (2025) have no temporal overlap
2. **Ward mismatch**: Census has 57 wards, GIS has 48 wards
3. **Missing health data**: Mortality and hospitalization data not available

## Recommendation

**BLOCKED** - Cannot proceed with ML training until:
1. Full-year ERA5-Land data is acquired (matching AQI period)
2. Census-GIS crosswalk is established
3. Health data (mortality/hospitalization) is obtained
