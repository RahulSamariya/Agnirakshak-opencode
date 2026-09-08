# Source Register: CPCB CAAQMS PM2.5 Data

**Last Updated:** 2026-09-08  
**Maintainer:** Agnirakshak Project Team

## Primary Data Sources

### 1. CPCB CAAQMS Comparison Data Portal

**Source URL:** `https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/caaqm-comparison-data`  
**Data Type:** PM2.5 concentration data (µg/m³)  
**Temporal Resolution:** Hourly  
**Coverage:** Ahmedabad, Gujarat, India  
**Access Method:** Browser session (requires authentication)  
**Status:** SOURCE_AVAILABLE, ACTUALLY_ACQUIRED (partial)

**Description:**
Central Pollution Control Board (CPCB) Continuous Ambient Air Quality Monitoring System (CAAQMS) comparison data portal. Provides real-time and historical PM2.5 concentration data from monitoring stations across India.

**Station Coverage:**
- 9 known Ahmedabad stations (site_308, site_5449-site_5456)
- Additional stations may exist (requires verification)

**Data Format:**
- Excel/CSV downloads from web interface
- Column headers include pollutant names with units (µg/m³)
- Timestamp format: YYYY-MM-DD HH:MM:SS

**Access Limitations:**
- Requires browser session authentication
- Angular SPA does not fully load in automated browsers
- Manual browser session required for initial authentication
- Rate limiting: 5 seconds between requests recommended

### 2. Existing Chandkheda PM2.5 Data

**File:** `raw_data_hourly_chandkheda,_ahmedabad_-_iitm_1H.csv`  
**Data Type:** PM2.5 concentration data (µg/m³)  
**Temporal Resolution:** Hourly  
**Coverage:** Chandkheda, Ahmedabad (site_5453)  
**Date Range:** 2026-01-01 to 2026-08-31 (8 months)  
**Records:** 5088 hourly observations  
**Status:** ACTUALLY_ACQUIRED

**Description:**
High-quality PM2.5 concentration data from Chandkheda monitoring station. Includes multiple pollutants (PM2.5, PM10, NO, NO2, NOx, NH3, SO2, CO, Ozone) and meteorological variables (AT, RH, WS, WD, RF, SR, BP).

**Data Quality:**
- Completeness: ~98%
- Missing values: ~88 records (1.7%)
- QC Status: VALID
- Units: µg/m³ (verified)

**Provenance:**
- Source: CPCB CAAQMS monitoring station
- Agency: IITM (Indian Institute of Tropical Meteorology)
- Location: Chandkheda, Ahmedabad
- Coordinates: 23.108°N, 72.5746°E

### 3. CPCB Station Metadata

**File:** `data/metadata/ahmedabad_cpcb_station_inventory.csv`  
**Data Type:** Station metadata  
**Coverage:** Ahmedabad monitoring stations  
**Status:** PARTIALLY_ACQUIRED

**Description:**
Metadata for Ahmedabad CPCB monitoring stations including station IDs, names, coordinates, and status information.

**Known Stations (9):**

| Station ID | Station Name | Agency | Coordinates |
|------------|--------------|--------|-------------|
| site_308 | Maninagar, Ahmedabad | GPCB | 23.0225°N, 72.5967°E |
| site_5449 | Sardar Vallabhbhai Patel Stadium | IITM | 23.0225°N, 72.5967°E |
| site_5450 | Gyaspur, Ahmedabad | IITM | 23.0225°N, 72.5967°E |
| site_5451 | Rakhial, Ahmedabad | IITM | 23.0225°N, 72.5967°E |
| site_5452 | Raikhad, Ahmedabad | IITM | 23.0225°N, 72.5967°E |
| site_5453 | Chandkheda, Ahmedabad | IITM | 23.108°N, 72.5746°E |
| site_5454 | SAC ISRO Bopal | IITM | 23.0225°N, 72.5967°E |
| site_5455 | SAC ISRO Satellite | IITM | 23.0225°N, 72.5967°E |
| site_5456 | SVPI Airport Hansol | IITM | 23.0225°N, 72.5967°E |

**Note:** Coordinates are estimated and should be verified through manual browser session.

## Data Processing Pipeline

### Raw Data Acquisition
1. Browser session to CPCB portal
2. Manual authentication (if required)
3. Station/parameter/date selection
4. Excel/CSV download
5. Raw file preservation with SHA-256 hash

### Data Normalization
1. Schema standardization
2. Unit verification (µg/m³)
3. Timestamp normalization
4. Missing value documentation

### Quality Control
1. Completeness check (expected vs observed hours)
2. Range validation (0-500 µg/m³)
3. Negative value detection
4. Statistical outlier identification

## Data Provenance

### Chandkheda Data (site_5453)

**Acquisition Date:** 2026-09-08  
**Source File:** `raw_data_hourly_chandkheda,_ahmedabad_-_iitm_1H.csv`  
**SHA-256:** [To be computed]  
**Retrieval Method:** Existing repository file  
**Validation Status:** VALID

**Provenance Chain:**
1. CPCB CAAQMS monitoring station (Chandkheda)
2. Data transmission to CPCB central server
3. Data processing and quality control
4. Publication on CPCB portal
5. Download to local repository
6. Validation and documentation

## Access Requirements

### Browser Session Authentication
- **URL:** `https://airquality.cpcb.gov.in/ccr/`
- **Authentication:** Session-based (cookies)
- **CAPTCHA:** May appear on first access
- **Rate Limiting:** 5 seconds between requests

### API Access
- **Endpoint:** Unknown (requires browser session capture)
- **Authentication:** Token-based (requires manual capture)
- **Documentation:** Not publicly available

## Data Usage Guidelines

1. **Attribution:** Credit CPCB as primary data source
2. **Citation:** Include retrieval date and version
3. **Quality Disclaimer:** Data may contain errors or gaps
4. **Update Frequency:** Check for data updates periodically
5. **License:** Government data (public domain in India)

## Contact Information

**CPCB:** Central Pollution Control Board, India  
**Website:** https://cpcb.nic.in  
**Data Portal:** https://airquality.cpcb.gov.in  

**Agnirakshak Project:**  
**Repository:** https://github.com/RahulSamariya/Agnirakshak-opencode  
**Branch:** Rahul

---

**Register Version:** 1.0  
**Last Reviewed:** 2026-09-08  
**Next Review:** After manual browser session completion