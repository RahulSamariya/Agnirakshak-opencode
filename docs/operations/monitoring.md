# Monitoring Guide

## Overview

The platform supports structured logging, metrics, and health checks.

## Health Endpoints

- `GET /api/v1/health` - Basic health check
- `GET /api/v1/health/ready` - Readiness check

## Structured Logging

All logs are output in JSON format with:
- Timestamp
- Log level
- Logger name
- Message
- Correlation ID (from request headers)

## Metrics

Prometheus metrics are exposed at `/metrics` on the API.

### Key Metrics

- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request duration
- `celery_tasks_total` - Total Celery tasks
- `celery_task_duration_seconds` - Task duration

## Monitoring Stack

### Prometheus

Configuration: `infra/monitoring/prometheus.yml`

Scrape targets:
- API (port 8000)
- Worker (port 8080)
- Redis (port 6379)
- PostgreSQL (port 5432)

### Grafana

Configuration: `infra/monitoring/grafana-datasources.yml`

Data sources:
- Prometheus
- PostgreSQL

## Alerting

### Application Alerts

Alerts are generated based on risk thresholds:
- LOW: HSRI 0 - 0.33
- MEDIUM: HSRI 0.33 - 0.66
- HIGH: HSRI 0.66 - 1.00

### Infrastructure Alerts

Monitor:
- API response time
- Worker queue length
- Database connection pool
- Redis memory usage
