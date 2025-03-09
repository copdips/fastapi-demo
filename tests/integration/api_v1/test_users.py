from fastapi import status
from fastapi.testclient import TestClient

from tests.integration.api_v1 import API_ROUTE_VERSION

base_url = f"/{API_ROUTE_VERSION}/users"


def test_create_user(client: TestClient):
    body = {
        "name": "a1",
        "first_name": "b1",
        "last_name": "c1",
        "email": "test@test.com",
    }
    response = client.post(
        base_url,
        json=body,
    )
    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response.items() > body.items()
    assert json_response["id"] is not None


def test_get_all_users(client: TestClient):
    user_count = 2
    response = client.get(f"{base_url}?offset=0&limit={user_count}")
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert len(json_response) == user_count
    user = json_response[0]
    assert user["id"] is not None
    assert user["name"] is not None
    assert user["first_name"] is not None
    assert user["last_name"] is not None
    assert "team" in user
