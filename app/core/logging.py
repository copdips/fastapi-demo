import logging

import asgi_correlation_id

from app.config import settings
from app.core.middlewares.request_id import get_request_id


def get_logger():
    return logging.getLogger(settings.api_title_slug)


class RequestIdFilter(logging.Filter):
    # https://github.com/tiangolo/fastapi/issues/397#issuecomment-513480791
    def filter(self, record):
        # record.correlation_id = get_correlation_id()
        record.request_id = get_request_id()
        return True


def configure_logger():
    logger = logging.getLogger(settings.api_title_slug)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(correlation_id)s] [%(request_id)s] - %(name)s - %(message)s",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(settings.logging_level)
    logger.addFilter(asgi_correlation_id.CorrelationIdFilter())
    # logger.addFilter(RequestIdFilter())
