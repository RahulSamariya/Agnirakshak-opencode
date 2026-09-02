# Unresolved Data Gaps

**Version:** 1.0
**Date:** 2026-09-02

---

## Critical Gaps (BLOCKING)

| # | Gap | Impact | Resolution Path | Status |
|---|-----|--------|-----------------|--------|
| 1 | **No Census 2011 → current 48 ward crosswalk** | Cannot assign Census 2011 demographics to current 48 wards | Acquire SEC 2015 delimitation order with ward mapping, or acquire 2011 ward boundary GIS | BLOCKED |
| 2 | **No 2011 ward boundary geometry** | Cannot spatially join Census 2011 PCA to current wards | Acquire from NYU/Princeton (restricted) or DataMeet (unverified year) | BLOCKED |
| 3 | **Mortality/hospitalization health targets** | Cannot train or validate health-outcome ML models | Data remains restricted by government; must not be fabricated | BLOCKED (by design) |

## Moderate Gaps (AFFECTING V/E)

| # | Gap | Impact | Resolution Path | Status |
|---|-----|--------|-----------------|--------|
| 4 | **No ward-level AQI data** | Cannot compute ward-level air_quality exposure factor | Acquire station-level AQI for Ahmedabad; use spatial interpolation if multiple stations exist | **PARTIALLY RESOLVED** — 9 station-level AQI series acquired (Jan 2025 only); Feb–May station files not locally acquired; station→ward coverage assessed (7 DIRECT, 11 NEAR_2KM, 26 NEAR_5KM, 4 FAR); ward-level AQI BLOCKED_PENDING_ACQUISITION |
| 5 | **No ward-level occupation data** | Cannot compute outdoor_worker_share for E | Census 2011 has worker classification at ward level (TOT_WORK, MAINWORK, MARGWORK) but not outdoor vs indoor distinction | PARTIALLY Available |
| 6 | **No ward-level housing quality data** | Cannot assess housing vulnerability | Census 2011 HH data available but limited; no cooling access, construction material at ward level | PARTIALLY Available |
| 7 | **No ward-level healthcare access data** | Cannot assess healthcare_accessibility for E | Facility locations exist in GIS (AMC Facilities.kml) but not processed to ward-level distance metrics | UNRESOLVED |
| 8 | **No current population estimates** | Census 2011 is 15 years old | Use Census 2011 as baseline; note temporal limitation | ACCEPTED LIMITATION |

## Minor Gaps (NON-BLOCKING)

| # | Gap | Impact | Resolution Path | Status |
|---|-----|--------|-----------------|--------|
| 9 | **BBWM weights not scientifically validated** | Current V/E weights may not reflect Ahmedabad-specific expert judgment | Conduct expert elicitation survey or use literature-derived weights | UNVALIDATED |
| 10 | **No NDVI/urban heat island data at ward level** | Could improve exposure assessment | Acquire Landsat/Sentinel LST data | NICE-TO-HAVE |
| 11 | **ERA5 grid resolution (0.25°) is coarse** | Each grid cell ~714 km², ward ~10-20 km² | Area-weighted intersection handles this; ERA5-Land (0.1°) available as alternative | ACCEPTED LIMITATION |
