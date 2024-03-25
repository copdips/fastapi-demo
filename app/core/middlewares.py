from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import async_session_factory, init_db
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
