from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi_mcp import FastApiMCP

from app_layer_based_sqlmodel.config import settings
from app_layer_based_sqlmodel.core.db import engine
from app_layer_based_sqlmodel.core.docs import add_scalar_docs
from app_layer_based_sqlmodel.core.exceptions import register_exception_handlers
from app_layer_based_sqlmodel.core.logging import configure_logger
from app_layer_based_sqlmodel.core.middleware import lifespan, register_middlewares
from app_layer_based_sqlmodel.core.router import register_routers
from app_layer_based_sqlmodel.core.sql_admin import init_sqladmin
from app_layer_based_sqlmodel.routes import v1_routes


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
    )

    # ! till here, lifespan is just declared but not called yet.
    # so configure_logger() is not set in lifesapn, but manually here.
    configure_logger(app)
    register_exception_handlers(app)
    register_middlewares(app)
    register_routers(app, v1_routes)
    add_scalar_docs(app)
    init_sqladmin(app, engine)
    mcp = FastApiMCP(app)
    mcp.mount_http()

    return app


app = create_app()
