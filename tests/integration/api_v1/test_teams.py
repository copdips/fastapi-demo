from fastapi import status
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
