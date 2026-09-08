# CPCB CAAQMS PM2.5 Acquisition Test Report

**Station:** Chandkheda, Ahmedabad (`site_5453`)  
**Date Range Tested:** 2026-01-01 to 2026-01-03  
**Test Date:** 2026-09-08  
**Status:** BROWSER_SESSION_REQUIRED

## Executive Summary

The CPCB CAAQMS comparison-data API **requires browser session authentication** with time-based tokens. Direct HTTP requests without authentication return 405 errors. No PM2.5 concentration data (µg/m³) is accessible via public APIs without authentication.

## Decision

**BROWSER_SESSION_REQUIRED**

The API is protected by:
1. Time-based authentication tokens (base64 encoded)
2. CORS restrictions (origin: `https://airquality.cpcb.gov.in`)
3. SSL certificate validation (self-signed cert in chain)

## Investigation Results

### 1. API Endpoints Tested

| Endpoint | Method | Status | Result |
|----------|--------|--------|--------|
| `/ccr/caaqm-comparison-data/caaqm-comparison-data` | POST | 405 | Requires authentication token |
| `/ccr/caaqm-comparison-data/getStationList` | GET | 200 | Returns HTML (Angular SPA) |
| `api.data.gov.in` | GET | Timeout | Rate-limited or requires API key |
| `api.openaq.org/v3/measurements` | GET | 401 | Requires OpenAQ API key |

### 2. Authentication Token System

The CPCB API uses a time-based authentication token:

```python
# Token generation (conceptual)
import base64, time, datetime

# Token payload
token_data = {
    "time": int(time.time()),
    "timeZoneOffset": int((datetime.utcnow() - datetime.now()).total_seconds() / 60)
}

# Base64 encode
access_token = base64.b64encode(str(token_data).encode()).decode()
# Result: "eyJ0aW1lIjoxNjcyNTM0NDAwLCJ0aW1lWm9uZU9mZnNldCI6MzMwfQ=="
```

**Headers required:**
```
accept: application/json, text/javascript, */*; q=0.01
accesstoken: <base64_encoded_token>
content-type: application/x-www-form-urlencoded; charset=UTF-8
origin: https://airquality.cpcb.gov.in
referer: https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/caaqm-comparison-data
```

### 3. Request Payload Structure

```json
{
  "draw": 1,
  "columns": [{"data": 0, "name": "", "searchable": true, "orderable": false}],
  "order": [],
  "start": 0,
  "length": 50,
  "search": {"value": "", "regex": false},
  "filtersToApply": {
    "parameter_list": [{"id": 0, "itemName": "PM2.5", "itemValue": "parameter_193"}],
    "criteria": "24 Hours",
    "reportFormat": "Tabular",
    "fromDate": "01-01-2026 T00:00:00Z",
    "toDate": "03-01-2026 T23:59:59Z",
    "state": "Gujarat",
    "city": "Ahmedabad",
    "station": "site_5453",
    "parameter": ["parameter_193"],
    "parameterNames": ["PM2.5"]
  },
  "pagination": 1
}
```

### 4. Existing File Analysis

**File:** `aqi_hourly_station_level_chandkheda,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx`

| Property | Value |
|----------|-------|
| Rows | 31 (days in January) |
| Columns | 25 (Date + 24 hourly columns) |
| Value Range | 71-177 |
| Mean | 101.1 |
| Units | Not specified |
| Pollutant | Not labeled |

**Interpretation:** Values are **AQI sub-index** (0-500 scale), not PM2.5 concentration (µg/m³). AQI values are calculated from concentrations using breakpoints, but the reverse calculation is not straightforward.

## CAPTCHA Detection

- **Detected:** No
- **Type:** None
- **Notes:** No CAPTCHA on page load, but API requires authentication token

## Alternative Data Sources

| Source | Status | Notes |
|--------|--------|-------|
| data.gov.in | Requires API key | Public key rate-limited |
| OpenAQ | Requires API key | Free registration at openaq.org |
| CPCB data.gov.in portal | Limited | Returns AQI, not concentration |
| State PCB websites | Varied | Gujarat PCB may have data |

## Smallest Manual Step

1. Open browser to: `https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/caaqm-comparison-data`
2. Navigate to Gujarat → Ahmedabad → Chandkheda
3. Select PM2.5 parameter and date range
4. Click "Submit"
5. Download Excel file from results

**Estimated time:** 2-3 minutes per station per month

## Automation Approach

To fully automate, implement Selenium-based scraper:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Navigate to page
driver.get("https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing")

# 2. Select state/city/station via dropdowns
# 3. Select PM2.5 parameter
# 4. Set date range
# 5. Click Submit
# 6. Wait for results
# 7. Click Excel download button
# 8. Parse downloaded file
```

## Files Generated

- `data/raw/aqi/cpcb_caaqms_endpoint_test.json` - Complete API test results
- `scripts/test_cpcb_methods.py` - API testing script
- `scripts/test_cpcb_api.py` - Initial API test (SSL bypass)
- `scripts/test_cpcb_api_ssl.py` - API test with SSL verification disabled

## Recommendation

**For immediate needs:** Use manual download from CPCB portal (2-3 min/station/month)

**For automation:** Implement Selenium-based scraper with:
- Token refresh mechanism
- Session management
- Rate limiting (1 request per 5 seconds)
- Error handling for SSL/authentication failures

**For data acquisition:** Consider OpenAQ API with free API key for historical PM2.5 data

## Conclusion

The CPCB CAAQMS PM2.5 concentration data **requires browser session authentication**. Direct API access is not possible without implementing the token-based authentication system. For production use, either:
1. Implement Selenium scraper with authentication
2. Use OpenAQ API with API key
3. Manual download from CPCB portal

---

**Report Version:** 1.0  
**Generated:** 2026-09-08  
**Next Review:** When API access requirements change