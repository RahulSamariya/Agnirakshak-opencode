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
PostgreSQL 16.15                PASS
PostGIS 3.6 (5 geometry cols)  PASS
TimescaleDB 2.29.2              PASS
Alembic clean migration         PASS
Weather hypertables (2)         PASS
Spatial model verification      PASS
API startup                     PASS
Worker startup                  PASS
Frontend build                  PASS
Frontend typecheck              PASS
Frontend lint                   PASS
Secrets check                   PASS
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
