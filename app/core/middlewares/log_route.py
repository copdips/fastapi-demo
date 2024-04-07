import contextlib
from typing import Any

import orjson
from starlette.datastructures import Headers
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.routing import Match

from app.core.logging import get_logger

logger = get_logger()


def remove_secrets_from_headers(headers: Headers) -> dict[str, Any]:
    return {
        f"headers_{k.lower()}": v
        for k, v in headers.items()
        if k.lower() not in ["authorization", "cookie"]
    }


def get_path_params(request: Request) -> dict[str, Any]:
    # ! path_params is not available in middleware, so request.path_params is always empty
    # we need to iterate over all the routes to get the path_params, but this takes time.
    # https://github.com/tiangolo/fastapi/discussions/7902#discussioncomment-5145119
    routes = request.app.router.routes
    for route in routes:
        match, scope = route.matches(request)
        if match == Match.FULL:
            return scope["path_params"]
    return {}


class LogRouteMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        safe_request_headers = remove_secrets_from_headers(request.headers)
        method = request.method
        path = request.url.path
        # ! must not read body inside middleware if it's a stream request
        # https://github.com/encode/starlette/issues/495#issuecomment-494008175
        body_dict = {}
        with contextlib.suppress(Exception):
            body_dict = await request.json()
        body_bytes = await request.body()
        request_msg = f"new request: {method} {path}"
        path_params = get_path_params(request)
        extra: dict[str, Any] = {
            "type": "request",
            "method": request.method,
            "url": str(request.url),
            "base_url": str(request.base_url),
            "path": str(request.url.path),
            "headers": orjson.dumps(
                safe_request_headers,
                option=orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY,
            ),
            "path_params": orjson.dumps(path_params),
            "query_params": str(request.url.query),
            "body": body_bytes,
            "body_dict": orjson.dumps(
                body_dict,
                option=orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY,
            ),
            "client": str(request.client),
        }
        logger.info(
            request_msg,
            extra=extra,
        )
        response = await call_next(request)
        response_msg = f"new response: {method} {path}"
        safe_response_headers = remove_secrets_from_headers(response.headers)
        logger.info(
            response_msg,
            extra={
                "type": "response",
                "status_code": response.status_code,
                "headers": orjson.dumps(
                    safe_response_headers,
                    option=orjson.OPT_NAIVE_UTC | orjson.OPT_SERIALIZE_NUMPY,
                ),
            },
        )

        return response
