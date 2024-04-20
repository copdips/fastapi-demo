from app.core.celery import celery_app
from app.core.logging import get_logger

logger = get_logger()


@celery_app.task(queue="low")
def celery_task_q_low(sleep_seconds: int = 2):
    import time

    time.sleep(sleep_seconds)
    logger.info("Finished task: celery_task_q_low")
    return "ok for celery_task_q_low"


@celery_app.task(queue="high", bind=True, max_retries=3)
def celery_task_q_high(self, sleep_seconds: int = 2):
    try:
        import time

        time.sleep(sleep_seconds)
        1 / 0  # noqa: B018
        logger.info("Finished task: celery_task_q_high")
    except Exception as ex:
        msg = f"Got exception in task: celery_task_q_high with error: {ex}"
        logger.exception(msg)
        # countdown specifies the delay before retrying the task
        raise self.retry(exc=ex, countdown=2)  # noqa: B904
    else:
        return "ok for celery_task_q_high"
