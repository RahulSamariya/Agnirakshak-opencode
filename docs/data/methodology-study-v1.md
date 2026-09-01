# Methodology Study: Ahmedabad Ward-Level Deterministic Risk Layer

**Version:** 1.0
**Date:** 2026-09-02
**Status:** COMPLETE — METHODOLOGY DECISION PACKAGE
**Scope:** Source-backed methodology study for V, E, HSRI. No implementation.

---

## Executive Summary

This study determines what can be implemented next for the Agnirakshak ward-level deterministic risk layer and what remains blocked. The multiplicative HSRI = H × V × E formulation is retained as the default. Current-48 ward vulnerability from Census 2011 is **BLOCKED** due to missing crosswalk. V and E variable selection is documented below with literature support. BBWM weights are **UNVALIDATED** and must be re-elicited.

---

## PART A: Census 2011 Wards vs Current 48 AMC Wards

### Finding: CASE 3 — No authoritative crosswalk or 2011 geometry available

| Item | Finding |
|------|---------|
| Census 2011 wards | 57 AMC wards, IDs 1–57, in `data/staging/census/wards_census_2011_amc.csv` |
| Current GIS | 48 wards, 2024 delimitation, in `data/raw/gis/wards_ahmedabad.geojson` |
| Reduction mechanism | Gujarat SEC delimitation order, May 2015 (Indian Express 2015-05-29) |
| Crosswalk | NOT found in repository or authoritative online sources |
| 2011 ward geometry | NOT found; NYU/Princeton may have it (restricted access) |

**Authoritative sources evaluated:**
- AMC official website → confirms 48 wards, no crosswalk
- Census of India → PCA data only, no ward boundary GIS
- Gujarat SEC → delimitation order exists but not machine-readable
- NYU Spatial Data Repository → restricted access, may contain 2011 shapefile
- DataMeet GitHub → ward geometry available but year unclear
- OpenCity/BharatAtlas → 2024 delimitation only

**Decision:** Retain vulnerability on Census 2011 57-ward geography. Do NOT map to current 48 wards.

**Next step:** Attempt to acquire NYU/Princeton 2011 ward shapefile (requires access request) or Gujarat SEC delimitation order.

---

## PART B: Weather/Grid → Ward Aggregation

### Finding: Area-weighted intersection at MRT/UTCI level, then compute H

**ERA5 grid:**
- ERA5-Land 0.1° = 25 cells (~114 km² each)
- ERA5 reanalysis 0.25° = 12 cells (~714 km² each)
- 11 of 12 reanalysis cells intersect Ahmedabad wards

**Recommended method:** Area-weighted intersection (Auffhammer et al. 2013; Schwarzwald & Geil 2024, xagg; Weighted Climate Dataset, Nature 2024)

**Aggregation level:** Aggregate at MRT or UTCI level, NOT at H level. Reason: H is already normalized to [0,1]; averaging a normalized index loses physical meaning. Compute H from ward-level aggregate UTCI.

**For peak/daily-maximum H:** Compute daily maximum UTCI per grid cell, then area-weight to ward, then compute H.

**For daily-mean H:** Compute daily mean UTCI per grid cell, then area-weight to ward, then compute H.

**Edge cases handled by area-weighted intersection:**
- Partial grid-cell overlap → fractional weights
- Ward spanning multiple cells → natural in area-weighted mean
- No-overlap wards → flag as NO_DATA
- Missing cells → flag as INCOMPLETE

**QA rules:**
- Weights sum ≈ 1.0 per ward (tolerance 0.01)
- No negative weights
- CRS consistent (WGS84/EPSG:4326)

---

## PART C: Vulnerability (V) Variable Selection

### Literature Sources
- Tran et al. 2013 (IJERPH): Ahmedabad slum heat vulnerability survey
- Azhar et al. 2017 (IJERPH): India-wide district-level HVI
- Sharma et al. 2026 (Jodhpur ward-level HVI): Indian ward-level methodology
- Ahmedabad HAP (NRDC/IIPH): Vulnerability assessment methodology
- RAND Heat Vulnerability Index: District-level India mapping

### Recommended V Variables

| Variable | Definition | Census Source | Direction | Evidence | Recommended |
|----------|-----------|---------------|-----------|----------|-------------|
| **Age (elderly)** | Population 60+ share | TOT_P, P_06 (compute 60+ as residual) | Higher → more vulnerable | Tran 2013: age >60 increases odds; Azhar 2017; Sharma 2026 | YES |
| **Age (children)** | Population 0-6 share | P_06 / TOT_P | Higher → more vulnerable | Azhar 2017; HAP vulnerable groups | YES |
| **Economic status** | Non-worker share | NON_WORK_P / TOT_P | Higher → more vulnerable | Tran 2013: poverty proxy; Azhar 2017 | YES |
| **Social isolation** | Single-person or female-headed household proxy | NOT AVAILABLE at ward level | Higher → more vulnerable | Tran 2013; literature | BLOCKED — no data |
| **Education** | Illiterate share | P_ILL / TOT_P | Higher → more vulnerable | Azhar 2017; Sharma 2026: education correlates with awareness | YES |
| **Gender** | Female population share | TOT_F / TOT_P | Higher → more vulnerable (in Indian context) | Azhar 2017; Sharma 2026 | YES |
| **Health issues** | Cannot be directly measured from Census | NOT AVAILABLE | Higher → more vulnerable | Tran 2013: preexisting conditions key factor | BLOCKED — no ward-level data |
| **Disability** | Cannot be directly measured from Census | NOT AVAILABLE | Higher → more vulnerable | Literature supports | BLOCKED — no ward-level data |
| **Slum population** | Slum household count | Census 2011 PCA-SLUM (town-level only, not ward-level) | Higher → more vulnerable | Tran 2013; Sheffield 2013; HAP | BLOCKED — only town-level |
| **SC/ST share** | Scheduled Caste + Tribe share | (P_SC + P_ST) / TOT_P | Higher → more vulnerable | Azhar 2017: caste as socioeconomic proxy | YES |
| **Literacy rate** | Literate share | P_LIT / TOT_P | Lower → more vulnerable | Azhar 2017; Sharma 2026 | YES (proxy for education) |

**Note on current BBWM V factors:** The existing code uses age, bmi, economic_status, social_isolation, education, gender, health_issues, disability. Of these, only age, economic_status, education, and gender are directly available from Census 2011 ward data. BMI, social_isolation, health_issues, and disability are NOT available at ward level.

---

## PART D: Exposure (E) Variable Selection

### Recommended E Variables

| Variable | Definition | Source | Resolution | Evidence | Recommended |
|----------|-----------|--------|------------|----------|-------------|
| **AQI / PM2.5** | Air quality index | NOT AVAILABLE at ward level | City-level only | Literature: AQI interacts with heat | BLOCKED — city-level only |
| **Outdoor worker share** | Workers in outdoor occupations | Census 2011 TOT_WORK, MAINWORK | Ward-level | Tran 2013: outdoor work increases vulnerability | PARTIALLY — occupation class available, not outdoor distinction |
| **Infrastructure condition** | Housing quality, construction material | NOT AVAILABLE at ward level | — | Literature supports | BLOCKED — no data |
| **Fluid intake activity** | Access to drinking water | NOT AVAILABLE at ward level | — | HAP: water access critical | BLOCKED — no data |
| **Healthcare access** | Distance to health facilities | AMC Facilities.kml available | Point locations | Literature supports | POSSIBLE — needs distance calculation |
| **Lifestyle factors** | Alcohol, tobacco, sleep, caffeine | NOT AVAILABLE at ward level | — | Not standard Census variables | BLOCKED — no data |
| **Built environment** | Urban heat island, NDVI, impervious surface | Satellite-derived (Landsat/Sentinel) | 30m resolution | Literature supports | NICE-TO-HAVE — not essential |

**Note on current BBWM E factors:** The existing code uses infrastructure_transit, fluid_intake_activity, lifestyle, air_quality, healthcare_accessibility. Of these, healthcare_accessibility is the only one that could potentially be computed from available data (AMC Facilities locations + ward centroids). All others are BLOCKED due to missing ward-level data.

---

## PART E: BBWM / Weighting Audit

### Current Implementation

| Aspect | Finding |
|--------|---------|
| Method | BBWM (Best-Worst Method) — a variant of AHP |
| Configuration | YAML files: `vulnerability_weights.yaml`, `exposure_weights.yaml` |
| Validation | Pydantic models enforce weight sums ≈ 1.0, discrete scores {0.33, 0.66, 1.00} |
| Residual floor | 0.33 |
| Status in model registry | `interface_only` for all models |

### Weight Source Assessment

| Weights | Source | Status |
|---------|--------|--------|
| V weights (age=0.160, health_issues=0.198, etc.) | UNDOCUMENTED — no source recorded | **UNVALIDATED** |
| E weights (infrastructure_transit=0.282, etc.) | UNDOCUMENTED — no source recorded | **UNVALIDATED** |
| Health_issues sub-weights (pre_illness=0.530, medication=0.470) | UNDOCUMENTED | **UNVALIDATED** |
| Lifestyle sub-weights (alcohol=0.341, etc.) | UNDOCUMENTED | **UNVALIDATED** |

### Method Assessment

BBWM (Rezaei 2015, 2016) is a legitimate MCDM method:
- Reduces cognitive load vs full AHP (only best-worst comparisons)
- Consistency ratio available
- Suitable for group decision-making
- Used in climate change vulnerability studies

**But:** The current weights appear to be **arbitrary or placeholder values**, not derived from any documented expert elicitation or literature review. They must NOT be treated as scientifically validated.

### Recommended Next Steps

1. **Mark current weights as PROVISIONAL/UNVALIDATED** in code comments and documentation
2. **Conduct expert elicitation** using BBWM survey with 5-10 Ahmedabad heat-health experts
3. **Or use literature-derived equal weights** as interim: each factor = 1/N
4. **Validate against known vulnerability patterns** (e.g., slum areas should score higher)

### Weighting Strategy Comparison

| Method | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| Equal weights | Simple, transparent, defensible | Ignores differential importance | INTERIM DEFAULT |
| Literature-derived weights | Evidence-based, replicable | May not match Ahmedabad context | GOOD IF available |
| Expert elicitation (BBWM) | Captures local knowledge, systematic | Requires expert access, time | BEST LONG-TERM |
| PCA/latent-index | Data-driven, captures correlations | Requires large N, unstable at ward level | NOT RECOMMENDED for 48 wards |

**Note on PCA:** Do NOT choose PCA merely because Indian HVI papers use it. PCA requires N >> p (many more observations than variables). With only 48 wards (or 57 Census wards), PCA would be unstable. BBWM or equal weights are more appropriate.

---

## PART F: Conceptual Equations

### Deterministic Layer Structure

```
H(grid, t)  →  spatial aggregation  →  H(ward, t)
V(ward)  ←  Census/static variables  →  normalization + weighting
E(ward, t)  ←  AQI/exposure variables  →  normalization + weighting
HSRI(ward, t) = H(ward, t) × V(ward) × E(ward, t)
```

### HSRI = H × V × E (Multiplicative)

**Assessment:**
- Multiplicative formulation is standard in climate-health risk (IPCC vulnerability framework)
- Creates pathological zeros if any component is zero → mitigated by residual floor (0.33)
- Geometric mean alternative: `(H × V × E)^(1/3)` — same ranking, different scale → NOT recommended (loses interpretability)
- V and E bounded [0.33, 1.0] via residual floor → prevents total collapse

**Normalization:**
- V: min-max or percentile normalization of Census variables → scale to [0, 1] → then apply residual floor 0.33
- E: same approach
- H: already [0, 1] from UTCI normalization
- Directionality: higher = more vulnerable/exposed for all components

**Missing values:**
- If a V variable is missing for a ward → set that factor to residual floor (0.33)
- If an E variable is missing → set that factor to residual floor (0.33)
- Do NOT impute with city mean (would bias toward average)

---

## PART G: Documentation Output

Files created:
1. `docs/data/spatial-strategy.md` — Ward geography reconciliation and aggregation strategy
2. `docs/data/source-register.md` — Source registry with evidence classification
3. `docs/data/unresolved-data-gaps.md` — Data gaps and blocking issues
4. `docs/data/methodology-study-v1.md` — This file

---

## PART H: No Implementation Verification

**Verified: No prohibited implementations were made.** This study only:
- Inspected existing files
- Searched authoritative literature
- Produced documentation
- Did NOT modify production scientific code
- Did NOT calculate V, E, or HSRI values
- Did NOT fabricate crosswalks
- Did NOT create synthetic health targets

---

## Final Answers to the 11 Questions

### Q1: Can 2011 Census 57-ward data be defensibly mapped to today's 48 AMC wards?

**NO.** CASE 3 applies. No authoritative crosswalk or 2011 ward geometry has been established. The 2015 SEC delimitation reduced wards from 57→48 but the exact mapping is not documented in a machine-readable format. **Current-48 ward vulnerability from Census 2011 is BLOCKED.**

### Q2: Is there authoritative historical 2011 ward geometry or a crosswalk?

**UNVERIFIED.** The NYU Spatial Data Repository (Princeton dataset) may contain 2011 ward boundary shapefiles, but access is restricted. DataMeet GitHub has ward geometry but the year is unclear. Gujarat SEC delimitation order exists but is not machine-readable. **Action required: acquire 2011 ward GIS or SEC order.**

### Q3: What exact weather-to-ward aggregation method should Agnirakshak use?

**Area-weighted intersection.** For each ward polygon and ERA5 grid cell, compute the fractional overlap area. Weight = (intersection area) / (total ward area). Ward value = Σ(weight × cell_value). This is the peer-reviewed standard (Auffhammer et al. 2013; xagg; Weighted Climate Dataset, Nature 2024).

### Q4: At what stage should aggregation occur: MRT, UTCI, H, or daily statistics?

**At the UTCI level.** Aggregate raw UTCI (or MRT) from grid cells to wards via area-weighted mean. Then compute H from ward-level UTCI. Do NOT aggregate H directly — it is a normalized index and averaging it loses physical meaning. For daily maximum H: compute daily max UTCI per cell, area-weight to ward, then compute H.

### Q5: Which V variables are actually supported by literature and available data?

**Supported by literature AND available at ward level:**
- Age (elderly/children share) — Census 2011
- Economic status (non-worker share) — Census 2011
- Education (illiteracy rate) — Census 2011
- Gender (female share) — Census 2011
- SC/ST share — Census 2011

**Supported by literature but NOT available at ward level:**
- BMI, social isolation, health issues, disability, slum population — BLOCKED

### Q6: Which E variables are actually supported and available?

**Very limited.** Most E variables require data not available at ward level:
- AQI → city-level only
- Outdoor worker share → occupation class available but not outdoor distinction
- Healthcare access → POSSIBLE if AMC facility locations are processed
- Infrastructure, fluid intake, lifestyle → BLOCKED

### Q7: Which variables are blocked because spatial/temporal resolution is inadequate?

- **AQI**: city-level, cannot disaggregate to ward without defensible spatial method
- **Slum population**: town-level only in Census 2011 PCA-SLUM
- **BMI, health issues, disability**: not in Census at all
- **Housing quality, water access**: not in Census at ward level
- **Lifestyle (alcohol, tobacco, etc.)**: not in Census

### Q8: Are current BBWM weights scientifically defensible?

**NO.** The current V and E weights in `vulnerability_weights.yaml` and `exposure_weights.yaml` are **UNVALIDATED**. No source, expert elicitation, or literature reference is documented. They appear to be placeholder or arbitrary values. Mark as PROVISIONAL. Recommend: (a) equal weights as interim, or (b) expert elicitation via BBWM survey.

### Q9: Is HSRI = H × V × E still recommended?

**YES**, with conditions:
- Retain multiplicative formulation (standard in IPCC framework)
- V and E bounded [0.33, 1.0] via residual floor
- Document that V and E are PROVISIONAL until validated
- Monitor for pathological zeros (should not occur with residual floor)

### Q10: What is the exact next implementation step after this study?

1. **Acquire 2011 ward boundary GIS** (NYU/Princeton or Gujarat SEC) → unblocks crosswalk
2. **Implement grid-to-ward aggregation** (area-weighted intersection) → ready now
3. **Compute V using available Census variables** on 57-ward geography → ready now (on historical geography)
4. **Mark current BBWM weights as PROVISIONAL** → immediate
5. **Conduct expert elicitation for V/E weights** → requires access to Ahmedabad heat-health experts

### Q11: What remains BLOCKED?

| Blocker | Reason | Resolution |
|---------|--------|------------|
| Current-48 ward V | No 57→48 crosswalk | Acquire 2011 ward GIS or SEC order |
| Ward-level AQI for E | City-level only | Acquire station-level AQI |
| BMI/health/disability for V | Not in Census | Accept limitation or use DLHS/NFHS |
| Validated BBWM weights | No expert elicitation | Conduct BBWM survey |
| Mortality/hospitalization ML | Data restricted by government | Cannot fabricate |
| Ward-level lifestyle for E | Not in Census | Accept limitation |
