"""
Celery Application Configuration
"""
import os
from celery import Celery
from celery.schedules import crontab

# Redis connection from environment
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "vajra_core",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.audit_tasks",
        "app.tasks.report_tasks",
        "app.tasks.upload_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3000,  # 50 minutes soft limit
    task_acks_late=True,  # Acknowledge after task completion
    worker_prefetch_multiplier=1,  # One task at a time per worker
    
    # Result backend settings
    result_expires=86400,  # Results expire after 24 hours
    result_backend_transport_options={
        'master_name': 'mymaster',
        'socket_keepalive': True,
        'retry_on_timeout': True
    },
    
    # Worker settings
    worker_max_tasks_per_child=1000,  # Restart worker after 1000 tasks
    worker_disable_rate_limits=False,
    
    # Routing
    task_routes={
        'app.tasks.audit_tasks.*': {'queue': 'audit'},
        'app.tasks.report_tasks.*': {'queue': 'reports'},
        'app.tasks.upload_tasks.*': {'queue': 'upload'}
    },
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'cleanup-old-audits': {
            'task': 'app.tasks.audit_tasks.cleanup_old_audits',
            'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
        },
        'generate-daily-summary': {
            'task': 'app.tasks.report_tasks.generate_daily_summary',
            'schedule': crontab(hour=6, minute=0),  # Run at 6 AM daily
        }
    }
)

# Optional: Configure Redis Socket keepalive
celery_app.conf.broker_transport_options = {
    'visibility_timeout': 3600,
    'fanout_prefix': True,
    'fanout_patterns': True,
    'socket_keepalive': True,
    'socket_keepalive_options': {
        1: 1,  # TCP_KEEPIDLE
        2: 1,  # TCP_KEEPINTVL
        3: 5   # TCP_KEEPCNT
    }
}
