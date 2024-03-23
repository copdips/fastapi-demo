from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import NoResultFound


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


def register_exception_handlers(app: FastAPI):
    for exception, status_code in EXCEPTION_AND_STATUS_CODE:
        register_exception_handler(app, exception, status_code)
