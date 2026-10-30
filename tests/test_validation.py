import sqlite3
import pytest
from pathlib import Path
from datetime import date, timedelta

from database import db_select, db_insert, db_delete, db_update
from seed import adapt_date_iso

member_id = 900
book_id = 900
book_id2 = 901
due_delta = timedelta(days=14)


@pytest.fixture
def test_conn(tmp_path):
    # Create a separate database for this test.
    db_path = tmp_path / 'test_bookclub.db'
    schema_path = Path(__file__).resolve().parents[1] / 'schema.sql'
    sqlite3.register_adapter(date, adapt_date_iso)

    conn = sqlite3.connect(db_path)
    try:
        conn.execute('PRAGMA foreign_keys = ON')
        conn.executescript(schema_path.read_text())

        conn.execute(
            'INSERT INTO members (member_id, member_name, email, phone, joined) '
            'VALUES (?, ?, ?, ?, ?)',
            (member_id, 'Test Member', 'test@example.com', '000', date.today())
        )
        conn.execute(
            'INSERT INTO books (book_id, title, published) '
            'VALUES (?, ?, ?)',
            (book_id, 'Test Book', date(2000,1,1))
        )
        conn.execute(
            'INSERT INTO books (book_id, title, published) '
            'VALUES (?, ?, ?)',
            (book_id2, 'Test Book 2', date(2000,1,1))
        )
        conn.execute(
            'INSERT INTO loans (member_id, book_id, loan_date, due_date) '
            'VALUES (?, ?, ?, ?)',
            (member_id, book_id, date(2000,1,15), date(2000,1,15)+due_delta)
        )
        conn.execute(
            'INSERT INTO loans (member_id, book_id, loan_date, due_date) '
            'VALUES (?, ?, ?, ?)',
            (member_id, book_id2, date(2000,1,15), date(2000,1,15)+due_delta)
        )
        conn.commit()
    finally:
        conn.close()

    try:
        with sqlite3.connect(db_path) as conn:
            conn.execute('PRAGMA foreign_keys = ON')
            yield conn
    finally:
        conn.close()


def test_one_loan_per_book(test_conn):
    loans_per_book = db_select(
        'SELECT COUNT(*) FROM loans WHERE return_date IS NULL GROUP BY book_id',
        conn=test_conn
    )
    assert all(count[0] == 1 for count in loans_per_book)

def test_second_loan_on_active_rejected(test_conn):
    # An active loan exists
    assert db_select(
        'SELECT * FROM loans WHERE member_id == ? AND book_id == ? AND return_date IS NULL',
        member_id, book_id,
        conn=test_conn
    )
    # We attempt loan on the book with an active loan expecting IntegrityError
    with pytest.raises(sqlite3.IntegrityError) as error:
        db_insert(
            'INSERT INTO loans (member_id, book_id, loan_date, due_date) VALUES (?, ?, ?, ?)',
            member_id, book_id, '2000-01-01', '2000-01-15',
            conn=test_conn
        )
    # Database returns IntegrityError when trying to loan the already borrowed book
    assert error.type == sqlite3.IntegrityError

    # Only one active loan exists after refused second loan
    active_loans = db_select(
        'SELECT * FROM loans WHERE member_id == ? AND book_id == ? AND return_date IS NULL',
        member_id, book_id,
        conn=test_conn
    )
    assert len(active_loans) == 1


def test_returned_book_can_loan_after(test_conn):
    # The book has a active loan
    assert db_select(
        'SELECT * FROM loans WHERE member_id == ? AND book_id == ? AND return_date IS NULL',
        member_id, book_id,
        conn=test_conn
    )
    # We return the book with an UPDATE on return_date field
    db_update(
        'UPDATE loans SET return_date = ? WHERE member_id == ? AND book_id == ?',
        date.today(), member_id, book_id,
        conn=test_conn
    )
    # The book now has no active loans
    assert not db_select(
        'SELECT * FROM loans WHERE member_id == ? AND book_id == ? AND return_date IS NULL',
        member_id, book_id,
        conn=test_conn
    )
    # We attempt to loan the book
    db_insert(
        'INSERT INTO loans (member_id, book_id, loan_date, due_date) VALUES (?, ?, ?, ?)',
        member_id, book_id, date.today(), date.today()+due_delta,
        conn=test_conn
    )

    active_loans = db_select(
        'SELECT * FROM loans WHERE member_id == ? AND book_id == ? AND return_date IS NULL',
        member_id, book_id,
        conn=test_conn
    )
    total_loans = db_select(
        'SELECT * FROM loans WHERE member_id == ? AND book_id == ?',
        member_id, book_id,
        conn=test_conn
    )
    # The book has 1 active loan and 2 total loans including returned ones.
    assert len(active_loans) == 1
    assert len(total_loans) == 2