"""
Celery worker application for background tasks.
"""

import os
from celery import Celery
from kombu import Queue

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Celery configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
app = Celery(
    "reddit-worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks.alerts", "tasks.indexing"],
)

# Configuration
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Queue configuration
app.conf.task_routes = {
    "tasks.alerts.*": {"queue": "alerts"},
    "tasks.indexing.*": {"queue": "indexing"},
}

app.conf.task_default_queue = "default"
app.conf.task_queues = (
    Queue("default"),
    Queue("alerts"),
    Queue("indexing"),
)

# Beat schedule for periodic tasks (TODO: implement)
app.conf.beat_schedule = {
    # 'scan-alerts': {
    #     'task': 'tasks.alerts.scan_all_alerts',
    #     'schedule': 60.0 * 15,  # Every 15 minutes
    # },
}

if __name__ == "__main__":
    app.start()
