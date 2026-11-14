from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app_domain_based_sqlalchemy.main import app as domain_based_sqlalchemy_app
from app_layer_based_sqlmodel.main import app as layer_based_sqlmodel_app

API_ROUTE_VERSION = "v1"

# The same API contract is tested against both layouts.
APPS = {
    "app_layer_based_sqlmodel": layer_based_sqlmodel_app,
    "app_domain_based_sqlalchemy": domain_based_sqlalchemy_app,
}


@pytest.fixture(params=list(APPS), scope="module")
def client(request: pytest.FixtureRequest) -> Generator[TestClient]:
    # env TESTING=yes is set in the tool.pytest.ini_options part of pyproject.toml
    with TestClient(APPS[request.param]) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def api_route_version() -> str:
    return API_ROUTE_VERSION
