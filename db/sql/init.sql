-- Extension bootstrap for the heatwave platform
-- This file is loaded automatically by Docker PostgreSQL initdb
-- It enables required extensions before Alembic migrations run

-- Enable PostGIS (required for spatial data)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Enable TimescaleDB (required for time-series hypertables)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Enable UUID extension (required for UUID primary keys)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- NOTE: Table creation and indexes are handled by Alembic migrations
-- Run: alembic upgrade head