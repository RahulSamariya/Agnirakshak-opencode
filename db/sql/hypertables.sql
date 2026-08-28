-- TimescaleDB hypertable configuration
-- NOTE: Hypertable creation is now integrated into Alembic migration
-- (001_initial_schema.py). This file is retained for reference and
-- manual operations if needed.

-- The Alembic migration creates hypertables automatically:
-- - weather_observations (observation_time, 1 day chunks)
-- - weather_forecasts (valid_time, 1 day chunks)

-- To manually create hypertables (if needed for recovery):
-- SELECT create_hypertable('weather_observations', 'observation_time', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);
-- SELECT create_hypertable('weather_forecasts', 'valid_time', chunk_time_interval => INTERVAL '1 day', if_not_exists => TRUE);