from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    # env TESTING=yes is set in the tool.pytest.ini_options part of pyproject.toml
    with TestClient(app) as test_client:
        yield test_client
