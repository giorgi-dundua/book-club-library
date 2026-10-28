import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app, get_db


@pytest.fixture
def client(tmp_path):
    # Create a separate database for this test.
    db_path = tmp_path / "test_bookclub.db"
    schema_path = Path(__file__).resolve().parents[1] / "schema.sql"

    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(schema_path.read_text())

        # Add only the records needed for loan tests.
        conn.execute(
            "INSERT INTO members (member_id, member_name, email, phone) "
            "VALUES (?, ?, ?, ?)",
            (1, "Test Member", "test@example.com", "000"),
        )
        conn.execute(
            "INSERT INTO books (book_id, title) VALUES (?, ?)",
            (4, "Test Book"),
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
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_create_loan_missing_due_date(client):
    response = client.post(
        "/loans",
        json={
            "member_id": 1,
            "book_id": 4,
            "loan_date": "2026-10-28",
        },
    )

    assert response.status_code == 422


def test_create_loan_success(client, tmp_path):
    response = client.post(
        "/loans",
        json={
            "member_id": 1,
            "book_id": 4,
            "loan_date": "2026-10-28",
            "due_date": "2026-11-11",
        },
    )

    assert response.status_code == 201

    loan_id = response.json()["loan_id"]
    assert isinstance(loan_id, int)

    conn = sqlite3.connect(tmp_path / "test_bookclub.db")
    try:
        saved_loan = conn.execute(
            """
            SELECT member_id, book_id, loan_date, due_date, return_date
            FROM loans
            WHERE loan_id = ?
            """,
            (loan_id,),
        ).fetchone()
    finally:
        conn.close()

    assert saved_loan == (1, 4, "2026-10-28", "2026-11-11", None)


def test_create_loan_already_borrowed(client, tmp_path):
    loan_data = {
        "member_id": 1,
        "book_id": 4,
        "loan_date": "2026-10-28",
        "due_date": "2026-11-11",
    }

    # First borrowing should succeed.
    first_response = client.post("/loans", json=loan_data)
    assert first_response.status_code == 201

    # Borrowing the same book again should fail.
    second_response = client.post("/loans", json=loan_data)

    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "Book is already borrowed"}

    # Verify that only one loan was actually inserted.
    conn = sqlite3.connect(tmp_path / "test_bookclub.db")
    try:
        loan_count = conn.execute(
            "SELECT COUNT(*) FROM loans WHERE book_id = ?",
            (4,),
        ).fetchone()[0]
    finally:
        conn.close()

    assert loan_count == 1


def test_create_loan_member_not_found(client):
    response = client.post(
        "/loans",
        json={
            "member_id": 999,
            "book_id": 4,
            "loan_date": "2026-10-28",
            "due_date": "2026-11-11",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Member not found"}


def test_create_loan_book_not_found(client):
    response = client.post(
        "/loans",
        json={
            "member_id": 1,
            "book_id": 999,
            "loan_date": "2026-10-28",
            "due_date": "2026-11-11",
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Book not found"}


def test_create_loan_after_return(client, tmp_path):
    db_path = tmp_path / "test_bookclub.db"

    # Create a historical loan that has already been returned.
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(
            """
            INSERT INTO loans
                (member_id, book_id, loan_date, due_date, return_date)
            VALUES (?, ?, ?, ?, ?)
            """,
            (1, 4, "2026-09-01", "2026-09-15", "2026-09-10"),
        )
        conn.commit()
    finally:
        conn.close()

    # Borrow the same book again.
    response = client.post(
        "/loans",
        json={
            "member_id": 1,
            "book_id": 4,
            "loan_date": "2026-10-28",
            "due_date": "2026-11-11",
        },
    )

    assert response.status_code == 201

    # Verify that both the historical and new loans exist.
    conn = sqlite3.connect(db_path)
    try:
        total_loans = conn.execute(
            "SELECT COUNT(*) FROM loans WHERE book_id = ?",
            (4,),
        ).fetchone()[0]

        active_loans = conn.execute(
            """
            SELECT COUNT(*) FROM loans
            WHERE book_id = ? AND return_date IS NULL
            """,
            (4,),
        ).fetchone()[0]
    finally:
        conn.close()

    assert total_loans == 2
    assert active_loans == 1
