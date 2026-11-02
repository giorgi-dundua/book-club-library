import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from main import app, get_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Create a separate database for this test.
    db_path = tmp_path / 'test_bookclub.db'
    schema_path = Path(__file__).resolve().parents[1] / 'schema.sql'

    test_key = 'somekey'
    monkeypatch.setenv('API_KEY', test_key)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute('PRAGMA foreign_keys = ON')
        conn.executescript(schema_path.read_text())

        # Adding test data needed for testing
        conn.execute(
            'INSERT INTO members (member_id, member_name, email, phone) '
            'VALUES (?, ?, ?, ?)',
            (1, 'Test Member', 'test@example.com', '555-123456'),
        )
        conn.commit()
    finally:
        conn.close()

    # Replace the application's database dependency during this test.
    def override_get_db():
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.execute('PRAGMA foreign_keys = ON')
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            test_client.headers['X-API-Key'] = test_key
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_update_non_valid_member(client):
    response = client.patch(
        '/members/900',
        json={
            'member_name': 'f00',
            'email': 'f00',
            'phone': 'f00'
        }
    ) 
    assert response.status_code == 404
    assert response.json() == {'detail': 'Member not found'}

def test_update_partial(client):
    response = client.patch(
        '/members/1',
        json={
            'email': 'changed@example.com'
        }
    )
    assert response.status_code == 200
    assert response.json().get('email') == 'changed@example.com'


def test_update_no_changes(client):
    response = client.patch(
        '/members/1',
        json={
            'member_name': 'Test Member'
        }
    )
    assert response.status_code == 200
    assert response.json() == {'message': 'No changes'}


def test_update_member_invalid_type(client):
    response = client.patch(
        '/members/1',
        json={
            'member_name': 1
        }
    )
    assert response.status_code == 422
    assert response.json().get('detail')[0].get('msg') == 'Input should be a valid string'


def test_update_member_invalid_column(client):
    response = client.patch(
        '/members/1',
        json={
            'member_id': 2
        }
    )
    assert response.status_code == 200
    assert response.json() == {'message': 'No changes'}

