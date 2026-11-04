import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app, get_db


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test_bookclub.db"
    schema_path = Path(__file__).resolve().parents[1] / "schema.sql"

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(schema_path.read_text())
        conn.commit()
    finally:
        conn.close()

    def override_get_db():
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_create_one_book(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")

    response = client.post(
        "/books",
        json={
            "title": "The Hobbit",
            "authors": ["J.R.R. Tolkien"],
            "published_year": 1937,
        },
        headers={"X-API-Key": "test-key"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["count"] == 1
    assert data["books"][0]["title"] == "The Hobbit"
    assert data["books"][0]["authors"] == ["J.R.R. Tolkien"]
    assert data["books"][0]["published"] == "1937-01-01"


def test_create_book_with_multiple_authors(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")

    response = client.post(
        "/books",
        json={
            "title": "Good Omens",
            "authors": ["Neil Gaiman", "Terry Pratchett"],
            "published_year": 1990,
        },
        headers={"X-API-Key": "test-key"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["books"][0]["authors"] == [
        "Neil Gaiman",
        "Terry Pratchett",
    ]


def test_create_multiple_books(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")

    response = client.post(
        "/books",
        json=[
            {
                "title": "The Hobbit",
                "authors": ["J.R.R. Tolkien"],
                "published_year": 1937,
            },
            {
                "title": "1984",
                "authors": ["George Orwell"],
                "published_year": 1949,
            },
        ],
        headers={"X-API-Key": "test-key"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["count"] == 2
    assert len(data["books"]) == 2
    assert data["books"][0]["title"] == "The Hobbit"
    assert data["books"][1]["title"] == "1984"


def test_reject_book_without_title(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")

    response = client.post(
        "/books",
        json={
            "title": " ",
            "authors": ["Author One"],
            "published_year": 2020,
        },
        headers={"X-API-Key": "test-key"},
    )

    assert response.status_code == 422


def test_reject_book_without_authors(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")

    response = client.post(
        "/books",
        json={
            "title": "A Book",
            "authors": [],
            "published_year": 2020,
        },
        headers={"X-API-Key": "test-key"},
    )

    assert response.status_code == 422


def test_reject_empty_book_list(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")

    response = client.post(
        "/books",
        json=[],
        headers={"X-API-Key": "test-key"},
    )

    assert response.status_code == 422


def test_create_book_without_api_key_returns_401(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")

    response = client.post(
        "/books",
        json={
            "title": "The Hobbit",
            "authors": ["J.R.R. Tolkien"],
            "published_year": 1937,
        },
    )

    assert response.status_code == 401


def test_create_book_with_wrong_api_key_returns_401(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")

    response = client.post(
        "/books",
        json={
            "title": "The Hobbit",
            "authors": ["J.R.R. Tolkien"],
            "published_year": 1937,
        },
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401


def test_replace_book_information(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    headers = {"X-API-Key": "test-key"}

    # Create a book first.
    create_response = client.post(
        "/books",
        json={
            "title": "Wrong Title",
            "authors": ["Wrong Author"],
            "published_year": 2000,
        },
        headers=headers,
    )

    assert create_response.status_code == 201

    book_id = create_response.json()["books"][0]["book_id"]

    # Replace all book information.
    response = client.put(
        f"/books/{book_id}",
        json={
            "title": "Corrected Title",
            "authors": ["Correct Author"],
            "published_year": 2020,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Corrected Title"
    assert response.json()["authors"] == ["Correct Author"]
    assert response.json()["published"] == "2020-01-01"


def test_partially_update_book_information(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    headers = {"X-API-Key": "test-key"}

    create_response = client.post(
        "/books",
        json={
            "title": "Original Title",
            "authors": ["Original Author"],
            "published_year": 2000,
        },
        headers=headers,
    )

    book_id = create_response.json()["books"][0]["book_id"]

    # Change only the title.
    response = client.patch(
        f"/books/{book_id}",
        json={"title": "Updated Title"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"

    # Other information should remain unchanged.
    assert response.json()["authors"] == ["Original Author"]
    assert response.json()["published"] == "2000-01-01"


def test_update_nonexistent_book(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    headers = {"X-API-Key": "test-key"}

    response = client.patch(
        "/books/99999",
        json={"title": "New Title"},
        headers=headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_patch_book_without_changes(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    headers = {"X-API-Key": "test-key"}

    create_response = client.post(
        "/books",
        json={
            "title": "Original Title",
            "authors": ["Original Author"],
            "published_year": 2000,
        },
        headers=headers,
    )

    book_id = create_response.json()["books"][0]["book_id"]

    response = client.patch(
        f"/books/{book_id}",
        json={},
        headers=headers,
    )

    assert response.status_code == 422


def test_get_book_with_multiple_authors(client, monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")

    response = client.post(
        "/books",
        json={
            "title": "Good Omens",
            "authors": ["Neil Gaiman", "Terry Pratchett"],
            "published_year": 1990,
        },
        headers={"X-API-Key": "test-key"},
    )

    assert response.status_code == 201
    book_id = response.json()["books"][0]["book_id"]

    response = client.get(f"/books/{book_id}")

    assert response.status_code == 200
    assert response.json() == {
        "book_id": book_id,
        "title": "Good Omens",
        "published_year": 1990,
        "authors": ["Neil Gaiman", "Terry Pratchett"],
    }


def test_get_nonexistent_book_returns_404(client):
    response = client.get("/books/99999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"
