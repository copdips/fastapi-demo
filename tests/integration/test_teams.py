from typing import TYPE_CHECKING

from fastapi import status

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_create_team(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/teams"
    body = {
        "name": "t1",
        "headquarters": "h1",
    }
    response = client.post(
        base_url,
        json=body,
    )
    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response.items() > body.items()
    assert json_response["id"] is not None


def test_get_single_team(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/teams"
    body = {
        "name": "single-team",
        "headquarters": "h2",
    }
    team_id = client.post(base_url, json=body).json()["id"]

    response = client.get(f"{base_url}/{team_id}")

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["name"] == body["name"]
    assert json_response["tags"] == []
    assert json_response["users"] == []


def test_get_unknown_team(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/teams"

    response = client.get(f"{base_url}/unknown")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "unknown" in response.json()["message"]


def test_update_team(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/teams"
    body = {
        "name": "team-to-update",
        "headquarters": "h3",
    }
    team_id = client.post(base_url, json=body).json()["id"]

    response = client.patch(
        f"{base_url}/{team_id}",
        json={
            "headquarters": "new-headquarters",
            "users_names": ["Deadpond"],
            "tags_names": ["admin"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["headquarters"] == "new-headquarters"
    assert [user["name"] for user in json_response["users"]] == ["Deadpond"]
    assert [tag["name"] for tag in json_response["tags"]] == ["admin"]


def test_update_team_with_unknown_tag(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/teams"
    body = {
        "name": "team-to-update-with-unknown-tag",
        "headquarters": "h4",
    }
    team_id = client.post(base_url, json=body).json()["id"]

    response = client.patch(
        f"{base_url}/{team_id}",
        json={"tags_names": ["unknown-tag"]},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Some tags not found" in response.json()["message"]


def test_update_unknown_team(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/teams"

    response = client.patch(f"{base_url}/unknown", json={"headquarters": "h5"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_team(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/teams"
    body = {
        "name": "team-to-delete",
        "headquarters": "h6",
    }
    team_id = client.post(base_url, json=body).json()["id"]

    response = client.delete(f"{base_url}/{team_id}")

    assert response.status_code == status.HTTP_200_OK
    assert client.get(f"{base_url}/{team_id}").status_code == status.HTTP_404_NOT_FOUND


def test_delete_unknown_team(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/teams"

    response = client.delete(f"{base_url}/unknown")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_teams(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/teams"
    team_count = 2
    response = client.get(f"{base_url}?offset=0&limit={team_count}")
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert len(json_response) == team_count
    team = json_response[0]
    assert team["id"] is not None
    assert team["name"] is not None
    assert team["headquarters"] is not None
    assert "tags" in team
