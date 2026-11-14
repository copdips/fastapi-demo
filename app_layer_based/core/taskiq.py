"""taskiq

worker:
taskiq worker app_layer_based.core.taskiq:taskiq_broker
"""

from taskiq_aio_pika import AioPikaBroker
from taskiq_redis import RedisAsyncResultBackend

from app_layer_based.config import settings

taskiq_broker = AioPikaBroker(
    settings.rabbitmq_url,
).with_result_backend(RedisAsyncResultBackend(f"redis://{settings.redis_host}"))
