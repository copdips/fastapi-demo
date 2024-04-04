import logging

import asgi_correlation_id

from app.settings import settings


def get_logger():
    return logging.getLogger(settings.api_title_slug)


def configure_logger():
    logger = logging.getLogger(settings.api_title_slug)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - [%(correlation_id)s] - %(name)s - %(message)s",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(settings.logging_level)
    logger.addFilter(asgi_correlation_id.CorrelationIdFilter())
