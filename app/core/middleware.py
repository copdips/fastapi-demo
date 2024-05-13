from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from msgpack_asgi import MessagePackMiddleware
from opentelemetry import trace

from app.config import settings
from app.core.db import async_session_factory, init_db
from app.core.logging import force_flush_logs, get_logger
from app.core.middlewares.log_route import LogRouteMiddleware
from app.core.middlewares.profiling import PyInstrumentMiddleware
from app.core.middlewares.request_id import RequestContextLogMiddleware
from app.core.taskiq import taskiq_broker

logger = get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # access app.state in request by request.app.state:
    # https://github.com/tiangolo/fastapi/discussions/8054#discussioncomment-5146686
    # ! be careful if the value is changed in the request, it wont change the value in the app running in other process, or in other node. The change is app local.
    _app.state.settings = settings
    if settings.testing:
        await init_db(async_session_factory)
    await taskiq_broker.startup()

    logger.info("App started successfully.")
    yield
    # even got ctrl+c SIGINT signal, this block will be executed.
    # but if we close the bash console forcefully, this block will not be executed.
    logger.info("App is shutting down.")
    force_flush_logs()
    # trace_provider.force_flush(2000)
    # meter_provider.force_flush(2000)
    # log_provider.force_flush(2000)
    # this final message will only be shown in the console.
    logger.info("App shutdown successfully.")


def get_formatted_trace_id() -> str:
    # return 32-bytes long format of trace id
    span = trace.get_current_span()
    trace_id = span.get_span_context().trace_id
    return trace.format_trace_id(trace_id)


def register_middlewares(_app: FastAPI):
    # ! multiple middlewares order:
    # https://github.com/tiangolo/fastapi/issues/5018#issuecomment-1152795409
    # ! after test, first added middleware is called last
    # _app.add_middleware(A)
    # _app.add_middleware(B)
    #  request -> B -> A
    #  B -> A -> response
    # apitally dashboard: https://app.apitally.io/traffic/fastapi-demo?period=24h
    # ! to add consumer_identifier, add it in request depends:
    # https://docs.apitally.io/frameworks/fastapi#identify-consumers
    # request.state.consumer_identifier = current_user.username
    # _app.add_middleware(
    #     ApitallyMiddleware,
    #     client_id=settings.apitally_client_id,
    #     env="dev",  # or "prod"
    # )

    """
    https://github.com/florimondmanca/msgpack-asgi
    curl -X 'GET' 'http://localhost:8000/v1/health/' -H 'accept: application/json'
    curl -X 'GET' 'http://localhost:8000/v1/health/' -H 'accept: application/x-msgpack'
    """
    _app.add_middleware(MessagePackMiddleware)
    # https://fastapi.tiangolo.com/advanced/middleware/#gzipmiddleware
    _app.add_middleware(GZipMiddleware, minimum_size=1000)
    _app.add_middleware(LogRouteMiddleware)
    _app.add_middleware(
        # ! CorrelationIdMiddleware could use BaseHTTPMiddleware as
        # StreamingResponse/FileResponse issue has been resolved:
        # https://github.com/encode/starlette/issues/1012#issuecomment-673461832
        CorrelationIdMiddleware,
        header_name="x-correlation-id",  # locally generated unique x-request-id is handled by RequestContextLogMiddleware
        # ULID is not used as generator for a better consistency, and CorrelationIdMiddleware generates by default uuid4 by eliminating the hyphen, which is very nice for copy.
        # as if x-request-id is given by client, CorrelationIdMiddleware only validates uuid format, but not ULID.
        # Otherwise, we need to also provide a validator for ULID.
        # generator=lambda: str(ULID()),
        # in opentelemetry, each request has a unique trace id, all the spans within the same request share the same trace id.
        generator=get_formatted_trace_id,
    )
    # ! RequestContextLogMiddleware is not compatible with ApitallyMiddleware
    _app.add_middleware(RequestContextLogMiddleware)
    if settings.profiling:
        # run profyle start to start the ProfyleMiddleware profiling
        # and visit http://127.0.0.1:5432 to see the result
        _app.add_middleware(PyInstrumentMiddleware)
        # if settings.debug:
        #     _app.add_middleware(ProfyleMiddleware)
