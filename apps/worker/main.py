"""Worker application - Celery configuration."""
import os
from celery import Celery
from celery.signals import worker_ready, worker_shutting_down
import structlog

logger = structlog.get_logger()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://heatwave:CHANGE_ME@localhost:5432/heatwave_db",
)

app = Celery("heatwave_worker")
app.config_from_object({
    "broker_url": REDIS_URL,
    "result_backend": REDIS_URL,
    "task_serializer": "json",
    "result_serializer": "json",
    "accept_content": ["json"],
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_time_limit": 3600,
    "task_soft_time_limit": 3000,
    "worker_prefetch_multiplier": 1,
    "worker_max_tasks_per_child": 100,
})

app.autodiscover_tasks(["worker.tasks"])

worker_ready.connect(lambda sender, **kwargs: logger.info("worker_started"))
worker_shutting_down.connect(lambda sender, **kwargs: logger.info("worker_shutting_down"))


@app.task(bind=True, name="worker.heartbeat")
def heartbeat(self):
    """Worker heartbeat task for monitoring."""
    return {
        "status": "ok",
        "worker_id": self.request.id,
        "hostname": self.request.hostname,
    }
