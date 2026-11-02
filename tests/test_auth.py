import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from auth import require_api_key
from main import app


@pytest.mark.parametrize(
    "configured_key, supplied_key, expected_status",
    [
        ("secret", "secret", 200),
        ("secret", "wrong", 401),
        ("secret", None, 401),
        (None, "secret", 401),
    ],
)
def test_api_key(monkeypatch, configured_key, supplied_key, expected_status):
    if configured_key is None:
        monkeypatch.delenv("API_KEY", raising=False)
    else:
        monkeypatch.setenv("API_KEY", configured_key)

    if expected_status == 200:
        require_api_key(supplied_key)
    else:
        with pytest.raises(HTTPException) as exc:
            require_api_key(supplied_key)

        assert exc.value.status_code == expected_status


def test_missing_api_key_http(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-secret")

    with TestClient(app) as client:
        response = client.post(
            "/loans",
            json={
                "member_id": 1,
                "book_id": 4,
                "loan_date": "2026-10-28",
                "due_date": "2026-11-11",
            },
        )

    assert response.status_code == 401


def test_invalid_api_key_http(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-secret")

    with TestClient(app) as client:
        client.headers["X-API-Key"] = "invalid_key"
        response = client.post(
            "/loans",
            json={
                "member_id": 1,
                "book_id": 4,
                "loan_date": "2026-10-28",
                "due_date": "2026-11-11",
            },
        )

    assert response.status_code == 401


def test_unconfigured_api_key_http(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    with TestClient(app) as client:
        client.headers["X-API-Key"] = "invalid_key"
        response = client.post(
            "/loans",
            json={
                "member_id": 1,
                "book_id": 4,
                "loan_date": "2026-10-28",
                "due_date": "2026-11-11",
            },
        )

    assert response.status_code == 401


def test_missing_api_key_return_http(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-secret")

    with TestClient(app) as client:
        response = client.patch(
            "/loans/1/return",
            json={
                "return_date": "2026-11-11",
            },
        )

    assert response.status_code == 401


def test_health_without_api_key(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-secret")

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
