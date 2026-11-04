'''
Init and Seed bookclub.db with Test Data
'''

import os.path
import sqlite3
from datetime import date, datetime, timedelta

from database import db_connect, db_insert_many

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'bookclub.db')
schema_path = os.path.join(base_dir, 'schema.sql')

conn = db_connect()

delta = timedelta(days=14)

books = [
    ('The Great Gatsby', date(1925, 1, 1)),
    ('To Kill a Mockingbird', date(1960, 1, 1)),
    ('1984', date(1949, 1, 1)),
    ('Pride and Prejudice', date(1813, 1, 1)),
    ('The Catcher in the Rye', date(1945, 1, 1)),
    ('The Hobbit', date(1937, 1, 1)),
    ('Fahrenheit 451', date(1953, 1, 1)),
    ('Jane Eyre', date(1847, 1, 1)),
    ('Animal Farm', date(1945, 1, 1)),
    ('The Lord of the Rings', date(1954, 1, 1)),
    ('Brave New World', date(1932, 1, 1)),
    ('The Alchemist', date(1988, 1, 1)),
    ('Moby Dick', date(1851, 1, 1)),
    ('War and Peace', date(1845, 1, 1)),
    ('The Odyssey', date(1488, 1, 1)),
    ('Crime and Punishment', date(1866, 1, 1)),
    ('Les Misérables', date(1852, 1, 1)),
    ('Dracula', date(1897, 1, 1)),
    ('The Shining', date(1977, 1, 1)),
    ('It', date(1986, 1, 1)),
    ('Good Omens', date(1990,1,1)),
]

members = [
    ('Anna Lindqvist', 'anna.lindqvist@example.com', '555-908070', date(2024, 3, 14)),
    ('Erik Johansson', 'erik.j@example.com', '555-123456', date(2023, 11, 2)),
    ('Sara Ahmed', 'sara.ahmed@example.com', '555-234567', date(2025, 1, 20)),
    ('Johan Berg', 'johan.berg@example.com', '555-345678', date(2022, 6, 30)),
    ('Maria Nilsson', 'maria.n@example.com', '555-456789', date(2025, 8, 11)),
    ('Ali Hassan', 'ali.hassan@example.com', '555-567890', date(2024, 9, 5)),
    ('Emma Karlsson', 'emma.k@example.com', '555-678901', date(2023, 2, 17)),
    ('Oskar Persson', 'oskar.p@example.com', '555-789012', date(2025, 5, 28)),
    ('Fatima Yilmaz', 'fatima.y@example.com', '555-890123', date(2024, 12, 1)),
    ('Lukas Ek', 'lukas.ek@example.com', '555-901234', date(2026, 1, 9)),
]

authors = [
    ('F. Scott Fitzgerald',),
    ('Harper Lee',),
    ('George Orwell',),
    ('Jane Austen',),
    ('J.D. Salinger',),
    ('J.R.R. Tolkien',),
    ('Ray Bradbury',),
    ('Charlotte Brontë',),
    ('J.R.R. Tolkien',),
    ('Aldous Huxley',),
    ('Paulo Coelho',),
    ('Herman Melville',),
    ('Leo Tolstoy',),
    ('Homer',),
    ('Fyodor Dostoevsky',),
    ('Victor Hugo',),
    ('Bram Stoker',),
    ('Stephen King',),
    ('Terry Pratchett',),
    ('Neil Gaiman',),
]

book_author = [
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
    (7, 7),
    (8, 8),
    (9, 3),
    (10, 9),
    (11, 10),
    (12, 11),
    (13, 12),
    (14, 13),
    (15, 14),
    (16, 15),
    (17, 16),
    (18, 17),
    (19, 18),
    (20, 18),
    (21, 19),
    (21, 20)
]

loans = [
    (1, 1,
        date(2026, 3, 1),
        date(2026, 3, 1) + delta,
        date(2026, 3, 10),
    ),
    (2, 2,
        date(2026, 5, 1),
        date(2026, 5, 1) + delta,
        date(2026, 5, 10),
    ),
    (3, 3,
        date(2026, 7, 1),
        date(2026, 7, 1) + delta,
        date(2026, 7, 10),
    ),
    (4, 1, date(2026, 9, 1), date(2026, 9, 1) + delta, None),
    (5, 2, date(2026, 10, 1), date(2026, 10, 1) + delta, None),
    (6, 3, date(2026, 10, 10), date(2026, 10, 10) + delta, None),
    (10, 21, date(2026, 10, 10), date(2026, 10, 10) + delta, None),
]


def read_schema() -> list:
    fd = open(schema_path, 'r')
    sql_file = fd.read()
    fd.close()
    return sql_file.split(';')


def db_init() -> None:
    '''Recreate the database tables and populate them with sample data.

    WARNING: Deletes existing records. Call only when a reset is intended.
    '''
    sqlite3.register_adapter(date, adapt_date_iso)
    sqlite3.register_adapter(datetime, adapt_datetime_iso)

    commands = read_schema()
    cursor = conn.cursor()
    for command in commands:
        try:
            cursor.execute(command)
        except sqlite3.Error as e:
            print('Failed SQL: ', command.strip())
            print('Error: ', e)
            raise
    cursor.close()
    db_seed_fields()
    conn.commit()


def adapt_date_iso(val):
    """Adapt datetime.date to ISO 8601 date."""
    return val.isoformat()


def adapt_datetime_iso(val):
    """Adapt datetime.datetime to timezone-naive ISO 8601 date."""
    return val.isoformat()


# Incase we need to delete db file before init
def db_delete_file() -> None:
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass


def format_seed_dates(rows: list) -> list:
    """Convert datetime values to ISO date strings before insertion."""
    return [
        tuple(
            value.date().isoformat() if isinstance(value, datetime) else value
            for value in row
        )
        for row in rows
    ]


def db_seed_fields() -> None:
    db_insert_many(
        'INSERT INTO books (title, published) VALUES (?, ?)',
        format_seed_dates(books),
    )
    db_insert_many(
        'INSERT INTO members (member_name, email, phone, joined) VALUES (?, ?, ?, ?)',
        format_seed_dates(members),
    )
    db_insert_many(
        'INSERT INTO authors (author_name) VALUES (?)', authors
    )
    db_insert_many(
        'INSERT INTO book_author (book_id, author_id) VALUES (?, ?)', book_author
    )
    db_insert_many(
        'INSERT INTO loans (member_id, book_id, loan_date, due_date, return_date) VALUES (?, ?, ?, ?, ?)',
        format_seed_dates(loans),
    )


if __name__ == "__main__":
    # Check for existing user tables before allowing a potentially destructive reset.
    tables_exist = conn.execute(
        "SELECT 1 FROM sqlite_master "
        "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
        "LIMIT 1"
    ).fetchone()

    if tables_exist:
        confirmation = input(
            "Existing database tables will be deleted and recreated. "
            "Type RESET to continue: "
        )

        if confirmation != "RESET":
            print("Initialization cancelled.")
            raise SystemExit(0)

    db_init()
    print("Database initialized and seeded.")
