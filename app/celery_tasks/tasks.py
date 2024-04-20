from app.core.celery import celery_app
from app.core.logging import get_logger

logger = get_logger()


@celery_app.task(queue="low")
def celery_task_demo_queue_low(sleep_seconds: int = 2):
    import time

    time.sleep(sleep_seconds)
    logger.info("Finished task: celery_task_demo_queue_low")
    return "ok for celery_task_demo_queue_low"


@celery_app.task(queue="high")
def celery_task_demo_queue_high(sleep_seconds: int = 2):
    import time

    time.sleep(sleep_seconds)
    logger.info("Finished task: celery_task_demo_queue_high")
    return "ok for celery_task_demo_queue_high"
