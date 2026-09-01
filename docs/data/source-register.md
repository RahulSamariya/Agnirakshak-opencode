# Source Register

**Version:** 1.0
**Date:** 2026-09-02

---

## Acquired Sources

| # | Source | File/Path | evidence_type | source_status | access_status | ml_suitability | What It Proves |
|---|--------|-----------|---------------|---------------|---------------|----------------|----------------|
| 1 | Census 2011 PCA (India) | `data/raw/census/DDW_PCA2407_2011_MDDS with UI (1).xlsx` | PRIMARY_OFFICIAL | VERIFIED | PUBLIC | SUITABLE | 57 AMC ward demographics, literacy, work status |
| 2 | Census 2011 AMC Staging | `data/staging/census/wards_census_2011_amc.csv` | PRIMARY_OFFICIAL | VERIFIED | PUBLIC | SUITABLE | Cleaned 57-ward Census data with 37 columns |
| 3 | Ahmedabad 48-ward GIS | `data/raw/gis/wards_ahmedabad.geojson` | OFFICIAL_DOCUMENTATION | VERIFIED | PUBLIC | SUITABLE | Current 48 ward boundaries, LGD codes |
| 4 | ERA5-Land (0.1°) | `data/raw/weather/data_0.nc` | PRIMARY_OFFICIAL | VERIFIED | PUBLIC | SUITABLE | Meteorology + radiation, 6-hourly, March 2010 |
| 5 | ERA5 Reanalysis (0.25°) | `53968a80e95eb41e9fe5c5f804eacbd8.nc` | PRIMARY_OFFICIAL | VERIFIED | PUBLIC | SUITABLE | Reference meteorology |
| 6 | ERA5-HEAT | `cde4e619c080209e1ec505565f79b8e.nc` | SECONDARY_RESEARCH | VERIFIED | PUBLIC | PARTIALLY_SUITABLE | Reference MRT/UTCI for validation only |
| 7 | ERA5 Radiation | `97c99a12bac0f84dae69bd5460cde459.nc` | PRIMARY_OFFICIAL | VERIFIED | PUBLIC | SUITABLE | SSRD, FDIR, STRD for MRT calculation |
| 8 | Census 2011 Slum Data | Census India `PC11 PCA-SLUM` | PRIMARY_OFFICIAL | UNVERIFIED | PUBLIC | UNKNOWN | Town-level slum population (not ward-level) |
| 9 | Ahmedabad HAP (NRDC) | `heathealth.info`, `nrdc.org` | OFFICIAL_DOCUMENTATION | VERIFIED | PUBLIC | PARTIALLY_SUITABLE | Heat Action Plan methodology, vulnerability factors |
| 10 | Tran et al. 2013 (IJERPH) | PMC3717750 | SECONDARY_RESEARCH | VERIFIED | PUBLIC | SUITABLE | Ahmedabad slum heat vulnerability factors |

## Candidate Sources (Not Yet Acquired)

| # | Source | URL | evidence_type | source_status | access_status | What It Would Prove |
|---|--------|-----|---------------|---------------|---------------|---------------------|
| 11 | NYU Princeton 2011 Ward Boundaries | `geo.nyu.edu/catalog/princeton-9c67wr21b` | SECONDARY_RESEARCH | UNVERIFIED | RESTRICTED | 2011 ward boundary geometry |
| 12 | DataMeet Ahmedabad Wards | `github.com/datameet/Municipal_Spatial_Data` | SECONDARY_RESEARCH | UNVERIFIED | PUBLIC | Ward geometry (year unclear) |
| 13 | Gujarat SEC Delimitation Order 2015 | Official SEC website | PRIMARY_OFFICIAL | UNVERIFIED | UNKNOWN | Official ward reorganization mapping |
| 14 | OpenCity Ahmedabad 48-ward | `data.opencity.in` | OFFICIAL_DOCUMENTATION | VERIFIED | PUBLIC | Current 48-ward boundaries (already in repo) |
| 15 | Azhar et al. 2017 (IJERPH) | DOI:10.3390/ijerph14040357 | SECONDARY_RESEARCH | UNVERIFIED | PUBLIC | India-wide HVI methodology |
| 16 | Sharma et al. 2026 (Jodhpur HVI) | ScienceDirect | SECONDARY_RESEARCH | UNVERIFIED | PUBLIC | Ward-level HVI for Indian city |

---

## LLM-Only Sources (DO NOT IMPLEMENT)

None. All sources above are from peer-reviewed literature, official government data, or established open-data repositories.
