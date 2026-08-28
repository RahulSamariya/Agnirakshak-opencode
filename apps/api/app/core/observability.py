"""Observability configuration for the Heatwave Platform."""
import logging
import uuid
from typing import Any

import structlog
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


def configure_logging(log_level: str = "INFO") -> None:
    """Configure structured logging with structlog."""
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level.upper(), logging.INFO),
    )


class RequestCorrelationMiddleware(BaseHTTPMiddleware):
    """Middleware to add correlation ID to each request."""

    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get(
            "X-Correlation-ID", str(uuid.uuid4())
        )
        request.state.correlation_id = correlation_id

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class HealthChecker:
    """Centralized health checking for application components."""

    def __init__(self):
        self.checks: dict[str, Any] = {}

    def register_check(self, name: str, check_fn):
        """Register a health check function."""
        self.checks[name] = check_fn

    async def run_checks(self) -> dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        for name, check_fn in self.checks.items():
            try:
                result = await check_fn()
                results[name] = {"status": "healthy", "details": result}
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
        return results


health_checker = HealthChecker()
