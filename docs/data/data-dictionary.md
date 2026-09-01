# Ahmedabad Pilot Data Dictionary

## ERA5-Land Variables

| Variable | Description | Units | Valid Range | Notes |
|----------|-------------|-------|-------------|-------|
| t2m | 2 metre temperature | K | 200-350 | Convert to C: -273.15 |
| d2m | 2 metre dewpoint temperature | K | 200-350 | Convert to C: -273.15 |
| u10 | 10 metre U wind component | m/s | -100 to 100 | East-west component |
| v10 | 10 metre V wind component | m/s | -100 to 100 | North-south component |
| sp | Surface pressure | Pa | 50000-110000 | Standard atmosphere ~101325 Pa |
| ssrd | Surface short-wave radiation downwards | J/m2 | 0-5000000 | Solar radiation |
| strd | Surface long-wave radiation downwards | J/m2 | 0-5000000 | Thermal radiation |

## GIS Fields

| Field | Description | Type | Example |
|-------|-------------|------|---------|
| ward_lgd_code | LGD ward identifier | string | "2401001" |
| ward_lgd_name | Ward name | string | "Danapith" |
| sourcewardname | Source ward name | string | "Danapith" |
| sourcewardcode | Source ward code | string | "2401001" |
| geometry | Ward boundary polygon | GeoJSON | Polygon |

## AQI Fields

| Field | Description | Type | Example |
|-------|-------------|------|---------|
| Date | Day number (1-31) | int | 15 |
| 00:00:00 - 23:00:00 | Hourly AQI values | float | 142.0 |

## Station AQI Fields (Curated)

| Field | Description | Type | Source |
|-------|-------------|------|--------|
| station_name | Station name | string | "Chandkheda, Ahmedabad" |
| agency | Operating agency | string | "IITM" or "GPCB" |
| timestamp_local | Local timestamp | datetime | Excel date + hour |
| aqi | AQI value (US EPA standard) | float | Excel value; NaN = missing |
| source_file | Source filename | string | Original Excel filename |
| year | Year | string | "2025" |
| month | Month name | string | "January" |

## Station Metadata Fields

| Field | Description | Type | Source |
|-------|-------------|------|--------|
| station_name | Station name | string | CPCB |
| agency | Operating agency | string | CPCB/GPCB |
| latitude | Station latitude (deg N) | float | CPCB CAAQMS list |
| longitude | Station longitude (deg E) | float | CPCB CAAQMS list |
| spatial_level | STATION or CITY | string | "STATION" |
| coordinate_source | Source of coordinates | string | "CPCB CAAQMS All India list" |
| verification_status | Verification status | string | "VERIFIED CPCB" |
| available_months | Months with data | string | "January" |
| temporal_resolution | Data resolution | string | "hourly" |
| record_count | Total records | int | 744 |
| expected_record_count | Expected records | int | 744 |
| completeness_pct | Data completeness % | float | 99.7 |
| qc_status | QA status | string | "VALID" / "VALID_WITH_MISSING" / "QUARANTINED" |

## Station-Month QC Fields

| Field | Description | Type | Source |
|-------|-------------|------|--------|
| station_name | Station name | string | Derived |
| year | Year | string | Derived |
| month | Month name | string | Derived |
| expected_hours | Expected hours in month | int | Calendar |
| observed_hours | Hours with valid AQI | int | Count |
| missing_hours | Hours with missing AQI | int | Count |
| completeness_pct | Completeness percentage | float | observed/expected * 100 |
| min_aqi | Minimum AQI | float | Station-month |
| max_aqi | Maximum AQI | float | Station-month |
| mean_aqi | Mean AQI | float | Station-month |
| median_aqi | Median AQI | float | Station-month |
| p95_aqi | 95th percentile AQI | float | Station-month |
| max_consecutive_missing_hours | Longest consecutive gap | int | Gap analysis |
| max_gap_length_hours | Maximum gap length | int | Gap analysis |
| qc_status | QA classification | string | VALID/VALID_WITH_MISSING/QUARANTINED/INVALID |

## Staging Table: WeatherRecord

| Field | Description | Type | Source |
|-------|-------------|------|--------|
| station_id | Grid cell identifier | string | Derived |
| valid_time | Observation timestamp (UTC) | datetime | ERA5 valid_time |
| air_temperature | Temperature (C) | float | t2m - 273.15 |
| relative_humidity | Relative humidity (%) | float | Derived from t2m/d2m |
| wind_speed | Wind speed (m/s) | float | Derived from u10/v10 |
| mean_radiant_temperature | MRT (C) | float | Derived from ssrd/strd |
| data_source | Source identifier | string | "era5land" |

## Staging Table: AQIRecord

| Field | Description | Type | Source |
|-------|-------------|------|--------|
| timestamp | Observation time | datetime | Derived from Date + Hour |
| location_id | Location identifier | string | "ahmedabad_city" |
| aqi | AQI value | float | Excel value |
| source_id | Source identifier | string | "cpcb_ahmedabad_2025_MM" |
| quality_flag | QC flag | string | "VALID" or "MISSING" |

## Staging Table: WardBoundary

| Field | Description | Type | Source |
|-------|-------------|------|--------|
| ward_id | Ward identifier | string | ward_lgd_code |
| ward_name | Ward name | string | ward_lgd_name |
| ward_code | Administrative code | string | sourcewardcode |
| lgd_code | LGD code | string | ward_lgd_code |
| geometry | GeoJSON geometry | dict | geometry |
| centroid_lat | Centroid latitude | float | Derived |
| centroid_lon | Centroid longitude | float | Derived |
| crs | Coordinate system | string | "EPSG:4326" |

## HSRI Formula (unchanged)

```
HSRI = H x V x E
```

Where:
- **H** = Hazard index (0.0 to 1.0, derived from UTCI)
- **V** = Vulnerability index (0.33 to 1.0, from demographics)
- **E** = Exposure index (0.33 to 1.0, from environmental factors)

Risk thresholds:
- LOW: HSRI <= 0.33
- MEDIUM: 0.33 < HSRI <= 0.66
- HIGH: HSRI > 0.66
