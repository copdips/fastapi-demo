from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.routing import APIRoute

import app_domain_based as app_root_module
from app_domain_based.config import settings
from app_domain_based.core.db import engine
from app_domain_based.core.exceptions import register_exception_handlers
from app_domain_based.core.logging import configure_logger
from app_domain_based.core.middleware import lifespan, register_middlewares
from app_domain_based.core.router import register_domain_based_routers
from app_domain_based.core.sql_admin import init_sqladmin


def custom_generate_unique_id(route: APIRoute) -> str:
    # output: health-get_health@v1
    return f"{route.tags[0]}-{route.name}@{route.path.split('/')[1]}"


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
    register_domain_based_routers(app, app_root_module)
    init_sqladmin(app, engine)
    return app


app = create_app()
