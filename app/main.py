from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute
from fastapi_mcp import add_mcp_server

from app.config import settings
from app.core.db import engine
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logger
from app.core.middleware import lifespan, register_middlewares
from app.core.router import register_routers
from app.core.sql_admin import init_sqladmin
from app.routes import v1_routes


def custom_generate_unique_id(route: APIRoute) -> str:
    # output: health-get_health@v1
    tags = route.tags
    # fastapi-mcp mounts /mount route without tags
    tag = tags[0] if tags else "default"
    return f"{tag}-{route.name}@{route.path.split('/')[1]}"


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        contact=settings.api_contact,
        lifespan=lifespan,
        # `useUnsafeMarkdown` to add style to description
        swagger_ui_parameters={"useUnsafeMarkdown": True},
        generate_unique_id_function=custom_generate_unique_id,
        # https://fastapi.tiangolo.com/advanced/custom-response/#use-orjsonresponse
        # https://fastapi.tiangolo.com/advanced/custom-response/#default-response-class
        default_response_class=ORJSONResponse,
    )

    # ! till here, lifespan is just declared but not called yet.
    # so configure_logger() is not set in lifesapn, but manually here.
    configure_logger(app)
    register_exception_handlers(app)
    register_middlewares(app)
    register_routers(app, v1_routes)
    init_sqladmin(app, engine)
    add_mcp_server(app, mount_path="/mcp", name="mcp")

    return app


app = create_app()
