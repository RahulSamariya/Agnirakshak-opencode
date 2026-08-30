# Ahmedabad Temporal Availability Matrix v2

## Dataset Coverage

| Dataset | Start | End | Frequency | Timezone | Geography | Status |
|---------|-------|-----|-----------|----------|-----------|--------|
| ERA5-Land | 2010-03-01 | 2010-03-31 | 6-hourly | UTC | 5x5 grid (22.8-23.2N, 72.4-72.8E) | READY |
| AQI (CPCB) | 2025-01-01 | 2025-05-31 | Hourly | IST | City-level | PARTIAL |
| Census 2011 | 2011-03-01 | 2011-03-31 | Static | N/A | 57 AMC wards | BLOCKED |
| GIS (current) | 2024-01-01 | 2024-12-31 | Static | N/A | 48 wards | READY |
| IMDAA | N/A | N/A | N/A | N/A | N/A | UNKNOWN |
| Mortality | N/A | N/A | N/A | N/A | N/A | BLOCKED |
| Hospitalization | N/A | N/A | N/A | N/A | N/A | BLOCKED |

## Temporal Overlap Analysis

### ERA5-Land vs AQI
- **ERA5-Land**: March 2010 (124 timesteps)
- **AQI**: January-May 2025 (hourly)
- **Overlap**: NONE — different years (2010 vs 2025)
- **Gap**: 15 years between datasets

### ERA5-Land vs Census
- **ERA5-Land**: March 2010
- **Census**: 2011 (static)
- **Overlap**: Partial (adjacent years, different data types)

### Census vs GIS
- **Census**: 2011 (57 wards)
- **GIS**: 2024 (48 wards)
- **Overlap**: Spatial only (different time periods, different ward counts)

### AQI vs Health Data
- **AQI**: January-May 2025
- **Mortality/Hospitalization**: Not available
- **Overlap**: N/A

## Common Periods

**No common time period exists across all datasets.**

| Period | ERA5 | AQI | Census | Health |
|--------|------|-----|--------|--------|
| March 2010 | Yes | No | No | No |
| 2011 | No | No | Yes | No |
| Jan-May 2025 | No | Yes | No | No |

## Non-overlapping Periods

- ERA5-Land (2010) does not overlap with AQI (2025)
- Census (2011) does not overlap with current GIS (2024)
- No health data available for any period

## Unknown Periods

- IMDAA: Not provided
- Mortality: Not available
- Hospitalization: Not available

## Impact on Pipeline

1. **Weather → UTCI → H**: Can use ERA5-Land for March 2010 only
2. **Vulnerability V**: Cannot compute from Census (BLOCKED)
3. **Exposure E**: Cannot compute from AQI + health data (BLOCKED)
4. **HSRI = H x V x E**: Partial (H available, V and E blocked)
5. **ML training**: BLOCKED (no common period, no health targets)

## Recommendation

Acquire full-year ERA5-Land data matching the AQI period (2025) to enable weather-air quality correlation analysis.
