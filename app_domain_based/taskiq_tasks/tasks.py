import asyncio

from app_domain_based.core.logging import get_logger
from app_domain_based.core.taskiq import taskiq_broker

logger = get_logger()


@taskiq_broker.task()
async def taskiq_task_q_low(sleep_seconds: int = 2):
    await asyncio.sleep(sleep_seconds)
    logger.info("Finished task: taskiq_task_q_low")
    return "ok for taskiq_task_q_low"
