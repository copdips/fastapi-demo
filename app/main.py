from fastapi import FastAPI

from app.core.exceptions import register_exception_handlers
from app.core.middlewares import lifespan
from app.core.router import register_routers
from app.routes import v1
from app.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        contact=settings.api_contact,
        lifespan=lifespan,
        # `useUnsafeMarkdown` to add style to description
        swagger_ui_parameters={"useUnsafeMarkdown": True},
    )

    # app.include_router(v1.router, prefix=v1.VERSION_PREFIX)
    register_exception_handlers(app)
    register_routers(app, v1)
    return app


app = create_app()
