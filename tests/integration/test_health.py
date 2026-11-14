from typing import TYPE_CHECKING

from fastapi import status

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_health(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/health"

    response = client.get(base_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["cache-control"] == "no-cache"
    json_response = response.json()
    assert json_response["status"] == "ok"
    assert json_response["meta"]["db_engine"] == "sqlite"
