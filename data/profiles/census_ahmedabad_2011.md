# Census 2011 — Ahmedabad AMC Profiling

**Status**: BLOCKED — Census file not found in repository

## Expected File

`DDW_PCA2407_2011_MDDS with UI (1).xlsx`

## Finding

The Census 2011 workbook `DDW_PCA2407_2011_MDDS with UI (1).xlsx` is **NOT present** in the repository.

- `data/raw/census/` directory exists but is **empty**
- No `.xlsx` files matching `*DDW*` or `*MDDS*` found anywhere in the repo
- The `.gitignore` does not exclude `.xlsx` files
- The file was never committed or copied to the working tree

## Expected Structure (from Census of India documentation)

The DDW_PCA2407_2011_MDDS workbook typically contains:

| Field | Description |
|-------|-------------|
| District Code | Census district identifier |
| Town Code | Census town identifier |
| Ward Code | Ward-level identifier |
| Total Population | Overall population count |
| Male Population | Male population count |
| Female Population | Female population count |
| Age Group Fields | 0-14, 15-29, 30-44, 45-59, 60+ |
| Literacy Fields | Literate, Illiterate |
| Worker Fields | Main Worker, Marginal Worker |
| Non-Worker Fields | Non-worker count |
| Household Fields | Number of households |

## Expected Record Counts

- **57 AMC wards** (2011 delimitation)
- District: Ahmedabad
- State: Gujarat

## Blocker

Cannot profile Census data without the actual file.

**Action required**: Obtain `DDW_PCA2407_2011_MDDS with UI (1).xlsx` and place in `data/raw/census/`.

## Profiling Script

A profiling script is prepared at `scripts/profile_census.py` and will execute once the file is available.

## Output Files (when available)

- `data/profiles/census_ahmedabad_2011.json`
- `data/profiles/census_ahmedabad_2011.md`
- `data/staging/census/wards_census_2011_amc.csv`
