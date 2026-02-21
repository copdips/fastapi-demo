from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app

API_ROUTE_VERSION = "v1"


@pytest.fixture(scope="module")
def client() -> Generator[TestClient]:
    # env TESTING=yes is set in the tool.pytest.ini_options part of pyproject.toml
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def api_route_version() -> str:
    return API_ROUTE_VERSION
