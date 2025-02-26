from fastapi import Request
from fastapi.responses import HTMLResponse
from pyinstrument import Profiler
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app_domain_based.config import settings


class PyInstrumentMiddleware(BaseHTTPMiddleware):
    # https://pyinstrument.readthedocs.io/en/latest/guide.html#profile-a-web-request-in-fastapi
    # To invoke, make any request to your application with the GET parameter profile=1
    # and it will print the HTML result from pyinstrument.
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        profiling = request.query_params.get("profile", False)
        if profiling:
            profiler = Profiler(
                interval=settings.profiling_interval_seconds,
                async_mode="enabled",
            )
            profiler.start()
            await call_next(request)
            profiler.stop()

            return HTMLResponse(profiler.output_html())

        return await call_next(request)
