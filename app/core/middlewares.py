from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.database import async_session_factory, init_db
from app.settings import settings


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.testing:
        await init_db(async_session_factory)
    yield
