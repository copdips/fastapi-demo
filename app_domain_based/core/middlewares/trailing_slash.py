from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RemoveTailingSlashMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint):
        if request.url.path.endswith("/") and request.url.path != "/":
            return RedirectResponse(url=request.url.path.rstrip("/"), status_code=308)
        return await call_next(request)
