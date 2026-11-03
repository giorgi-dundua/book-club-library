import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app, get_db

books = [
    (4, "Test Book A"),
    (5, "Test Book B"),
    (6, "Test Book C"),
]

loans = [
    # Book A: borrowed and returned
    (1, 1, 4, "2026-09-01", "2026-09-15", "2026-09-12"),
    # Book A: borrowed again, still active
    (2, 1, 4, "2026-10-01", "2026-10-15", None),
    # Book B: borrowed once, still active
    (3, 1, 5, "2026-10-05", "2026-10-19", None),
]


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Create a separate database for this test.
    db_path = tmp_path / "test_bookclub.db"
    schema_path = Path(__file__).resolve().parents[1] / "schema.sql"

    test_key = "somekey"
    monkeypatch.setenv("API_KEY", test_key)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(schema_path.read_text())

        # Add only the records needed for statistics tests.
        conn.execute(
            "INSERT INTO members (member_id, member_name, email, phone) "
            "VALUES (?, ?, ?, ?)",
            (1, "Test Member", "test@example.com", "000"),
        )
        conn.executemany(
            "INSERT INTO books (book_id, title) VALUES (?, ?)",
            books,
        )
        conn.executemany(
            "INSERT INTO loans "
            "(loan_id, member_id, book_id, loan_date, due_date, return_date) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            loans,
        )
        conn.commit()
    finally:
        conn.close()

    # Replace the application's database dependency during this test.
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
            test_client.headers["X-API-Key"] = test_key
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_book_loan_statistics(client):
    response = client.get("/statistics/most-borrowed")

    assert response.status_code == 200

    assert response.json() == [
        {"book_id": 4, "title": "Test Book A", "total_loans": 2},
        {"book_id": 5, "title": "Test Book B", "total_loans": 1},
        {"book_id": 6, "title": "Test Book C", "total_loans": 0},
    ]
