from typing import Any

from asgi_correlation_id import correlation_id
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound

from app.core.logging import get_logger
from app.core.middlewares.request_id import get_request_id


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


def register_exception_handler(app: FastAPI, exception: Any, status_code: int):
    @app.exception_handler(exception)
    async def exception_handler(
        request: Request,  # noqa: ARG001, Unused function argument
        exc: Any,
    ):
        return JSONResponse(status_code=status_code, content={"message": str(exc)})


def register_unhandled_exception(app: FastAPI):
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        ex: Exception,
    ):
        logger = get_logger()
        current_correlation_id = correlation_id.get() or ""
        current_request_id = get_request_id()
        err_msg = (
            f"correlation_id: {current_correlation_id}, "
            f"request_id: {current_request_id}, "
            f"Internal server error occurred: {ex}"
        )
        logger.exception(err_msg)
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
