from fastapi.testclient import TestClient

from main import app


def test_healthz() -> None:
    with TestClient(app) as client:
        response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_required_routes_are_documented() -> None:
    paths = set(app.openapi()["paths"])
    assert {"/api/v1/auth/login", "/api/v1/posts", "/api/v1/posts/breaking", "/api/v1/posts/{post_id}/comments", "/api/v1/search"} <= paths
