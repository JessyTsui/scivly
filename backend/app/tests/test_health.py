from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.1.0"}


def test_ready_returns_ok(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == "0.1.0"
    assert payload["checks"]["auth_middleware"] == "ok"


def test_auth_me_returns_mock_user(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "researcher@scivly.dev"
    assert payload["role"] == "owner"
    assert "x-request-id" in response.headers


def test_cors_preflight_allows_frontend_origin(client: TestClient) -> None:
    response = client.options(
        "/workspaces",
        headers={
            "Origin": "http://localhost:3100",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3100"


def test_not_found_uses_standard_error_shape(client: TestClient) -> None:
    response = client.get("/workspaces/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"] == "workspace_not_found"
    assert payload["message"] == "Workspace not found."
    assert payload["request_id"]
