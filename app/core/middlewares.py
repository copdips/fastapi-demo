from contextlib import asynccontextmanager

from apitally.fastapi import ApitallyMiddleware
from fastapi import FastAPI

from app.core.db import async_session_factory, init_db
from app.settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # access app.state in request by request.app.state:
    # https://github.com/tiangolo/fastapi/discussions/8054#discussioncomment-5146686
    # ! be careful if the value is changed in the request, it wont change the value in the app running in other process, or in other node. The change is app local.
    _app.state.settings = settings
    if settings.testing:
        await init_db(async_session_factory)
    yield


def register_middlewares(_app: FastAPI):
    # apitally dashboard: https://app.apitally.io/traffic/fastapi-demo?period=24h
    # ! to add consumer_identifier, add it in request depends:
    # https://docs.apitally.io/frameworks/fastapi#identify-consumers
    # request.state.consumer_identifier = current_user.username
    _app.add_middleware(
        ApitallyMiddleware,
        client_id=settings.apitally_client_id,
        env="dev",  # or "prod"
    )
