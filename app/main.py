import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute

from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logger
from app.core.middlewares import lifespan, register_middlewares
from app.core.router import register_routers
from app.routes import v1
from app.settings import settings


def custom_generate_unique_id(route: APIRoute) -> str:
    # output: health-get_health@v1
    return f"{route.tags[0]}-{route.name}@{route.path.split('/')[1]}"


def create_app() -> FastAPI:
    sentry_sdk.init(
        # https://github.com/getsentry/sentry-python/blob/master/sentry_sdk/integrations/fastapi.py
        dsn="https://5cb8253e43f645566f0d1ae3cbbffb40@o4506997041135616.ingest.us.sentry.io/4506997043298304",
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )
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
    configure_logger()
    register_exception_handlers(app)
    register_middlewares(app)
    register_routers(app, v1)
    return app


app = create_app()
