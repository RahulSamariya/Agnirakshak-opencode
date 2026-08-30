# Source Register

**Last Updated**: 2026-08-30

## Active Sources

### 1. ERA5-Land (Weather)
- **Provider**: ECMWF Copernicus Climate Data Store
- **Dataset**: ERA5-Land hourly aggregation
- **URL**: https://cds.climate.copernicus.eu/
- **Format**: NetCDF (`.nc`)
- **Coverage**: Ahmedabad, March 2010 (124 timesteps)
- **Variables**: 2m_temp, 2m_dewpoint, 10m_u_component, 10m_v_component, surface_pressure, surface_solar_radiation_downwards, total_precipitation
- **Resolution**: 0.1° x 0.1° (~9km)
- **License**: CC-BY-4.0
- **File**: `data/raw/weather/data_0.nc`
- **SHA256**: Recorded in `data/metadata/provenance-manifest.json`
- **Status**: READY

### 2. Census of India 2011 (Population)
- **Provider**: Office of the Registrar General & Census Commissioner, India
- **URL**: https://censusindia.gov.in/
- **Format**: Excel (`.xlsx`)
- **Coverage**: Ahmedabad district (code 474), 57 AMC wards
- **Fields**: Population, gender, age, literacy, workers, households
- **License**: Open Government License - India
- **File**: `data/raw/census/DDW_PCA2407_2011_MDDS with UI (1).xlsx`
- **SHA256**: Recorded in `data/metadata/provenance-manifest.json`
- **Status**: READY

### 3. GIS Ward Boundaries
- **Provider**: Ahmedabad Municipal Corporation / Survey of India
- **Format**: GeoJSON (`.geojson`)
- **Coverage**: 48 current AMC wards
- **CRS**: EPSG:4326 (WGS84)
- **Coordinate Order**: Raw = [lat, lon]; Normalized = [lon, lat]
- **License**: Government
- **File (raw)**: `data/raw/gis/wards_ahmedabad.geojson`
- **File (normalized)**: `data/staging/gis/wards_ahmedabad_epsg4326_normalized.geojson`
- **SHA256**: Recorded in `data/metadata/provenance-manifest.json`
- **Status**: READY

### 4. AQI (Air Quality Index)
- **Provider**: Central Pollution Control Board (CPCB)
- **Format**: Excel (`.xlsx`)
- **Coverage**: Ahmedabad city-level, January–May 2025
- **Files**: 5 monthly files (131–152 rows each, 24 hourly columns)
- **License**: Government
- **Directory**: `data/raw/aqi/`
- **SHA256**: Per-file hashes in `data/metadata/provenance-manifest.json`
- **Status**: PARTIAL (city-level only, no ward-level breakdown)

## Unavailable Sources

### 5. Mortality Data
- **Status**: BLOCKED
- **Required for**: Vulnerability model calibration
- **Action needed**: Request from Gujarat DHS / AMC

### 6. Hospitalization Data
- **Status**: BLOCKED
- **Required for**: Vulnerability model calibration
- **Action needed**: Request from Gujarat DHS / AMC

### 7. IMDAA Reanalysis
- **Status**: NOT ACCESSED
- **Action needed**: Register at https://imdaa.imd.gov.in/

### 8. Population Census 2024
- **Status**: NOT AVAILABLE
- **Action needed**: Use 2011 Census as proxy with caution
