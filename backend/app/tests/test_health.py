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
    assert payload["checks"]["database"] == "ok"


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


def test_invalid_auth_header_returns_standard_error(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"x-scivly-user-id": "not-a-uuid"})

    assert response.status_code == 400
    payload = response.json()
    assert payload["error"] == "invalid_auth_header"
    assert payload["details"][0]["header"] == "x-scivly-user-id"
    assert response.headers["x-request-id"]


def test_workspace_creation_always_returns_owner_role(client: TestClient) -> None:
    response = client.post(
        "/workspaces",
        json={"name": "Signals Lab", "slug": "signals-lab", "plan": "pro"},
        headers={"x-scivly-user-role": "admin"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["role"] == "owner"

    follow_up = client.get(f"/workspaces/{payload['id']}")
    assert follow_up.status_code == 200
    assert follow_up.json()["slug"] == "signals-lab"


def test_openapi_version_matches_health_version(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["version"] == "0.1.0"


def test_delete_workspace_removes_it_from_follow_up_reads(client: TestClient) -> None:
    workspace_id = "00000000-0000-0000-0000-000000000201"

    delete_response = client.delete(f"/workspaces/{workspace_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/workspaces/{workspace_id}")
    assert get_response.status_code == 404
    assert get_response.json()["error"] == "workspace_not_found"


def test_list_workspaces_reads_seeded_rows(client: TestClient) -> None:
    response = client.get("/workspaces")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["name"] == "Scivly Demo Workspace"
    assert payload["items"][0]["role"] == "owner"


def test_papers_and_scores_read_from_database(client: TestClient) -> None:
    response = client.get("/papers")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 6
    first_paper = payload["items"][0]
    assert first_paper["arxiv_id"].startswith("2603.")

    score_response = client.get(f"/papers/{first_paper['id']}/scores")
    assert score_response.status_code == 200
    scores = score_response.json()
    assert scores
    assert scores[0]["workspace_id"] == "00000000-0000-0000-0000-000000000201"
