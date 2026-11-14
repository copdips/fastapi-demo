from typing import TYPE_CHECKING

from fastapi import status

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


def test_create_tag(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/tags"
    body = {
        "name": "t1",
    }
    response = client.post(
        base_url,
        json=body,
    )
    assert response.status_code == status.HTTP_201_CREATED
    json_response = response.json()
    assert json_response.items() >= body.items()
    assert json_response["id"] is not None


def test_get_single_tag(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/tags"
    body = {"name": "single-tag"}
    tag_id = client.post(base_url, json=body).json()["id"]

    response = client.get(f"{base_url}/{tag_id}")

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["name"] == body["name"]
    assert json_response["teams"] == []


def test_get_unknown_tag(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/tags"

    response = client.get(f"{base_url}/unknown")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "unknown" in response.json()["message"]


def test_update_tag(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/tags"
    body = {"name": "tag-to-update"}
    tag_id = client.post(base_url, json=body).json()["id"]

    response = client.patch(
        f"{base_url}/{tag_id}",
        json={"name": "tag-updated", "teams_names": ["Preventers"]},
    )

    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert json_response["name"] == "tag-updated"
    assert [team["name"] for team in json_response["teams"]] == ["Preventers"]


def test_update_tag_with_unknown_team(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/tags"
    body = {"name": "tag-to-update-with-unknown-team"}
    tag_id = client.post(base_url, json=body).json()["id"]

    response = client.patch(
        f"{base_url}/{tag_id}",
        json={"teams_names": ["unknown-team"]},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "Some teams not found" in response.json()["message"]


def test_update_unknown_tag(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/tags"

    response = client.patch(f"{base_url}/unknown", json={"name": "updated"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_tag(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/tags"
    body = {"name": "tag-to-delete"}
    tag_id = client.post(base_url, json=body).json()["id"]

    response = client.delete(f"{base_url}/{tag_id}")

    assert response.status_code == status.HTTP_200_OK
    assert client.get(f"{base_url}/{tag_id}").status_code == status.HTTP_404_NOT_FOUND


def test_delete_unknown_tag(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/tags"

    response = client.delete(f"{base_url}/unknown")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_all_tags(client: TestClient, api_route_version: str):
    base_url = f"/{api_route_version}/tags"
    tag_count = 2
    response = client.get(f"{base_url}?offset=0&limit={tag_count}")
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert len(json_response) == tag_count
    tag = json_response[0]
    assert tag["id"] is not None
    assert tag["name"] is not None
    assert "teams" in tag
