# Census 2011 - Ahmedabad AMC Profiling

**Status**: READY
**Source**: Census of India 2011
**File**: `data/raw/census/DDW_PCA2407_2011_MDDS with UI (1).xlsx`
**SHA256**: `3a601d501e437f85f2388b6460a0ebf4df5c784d1fb1484eb846b4df7913433b`

## Workbook Structure

| Property | Value |
|----------|-------|
| Sheet names | ['EB-2407'] |
| Total rows | 711 |
| Total columns | 94 |
| AMC ward count | 57 |

## Key Demographic Fields (AMC Wards Total)

| Field | Description | Value |
|-------|-------------|-------|
| TOT_P | Total population | 5,577,940 |
| TOT_M | Male population | 2,938,985 |
| TOT_F | Female population | 2,638,955 |
| P_06 | Child 0-6 | 621,034 |
| P_LIT | Literate | 4,376,393 |
| P_ILL | Illiterate | 1,201,547 |
| TOT_WORK_P | Total workers | 1,951,129 |
| NON_WORK_P | Non-workers | 3,626,811 |
| No_HH | Households | 1,179,823 |

## Quality Checks

- Duplicate ward IDs: 0
- Missing ward IDs: 0
- Missing population: 0

## Known Limitations

- Census 2011 has 57 AMC wards (2011 delimitation)
- Current GIS has 48 wards (2024 delimitation)
- CROSSWALK REQUIRED between 2011 and 2024 ward boundaries