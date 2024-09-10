from celery import Celery

# Configura el broker y backend
celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',  # Redis como broker
    backend='redis://localhost:6379/0',  # Redis como backend
)

# Configuración opcional
celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)