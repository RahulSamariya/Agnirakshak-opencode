# Unresolved Data Gaps

**Last Updated:** 2026-09-08  
**Maintainer:** Agnirakshak Project Team

## Critical Gaps

### 1. Browser Automation Angular SPA Loading

**Gap:** Selenium-based browser automation cannot fully initialize the CPCB Angular SPA  
**Impact:** HIGH - Prevents automated data acquisition  
**Status:** UNRESOLVED  
**Priority:** CRITICAL

**Description:**
The CPCB CAAQMS comparison data portal uses an Angular single-page application (SPA) that does not fully load in automated browser sessions. The page loads (258KB HTML) but the Angular router redirects to the root URL (`/ccr/#/`), and form elements are not interactable.

**Evidence:**
- Page loads but URL redirects to root
- Angular elements found (`<router-outlet>`) but content not rendered
- Menu items visible but not interactable (no size/location)
- Dropdown elements not found in DOM

**Root Causes (Hypothesized):**
1. Angular lazy loading requires specific navigation path
2. JavaScript execution issues in automated browsers
3. Session initialization requirements not met
4. Anti-bot detection mechanisms

**Recommended Actions:**
1. Manual browser session to capture API endpoints
2. Analyze network requests for authentication tokens
3. Investigate Angular application initialization requirements
4. Consider alternative automation frameworks (Playwright, Puppeteer)

### 2. Complete Ahmedabad Station Inventory

**Gap:** Unknown if all Ahmedabad stations are documented  
**Impact:** MEDIUM - May miss stations with PM2.5 data  
**Status:** PARTIALLY_RESOLVED  
**Priority:** HIGH

**Description:**
Currently documented 9 Ahmedabad stations, but the complete inventory is unknown. Additional stations may exist that are not in the current list.

**Current Known Stations (9):**
- site_308 (Maninagar)
- site_5449 (SVP Stadium)
- site_5450 (Gyaspur)
- site_5451 (Rakhial)
- site_5452 (Raikhad)
- site_5453 (Chandkheda)
- site_5454 (SAC ISRO Bopal)
- site_5455 (SAC ISRO Satellite)
- site_5456 (SVPI Airport Hansol)

**Recommended Actions:**
1. Manual browser session to verify complete station list
2. Check CPCB portal for additional stations
3. Cross-reference with other data sources (OpenAQ, data.gov.in)

### 3. Station Coordinates Verification

**Gap:** Station coordinates are estimated, not verified  
**Impact:** LOW - Does not affect PM2.5 data acquisition  
**Status:** UNRESOLVED  
**Priority:** MEDIUM

**Description:**
Station coordinates in the metadata file are estimated based on general Ahmedabad location. Exact coordinates from CPCB or authoritative sources are needed for spatial analysis.

**Recommended Actions:**
1. Extract coordinates from CPCB portal during manual session
2. Verify against Google Maps or other mapping services
3. Update metadata file with verified coordinates

### 4. Multi-Station PM2.5 Data Acquisition

**Gap:** Only Chandkheda station has complete PM2.5 data  
**Impact:** HIGH - Limits model development to single station  
**Status:** UNRESOLVED  
**Priority:** HIGH

**Description:**
The repository contains PM2.5 data for only one station (Chandkheda, site_5453). Data for other Ahmedabad stations is not available, limiting the ability to develop a city-wide PM2.5 estimation model.

**Current Data Coverage:**
- Chandkheda (site_5453): 5088 hourly records (Jan-Aug 2026)
- Other 8 stations: No PM2.5 data in repository

**Recommended Actions:**
1. Manual browser session to acquire data for all stations
2. Determine available date ranges for each station
3. Acquire longest practical continuous period
4. Document data availability and completeness

### 5. Date Range Completeness

**Gap:** Unknown if January-August 2026 is complete for all stations  
**Impact:** MEDIUM - May affect temporal analysis  
**Status:** UNRESOLVED  
**Priority:** MEDIUM

**Description:**
The Chandkheda data covers January-August 2026, but it's unknown if this period is complete or if there are gaps. Other stations may have different date ranges.

**Recommended Actions:**
1. Analyze existing data for gaps and completeness
2. Determine actual date ranges for each station
3. Document missing periods and their impact

## Technical Gaps

### 1. Authentication Token Capture

**Gap:** CPCB API authentication tokens not captured  
**Impact:** HIGH - Prevents direct API access  
**Status:** UNRESOLVED  
**Priority:** HIGH

**Description:**
The CPCB API requires authentication tokens that are generated during browser sessions. These tokens have not been captured, preventing direct API access without browser automation.

**Recommended Actions:**
1. Manual browser session to capture network requests
2. Identify authentication token format and generation
3. Implement token refresh mechanism
4. Test direct API access with captured tokens

### 2. CAPTCHA Handling

**Gap:** CAPTCHA appearance and handling not documented  
**Impact:** MEDIUM - May block automated access  
**Status:** UNRESOLVED  
**Priority:** MEDIUM

**Description:**
The CPCB portal may display CAPTCHA challenges during browser sessions. The appearance, type, and handling of these CAPTCHAs are not documented.

**Recommended Actions:**
1. Manual browser session to document CAPTCHA behavior
2. Determine if CAPTCHA appears on first access or periodically
3. Document CAPTCHA type and difficulty
4. Implement manual CAPTCHA intervention if needed

### 3. Rate Limiting Documentation

**Gap:** Exact rate limits not documented  
**Impact:** LOW - Can use conservative rate limiting  
**Status:** PARTIALLY_RESOLVED  
**Priority:** LOW

**Description:**
The CPCB portal may have rate limiting to prevent abuse. The exact limits are not documented, but conservative 5-second delays are recommended.

**Current Mitigation:**
- 5-second delay between requests
- Retry logic with exponential backoff
- Session renewal when needed

**Recommended Actions:**
1. Test rate limits with controlled requests
2. Document actual limits and penalties
3. Optimize acquisition speed while respecting limits

## Data Quality Gaps

### 1. PM2.5 Data Validation

**Gap:** Existing Chandkheda data not fully validated against CPCB portal  
**Impact:** MEDIUM - May contain errors or inconsistencies  
**Status:** UNRESOLVED  
**Priority:** MEDIUM

**Description:**
The existing Chandkheda data file has been analyzed but not validated against the CPCB portal to confirm accuracy and completeness.

**Recommended Actions:**
1. Manual browser session to verify Chandkheda data
2. Compare values with portal display
3. Check for any discrepancies or errors
4. Update validation status

### 2. Missing Value Documentation

**Gap:** Missing values not documented with reasons  
**Impact:** LOW - Does not affect data usability  
**Status:** UNRESOLVED  
**Priority:** LOW

**Description:**
The Chandkheda data contains approximately 88 missing values (1.7%), but the reasons for these gaps are not documented (e.g., equipment maintenance, data transmission issues).

**Recommended Actions:**
1. Document missing value patterns
2. Investigate potential causes
3. Assess impact on analysis
4. Consider imputation strategies if needed

## Documentation Gaps

### 1. API Documentation

**Gap:** CPCB API documentation not available  
**Impact:** MEDIUM - Limits automation development  
**Status:** UNRESOLVED  
**Priority:** MEDIUM

**Description:**
The CPCB API endpoints, parameters, and authentication methods are not publicly documented. This limits the ability to develop robust automation.

**Recommended Actions:**
1. Reverse-engineer API from browser network requests
2. Document discovered endpoints and parameters
3. Create internal API documentation
4. Share findings with community (if permitted)

### 2. Data Format Specification

**Gap:** Exact data format specification not available  
**Impact:** LOW - Can infer from existing data  
**Status:** PARTIALLY_RESOLVED  
**Priority:** LOW

**Description:**
The exact data format specification (column names, units, timestamp format) is not formally documented, but can be inferred from existing data files.

**Current Understanding:**
- Column headers include pollutant names with units (µg/m³)
- Timestamp format: YYYY-MM-DD HH:MM:SS
- Multiple pollutants in single file
- Meteorological variables included

## Resolution Timeline

### Immediate (This Week)
1. Manual browser session to capture API endpoints
2. Verify complete Ahmedabad station inventory
3. Validate existing Chandkheda data

### Short-term (Next 2 Weeks)
1. Acquire PM2.5 data for all Ahmedabad stations
2. Document API endpoints and authentication
3. Complete station coordinates verification

### Medium-term (Next Month)
1. Implement token-based API access
2. Complete multi-station data acquisition
3. Finalize data quality assessment

### Long-term (Next Quarter)
1. Optimize automation pipeline
2. Implement automated data updates
3. Extend to other cities/stations

## Impact Assessment

### On PM2.5 Estimation Model
- **Single Station Limitation:** Model can only be developed for Chandkheda initially
- **Temporal Coverage:** 8 months of data may be sufficient for initial model
- **Data Quality:** High-quality data available for model development

### On Project Timeline
- **Delay:** Manual browser sessions add 1-2 weeks to data acquisition phase
- **Mitigation:** Can proceed with Chandkheda data while acquiring other stations
- **Risk:** Low - existing data provides solid foundation

### On Scalability
- **Manual Intervention:** Required for initial setup but not ongoing operations
- **Automation Potential:** High once API endpoints are captured
- **Maintenance:** Low once pipeline is established

## Recommendations

1. **Proceed with Chandkheda Data:** Use existing high-quality data for initial model development
2. **Manual Browser Session:** Complete within 1 week to capture API endpoints
3. **Gradual Expansion:** Acquire additional stations incrementally
4. **Documentation First:** Document all findings before expanding automation

---

**Gap Register Version:** 1.0  
**Last Reviewed:** 2026-09-08  
**Next Review:** After manual browser session completion