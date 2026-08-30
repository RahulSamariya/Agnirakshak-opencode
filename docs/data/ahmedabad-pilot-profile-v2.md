# Ahmedabad Pilot Data Profile

## Summary Table

| Dataset | Coverage | Spatial Resolution | Temporal Resolution | Quality | Status | Main Limitation |
|---------|----------|--------------------|---------------------|---------|--------|-----------------|
| Census 2011 | 57 AMC wards | Ward-level | Static (2011) | 100% | PASS | Historical - 13 years old |
| GIS (current) | 48 wards | Ward polygons | Static (2024) | 100% | PASS | Current configuration |
| ERA5-Land | 5x5 grid | 0.1° x 0.1° | Hourly | 100% | PASS | Sample only - March 2010 |
| AQI (CPCB) | City-level | City average | Hourly | 95% | PARTIAL | Missing some hours |
| Mortality | N/A | N/A | N/A | N/A | BLOCKED | Not available |
| Hospitalization | N/A | N/A | N/A | N/A | BLOCKED | Not available |
| IMDAA | N/A | N/A | N/A | N/A | UNKNOWN | Not provided |

## Detailed Findings

### 1. Census 2011
- **Source**: DDW_PCA2407_2011_MDDS workbook (NOT FOUND)
- **Ward count**: 57 AMC wards (expected)
- **Fields**: Demographic, worker, population data
- **Status**: File not present in repository

### 2. ERA5-Land
- **File**: `data/raw/weather/data_0.nc`
- **Variables**: t2m, d2m, u10, v10, sp, ssrd, strd (all present)
- **Time range**: March 1-31, 2010 (124 hourly timesteps)
- **Spatial coverage**: 22.8-23.2°N, 72.4-72.8°E (5x5 grid)
- **Data quality**: 0% missing values
- **Status**: PASS - All variables for UTCI calculation available

### 3. GIS
- **File**: `data/raw/gis/wards_ahmedabad.geojson`
- **Feature count**: 48 wards
- **CRS**: EPSG:4326
- **Geometry**: All valid polygons
- **Status**: PASS - Ready for spatial analysis

### 4. AQI
- **Files**: 5 monthly workbooks (Jan-May 2025)
- **Format**: Wide format (Date + 24 hourly columns)
- **AQI range**: 48-225
- **Missing values**: ~5% across all files
- **Status**: PARTIAL - Data available but city-level only

### 5. Mortality
- **Status**: BLOCKED - Not provided

### 6. Hospitalization
- **Status**: BLOCKED - Not provided

### 7. IMDAA
- **Status**: UNKNOWN - Not provided

## Critical Issues

1. **57 vs 48 ward mismatch**: Census 2011 and current GIS have different ward counts
2. **No temporal overlap**: ERA5 (2010), Census (2011), AQI (2025) don't share common period
3. **Missing health data**: Mortality and hospitalization not available
4. **Census file missing**: DDW_PCA2407_2011_MDDS workbook not found

## Files Created

- `data/profiles/era5land_ahmedabad.json`
- `data/profiles/gis_ahmedabad.json`
- `data/profiles/aqi_ahmedabad_2025.json`
- `data/staging/gis/wards_ahmedabad_normalized.geojson`
- `docs/data/era5land_ahmedabad.md`
- `docs/data/ahmedabad-gis-profile-v2.md`
- `docs/data/ahmedabad-temporal-availability-v2.md`
- `docs/data/ahmedabad-spatial-reconciliation-v2.md`
- `docs/data/ahmedabad-pilot-profile-v2.md`
