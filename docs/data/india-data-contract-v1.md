# India Data Contract v1

**Dataset**: MoES Heatwave Early Warning System
**Version**: 1.0
**Status**: ACTIVE
**Owner**: MoES / IITM / Agnirakshak Team

## Data Domains

| Domain | Source | License | Update Frequency |
|--------|--------|---------|-----------------|
| Weather (ERA5-Land) | ECMWF CDS | CC-BY-4.0 | Hourly |
| Population (Census 2011) | Census of India | OGL-India | Decadal |
| GIS Wards | AMC / Survey of India | Government | Static |
| Air Quality (AQI) | CPCB | Government | Hourly |
| Mortality | NOT AVAILABLE | N/A | N/A |
| Hospitalization | NOT AVAILABLE | N/A | N/A |

## Data Classification

- **PRIMARY_OFFICIAL**: Census 2011, ERA5-Land, GIS wards, AQI
- **SYNTHETIC**: None (policy prohibits synthetic data for scientific use)
- **DERIVED**: None at profiling stage

## Access Rules

1. All raw files must be preserved byte-for-byte
2. Staging copies must track source checksums (SHA-256)
3. No data fabrication or imputation at profiling stage
4. Ward crosswalk required before joining Census and GIS

## Quality Standards

- Zero missing values in key fields for weather data
- Valid geometries for all GIS features
- AQI values in [0, 500] range
- No duplicate identifiers within datasets
