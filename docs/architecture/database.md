# Database Schema

## Extensions

- **PostGIS**: Spatial data support
- **TimescaleDB**: Time-series data optimization
- **uuid-ossp**: UUID generation

## Tables

### Geography
- `states` - Indian states with boundaries
- `cities` - Cities within states
- `wards` - Municipal wards within cities
- `grid_cells` - 333m computational grid
- `grid_ward_intersections` - Spatial intersections for accurate ward aggregation

### Weather
- `weather_stations` - Meteorological stations
- `weather_observations` - Historical observations
- `weather_forecast_runs` - Forecast model runs
- `weather_forecasts` - Forecast data per grid cell

### Scientific
- `scientific_models` - Registered models
- `model_runs` - Model execution history

### Hazard
- `hazard_assessments` - UTCI-based hazard indices

### Vulnerability
- `vulnerability_profiles` - Ward vulnerability scores
- `vulnerability_factors` - Individual factor scores

### Exposure
- `exposure_profiles` - Ward exposure scores
- `exposure_factors` - Individual factor scores

### Risk
- `risk_runs` - Risk calculation runs
- `risk_assessments` - Grid cell risk scores
- `risk_assessment_components` - Detailed breakdowns
- `ward_risk_summaries` - Aggregated ward risk

### Operations
- `alerts` - Heatwave warnings
- `action_recommendations` - Recommended actions

## Indexes

- GiST indexes on all geometry columns
- B-tree indexes on foreign keys
- Composite indexes for common queries
- TimescaleDB hypertables for time-series data (created by Alembic migration)

## Migration Lifecycle

1. Docker PostgreSQL starts with extensions enabled via `db/sql/init.sql`
2. Run `alembic upgrade head` to create all tables, indexes, and hypertables
3. Supplementary performance indexes available in `db/sql/indexes.sql` (optional)
