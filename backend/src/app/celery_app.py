from celery import Celery
from app.config.settings import settings

celery_app = Celery(
    'app',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'app.tasks.deposit_monitoring_tasks',
        'app.tasks.sweep_tasks'
    ]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 година
    worker_max_tasks_per_child=1000,
    worker_prefetch_multiplier=1,
    
    beat_schedule={
        'monitor-deposits': {
            'task': 'monitor_deposits',
            'schedule': 60.0,  # кожну хвилину
        },
        'confirm-deposits': {
            'task': 'confirm_deposits',
            'schedule': 60.0,  # кожну хвилину
        },
        'sweep-derived-addresses': {
            'task': 'sweep_derived_addresses',
            'schedule': 300.0,  # кожні 5 хвилин
        },
        'confirm-sweeps': {
            'task': 'confirm_sweeps',
            'schedule': 60.0,  # кожну хвилину
        }
    }
) 