from typing import Any

from asgi_correlation_id import correlation_id
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from opentelemetry import trace
from sqlalchemy.exc import NoResultFound

from app_domain_based.core.logging import get_logger
from app_domain_based.core.middlewares.request_id import get_request_id


class NotFoundError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class UnauthorizedError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


EXCEPTION_AND_STATUS_CODE = [
    (NoResultFound, status.HTTP_404_NOT_FOUND),
    (NotFoundError, status.HTTP_404_NOT_FOUND),
    (UnauthorizedError, status.HTTP_403_FORBIDDEN),
]


def get_operation_from_request(request: Request) -> dict[str, Any]:
    path = request.url.path
    method = request.method
    return {
        "method": method,
        "path": path,
        "operation": f"{method.upper()} {path}",
    }


def log_exception(ex: Exception, request: Request):
    logger = get_logger()
    # it seems that for whatever instrumenting_module_name we use, we get the same trace
    # but the doc says that we should be take care of the instrumenting_module_name,
    # it should be the same with in the app:
    # https://github.com/open-telemetry/opentelemetry-python/blob/eef2015edd0d7c0a85840fd7bd1c7d57f1a8c2ee/opentelemetry-api/src/opentelemetry/trace/__init__.py#L202-L212
    # ! to be tested more
    # tracer = trace.get_tracer("opentelemetry.instrumentation.asgi")
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("log_expcetion") as span:
        current_correlation_id = correlation_id.get() or ""
        err_msg = f"[correlation_id: {current_correlation_id}] Got error: {ex}"
        logger.exception(
            err_msg,
            extra=get_operation_from_request(request)
            | {"exception_name": ex.__class__.__name__},
        )
        span.set_attribute("exception_name", ex.__class__.__name__)
        span.set_attribute("exception_message", err_msg)


def register_exception_handler(app: FastAPI, exception: Any, status_code: int):
    @app.exception_handler(exception)
    async def exception_handler(
        request: Request,  # , Unused function argument
        ex: Any,
    ):
        log_exception(ex, request)
        return JSONResponse(status_code=status_code, content={"message": str(ex)})


def register_unhandled_exception(app: FastAPI):
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        ex: Exception,
    ):
        log_exception(ex, request)
        current_correlation_id = correlation_id.get() or ""
        current_request_id = get_request_id()
        exc_name = ex.__class__.__name__
        return await http_exception_handler(
            request,
            HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    f"Internal server error {exc_name} occurred, "
                    f"correlation_id: {current_correlation_id} "
                    f"request_id: {current_request_id}, "
                ),
                headers={
                    "X-Correlation-ID": current_correlation_id,
                    "X-Request-ID": current_request_id,
                },
            ),
        )


def register_exception_handlers(app: FastAPI):
    register_unhandled_exception(app)
    for exception, status_code in EXCEPTION_AND_STATUS_CODE:
        register_exception_handler(app, exception, status_code)
