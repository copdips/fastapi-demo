from app.core.celery import celery_app
from app.core.logging import get_logger

logger = get_logger()


@celery_app.task
def celery_task_demo():
    import time

    time.sleep(2)
    logger.info("Finished task: celery_task_demo")
    return "okok"
