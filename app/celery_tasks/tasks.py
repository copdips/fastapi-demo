from app.core.celery import celery_app
from app.core.logging import get_logger

logger = get_logger()


@celery_app.task(queue="low")
def celery_task_demo_queue_low():
    import time

    time.sleep(2)
    logger.info("Finished task: celery_task_demo")
    return "okok"


@celery_app.task(queue="high")
def celery_task_demo_queue_high():
    import time

    time.sleep(2)
    logger.info("Finished task: celery_task_demo")
    return "okok"
