import asyncio
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    # https://github.com/pytest-dev/pytest-asyncio/issues/706#issuecomment-1838771298
    # https://github.com/pytest-dev/pytest-asyncio/issues/706#issuecomment-2282780197
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    # env TESTING=yes is set in the tool.pytest.ini_options part of pyproject.toml
    with TestClient(app) as test_client:
        yield test_client
