import logging

from app.settings import settings


def get_logger():
    logger = logging.getLogger(settings.api_title_slug)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(settings.logging_level)
    return logger
