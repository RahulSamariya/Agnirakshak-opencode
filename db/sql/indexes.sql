-- Spatial and performance indexes for the heatwave platform
-- Run after table creation

-- Geography spatial indexes
CREATE INDEX IF NOT EXISTS ix_states_geometry
    ON states USING GIST (geometry);

CREATE INDEX IF NOT EXISTS ix_cities_geometry
    ON cities USING GIST (geometry);

CREATE INDEX IF NOT EXISTS ix_wards_geometry
    ON wards USING GIST (geometry);

CREATE INDEX IF NOT EXISTS ix_grid_cells_geometry
    ON grid_cells USING GIST (geometry);

CREATE INDEX IF NOT EXISTS ix_grid_cells_centroid
    ON grid_cells USING GIST (centroid);

-- Weather station spatial index
CREATE INDEX IF NOT EXISTS ix_weather_stations_geometry
    ON weather_stations USING GIST (geometry);

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
