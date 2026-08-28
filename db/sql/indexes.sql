-- Spatial and performance indexes for the heatwave platform
-- NOTE: Most indexes are now created by Alembic migration
-- (001_initial_schema.py). This file contains additional performance
-- indexes that can be applied after migration for optimization.

-- Additional spatial indexes (not in Alembic migration)
-- These are supplementary to the primary indexes created by Alembic

-- Weather forecast performance indexes
CREATE INDEX IF NOT EXISTS ix_weather_forecasts_valid_time_grid
    ON weather_forecasts (valid_time, grid_cell_id);

CREATE INDEX IF NOT EXISTS ix_weather_forecasts_run_valid
    ON weather_forecasts (run_id, valid_time);

-- Hazard assessment indexes
CREATE INDEX IF NOT EXISTS ix_hazard_assessments_time_grid
    ON hazard_assessments (valid_time, grid_cell_id);

-- Risk assessment indexes
CREATE INDEX IF NOT EXISTS ix_risk_assessments_category_time
    ON risk_assessments (risk_category, valid_time);

-- Alert active alerts
CREATE INDEX IF NOT EXISTS ix_alerts_active_valid
    ON alerts (is_active, valid_from, valid_until);