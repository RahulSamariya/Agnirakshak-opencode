# ERA5-Land Ahmedabad Profile

## File
`data/raw/weather/data_0.nc`

## Dimensions
- `valid_time`: 124 timesteps
- `latitude`: 5 grid points
- `longitude`: 5 grid points

## Variables
| Variable | Long Name | Units | Shape |
|----------|-----------|-------|-------|
| `t2m` | 2 metre temperature | K | (124, 5, 5) |
| `d2m` | 2 metre dewpoint temperature | K | (124, 5, 5) |
| `u10` | 10 metre U wind component | m s-1 | (124, 5, 5) |
| `v10` | 10 metre V wind component | m s-1 | (124, 5, 5) |
| `sp` | Surface pressure | Pa | (124, 5, 5) |
| `ssrd` | Surface short-wave radiation downwards | J m-2 | (124, 5, 5) |
| `strd` | Surface long-wave radiation downwards | J m-2 | (124, 5, 5) |

## Coordinate Ranges
- **Latitude**: 22.8 to 23.2 (5 points)
- **Longitude**: 72.4 to 72.8 (5 points)
- **Time**: 2010-03-01 to 2010-03-31 (124 hourly timesteps)

## Data Quality
- **Missing values**: 0% for all variables
- **CRS**: EPSG:4326 (WGS84)

## Notes
- This is a small sample covering Ahmedabad area (0.4° x 0.4° grid)
- Time resolution: hourly
- All 7 variables required for UTCI calculation are present
- Units are standard SI (Kelvin, Pa, m/s, J/m²)
