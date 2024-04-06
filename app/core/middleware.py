from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from profyle.fastapi import ProfyleMiddleware

from app.config import settings
from app.core.db import async_session_factory, init_db
from app.core.middlewares.profiling import PyInstrumentMiddleware
from app.core.middlewares.request_id import RequestContextLogMiddleware


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # access app.state in request by request.app.state:
    # https://github.com/tiangolo/fastapi/discussions/8054#discussioncomment-5146686
    # ! be careful if the value is changed in the request, it wont change the value in the app running in other process, or in other node. The change is app local.
    _app.state.settings = settings
    if settings.testing:
        await init_db(async_session_factory)
    yield


def register_middlewares(_app: FastAPI):
    # ! multiple middlewares order:
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
    )
    # ! RequestContextLogMiddleware is not compatible with ApitallyMiddleware
    _app.add_middleware(RequestContextLogMiddleware)
    if settings.profiling:
        # run profyle start to start the ProfyleMiddleware profiling
        # and visit http://127.0.0.1:5432 to see the result
        _app.add_middleware(PyInstrumentMiddleware)
        if settings.debug:
            _app.add_middleware(ProfyleMiddleware)
