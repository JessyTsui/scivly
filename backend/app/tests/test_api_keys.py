from collections.abc import Callable

from fastapi.testclient import TestClient

from app.config import get_settings


def test_create_api_key_returns_secret_and_tracks_usage(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
) -> None:
    create_response = client.post(
        "/api-keys",
        json={"name": "Agent Worker", "scopes": ["papers:read", "digests:read"]},
        headers=auth_headers(),
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["token"].startswith("scv_")
    assert created["prefix"].startswith("scv_")
    assert created["usage_total"] == 0

    papers_response = client.get(
        "/papers",
        headers={"Authorization": f"Bearer {created['token']}"},
    )

    assert papers_response.status_code == 200
    assert papers_response.headers["x-ratelimit-limit"] == "60"

    list_response = client.get("/api-keys", headers=auth_headers())
    assert list_response.status_code == 200
    stored = next(item for item in list_response.json()["items"] if item["id"] == created["id"])
    assert stored["last_used_at"] is not None
    assert stored["usage_total"] == 1
    assert stored["usage_last_24h"] == 1


def test_api_key_rate_limit_returns_429(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
    monkeypatch,
) -> None:
    monkeypatch.setenv("SCIVLY_API_KEY_RATE_LIMIT_PER_KEY", "1")
    monkeypatch.setenv("SCIVLY_API_KEY_RATE_LIMIT_PER_WORKSPACE", "5")
    monkeypatch.setenv("SCIVLY_API_KEY_RATE_LIMIT_WINDOW_SECONDS", "60")
    get_settings.cache_clear()

    create_response = client.post(
        "/api-keys",
        json={"name": "Rate Limited Worker", "scopes": ["papers:read"]},
        headers=auth_headers(),
    )
    token = create_response.json()["token"]

    first_response = client.get("/papers", headers={"Authorization": f"Bearer {token}"})
    second_response = client.get("/papers", headers={"Authorization": f"Bearer {token}"})

    assert first_response.status_code == 200
    assert second_response.status_code == 429
    assert second_response.json()["error"] == "api_key_rate_limited"

    get_settings.cache_clear()


def test_revoked_api_key_is_rejected(
    client: TestClient,
    auth_headers: Callable[..., dict[str, str]],
) -> None:
    create_response = client.post(
        "/api-keys",
        json={"name": "Revocable Worker", "scopes": ["papers:read"]},
        headers=auth_headers(),
    )
    created = create_response.json()

    revoke_response = client.delete(f"/api-keys/{created['id']}", headers=auth_headers())
    assert revoke_response.status_code == 204

    follow_up = client.get("/papers", headers={"Authorization": f"Bearer {created['token']}"})
    assert follow_up.status_code == 401
    assert follow_up.json()["error"] == "api_key_revoked"
