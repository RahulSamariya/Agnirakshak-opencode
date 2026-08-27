-- TimescaleDB hypertable configuration
-- Convert high-volume time-series tables to hypertables

-- Convert weather_forecasts to hypertable
-- This must be run after the table is created
SELECT create_hypertable(
    'weather_forecasts',
    'valid_time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Convert weather_observations to hypertable
SELECT create_hypertable(
    'weather_observations',
    'observation_time',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- Add compression policy for older data (optional)
-- ALTER TABLE weather_forecasts SET (
--     timescaledb.compress,
--     timescaledb.compress_segmentby = 'grid_cell_id',
--     timescaledb.compress_orderby = 'valid_time DESC'
-- );

-- SELECT add_compression_policy('weather_forecasts', INTERVAL '7 days');
