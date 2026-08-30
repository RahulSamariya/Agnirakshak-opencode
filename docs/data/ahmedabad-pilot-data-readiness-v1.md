# Ahmedabad Pilot Data Readiness

## GO / NO-GO Assessment

### Can weather be processed?
**PARTIAL** - ERA5-Land sample available (March 2010 only). Need full-year data for operational use.

### Can population be processed?
**BLOCKED** - Census 2011 file (DDW_PCA2407_2011_MDDS) not found in repository.

### Can GIS be processed?
**PASS** - 48-ward GeoJSON with valid geometries available.

### Can AQI be processed?
**PARTIAL** - City-level hourly AQI available (Jan-May 2025). Missing some hours.

### Can Census be joined to current GIS?
**BLOCKED** - Ward count mismatch (57 vs 48). Crosswalk required.

### Can the available data support a common pilot period?
**NO** - No temporal overlap between ERA5 (2010), Census (2011), and AQI (2025).

### Is mortality available?
**NO** - Not provided.

### Is hospitalization available?
**NO** - Not provided.

## Overall Status: BLOCKED

### Blockers
1. **Census file missing** - Need DDW_PCA2407_2011_MDDS workbook
2. **Ward crosswalk required** - 57 Census wards vs 48 GIS wards
3. **Full-year ERA5 needed** - Current sample is only March 2010
4. **Health data missing** - Mortality/hospitalization not available

### Required Next Steps
1. Obtain Census 2011 workbook
2. Obtain 2011 ward boundary shapefile
3. Create Census-GIS crosswalk
4. Acquire full-year ERA5-Land data (2024 or 2025)
5. Obtain mortality/hospitalization data

### What Can Proceed
- GIS spatial analysis (48-ward geometry ready)
- ERA5 variable extraction (sample available)
- AQI preprocessing (city-level data available)

## Recommendation

**REQUIRES ACCESS / CROSSWALK**

Cannot proceed with ML training or scientific validation until:
1. Census data is obtained
2. Spatial crosswalk is established
3. Temporal alignment is achieved
