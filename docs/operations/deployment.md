# Deployment Guide

## Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Node.js 20+

## Local Development

### Start Infrastructure

```bash
docker-compose up -d
```

This starts:
- PostgreSQL with PostGIS and TimescaleDB (port 5432)
- Redis (port 6379)

### Start API

```bash
cd apps/api
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API available at: http://localhost:8000
API docs at: http://localhost:8000/docs

### Start Worker

```bash
cd apps/worker
pip install -r requirements.txt
celery -A worker.main worker --loglevel=info
```

### Start Frontend

```bash
cd apps/web
npm install
npm run dev
```

Frontend available at: http://localhost:3000

## Database Migrations

```bash
cd apps/api
alembic upgrade head
```

## Production Deployment

### Docker Build

```bash
docker build -f infra/docker/Dockerfile.api -t heatwave-api .
docker build -f infra/docker/Dockerfile.worker -t heatwave-worker .
docker build -f infra/docker/Dockerfile.web -t heatwave-web .
```

### Kubernetes

```bash
kubectl apply -f infra/kubernetes/namespace.yaml
kubectl apply -f infra/kubernetes/
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| DATABASE_URL | PostgreSQL connection string | postgresql+asyncpg://heatwave:heatwave_secret@localhost:5432/heatwave_db |
| REDIS_URL | Redis connection string | redis://localhost:6379/0 |
| ENVIRONMENT | Environment name | development |
| API_V1_PREFIX | API prefix | /api/v1 |
