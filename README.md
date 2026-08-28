# Heatwave Early Warning Platform

Extreme Heatwave Early Warning and Human Thermal Stress Index Platform for the Indian Ministry of Earth Sciences.

## Status: Phase 1 Complete

**Phase 1 is complete.** The repository is ready for Phase 2 scientific engine implementation.

| Component | Status |
|-----------|--------|
| Repository architecture | Complete |
| Backend foundation (FastAPI) | Complete |
| Frontend foundation (Next.js) | Complete |
| Database schema (22 tables) | Complete |
| Alembic migrations | Complete |
| PostGIS spatial support | Complete |
| TimescaleDB hypertables | Complete |
| Scientific interfaces | Complete |
| API contracts (scaffold) | Complete |
| Pipeline contracts (scaffold) | Complete |
| Testing infrastructure | Complete |
| Docker environment | Complete |
| Lint (Ruff) | All checks passed |
| Tests | 28 passed |

### Verification Results

```
Python install                PASS
pytest                        PASS (28 passed)
PostgreSQL 16.15              PASS
PostGIS 3.6                   PASS (5 geometry tables, spatial indexes)
TimescaleDB 2.29.2            PASS (2 hypertables)
Alembic clean migration       PASS (from empty DB, verified twice)
Weather hypertables           PASS (weather_observations, weather_forecasts)
Spatial model                 PASS (grid_ward_intersections, coverage_fraction, intersection_area)
API                           PASS (200 OK, all modules import)
Worker                        PASS (Celery app imports)
Frontend typecheck            PASS (tsc --noEmit)
Frontend build                PASS (9 routes, Next.js 14.2.0)
Frontend lint                 PASS (0 ESLint warnings)
Ruff                          PASS (0 errors)
Secrets check                 PASS (no real secrets found)
```

## Tasks Performed (Phase 1 Hardening)

### 1. Security
- Removed `apps/api/.env` from git tracking
- Replaced 5 hardcoded secrets with `CHANGE_ME` placeholders in `config.py`, `worker/main.py`, `alembic.ini`, `.env.example`, `grafana-datasources.yml`

### 2. Code Quality
- Fixed `datetime.utcnow()` to `datetime.now(timezone=True)` in `scientific/core/base.py`
- Updated all 8 schema files + `config.py` to Pydantic v2 (`model_config = ConfigDict(from_attributes=True)`)
- Added missing `__init__.py` to `pipelines/`, `pipelines/weather/`, `pipelines/vulnerability/`, `pipelines/exposure/`, `pipelines/risk/`
- Created `scientific/hazard/base.py` with `HazardModel` ABC and `HazardResult` dataclass

### 3. Type Annotations
- Fixed `get_db()` return type to `AsyncGenerator[AsyncSession, None]` in `database.py`

### 4. Database
- Added 7 missing indexes + downgrade paths to Alembic migration
- Added `grid_ward_intersections` table to migration, SQLAlchemy model, and `models/__init__.py`
- Fixed `weather_observations` PK to composite `(id, observation_time)` for TimescaleDB
- Fixed `weather_forecasts` PK to composite `(id, valid_time)` for TimescaleDB
- Integrated TimescaleDB hypertable creation into Alembic migration
- Added `drop_hypertable` to downgrade path

### 5. Docker
- Removed deprecated `version` key from `docker-compose.yml`
- Pinned all Docker images (`timescale/timescaledb-ha:pg16.4`, `redis:7.2.6-alpine`, `python:3.12.5-slim`, `node:20.15.1-alpine`)
- Fixed `docker-compose.yml` to use `postgres:16` base with PostGIS + TimescaleDB
- Created `infra/docker/Dockerfile.db` with PostGIS 3.6 + TimescaleDB 2.29.2

### 6. Test Infrastructure
- Created `conftest.py` with sys.path setup for API and worker modules
- Fixed `test_api_startup.py` for httpx v0.28+ (ASGITransport)
- Fixed `test_worker_import.py` with try/except imports
- Created `test_database.py` with model import and table name verification tests

### 7. Worker Fixes
- Celery signal handlers accept `**kwargs` for Celery 5.6 compatibility
- Task imports use try/except fallback for optional dependencies
- Fixed health route double-nesting (`/health/health/` to `/health/`)

### 8. Package Manager
- Fixed Makefile to use `pnpm` instead of `npm` (authoritative package manager)
- Updated README to use `pnpm` for all frontend commands
- Generated `pnpm-lock.yaml` (workspace install was never committed)
- Added `apps/web/.eslintrc.json` (next lint was failing without config)
- Allowed `unrs-resolver` build scripts in `pnpm-workspace.yaml`

### 9. Lint
- Added `pyproject.toml` with Ruff configuration
- Fixed 400+ Ruff lint issues (deprecated typing, import sorting, unused imports, etc.)
- Added `# noqa: B008` for FastAPI `Query()` patterns

### 10. Documentation
- Updated `database.md` with grid_ward_intersections and migration lifecycle
- Updated `system-overview.md` with spatial hierarchy
- Updated `data-flow.md` with Phase 1 vs Phase 2 distinction
- Updated README with verification results, task list, and implementation status

### 11. Configuration
- Changed `model_registry.yaml` status from `active` to `interface_only` for all 4 models (implementations not present)

### Commits
```
2baf61f  Phase-1 hardening: type annotations, imports, schema consistency
6921a86  Phase-1 hardening: worker fixes, test expansion, alembic indexes
cd29b3e  Phase-1 hardening: lint, types, docs, migration lifecycle
f905f91  Phase-1 hardening: lint, types, docs, migration lifecycle
1155de4  Update README with Phase 1 completion status
19c3411  Phase-1 final acceptance: fix package manager, ESLint, model statuses
cd0105f  Fix TimescaleDB hypertable PK and Docker image for Phase 1 verification
c659d79  Update README with Phase 1 verification results
ca775ba  Update prompt.txt with Phase 1 acceptance test checklist
```

## Overview

This platform converts meteorological forecasts and population vulnerability data into spatially and temporally resolved Human Thermal Stress Risk Index (HSRI) values.

### Core Formula

```
HSRI = H x V x E
```

Where:
- **H** = UTCI-derived Hazard Index (0.0 - 1.0) [Phase 2]
- **V** = BBWM-derived Vulnerability Index (0.0 - 1.0) [Phase 2]
- **E** = BBWM-derived Exposure Index (0.0 - 1.0) [Phase 2]

## Project Structure

```
heatwave-platform/
├── apps/
│   ├── api/           # FastAPI backend
│   │   ├── app/
│   │   │   ├── models/    # SQLAlchemy ORM models (22 tables)
│   │   │   ├── schemas/   # Pydantic v2 schemas
│   │   │   ├── api/v1/    # API route stubs
│   │   │   └── services/  # Business logic services
│   │   └── migrations/    # Alembic migrations
│   ├── worker/        # Celery background workers
│   └── web/           # Next.js frontend (scaffold)
├── scientific/        # Scientific module interfaces
│   ├── core/          # Abstract base classes
│   ├── hazard/        # Hazard model interface
│   ├── vulnerability/ # Vulnerability model interface
│   ├── exposure/      # Exposure model interface
│   ├── risk/          # Risk model interface
│   ├── thermal_comfort/ # Thermal comfort interface
│   └── configuration/ # Scientific configuration YAMLs
├── pipelines/         # Data pipeline stubs
├── db/               # Database SQL files
├── infra/            # Infrastructure (Docker, K8s, monitoring)
├── tests/            # Test suites (28 tests)
└── docs/             # Architecture documentation
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- pnpm (package manager)

### Development Setup

1. **Start infrastructure:**
```bash
docker-compose up -d
```

This starts:
- PostgreSQL + PostGIS + TimescaleDB (port 5432)
- Redis (port 6379)
- API (port 8000)
- Worker
- Web (port 3000)

2. **Run database migrations:**
```bash
cd apps/api
alembic upgrade head
```

3. **Install dependencies (for local development):**
```bash
# Frontend (from repo root)
pnpm install

# API
cd apps/api && pip install -r requirements.txt

# Worker
cd apps/worker && pip install -r requirements.txt
```

4. **Run tests:**
```bash
pytest
```

5. **Run linting:**
```bash
ruff check apps/ scientific/ pipelines/ tests/
```

### Access Services
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432
- Redis: localhost:6379

## Database Schema

### Tables (22 total)

**Geography:** states, cities, wards, grid_cells, grid_ward_intersections

**Weather:** weather_stations, weather_observations, weather_forecast_runs, weather_forecasts

**Scientific:** scientific_models, model_runs

**Hazard:** hazard_assessments

**Vulnerability:** vulnerability_profiles, vulnerability_factors

**Exposure:** exposure_profiles, exposure_factors

**Risk:** risk_runs, risk_assessments, risk_assessment_components, ward_risk_summaries

**Operations:** alerts, action_recommendations

### TimescaleDB Hypertables
- `weather_observations` (chunked by observation_time, 1 day)
- `weather_forecasts` (chunked by valid_time, 1 day)

### Spatial Model
```
grid_cells -> grid_ward_intersections -> wards
```
- `grid_ward_intersections` supports a grid cell intersecting multiple wards
- `coverage_fraction` and `intersection_area` available for weighted aggregation

## API Endpoints

| Endpoint | Description | Status |
|----------|-------------|--------|
| GET /api/v1/health | Health check | Implemented |
| GET /api/v1/forecasts | Weather forecasts | Scaffold |
| GET /api/v1/hazards | Hazard assessments | Scaffold |
| GET /api/v1/vulnerability | Vulnerability profiles | Scaffold |
| GET /api/v1/exposure | Exposure profiles | Scaffold |
| GET /api/v1/risk | Risk assessments | Scaffold |
| GET /api/v1/wards | Ward data | Scaffold |
| GET /api/v1/alerts | Active alerts | Scaffold |
| GET /api/v1/models | Scientific models | Scaffold |

## Scientific Models

Registered models (interfaces defined, implementations pending Phase 2):

| Model | Type | Status | Description |
|-------|------|--------|-------------|
| utci-v1 | Thermal Comfort | interface_only | UTCI calculation |
| vulnerability-bbwm-v1 | Vulnerability | interface_only | BBWM vulnerability scoring |
| exposure-bbwm-v1 | Exposure | interface_only | BBWM exposure scoring |
| hsri-multiplicative-v1 | Risk | interface_only | HSRI = H x V x E |

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_database.py -v

# Frontend lint
pnpm --filter heatwave-web lint

# Frontend type-check
pnpm --filter heatwave-web type-check

# Frontend build
pnpm --filter heatwave-web build
```

### Test Coverage
- API startup and health endpoints
- Database module imports
- All 22 domain model imports
- Scientific module imports
- Worker task imports
- Scientific interface contracts

## Linting

```bash
# Run Ruff linting
ruff check apps/ scientific/ pipelines/ tests/

# Run Ruff with auto-fix
ruff check apps/ scientific/ pipelines/ tests/ --fix
```

## Documentation

- [System Overview](docs/architecture/system-overview.md)
- [Data Flow](docs/architecture/data-flow.md)
- [Database Schema](docs/architecture/database.md)
- [Hazard Model](docs/scientific/hazard.md)
- [Vulnerability Model](docs/scientific/vulnerability.md)
- [Exposure Model](docs/scientific/exposure.md)
- [Risk Model](docs/scientific/risk.md)
- [Deployment Guide](docs/operations/deployment.md)
- [Monitoring Guide](docs/operations/monitoring.md)

## Implementation Status

### Phase 1 - IMPLEMENTED
- Repository architecture
- Backend foundation (FastAPI)
- Frontend foundation (Next.js)
- PostgreSQL + PostGIS + TimescaleDB
- Redis/Celery worker foundation
- Database schema (22 tables)
- Alembic migration system
- Spatial data architecture (grid_ward_intersections)
- Weather time-series architecture (hypertables)
- Scientific module interfaces (abstract base classes)
- Scientific configuration management (YAML files)
- API contracts (scaffold)
- Pipeline contracts (scaffold)
- Testing infrastructure
- Docker development environment
- Kubernetes/monitoring scaffolding
- Documentation

### Phase 2 - PLANNED
- UTCI/thermal comfort calculation
- Hazard index calculation
- Vulnerability scoring (BBWM)
- Exposure scoring (BBWM)
- HSRI calculation (H x V x E)
- Risk classification
- Alert generation algorithms
- Real weather-provider integration
- Full GIS analytics

### Later Phases - PLANNED
- Historical Health Dataset
- Mortality/Hospitalization ML
- 3-5 Day Health Impact Prediction
- SMS/WhatsApp integration
- Production alert algorithms

## License

Government of India - Ministry of Earth Sciences
