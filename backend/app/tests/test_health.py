from collections.abc import Callable

from fastapi.testclient import TestClient

DEMO_WORKSPACE_ID = "00000000-0000-0000-0000-000000000201"


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


def test_auth_me_returns_authenticated_user(client: TestClient, auth_headers: Callable[..., dict[str, str]]) -> None:
    response = client.get(
        "/auth/me",
        headers=auth_headers(
            sub="user_jessy",
            email="jessy@example.com",
            name="Jessy Tsui",
        ),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "jessy@example.com"
    assert payload["name"] == "Jessy Tsui"
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


def test_unauthenticated_interests_request_returns_401(client: TestClient) -> None:
    response = client.get("/interests/topic-profiles")

    assert response.status_code == 401
    payload = response.json()
    assert payload["error"] == "unauthorized"
    assert payload["message"] == "Authentication context is missing."


def test_authenticated_interests_request_is_workspace_scoped(client: TestClient, auth_headers: Callable[..., dict[str, str]]) -> None:
    response = client.get(
        "/interests/topic-profiles",
        headers=auth_headers(workspace_id=DEMO_WORKSPACE_ID),
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert {item["workspace_id"] for item in payload["items"]} == {DEMO_WORKSPACE_ID}


def test_invalid_token_uses_standard_error_shape(client: TestClient) -> None:
    response = client.get(
        "/workspaces/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": "Bearer invalid"},
    )

    assert response.status_code == 401
    payload = response.json()
    assert payload["error"] == "invalid_token"
    assert payload["request_id"]


def test_invalid_auth_header_returns_standard_error(client: TestClient) -> None:
    response = client.get("/auth/me", headers={"Authorization": "Token nope"})

    assert response.status_code == 400
    payload = response.json()
    assert payload["error"] == "invalid_auth_header"
    assert payload["details"][0]["header"] == "Authorization"
    assert response.headers["x-request-id"]


def test_workspace_is_auto_created_for_new_authenticated_user(client: TestClient, auth_headers: Callable[..., dict[str, str]]) -> None:
    headers = auth_headers(sub="user_new_signup", name="New User")

    me_response = client.get("/auth/me", headers=headers)
    workspaces_response = client.get("/workspaces", headers=headers)

    assert me_response.status_code == 200
    assert workspaces_response.status_code == 200
    me_payload = me_response.json()
    workspace_payload = workspaces_response.json()
    assert workspace_payload["total"] == 1
    assert workspace_payload["items"][0]["id"] == me_payload["workspace_id"]
    assert workspace_payload["items"][0]["role"] == "owner"


def test_workspace_creation_always_returns_owner_role(client: TestClient, auth_headers: Callable[..., dict[str, str]]) -> None:
    headers = auth_headers(workspace_id="33333333-3333-3333-3333-333333333333", role="admin")
    response = client.post(
        "/workspaces",
        json={"name": "Signals Lab", "slug": "signals-lab", "plan": "pro"},
        headers=headers,
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["role"] == "owner"

    follow_up = client.get(f"/workspaces/{payload['id']}", headers=headers)
    assert follow_up.status_code == 200
    assert follow_up.json()["slug"] == "signals-lab"


def test_openapi_version_matches_health_version(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["version"] == "0.1.0"


def test_delete_workspace_removes_it_from_follow_up_reads(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
) -> None:
    workspace_id = DEMO_WORKSPACE_ID
    headers = auth_headers(workspace_id=workspace_id)

    bootstrap_response = client.get("/workspaces", headers=headers)
    assert bootstrap_response.status_code == 200


    delete_response = client.delete(f"/workspaces/{workspace_id}", headers=headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/workspaces/{workspace_id}", headers=headers)
    assert get_response.status_code == 404
    assert get_response.json()["error"] == "workspace_not_found"


def test_list_workspaces_reads_seeded_rows(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
) -> None:
    response = client.get("/workspaces", headers=auth_headers(workspace_id=DEMO_WORKSPACE_ID))

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["name"] == "Scivly Demo Workspace"
    assert payload["items"][0]["role"] == "owner"


def test_papers_and_scores_read_from_database(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
) -> None:
    headers = auth_headers(workspace_id=DEMO_WORKSPACE_ID)
    response = client.get(
        "/papers",
        params={"sort": "score_desc"},
        headers=headers,
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] >= 5
    first_paper = payload["items"][0]
    assert first_paper["arxiv_id"].startswith("2603.")

    score_response = client.get(f"/papers/{first_paper['id']}/scores", headers=headers)
    assert score_response.status_code == 200
    scores = score_response.json()
    assert scores
    assert scores[0]["workspace_id"] == DEMO_WORKSPACE_ID
