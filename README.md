# Heatwave Early Warning Platform

Extreme Heatwave Early Warning and Human Thermal Stress Index Platform for the Indian Ministry of Earth Sciences.

## Status: Phase 2 Scientific Engine Complete

**Phase 1 is complete. Phase 2 scientific engine is implemented.**

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
| **UTCI polynomial (Fiala 2012)** | **Complete** |
| **Hazard index (UTCI → H)** | **Complete** |
| **Vulnerability scoring (BBWM)** | **Complete** |
| **Exposure scoring (BBWM)** | **Complete** |
| **HSRI = H × V × E** | **Complete** |
| **Vulnerability classifiers** | **Complete** |
| **Exposure classifiers** | **Complete** |
| **DeepTherm interfaces** | **Complete** |
| API contracts (scaffold) | Complete |
| Pipeline contracts (scaffold) | Complete |
| Testing infrastructure | Complete |
| Docker environment | Complete |
| Lint (Ruff) | All checks passed |
| Tests | 116 passed |

## Core Formula

```
HSRI = H × V × E
```

Where:
- **H** = UTCI-derived Hazard Index (0.0 - 1.0)
- **V** = BBWM-derived Vulnerability Index (0.0 - 1.0)
- **E** = BBWM-derived Exposure Index (0.0 - 1.0)

## Phase 2 Scientific Engine

### UTCI (Universal Thermal Climate Index)

Implemented using the Fiala et al. (2012) 210-coefficient polynomial regression, using the exact coefficient set from pythermalcomfort (BSD-3 licensed).

**Inputs:** air temperature (°C), relative humidity (%), wind speed (m/s at 10m), mean radiant temperature (°C)

**Valid ranges:** Ta ∈ [-50, 50]°C, Tmrt ∈ [Ta-30, Ta+70]°C, v ∈ [0.5, 17] m/s, VP ≤ 50 hPa

**Reference verification:**
```
tdb=25, rh=50, v=1, tmrt=25 → UTCI = 24.6°C (matches pythermalcomfort & utci PyPI package)
```

### Hazard Index (H)

Piecewise linear normalization of UTCI to [0, 1]:

| UTCI Range | H Range | Category |
|------------|---------|----------|
| < 9°C | 0.00 | No heat stress |
| 9–26°C | 0.00–0.25 | No thermal stress |
| 26–32°C | 0.25–0.50 | Moderate heat stress |
| 32–38°C | 0.50–0.75 | Strong heat stress |
| 38–46°C | 0.75–1.00 | Very strong heat stress |
| > 46°C | 1.00 | Extreme heat stress |

### Vulnerability Index (V)

Weighted BBWM with 8 factors:

| Factor | Weight | Scoring |
|--------|--------|---------|
| Age | 0.160 | <5→1.0, <24→0.66, ≤40→0.33, ≤65→0.66, >65→1.0 |
| BMI | 0.117 | <17→1.0, <18.5→0.66, <25→0.33, <30→0.66, ≥30→1.0 |
| Economic Status | 0.142 | HIG→0.33, MIG→0.66, LIG/EWS→1.0 |
| Social Isolation | 0.092 | >1 adult→0.33, 1→0.66, alone→1.0 |
| Education | 0.094 | High→0.33, secondary→0.66, none→1.0 |
| Gender | 0.097 | Male→0.66, female/intersex/pregnant→1.0 |
| Health Issues | 0.198 | 0.53×pre_illness + 0.47×medication |
| Disability | 0.100 | None→0.33, below_benchmark→0.66, above→1.0 |

### Exposure Index (E)

Weighted BBWM with 5 components:

| Component | Weight | Sub-weights |
|-----------|--------|-------------|
| Infrastructure/Transit | 0.282 | condition=0.508, facilities=0.492 |
| Lifestyle | 0.184 | alcohol=0.341, sleep=0.232, tobacco=0.218, caffeine=0.208 |
| Fluid/Activity | 0.282 | deficit≤4%→0.33, >4%→1.0 |
| Air Quality | 0.126 | Good/satisfactory→0.33, severe→1.0 |
| Healthcare Access | 0.125 | <30min→0.33, 30-60min→0.66, >60min→1.0 |

### DeepTherm Mortality Model (Architecture Only)

Interfaces created for later mortality prediction:
- **Transformer:** 14-day history, 32-dim positional embedding, 2 attention blocks, 2 heads, 2-layer MLP
- **Random Forest:** 1000 estimators (baseline comparison)
- **Quasi-Poisson:** 2-year rolling baseline for expected non-heat mortality
- **Excess Risk:** R(t) = (X_all_cause - X_non_hr) / X_non_hr; R>0.15→L1, R>0.30→L2

No models trained. No Indian data used. No Spanish data used as Indian data.

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
├── scientific/        # Scientific engine
│   ├── core/          # Abstract base classes
│   ├── thermal_comfort/ # UTCI polynomial (Fiala 2012)
│   ├── hazard/        # UTCI → Hazard normalization
│   ├── vulnerability/ # BBWM vulnerability scoring + classifiers
│   ├── exposure/      # BBWM exposure scoring + classifiers
│   ├── risk/          # HSRI = H × V × E
│   ├── mortality/     # DeepTherm interfaces (no training)
│   └── configuration/ # Scientific configuration YAMLs
├── pipelines/         # Data pipeline stubs
├── db/               # Database SQL files
├── infra/            # Infrastructure (Docker, K8s, monitoring)
├── tests/            # Test suites (116 tests)
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

2. **Run database migrations:**
```bash
cd apps/api
alembic upgrade head
```

3. **Install dependencies:**
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
grid_cells → grid_ward_intersections → wards
```

## Scientific Models

| Model | Type | Status | Description |
|-------|------|--------|-------------|
| utci-polynomial-v1 | Thermal Comfort | **Implemented** | UTCI from Fiala (2012) polynomial |
| vulnerability-bbwm-v1 | Vulnerability | **Implemented** | BBWM vulnerability scoring + classifiers |
| exposure-bbwm-v1 | Exposure | **Implemented** | BBWM exposure scoring + classifiers |
| hsri-multiplicative-v1 | Risk | **Implemented** | HSRI = H × V × E |
| deeptherm-transformer | Mortality | Interface only | 14-day Transformer (not trained) |
| deeptherm-rf | Mortality | Interface only | Random Forest baseline (not trained) |
| deeptherm-qp | Mortality | Interface only | Quasi-Poisson baseline (not trained) |

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/scientific_validation/test_utci_placeholder.py -v

# Frontend lint
pnpm --filter heatwave-web lint

# Frontend type-check
pnpm --filter heatwave-web type-check

# Frontend build
pnpm --filter heatwave-web build
```

### Test Coverage (116 tests)
- API startup and health endpoints
- Database module imports
- All 22 domain model imports
- Scientific module imports
- UTCI polynomial verification (matches reference implementation)
- Hazard normalization (boundary tests)
- Vulnerability scoring (all factor classifiers)
- Exposure scoring (all factor classifiers)
- HSRI calculation (boundary tests)
- Configuration validation (weight sums, scoring order)
- DeepTherm interface contracts
- Chain integration (UTCI → H)

## Scientific Discrepancies

### Diagnostic Vulnerability Case
- **Expected:** V ≈ 0.407
- **Computed:** V = 0.4006
- **Discrepancy:** 0.0064 (rounding in source specification scores 0.33/0.66 vs exact 1/3, 2/3)
- **Action:** Weights not modified. Discrepancy documented.

### UTCI Reference Test Cases
The supplied reference test cases (prompt.txt) use approximate expected values. Our implementation matches the reference Fortran-derived `utci` PyPI package and pythermalcomfort exactly. Small deviations from the supplied approximate values are expected.

## Documentation

- [System Overview](docs/architecture/system-overview.md)
- [Data Flow](docs/architecture/data-flow.md)
- [Database Schema](docs/architecture/database.md)
- [Phase 2 Specification](docs/scientific/phase-2-scientific-specification.md)
- [Hazard Model](docs/scientific/hazard.md)
- [Vulnerability Model](docs/scientific/vulnerability.md)
- [Exposure Model](docs/scientific/exposure.md)
- [Risk Model](docs/scientific/risk.md)
- [Open Questions](docs/scientific/open-questions.md)
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

### Phase 2 - IMPLEMENTED
- UTCI polynomial calculation (Fiala et al. 2012, 210 coefficients)
- Hazard index normalization (UTCI → H, piecewise linear)
- Vulnerability scoring (BBWM, 8 factors with raw-to-score classifiers)
- Exposure scoring (BBWM, 5 components with raw-to-score classifiers)
- HSRI calculation (H × V × E with residual-risk floors)
- Risk classification (LOW/MEDIUM/HIGH)
- Configuration validation (weight sums, scoring order, bounds)
- DeepTherm mortality model interfaces (Transformer, RF, Quasi-Poisson)
- 116 tests, ruff clean

### Later Phases - PLANNED
- DeepTherm model training (with Indian mortality/health data)
- Historical Health Dataset collection
- 3-5 Day Health Impact Prediction
- Real weather-provider integration
- Full GIS analytics
- SMS/WhatsApp integration
- Production alert algorithms

## Commits

### Phase 2
```
e76fd0f  Phase 2: UTCI polynomial fix, vulnerability/exposure classifiers, DeepTherm interfaces
5377bb8  fix hazard-category bug, semantic tests, config-driven constants
7741f5b  unified contracts, config validation, UTCI placeholder, chain
eff5a29  config-driven scientific engine
3b8af05  initial Phase 2 scientific modules
```

### Phase 1
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

## License

Government of India - Ministry of Earth Sciences
