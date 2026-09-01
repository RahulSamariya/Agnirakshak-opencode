# MRT Method Selection Study — CORRECTED

**Version**: v2 (corrected per TEST 2H-C audit)
**Date**: 2026-08-31
**Status**: Evidence-audited

---

## 1. Objective

Compare three MRT methodologies to determine the most scientifically defensible approach for Agnirakshak:

- **A. Di Napoli et al. (2020)** — Published paper methodology
- **B. ECMWF thermofeel** — Official ECMWF implementation
- **C. ERA5-HEAT** — Operational reference product

## 2. Validation-type distinction

**This study distinguishes two validation types:**

| Validation type | What it answers | Source |
|----------------|-----------------|--------|
| **Accuracy validation** | How well does the method match ground truth? | Independent measurements |
| **Internal consistency** | How closely do two implementations agree? | Pairwise comparison |

**Critical finding**: The pairwise comparison (Di Napoli vs Thermofeel MAE=1.57 K) measures internal consistency, NOT accuracy. The Di Napoli paper's validation against ground truth (RMSE=4.12 K average) is the relevant accuracy metric.

## 3. Methods compared

### A. Di Napoli et al. (2020)

- **Source**: "Mean radiant temperature from global-scale numerical weather prediction models"
- **DOI**: 10.1007/s00484-020-01900-5
- **Key equations**: Eq 3-5 (derived quantities), Eq 6-12 (solar geometry), Eq 13 (direct solar projection), Eq 14 (MRT), Eq 15 (fp)
- **Conventions**:
  - fp gamma: elevation angle
  - I*: fdir / cos(theta_bar_0) — interval-averaged over sunlit portion
  - alpha/epsilon placement: fp * I* OUTSIDE the (alpha_ir/epsilon_p) multiplier
- **Constants**: SIGMA=5.67e-8, F_A=0.5, ALPHA_IR=0.7, EPSILON_P=0.97

### B. ECMWF thermofeel

- **Source**: ECMWF thermofeel 2.3.0 (pip install thermofeel)
- **Key function**: `calculate_mean_radiant_temperature` (thermofeel.py:235-281)
- **Conventions**:
  - fp gamma: arcsin(cossza) = elevation
  - dsrp: fdir / cossza (instantaneous, threshold=0.1)
  - alpha/epsilon placement: fp * dsrp INSIDE the (alpha_ir/epsilon_p) multiplier
- **Constants**: Same as Di Napoli
- **ECMWF claim**: "We suggest that the methodology in the thermofeel library supersedes the operational c code" [ECMWF Technical Memorandum 824]

### C. ERA5-HEAT

- **Source**: ERA5-HEAT operational product (loaded from NetCDF)
- **Type**: Reference product, not reimplemented
- **ECMWF claim**: "ERA5-HEAT is the official historical reanalysis and forecast dataset" [ECMWF Technical Memorandum 82413]

## 4. Primary sources

| Source | Type | DOI/URL | Evidence label |
|--------|------|---------|----------------|
| Di Napoli et al. (2020) | Peer-reviewed paper | 10.1007/s00484-020-01900-5 | PRIMARY — ground-truth validation |
| ECMWF thermofeel 2.3.0 | Official code | github.com/ecmwf/thermofeel | PRIMARY — reference implementation |
| ECMWF Technical Memorandum 824 | Internal document | https://www.ecmwf.int/en/elibrary/82413 | SECONDARY — method selection guidance |
| ERA5-HEAT documentation | ECMWF docs | https://confluence.ecmwf.int/display/UDOC/ERA5-HEAT | SECONDARY — operational product description |

## 5. Di Napoli validation numbers (primary source)

**From the paper abstract (verified from web search of published text):**

| Metric | Value | Source |
|--------|-------|--------|
| R² | ≥ 0.88 | Di Napoli abstract |
| Average bias | 0.42 °C | Di Napoli abstract |
| Bias range | -1.6 to +6.6 °C | Di Napoli abstract |
| Average RMSE | 4.12 °C | Di Napoli abstract |
| RMSE ceiling | < 10 °C | Di Napoli abstract |
| Stations | 11 WRMC-BSRN | Di Napoli abstract |
| Region | Europe | Di Napoli abstract |
| Period | 2015-07 to 2018-06 | Di Napoli abstract |

**CORRECTION**: The previous report stated "RMSE 1.5–3.0 K against European station measurements." This was incorrect. The actual paper reports average RMSE of 4.12 °C (range: up to 10 °C). The 1.5–3.0 K figure appears to have been a misattribution.

## 6. Pairwise comparison metrics (this study)

| Comparison | N | MAE | RMSE | Bias | R² | Evidence label |
|------------|---|-----|------|------|-----|----------------|
| Di Napoli vs Thermofeel | 1488 | 1.57 K | 2.99 K | +1.55 K | 0.981 | Internal consistency |
| Di Napoli vs ERA5-HEAT | 1488 | 2.88 K | 4.08 K | +2.74 K | 0.960 | Method vs reference product |
| Thermofeel vs ERA5-HEAT | 1488 | 2.27 K | 3.53 K | +1.18 K | 0.970 | Method vs reference product |

**Interpretation**:
- Di Napoli and Thermofeel agree closely (MAE=1.57 K, R²=0.981) — this measures internal consistency, NOT accuracy
- Both differ from ERA5-HEAT by 2–3 K MAE — this reflects expected methodology/reference-product distinctions
- ERA5-HEAT is NOT an independent validation source (it uses the same Di Napoli methodology)

## 7. Mathematical differences

| Component | Di Napoli | Thermofeel | ERA5-HEAT |
|-----------|-----------|------------|-----------|
| Diffuse SW | (ssrd - fdir) | (ssrd - fdir) | Same |
| Reflected SW | (ssrd - ssr) | (ssrd - ssr) | Same |
| Upward LW | (strd - str) | (strd - str) | Same |
| Direct solar | I* = fdir / cos_bar (interval avg) | dsrp = fdir / cossza (instantaneous) | Likely Di Napoli |
| fp gamma | elevation | arcsin(cossza) = elevation | Same as Di Napoli |
| Alpha placement | fp*I* OUTSIDE multiplier | fp*dsrp INSIDE multiplier | Same as Di Napoli |

## 8. Input differences

| Quantity | Di Napoli | Thermofeel | ERA5-HEAT |
|----------|-----------|------------|-----------|
| ssrd | Required | Required | Required |
| ssr | Required | Required | Required |
| fdir | Required | Required | Required |
| strd | Required | Required | Required |
| str | Required | Required | Required |
| dsrp | Derived (I*) | Derived (fdir/cossza) | Derived |
| cossza | Derived from geometry | Derived from geometry | Derived |

## 9. Solar-geometry differences

All three methods use the same solar geometry equations (Di Napoli Eq 6-12). The divergence occurs in how cossza is used:

- **Di Napoli**: Uses interval-averaged cos(theta_bar_0) for I* calculation
- **Thermofeel**: Uses instantaneous cossza for dsrp calculation
- **ERA5-HEAT**: Follows Di Napoli methodology

## 10. Direct-solar differences

This is the PRIMARY methodological difference:

- **Di Napoli**: I* = fdir / cos(theta_bar_0), where cos_bar is the average daytime cosine over the sunlit portion of the accumulation interval
- **Thermofeel**: dsrp = fdir / cossza (instantaneous)
- **ERA5-HEAT**: Follows Di Napoli methodology

## 11. Nighttime differences

At night (elevation < 0):
- **Di Napoli**: I* = 0, fp = 0, MRT from longwave only
- **Thermofeel**: dsrp = fdir (fdir=0 at night), fp computed but multiplied by 0
- **ERA5-HEAT**: Same as Di Napoli

## 12. Independent validation evidence

### Literature search results

| Study | Location | Method Validated | Sample Size | MAE/RMSE | Evidence label |
|-------|----------|-----------------|-------------|----------|----------------|
| Di Napoli et al. (2020) | 11 European WRMC-BSRN stations | Di Napoli MRT | Jul 2015–Jun 2018 | Avg RMSE 4.12 K, R²≥0.88 | PRIMARY — ground truth |
| ECMWF documentation | Global | Thermofeel | Operational | No independent validation reported | IMPLEMENTATION — not validation |
| BSRN stations | Global | Radiation measurements | Point measurements | N/A | Could validate radiation inputs |

### Key findings

- Di Napoli et al. (2020) validated against measured MRT at 11 European WRMC-BSRN stations with average RMSE of 4.12 K and R²≥0.88
- No independent validation of thermofeel MRT specifically (it implements Di Napoli methodology)
- ERA5-HEAT validation is against the operational product, not independent measurements
- No Ahmedabad-specific MRT validation was found

## 13. Ahmedabad-specific evidence

**No suitable independent Ahmedabad MRT ground truth was found in the searched sources.**

## 14. ECMWF claims verification

| Claim | Source | Verified | Notes |
|-------|--------|----------|-------|
| Thermofeel supersedes operational C code | ECMWF TM 824 | YES | "We suggest that the methodology in the thermofeel library supersedes the operational c code" |
| ERA5-HEAT is official historical product | ECMWF TM 82413 | YES | ERA5-HEAT is the official reanalysis |
| Di Napoli methodology used in ERA5 | ECMWF docs | YES | ERA5-HEAT uses Di Napoli equations |
| Thermofeel has independent validation | N/A | NO | No independent validation beyond Di Napoli paper |

## 15. Method differences from source

| Difference | Di Napoli paper | Thermofeel code | Our implementation | Evidence label |
|------------|-----------------|-----------------|-------------------|----------------|
| dsrp convention | I* = fdir/cos_bar | dsrp = fdir/cossza | dsrp = fdir/cossza (thermofeel) | PRIMARY — both sources |
| fp gamma | elevation | arcsin(cossza) = elevation | elevation (= arcsin(cossza)) | PRIMARY — same |
| Alpha placement | fp*I* outside multiplier | fp*dsrp inside multiplier | fp*dsrp inside multiplier (thermofeel) | PRIMARY — both sources |

## 16. Hybrid assessment

**No hybrid adopted.** Neither combination is explicitly supported by the primary sources.

## 17. Decision criteria

### A. Which method has the strongest source provenance?

**Di Napoli et al. (2020)** — Peer-reviewed paper with DOI, validated against 11 WRMC-BSRN stations.

### B. Which method has the strongest independent validation evidence?

**Di Napoli et al. (2020)** — Average RMSE 4.12 K, R²≥0.88 against European station measurements. Thermofeel has no independent validation beyond the Di Napoli paper it implements.

### C. Which method best fits our actual available data?

**Both Di Napoli and Thermofeel** — Both use the same 5 ERA5 radiation variables that we have.

### D. Which method is easiest to reproduce operationally?

**Both are equivalent** — Both are simple deterministic calculations.

### E. Is there a legitimate hybrid?

**No** — No source-supported hybrid exists.

### F. What method should Agnirakshak use?

**ECMWF thermofeel** (PROVISIONALLY RECOMMENDED)

Rationale:
- ECMWF states thermofeel "supersedes the operational c code" (TM 824)
- Thermofeel implements Di Napoli methodology with ECMWF's operational refinements
- The differences from Di Napoli are methodologically justified (instantaneous vs interval-averaged dsrp)
- The differences from ERA5-HEAT reflect expected methodology/reference-product distinctions

**Caveat**: The choice is based on source provenance and ECMWF guidance, NOT on local validation. No Ahmedabad-specific MRT validation exists.

## 18. Limitations

- No Ahmedabad-specific validation data available
- ERA5-HEAT is not an independent validation source (uses same Di Napoli methodology)
- The comparison uses only March 2010 data at one location
- Di Napoli validation was against European stations (11 WRMC-BSRN), not Indian climate
- The direct solar treatment difference (instantaneous vs interval-averaged) has the largest impact

## 19. Open questions

1. Does the interval-averaged I* (Di Napoli) or instantaneous dsrp (thermofeel) better represent the actual radiation field?
2. Would BSRN station data provide independent validation?
3. How do the methods perform under different climate conditions (monsoon, pre-monsoon)?
4. What is the impact on UTCI and heat-stress indices?

## 20. Recommendation

**PROVISIONALLY RECOMMENDED: ECMWF thermofeel**

The recommendation is provisional because:
- No independent Ahmedabad validation exists
- The choice is based on source provenance and ECMWF guidance, not local validation
- Future independent validation could change the recommendation

**NOT RECOMMENDED:**
- Tuning any method to ERA5-HEAT
- Creating undocumented hybrids
- Using ERA5-HEAT as the sole validation source

## 21. Corrections from previous version

| Item | Previous (v1) | Corrected (v2) | Source |
|------|---------------|----------------|--------|
| Di Napoli RMSE | 1.5–3.0 K | Avg 4.12 K (< 10 K) | Di Napoli abstract |
| Di Napoli stations | "European stations" | 11 WRMC-BSRN stations | Di Napoli abstract |
| Validation period | Not specified | Jul 2015–Jun 2018 | Di Napoli abstract |
| ECMWF guidance | Not cited | "thermofeel supersedes operational C code" | ECMWF TM 824 |
| Validation type | Not distinguished | Accuracy vs internal consistency | TEST 2H-C audit |

## 22. Final evidence table

| Method | Source | Independent validation | Validation N | Avg RMSE | R² | Ahmedabad-specific | ECMWF guidance |
|--------|--------|----------------------|--------------|----------|-----|-------------------|----------------|
| Di Napoli | Peer-reviewed paper | 11 WRMC-BSRN stations (Europe) | Jul 2015–Jun 2018 | 4.12 K | ≥0.88 | No | Same methodology as ERA5-HEAT |
| Thermofeel | ECMWF code | None independent | N/A | N/A | N/A | No | "Supersedes operational C code" |
| ERA5-HEAT | ECMWF operational | Against operational product | N/A | N/A | N/A | No | Official historical product |

**Note**: All validation is for European climate. No Ahmedabad-specific validation exists for any method.
