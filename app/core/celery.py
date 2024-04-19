"""celery

worker:
celery -A app.core.celery worker --loglevel=info

flower:
celery -A app.core.celery flower --loglevel=info --port=5555
flower default port is to 5555
http://localhost:5555/
"""

from celery import Celery

from app.config import settings

celery_app = Celery(
    settings.api_title_slug,
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    broker_connection_retry_on_startup=True,
)

# app.celery_tasks module must has a file called tasks.py to let celery discover it,
# otherwise the task file name should be specified too, if the file name is celery_tasks.py, then:
# ["app.celery_tasks.celery_tasks"]
celery_app.autodiscover_tasks(["app.celery_tasks"], force=True)
