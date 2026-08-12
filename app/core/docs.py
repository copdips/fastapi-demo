from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference


def add_scalar_docs(app: FastAPI):
    @app.get("/scalar", include_in_schema=False)
    async def scalar_html():
        return get_scalar_api_reference(
            # Your OpenAPI document
            openapi_url=app.openapi_url,
            # Avoid CORS issues (optional)
            scalar_proxy_url="https://proxy.scalar.com",
        )
