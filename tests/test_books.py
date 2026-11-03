
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


def test_create_one_book(client):
    response = client.post(
        "/books",
        json={
            "title": "The Hobbit",
            "authors": ["J.R.R. Tolkien"],
            "published_year": 1937,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["count"] == 1
    assert data["books"][0]["title"] == "The Hobbit"
    assert data["books"][0]["authors"] == ["J.R.R. Tolkien"]
    assert data["books"][0]["published"] == "1937-01-01"


def test_create_book_with_multiple_authors(client):
    response = client.post(
        "/books",
        json={
            "title": "Good Omens",
            "authors": ["Neil Gaiman", "Terry Pratchett"],
            "published_year": 1990,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["books"][0]["authors"] == [
        "Neil Gaiman",
        "Terry Pratchett",
    ]


def test_create_multiple_books(client):
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
    )

    assert response.status_code == 201

    data = response.json()

    assert data["count"] == 2
    assert len(data["books"]) == 2
    assert data["books"][0]["title"] == "The Hobbit"
    assert data["books"][1]["title"] == "1984"


def test_reject_book_without_title(client):
    response = client.post(
        "/books",
        json={
            "title": " ",
            "authors": ["Author One"],
            "published_year": 2020,
        },
    )

    assert response.status_code == 422


def test_reject_book_without_authors(client):
    response = client.post(
        "/books",
        json={
            "title": "A Book",
            "authors": [],
            "published_year": 2020,
        },
    )

    assert response.status_code == 422


def test_reject_empty_book_list(client):
    response = client.post("/books", json=[])

    assert response.status_code == 422
