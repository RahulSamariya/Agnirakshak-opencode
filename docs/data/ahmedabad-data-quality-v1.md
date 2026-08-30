# Ahmedabad Data Quality Matrix v1

## ERA5-Land (`data/raw/weather/data_0.nc`)

| Check | Status | Details |
|-------|--------|---------|
| File loads | PASS | NetCDF opens successfully |
| Required variables present | PASS | All 7: t2m, d2m, u10, v10, sp, ssrd, strd |
| Missing values | PASS | 0% across all variables |
| Duplicate timestamps | PASS | 0 duplicates (124 unique) |
| Invalid coordinates | PASS | Latitude 22.8-23.2, Longitude 72.4-72.8 |
| Temperature range | PASS | 299-315 K (26-42 C) — physically plausible |
| Wind speed range | PASS | -7 to +7 m/s U/V components — plausible |
| Pressure range | PASS | 97000-101000 Pa — plausible for Ahmedabad |
| Radiation range | PASS | Non-negative, physically plausible |
| Time encoding | PASS | UTC standard for ERA5 |
| Spatial resolution | PASS | 0.1 degree (~11 km) |

**Overall**: PASS

## GIS (`data/raw/gis/wards_ahmedabad.geojson`)

| Check | Status | Details |
|-------|--------|---------|
| File loads | PASS | GeoJSON opens successfully |
| Feature count | PASS | 48 features |
| Geometry type | PASS | All Polygon |
| CRS | PASS | EPSG:4326 |
| Coordinate order | WARNING | Stored as [lat, lon] — normalized copy created |
| Valid geometries | PASS | 48/48 valid |
| Empty geometries | PASS | 0 empty |
| Duplicate ward IDs | PASS | 0 duplicates |
| Required columns | PASS | ward_lgd_code, ward_lgd_name present |
| LGD fields | PASS | ward_lgd_code present |
| Census-related fields | WARNING | No Census 2011 fields in current GIS |

**Overall**: PASS (with warnings)

## AQI (`data/raw/aqi/*.xlsx`)

| Check | Status | Details |
|-------|--------|---------|
| Files load | PASS | All 5 Excel files open |
| Date column present | PASS | Date column in all files |
| Hourly columns | PASS | 24 hourly columns (00:00:00 to 23:00:00) |
| Total observations | PASS | 3624 records (151 days x 24 hours) |
| Missing values | WARNING | ~5% missing across all files |
| Duplicate timestamps | PASS | 0 duplicates |
| AQI range | PASS | 48-225 — plausible for Ahmedabad |
| City-level only | WARNING | No station breakdown |
| No pollutant breakdown | WARNING | Only composite AQI, no PM2.5/PM10/O3 etc. |
| Date parsing | WARNING | Date column contains day numbers, month in filename |

**Overall**: PARTIAL

## Census 2011 (`data/raw/census/`)

| Check | Status | Details |
|-------|--------|---------|
| File present | FAIL | Directory is empty |
| Can profile | FAIL | No data to inspect |

**Overall**: BLOCKED

## Health Data

| Check | Status | Details |
|-------|--------|---------|
| Mortality data | FAIL | Not available |
| Hospitalization data | FAIL | Not available |

**Overall**: BLOCKED

## Cross-dataset Quality

| Check | Status | Details |
|-------|--------|---------|
| Temporal overlap | FAIL | No common period across all datasets |
| Spatial overlap | WARNING | ERA5 grid partially covers ward centroids |
| ID compatibility | FAIL | Census 57 wards vs GIS 48 wards — no crosswalk |
| Unit consistency | PASS | ERA5 in SI units, AQI as index |

**Overall**: PARTIAL
