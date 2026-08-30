# ERA5-Land Ahmedabad — Enhanced Profile

**Status**: READY
**Source**: ERA5-Land
**Format**: NetCDF (CF-1.6)
**SHA256**: `0d807637a3e74b4c62cdbe250e7ef670785ff8a9297302c12bb269d6aa9047db`
**File size**: 133,764 bytes

## Dimensions

| Dimension | Size |
|-----------|------|
| valid_time | 124 |
| latitude | 5 |
| longitude | 5 |

## Required Variables

| Variable | Status | Description | Units | Range | Missing |
|----------|--------|-------------|-------|-------|---------|
| t2m | present | 2 metre temperature | K | 16.5 to 39.9 C | 0 |
| d2m | present | 2 metre dewpoint temperature | K | -1.2 to 21.8 C | 0 |
| u10 | present | 10 metre U wind component | m s**-1 | -4.21 to 4.15 | 0 |
| v10 | present | 10 metre V wind component | m s**-1 | -3.64 to 3.80 | 0 |
| sp | present | Surface pressure | Pa | 99370.86 to 101362.25 | 0 |
| ssrd | present | Surface short-wave (solar) radiation downwards | J m**-2 | 6323036.00 to 25831884.00 | 0 |
| strd | present | Surface long-wave (thermal) radiation downwards | J m**-2 | 6952162.50 to 34055028.00 | 0 |

## Time Analysis

- **Min**: 2010-03-01T00:00:00.000000000
- **Max**: 2010-03-31T18:00:00.000000000
- **Timestamp count**: 124
- **Duplicate timestamps**: 0
- **Timezone**: UTC (ERA5 standard)

## Spatial Analysis

- **Latitude range**: [22.8, 23.2]
- **Longitude range**: [72.4, 72.8]
- **Resolution**: 0.10 deg
- **Grid cells**: 25

## Quality Checks

- Total missing values: 0
- Duplicate timestamps: 0
- All required variables present: True
