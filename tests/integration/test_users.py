from typing import TYPE_CHECKING

from fastapi import status

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_create_user(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/users"
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


def test_get_single_user(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/users"
    body = {
        "name": "single-user",
        "first_name": "b2",
        "last_name": "c2",
        "email": "single-user@test.com",
    }
    user_id = client.post(base_url, json=body).json()["id"]

    response = client.get(f"{base_url}/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["name"] == body["name"]
    assert json_response["email"] == body["email"]
    assert json_response["team"] is None


def test_get_unknown_user(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/users"

    response = client.get(f"{base_url}/unknown")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "unknown" in response.json()["message"]


def test_update_user(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/users"
    body = {
        "name": "user-to-update",
        "first_name": "b3",
        "last_name": "c3",
        "email": "user-to-update@test.com",
    }
    user_id = client.post(base_url, json=body).json()["id"]

    response = client.patch(
        f"{base_url}/{user_id}",
        json={"first_name": "updated", "team_name": "Z-Force"},
    )

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["first_name"] == "updated"
    assert json_response["last_name"] == body["last_name"]
    assert json_response["team"]["name"] == "Z-Force"


def test_update_unknown_user(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/users"

    response = client.patch(f"{base_url}/unknown", json={"first_name": "updated"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_user(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/users"
    body = {
        "name": "user-to-delete",
        "first_name": "b4",
        "last_name": "c4",
        "email": "user-to-delete@test.com",
    }
    user_id = client.post(base_url, json=body).json()["id"]

    response = client.delete(f"{base_url}/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    assert client.get(f"{base_url}/{user_id}").status_code == status.HTTP_404_NOT_FOUND


def test_delete_unknown_user(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/users"

    response = client.delete(f"{base_url}/unknown")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_users(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/users"
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
