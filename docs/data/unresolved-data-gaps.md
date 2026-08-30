# Unresolved Data Gaps

**Last Updated**: 2026-08-30

## Critical Gaps

### 1. Ward Crosswalk (2011 → 2024)
- **Impact**: HIGH — Cannot join Census demographics to current ward boundaries
- **Census 2011**: 57 AMC wards
- **Current GIS**: 48 AMC wards
- **Action needed**: Obtain 2011 ward shapefile or AMC crosswalk table
- **Workaround**: None (direct join would lose/merge wards)

### 2. Mortality Data
- **Impact**: HIGH — Vulnerability model cannot be calibrated
- **Action needed**: Request from Gujarat Directorate of Health Services
- **Workaround**: Use synthetic placeholder (BLOCKED by policy)

### 3. Hospitalization Data
- **Impact**: HIGH — Vulnerability model cannot be calibrated
- **Action needed**: Request from Gujarat DHS / AMC hospitals
- **Workaround**: Use synthetic placeholder (BLOCKED by policy)

### 4. IMDAA Reanalysis
- **Impact**: MEDIUM — Alternative to ERA5-Land for Indian conditions
- **Action needed**: Register at https://imdaa.imd.gov.in/
- **Workaround**: ERA5-Land sufficient for initial profiling

### 5. Population Census 2024
- **Impact**: MEDIUM — 2011 Census is 15 years old
- **Action needed**: None (not yet released)
- **Workaround**: Use 2011 Census with caution; document as known limitation

## Minor Gaps

### 6. Full-Year ERA5
- **Impact**: LOW — Current sample is March 2010 only (124 timesteps)
- **Action needed**: Download full-year 2010 or multi-year data
- **Workaround**: Sufficient for profiling; needed for operational pipeline

### 7. AQI Ward-Level
- **Impact**: LOW — City-level AQI applied uniformly
- **Action needed**: Obtain station-level AQI with coordinates
- **Workaround**: City-level average is reasonable for pilot

## Resolved Gaps

### ~~Census File Missing~~
- **Resolution**: Found in `C:\Users\DELL\Downloads\`, copied to `data/raw/census/`
- **Date resolved**: 2026-08-30
