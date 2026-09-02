# Spatial Strategy: Ward Geography Reconciliation & Grid-to-Ward Aggregation

**Version:** 1.0
**Date:** 2026-09-02
**Status:** METHODOLOGY STUDY — NO IMPLEMENTATION YET

---

## 1. Ahmedabad Ward Geography Reconciliation

### 1.1 Known Facts

| Fact | Status | Source |
|------|--------|--------|
| Census 2011 AMC has 57 wards (IDs 1–57) | VERIFIED | `data/staging/census/wards_census_2011_amc.csv` (57 rows) |
| Current AMC operational wards = 48 | VERIFIED | `data/raw/gis/wards_ahmedabad.geojson` (48 features); AMC website; Indian Express 2015 |
| Ward reduction: 57 → 48 via SEC delimitation order, May 2015 | VERIFIED | Indian Express (2015-05-29): "Delimitation order announced: Ahmedabad to have 48 wards" |
| No official Census 2011 → current 48 ward crosswalk exists in repository | VERIFIED | Repository inspection |
| No authoritative 2011 ward boundary GIS exists in repository | VERIFIED | Only 48-ward (2024) GIS present |

### 1.2 Ward ID Schemes

**Census 2011 (57 wards):**
- ID: `census_ward_id` (integer 1–57)
- Name format: `Ahmadabad (M Corp.) WARD NO.-0001` through `WARD NO.-0057`
- Source: `DDW_PCA2407_2011_MDDS with UI (1).xlsx`, sheet `EB-2407`

**Current 48-ward GIS:**
- `sourcewardcode`: AMC ward number (e.g., "12", "48")
- `ward_lgd_code`: LGD code (e.g., 1302512)
- `ward_lgd_name`: e.g., `Naroda, Ahmedabad (M.Corp.) Ward No. 12`
- CRS: EPSG:4326

### 1.3 Crosswalk Status

**CASE 3 applies: Neither authoritative historical geometry nor an authoritative crosswalk can be established.**

Reasons:
1. The 2015 SEC delimitation merged/split/reorganized wards; the exact mapping is not documented in a machine-readable crosswalk.
2. Ward names changed (e.g., current ward names like "Gota", "Chandlodiya" don't directly map to Census 2011 names).
3. Many-to-one mapping (multiple Census wards → single current ward) is common but the exact geometry is unknown.
4. Do NOT infer crosswalk from ward names alone.
5. Do NOT manufacture overlaps based on approximate visual matching.

### 1.4 Authoritative Sources Identified

| Source | URL | Evidence Type | Status |
|--------|-----|---------------|--------|
| NYU Spatial Data Repository (Princeton) | `geo.nyu.edu/catalog/princeton-9c67wr21b` | Shapefile, restricted access | UNVERIFIED — may contain 2011 ward boundaries |
| DataMeet Municipal Spatial Data | `github.com/datameet/Municipal_Spatial_Data` | GeoJSON, CC-BY-4.0 | UNVERIFIED — may be 2011 or later |
| OpenCity / Oorvani Foundation | `data.opencity.in` | KML, ODbL-1.0 | VERIFIED — 48 wards (2024 delimitation) |
| BharatAtlas | `bharatlas.com/view/wards_ahmedabad` | GeoJSON/Parquet, ODbL-1.0 | VERIFIED — 48 wards (2024) |
| Gujarat State Election Commission | Official delimitation orders | Official documentation | UNVERIFIED — may contain ward mapping |
| Census of India | `censusindia.gov.in` | PCA data only | NO geometry at ward level |

### 1.5 Recommended Geography Strategy

**Historical analysis geography:** Census 2011 57-ward PCA data (demographics, literacy, work status) — retained on original 57-ward geography.

**Operational/current geography:** 48-ward GIS from OpenCity/AMC — used for current risk assessment.

**Allowed transformation:** NONE until an authoritative crosswalk is established.

**Limitations:**
- Census 2011 ward-level demographics cannot be defensibly assigned to current 48 wards without a crosswalk.
- Any crosswalk would need to be validated against the 2015 SEC delimitation order.

**Condition for current-48 ward vulnerability:**
- BLOCKED until either:
  (a) Authoritative 2011 ward boundary GIS is acquired (e.g., from NYU/Princeton or DataMeet), OR
  (b) Authoritative SEC 2015 delimitation order with ward mapping is acquired.

**Clean fallback:** Retain vulnerability on historical Census 57-ward geography rather than inventing a transformation.

---

## 2. ERA5 Grid → Ward Aggregation

### 2.1 ERA5 Grid Structure

| Product | Resolution | Grid Size | Cell Footprint | CRS |
|---------|-----------|-----------|----------------|-----|
| ERA5-Land | 0.10° | 5×5 = 25 cells | ~114 km² | WGS84/EPSG:4326 |
| ERA5 reanalysis | 0.25° | 3×4 = 12 cells | ~714 km² | WGS84/EPSG:4326 |
| ERA5-HEAT | 0.25° | 3×4 = 12 cells | ~714 km² | WGS84/EPSG:4326 |

- Latitude: descending (north to south), spacing 0.10° or 0.25°
- Longitude: ascending (west to east), spacing 0.10° or 0.25°
- Cell bounds: constructed programmatically (center ± half-spacing)
- 11 of 12 ERA5 0.25° cells intersect Ahmedabad ward polygons

### 2.2 Recommended Aggregation Method

**Primary method: Area-weighted intersection** (Schwarzwald & Geil 2024, xagg; Auffhammer et al. 2013)

For each ward polygon and each ERA5 grid cell:
1. Compute intersection polygon area
2. Weight = (intersection area) / (total ward area)
3. Ward value = Σ(weight_i × grid_cell_value_i)

This is the peer-reviewed standard for climate-health impact assessment (Weighted Climate Dataset, Nature 2024).

**When to aggregate:** At the MRT/UTCI level, NOT at H level. Aggregating an already-normalized index loses physical meaning. Aggregate raw MRT or UTCI, then compute H from the ward-level aggregate.

**For peak thermal stress:** Compute daily maximum H per grid cell, then area-weight to ward.

### 2.3 Edge Cases

- **Partial grid-cell overlap:** Handled by area-weighted intersection (fractional weights)
- **Coastal/river cells:** No Ahmedabad wards are coastal; Sabarmati river runs through but doesn't create water-only cells within city limits
- **Invalid geometries:** Validate with `geopandas.GeoSeries.is_valid` before aggregation
- **Missing grid cells:** If a ward has no overlapping ERA5 cell, flag as UNAVAILABLE
- **Ward spanning multiple cells:** Area-weighted mean handles this correctly
- **No-overlap wards:** If ward polygon doesn't intersect any ERA5 cell, mark as NO_DATA
- **Time aggregation:** 6-hourly → daily maximum for H; 6-hourly → daily mean for mean UTCI

### 2.4 QA Rules for Ward Aggregation

- Weights must sum to ≈1.0 (tolerance 0.01) for each ward
- No negative weights
- No duplicated cell contributions
- CRS must be consistent (all WGS84/EPSG:4326)
- Missing source cells → flag ward as INCOMPLETE
- Reproducibility: fixed ERA5 grid, fixed ward polygons, deterministic intersection

---

## 3. Decision Matrix

| Question | Evidence | Decision | Status | Blocking Issue |
|----------|----------|----------|--------|----------------|
| Can 2011 57-ward data map to current 48 wards? | No authoritative crosswalk exists | BLOCKED | Not implemented | Need SEC 2015 delimitation order or 2011 ward GIS |
| Is there authoritative 2011 ward geometry? | NYU/Princeton may have it; DataMeet uncertain | UNVERIFIED | Need to acquire | Restricted access at NYU |
| What aggregation method for ERA5→ward? | Peer-reviewed literature supports area-weighted intersection | DECIDED | Ready to implement | None |
| When should aggregation occur? | Literature says aggregate at physical level, not index level | DECIDED | Ready to implement | None |
| Current-48 ward vulnerability from 2011 Census? | No crosswalk | BLOCKED | Cannot implement | Need crosswalk or use 57-ward geography |

---

## 4. CPCB/GPCB Station AQI → Current 48 Ward Coverage

### 4.1 Station Inventory

9 Ahmedabad stations with authoritative CPCB coordinates:

| Station | Agency | Lat | Lon | CPCB Code | Ward Inside |
|---------|--------|-----|-----|-----------|-------------|
| Chandkheda | IITM | 23.1080 | 72.5746 | #5453 | Ward 3 |
| Gyaspur | IITM | 22.9771 | 72.5530 | #5450 | Ward 35 |
| Maninagar | GPCB | 23.0027 | 72.5919 | #308 | Ward 36 |
| Raikhad | IITM | 23.0205 | 72.5793 | #5452 | Ward 29 |
| Rakhial | IITM | 23.0168 | 72.6258 | #5451 | Ward 39 |
| SAC ISRO Bopal | IITM | 23.0411 | 72.4567 | #5454 | — |
| SAC ISRO Satellite | IITM | 23.0234 | 72.5152 | #5455 | Ward 20 |
| SVPI Airport Hansol | IITM | 23.0768 | 72.6279 | #5456 | — |
| SVP Stadium | IITM | 23.0431 | 72.5630 | #5449 | Ward 10 |

Source: CPCB CAAQMS All India list (cpcbccr.com/pdf/caaqms_list_All_India.pdf)

### 4.2 Ward Coverage Summary

| Classification | Count | % |
|---------------|-------|---|
| DIRECT (station inside ward) | 7 | 14.6% |
| NEAR_2KM (0–2 km) | 11 | 22.9% |
| NEAR_5KM (2–5 km) | 26 | 54.2% |
| FAR (>5 km) | 4 | 8.3% |
| **Total** | **48** | **100%** |

- Average nearest station distance: 2.54 km
- Maximum nearest station distance: 6.67 km (Ward 47)
- 4 wards >5 km from any station: Wards 1, 24, 47, 48

### 4.3 Spatial Representativeness Assessment

**Strengths:**
- 37.5% of wards (7 direct + 11 near_2km) have strong station coverage within 2 km
- 91.7% of wards (7+11+26) have station coverage within 5 km
- All stations verified by CPCB with authoritative coordinates
- Station density: 0.188 stations/ward

**Limitations:**
- 8.3% of wards (4) are >5 km from any station (poorly represented)
- Station network is biased toward central/north Ahmedabad
- January-only data; seasonal representativeness unknown
- Ward-level AQI BLOCKED_PENDING_ACQUISITION (Feb–May station files not acquired)

### 4.4 Recommended Station-to-Ward Aggregation

**For E computation:** Use nearest-station assignment for wards within 3 km; flag wards >3 km as having limited representativeness.

**DO NOT** interpolate AQI across wards without a defensible spatial method. Current recommendation: assign station AQI to the containing ward, and nearest-station AQI to nearby wards.

**Next step:** Choose and document a defensible station-to-current-48-ward spatial aggregation method before creating E.
