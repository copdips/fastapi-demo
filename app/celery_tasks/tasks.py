from celery import chain, group
from celery.schedules import crontab

from app.core.celery import celery_app
from app.core.logging import get_logger

logger = get_logger()


@celery_app.task(queue="low")
def celery_task_q_low_in_schedule(sleep_seconds: int = 2):
    import time

    time.sleep(sleep_seconds)
    logger.info("Finished task: celery_task_q_low_in_schedule")
    return "ok for celery_task_q_low_in_schedule"


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
        1 / 0  # noqa: B018, pyright: ignore[reportUnusedExpression]
        logger.info("Finished task: celery_task_q_high")
    except Exception as ex:
        msg = f"Got exception in task: celery_task_q_high with error: {ex}"
        logger.exception(msg)
        # countdown specifies the delay before retrying the task
        raise self.retry(exc=ex, countdown=2)  # noqa: B904
    else:
        return "ok for celery_task_q_high"


celery_app.conf.beat_schedule = {
    "celery_task_q_low_in_schedule-every_minute": {
        "task": "app.celery_tasks.tasks.celery_task_q_low_in_schedule",
        "schedule": crontab(),
        "args": [2],  # args must be iterable, list or tuple all ok.
        "options": {
            "expires": 15.0,
        },
    },
}

# grouped task returns a new group task result
group_celery_task_q_low = group(
    celery_task_q_low.s(2)  # pyright: ignore[reportFunctionMemberAccess]
    for _ in range(10)
)

# chained task return the last task's result, can be queried by AsyncResult
# if use s(), the return of the previous task will e the argument of the next task
# with si(), the argument of the next task will e independent of the previous task's return
# https://docs.celeryq.dev/en/latest/userguide/canvas.html#immutability
chain_celery_task_q_low = chain(
    celery_task_q_low.si(2),  # pyright: ignore[reportFunctionMemberAccess]
    celery_task_q_low.si(2),  # pyright: ignore[reportFunctionMemberAccess]
)
