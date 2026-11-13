"""taskiq

worker:
taskiq worker app_standard.core.taskiq:taskiq_broker
"""

from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from app_standard.config import settings

taskiq_broker = AioPikaBroker(
    settings.rabbitmq_url,
).with_result_backend(RedisAsyncResultBackend(f"redis://{settings.redis_host}"))
