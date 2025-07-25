import asyncio
import logging
import os
from functools import wraps
from typing import Any

import asgi_correlation_id
import logfire
import sentry_sdk
from asgi_correlation_id import correlation_id
from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.asgi import OpenTelemetryMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from typing_extensions import deprecated

from app.config import settings
from app.core.middlewares.request_id import get_request_id


def get_logger():
    # must be used after configure_logger()
    return logging.getLogger(settings.api_title_slug)


class RequestIdFilter(logging.Filter):
    # https://github.com/tiangolo/fastapi/issues/397#issuecomment-513480791
    def filter(self, record: logging.LogRecord):
        # record.correlation_id = get_correlation_id()
        record.request_id = get_request_id()
        return True


class StaticExtraLogFilter(logging.Filter):
    def __init__(self, static_extra: dict[str, Any]) -> None:
        self.static_extra_tuples = tuple(static_extra.items())
        super().__init__()

    def filter(self, record: logging.LogRecord) -> bool:
        for k, v in self.static_extra_tuples:
            setattr(record, k, v)
        return True


def force_flush_logs():
    logger = get_logger()
    for h in logger.handlers:
        h.flush()
        # opentelemetry add _logger_provider to handlers
        if hasattr(h, "_logger_provider") and hasattr(
            h._logger_provider,  # pyright: ignore [reportAttributeAccessIssue]  # noqa: SLF001
            "force_flush",
        ):
            h._logger_provider.force_flush()  # pyright: ignore [reportAttributeAccessIssue]  # noqa: SLF001


def configure_logger(fastapi_app: FastAPI):
    sentry_sdk.init(
        # https://github.com/getsentry/sentry-python/blob/master/sentry_sdk/integrations/fastapi.py
        # although the doc says that if dns is not provided,
        # https://docs.sentry.io/concepts/key-terms/dsn-explainer/#what-the-dsn-does
        # it will search for SENTRY_DSN, the test shows KO,
        # so we need to provide the dsn explicitly
        dsn=settings.logging_settings.SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )
    # correlation_id.set(""), set default context var value to avoid opentelemetry span error:
    # Invalid type NoneType for attribute 'correlation_id' value.
    # Expected one of ['bool', 'str', 'bytes', 'int', 'float'] or a sequence of those types
    correlation_id.set("")
    if settings.enable_azure_monitor:
        configure_azure_monitor(
            logger_name=settings.api_title_slug,
        )
    logger = logging.getLogger(settings.api_title_slug)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s"
        " - %(levelname)s"
        " - [%(api_title_slug)s]"
        "[%(api_version)s]"
        "[%(api_env)s]"
        " - [%(correlation_id)s][%(request_id)s]"
        ": %(message)s",
    )
    stream_handler.setFormatter(formatter)
    if os.environ.get("TESTING") != "yes":
        logger.addHandler(stream_handler)
    logger.setLevel(settings.logging_level)
    logger.addFilter(asgi_correlation_id.CorrelationIdFilter())
    logger.addFilter(RequestIdFilter())
    logger.addFilter(StaticExtraLogFilter(settings.logging_static_extra))
    FastAPIInstrumentor.instrument_app(fastapi_app)

    # Pydantic logfire
    logfire.configure()
    logfire.instrument_fastapi(fastapi_app)

    # append trace info in error handler:
    # https://github.com/open-telemetry/opentelemetry-python/issues/3477#issuecomment-1915743854
    OpenTelemetryMiddleware(
        fastapi_app,
    )
    logger.info("logger configured")


@deprecated(
    """
    🚨 no need to add the decorator @trace_function anymore,
    as tracing is automatically enabled for FastAPI by:
    https://opentelemetry-python-contrib.readthedocs.io/en/latest/instrumentation/fastapi/fastapi.html#usage
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    FastAPIInstrumentor.instrument_app(app)

    @trace_function is still kept here to reference, usage:
    add `@trace_function` to the route function to enable tracing, between `@router` and `async def`:
        @router.get("/")
        @trace_function
        async def get_tags(): ...
    """,
)
def trace_function(func):
    tracer = trace.get_tracer(settings.api_title_slug)
    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def wrapper_async(*args, **kwargs):
            with tracer.start_as_current_span(func.__name__):
                return await func(*args, **kwargs)

        return wrapper_async

    @wraps(func)
    def wrapper_sync(*args, **kwargs):
        with tracer.start_as_current_span(func.__name__):
            return func(*args, **kwargs)

    return wrapper_sync
