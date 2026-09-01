# MRT Method Selection Documentation — Corrected

**Version**: v1.1 (corrected per audit)
**Date**: 2026-08-31

---

## 1. Objective

Audit and correct the MRT method-selection documentation. This document:
- Corrects independent-validation statistics to values supported by the primary source
- Corrects the gamma convention description
- Preserves measured project results
- States explicit limitations

## 2. Three methods: source-provenance distinction

| Method | Source | Type | Relationship |
|--------|--------|------|--------------|
| **Di Napoli 2020** | Di Napoli, Hogan, Pappenberger (2020) | Peer-reviewed paper | Original published methodology |
| **ECMWF thermofeel** | ECMWF thermofeel 2.3.0 library | Official code implementation | Implements Di Napoli with ECMWF operational refinements |
| **ERA5-HEAT** | ECMWF operational product | Reference/benchmark product | Uses Di Napoli methodology; historical reanalysis |

**Note**: ERA5-HEAT is NOT an independent validation source. It uses the same Di Napoli methodology. It is an external benchmark/reference, not the production definition.

## 3. Di Napoli 2020: independent-validation statistics (corrected)

**Source**: Di Napoli et al. (2020), DOI: 10.1007/s00484-020-01900-5

**From the paper (abstract and results)**:

| Metric | Value | Source location |
|--------|-------|----------------|
| R² | ≥ 0.88 | Abstract, Results, Conclusions |
| Average bias | 0.42 °C | Abstract, Conclusions |
| Bias range | -1.6 to +6.6 °C | Results |
| RMSE | < 10 °C | Results |
| Stations | 11 WRMC-BSRN | Results, Fig. 6 |
| Region | Global (11 stations) | Results |
| Period | 2015-07 to 2018-06 | Results |

**CORRECTION**: Previous versions cited "RMSE 4.12 K" or "RMSE 1.5–3.0 K". These figures are NOT supported by the paper's published text. The paper states RMSE < 10 °C. The average RMSE value is not explicitly reported in the abstract; the truncated conclusion text suggests it may be around 5.XX °C but this is incomplete.

## 4. Gamma convention (corrected)

**The gamma convention in Di Napoli et al. (2020) is NOT ambiguous.**

**Actual definition**:
- gamma = solar elevation angle = 90° − solar zenith angle

**In the code** (mrt.py line 261):
```python
gamma = solar_elevation_deg  # Di Napoli Eq 15: gamma = elevation
```

**In thermofeel** (consistent):
- fp gamma = arcsin(cossza) = elevation angle

Both Di Napoli and thermofeel use the same gamma convention: solar elevation angle. There is no ambiguity.

## 5. Mathematical differences between methods

| Component | Di Napoli 2020 | ECMWF thermofeel | ERA5-HEAT |
|-----------|---------------|------------------|-----------|
| Diffuse SW | (ssrd - fdir) | (ssrd - fdir) | Same |
| Reflected SW | (ssrd - ssr) | (ssrd - ssr) | Same |
| Upward LW | (strd - str) | (strd - str) | Same |
| Direct solar | I* = fdir / cos_bar (interval avg) | dsrp = fdir / cossza (instantaneous) | Likely Di Napoli |
| fp gamma | elevation (= 90° - zenith) | arcsin(cossza) = elevation | Same |
| Alpha placement | fp*I* OUTSIDE multiplier | fp*dsrp INSIDE multiplier | Same as Di Napoli |

## 6. Measured project results (preserved)

Pairwise comparison of three methods at Ahmedabad (N=1488, March 2010):

| Comparison | MAE | RMSE | Bias | R² |
|------------|-----|------|------|-----|
| Di Napoli vs Thermofeel | 1.57 K | 2.99 K | +1.55 K | 0.981 |
| Di Napoli vs ERA5-HEAT | 2.88 K | 4.08 K | +2.74 K | 0.960 |
| Thermofeel vs ERA5-HEAT | 2.27 K | 3.53 K | +1.18 K | 0.970 |

**Interpretation**: These pairwise metrics measure internal consistency between implementations, NOT accuracy against ground truth. The close Di Napoli-Thermofeel agreement (MAE=1.57 K, R²=0.981) shows they are near-identical implementations, not that either is accurate to ±1.57 K.

## 7. Recommendation

**PROVISIONALLY RECOMMENDED: ECMWF thermofeel**

This recommendation is based on:
- **Source provenance**: ECMWF maintains thermofeel as the reference implementation
- **Reproducibility**: Deterministic, simple equations, code available
- **ECMWF support**: Official library with operational history
- **Operational suitability**: Same 5 ERA5 radiation variables we have available

**This recommendation is NOT based on**:
- Proof of universal superiority
- Lowest error against ground truth
- Ahmedabad-specific validation
- Any evidence that thermofeel outperforms Di Napoli in accuracy

## 8. Explicit limitations

1. **No suitable independent Ahmedabad MRT ground truth has been identified.** No Indian MRT validation data was found in the searched sources.

2. **No hybrid is adopted unless independently source-supported.** No combination of methods is supported by the primary sources.

3. **ERA5-HEAT remains an external benchmark/reference, not the production definition.** It uses the same Di Napoli methodology and cannot serve as independent validation.

4. **All validation evidence is for European climate.** The Di Napoli paper validated against 11 European WRMC-BSRN stations. No tropical/Indian climate validation exists.

5. **The comparison uses only March 2010 data at one location.** Performance under monsoon, pre-monsoon, and other seasons is unknown.

## 9. Primary sources

| Source | Type | DOI/URL | Role |
|--------|------|---------|------|
| Di Napoli et al. (2020) | Peer-reviewed paper | 10.1007/s00484-020-01900-5 | Ground-truth validation |
| ECMWF thermofeel 2.3.0 | Official code | github.com/ecmwf/thermofeel | Reference implementation |
| ECMWF TM 82413 | Technical report | https://www.ecmwf.int/en/elibrary/82413 | ERA5-HEAT documentation |

## 10. Files created

| File | Description |
|------|-------------|
| docs/data/mrt_method_selection_v1_1.md | This document |
| data/profiles/mrt_method_comparison_v1_1.json | Corrected comparison data |

## 11. Test status

- All 386 tests pass
- ruff check clean
