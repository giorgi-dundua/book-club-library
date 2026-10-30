'''
SQLite Database Helpers
'''
import os.path
from sqlite3 import connect, Connection

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'bookclub.db')

def db_connect() -> Connection:
    conn = connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

conn = db_connect()

''' command using placeholder ? and *args for values '''
def db_select(command: str, *args) -> list:
    cursor = conn.cursor()
    cursor.execute(command, sanitize_input(*args))
    return cursor.fetchall()

def db_insert(command: str, *args) -> None:
    cursor = conn.cursor()
    cursor.execute(command, sanitize_input(*args))
    cursor.close()
    conn.commit()

def db_insert_many(command: str, values: list) -> None:
    cursor = conn.cursor()
    cursor.executemany(command, values)
    cursor.close()
    conn.commit()

def sanitize_input(*args) -> tuple:
    return (*args,)


def create_book(title: str, authors: list[str], published: str | None) -> int:
    """Insert a book and its authors in one transaction. Return the book_id."""
    book_conn = db_connect()
    try:
        cursor = book_conn.execute(
            "INSERT INTO books (title, published) VALUES (?, ?)",
            (title, published),
        )
        book_id = cursor.lastrowid

        for name in authors:
            row = book_conn.execute(
                "SELECT author_id FROM authors WHERE author_name = ?",
                (name,),
            ).fetchone()
            if row:
                author_id = row[0]
            else:
                author_id = book_conn.execute(
                    "INSERT INTO authors (author_name) VALUES (?)",
                    (name,),
                ).lastrowid
            book_conn.execute(
                "INSERT OR IGNORE INTO book_author (book_id, author_id) "
                "VALUES (?, ?)",
                (book_id, author_id),
            )
        book_conn.commit()
        return book_id
    except Exception:
        book_conn.rollback()
        raise
    finally:
        book_conn.close()


def get_book(book_id: int) -> dict | None:
    """Return one book with its authors, or None if it does not exist."""
    book_conn = db_connect()
    try:
        rows = book_conn.execute(
            "SELECT b.book_id, b.title, b.published, a.author_name "
            "FROM books b "
            "LEFT JOIN book_author ba ON ba.book_id = b.book_id "
            "LEFT JOIN authors a ON a.author_id = ba.author_id "
            "WHERE b.book_id = ?",
            (book_id,),
        ).fetchall()
    finally:
        book_conn.close()
    if not rows:
        return None
    return {
        "book_id": rows[0][0],
        "title": rows[0][1],
        "published_year": int(rows[0][2][:4]) if rows[0][2] else None,
        "authors": [row[3] for row in rows if row[3]],
    }