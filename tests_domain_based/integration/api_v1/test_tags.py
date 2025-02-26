from fastapi import status
from fastapi.testclient import TestClient

from tests.integration.api_v1 import API_ROUTE_VERSION

base_url = f"/{API_ROUTE_VERSION}/tags"


def test_create_tag(client: TestClient):
    body = {
        "name": "t1",
    }
    response = client.post(
        base_url,
        json=body,
    )
    print(f"response: {response.json()}")
    print(f"base_url: {base_url}")
    assert response.status_code == status.HTTP_201_CREATED

    json_response = response.json()
    assert json_response.items() > body.items()
    assert json_response["id"] is not None


def test_get_all_tags(client: TestClient):
    tag_count = 2
    response = client.get(f"{base_url}/?offset=0&limit={tag_count}")
    assert response.status_code == status.HTTP_200_OK
    json_response = response.json()
    assert len(json_response) == tag_count
    tag = json_response[0]
    assert tag["id"] is not None
    assert tag["name"] is not None
    assert "teams" in tag
