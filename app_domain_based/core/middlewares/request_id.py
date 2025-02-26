# https://github.com/tiangolo/fastapi/issues/397#issuecomment-513480791
from contextvars import ContextVar
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request

# CORRELATION_ID_CTX_KEY = "correlation_id"
REQUEST_ID_CTX_KEY = "request_id"

# _correlation_id_ctx_var: ContextVar[str | None] = ContextVar(
#     CORRELATION_ID_CTX_KEY, default=None
# )
_request_id_ctx_var: ContextVar[str | None] = ContextVar(
    REQUEST_ID_CTX_KEY,
    default=None,
)


# def get_correlation_id() -> str:
#     return _correlation_id_ctx_var.get()


def get_request_id() -> str:
    return _request_id_ctx_var.get() or ""


class RequestContextLogMiddleware(BaseHTTPMiddleware):
    # ! BaseHTTPMiddleware is not good when dealing with ContextVar,
    # use pure AGSI Middleware instead, like what it does in CorrelationIdMiddleware.
    # https://www.starlette.io/middleware/#limitations
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        # correlation_id = _correlation_id_ctx_var.set(
        #     request.headers.get(
        #         "X-Correlation-ID",
        #         uuid4().hex,
        #     ),
        # )
        request_id = _request_id_ctx_var.set(uuid4().hex)

        response = await call_next(request)
        # response.headers["X-Correlation-ID"] = get_correlation_id()
        response.headers["X-Request-ID"] = get_request_id()

        # _correlation_id_ctx_var.reset(correlation_id)
        _request_id_ctx_var.reset(request_id)

        return response
