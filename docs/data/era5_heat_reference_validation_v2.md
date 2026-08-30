# ERA5-HEAT Reference Validation — TEST 1 (Corrected)

**Status**: BLOCKED
**Reason**: Matching ERA5 meteorology unavailable
**Date**: 2026-08-30

## Previous Experiment (v1)

The previous validation (`era5_heat_reference_validation_v1.md`) used:

- ERA5-HEAT MRT and UTCI as reference
- **ERA5-Land** meteorological inputs (t2m, d2m, u10, v10) for the Agnirakshak UTCI engine

**Why this could not isolate UTCI error**: ERA5-Land is a separate downscaled product (0.1° resolution) based on ERA5, but its temperature, humidity, and wind fields differ from ERA5 itself. The 0.58°C MAE reflects a combination of:

1. UTCI polynomial implementation differences
2. Meteorological input differences (ERA5-Land vs ERA5)
3. Spatial mismatch (0.1° vs 0.25° grids)
4. Temporal mismatch (6-hourly vs hourly)

Previous statistics (MAE=0.58°C, RMSE=0.85°C, bias=+0.46°C) are preserved as historical evidence but cannot be attributed solely to the UTCI implementation.

## What Is Missing

For a clean TEST 1 validation, the following ERA5 reanalysis variables are required at **0.25° resolution** (matching ERA5-HEAT grid):

| Variable | ERA5 Short Name | Description | Unit |
|----------|----------------|-------------|------|
| 2m temperature | `t2m` | Air temperature at 2m | K |
| 2m dewpoint | `d2m` | Dewpoint temperature at 2m | K |
| 10m U-wind | `u10` | U-component of wind at 10m | m/s |
| 10m V-wind | `v10` | V-component of wind at 10m | m/s |
| Surface pressure | `sp` | Surface pressure | Pa |

These must be from the **ERA5 single-level reanalysis** (not ERA5-Land), covering:

- **Time**: 2010-03-01 to 2010-03-31
- **Frequency**: Hourly (to match ERA5-HEAT temporal resolution)
- **Region**: 22.75–23.25°N, 72.25–73.0°E (matching ERA5-HEAT grid)
- **Grid**: 0.25° (matching ERA5-HEAT spatial resolution)

## Available Files

| File | Type | Resolution | Usable for TEST 1? |
|------|------|-----------|-------------------|
| `cde4e619c080209e1ec505565f79b8e.nc` | ERA5-HEAT | 0.25° | YES (reference) |
| `data/raw/weather/data_0.nc` | ERA5-Land | 0.1° | NO (wrong product) |
| `ERA5/data_0.nc` | ERA5-Land | 0.1° | NO (wrong product) |
| `data_stream-mnth.nc` | Monthly ERA5 | 0.1° | NO (wrong frequency) |

**No matching ERA5 0.25° hourly meteorology exists in the repository.**

## CDS API Request to Acquire ERA5 Data

To obtain the required ERA5 meteorology, use the Copernicus Climate Data Store (CDS) API:

```python
import cdsapi

client = cdsapi.Client()

client.retrieve(
    "reanalysis-era5-single-levels",
    {
        "product_type": "reanalysis",
        "variable": [
            "2m_temperature",
            "2m_dewpoint_temperature",
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
            "surface_pressure",
        ],
        "year": "2010",
        "month": "03",
        "day": [str(d) for d in range(1, 32)],
        "time": [f"{h:02d}:00" for h in range(24)],
        "area": [23.25, 72.25, 22.75, 73.0],  # N, W, S, E
        "grid": [0.25, 0.25],
        "format": "netcdf",
    },
    "era5_meteorology_ahmedabad_2010_03.nc",
)
```

**After downloading**, place the file in `data/raw/weather/` and re-run the validation.

## TEST 1 Status

**BLOCKED** — corresponding ERA5 meteorology unavailable.

Do NOT substitute ERA5-Land and do not claim completion.

## Next Steps

1. Download ERA5 single-level reanalysis using the CDS API request above
2. Place `era5_meteorology_ahmedabad_2010_03.nc` in `data/raw/weather/`
3. Re-run the corrected validation script
4. Verify that ERA5-HEAT MRT, ERA5 meteorology, and ERA5-HEAT UTCI share identical spatial/temporal grids
