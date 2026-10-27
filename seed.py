'''
Init and Seed bookclub.db with Test Data
'''
import os.path
import sqlite3
from datetime import datetime, timedelta

from database import db_connect, db_insert_many

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'bookclub.db')
schema_path = os.path.join(base_dir, 'schema.sql')

conn = db_connect()

delta = timedelta(days=14)

# book published dates not accurate
books = [
    (1, 'The Great Gatsby', datetime(2024, 3, 14)),
    (2, 'To Kill a Mockingbird', datetime(2024, 3, 14)),
    (3, '1984', datetime(2024, 3, 14)),
    (4, 'Pride and Prejudice', datetime(2024, 3, 14)),
    (5, 'The Catcher in the Rye', datetime(2024, 3, 14)),
    (6, 'The Hobbit', datetime(2024, 3, 14)),
    (7, 'Fahrenheit 451', datetime(2024, 3, 14)),
    (8, 'Jane Eyre', datetime(2024, 3, 14)),
    (9, 'Animal Farm', datetime(2024, 3, 14)),
    (10, 'The Lord of the Rings', datetime(2024, 3, 14)),
    (11, 'Brave New World', datetime(2024, 3, 14)),
    (12, 'The Alchemist', datetime(2024, 3, 14)),
    (13, 'Moby Dick', datetime(2024, 3, 14)),
    (14, 'War and Peace', datetime(2024, 3, 14)),
    (15, 'The Odyssey', datetime(2024, 3, 14)),
    (16, 'Crime and Punishment', datetime(2024, 3, 14)),
    (17, 'Les Misérables', datetime(2024, 3, 14)),
    (18, 'Dracula', datetime(2024, 3, 14)),
    (19, 'The Shining', datetime(2024, 3, 14)),
    (20, 'It', datetime(2024, 3, 14))
]

members = [
    (1, 'Anna Lindqvist', 'anna.lindqvist@example.com', 'phone', datetime(2024, 3, 14), 0),
    (2, 'Erik Johansson', 'erik.j@example.com', 'phone', datetime(2023, 11, 2), 0),
    (3, 'Sara Ahmed', 'sara.ahmed@example.com', 'phone', datetime(2025, 1, 20), 0),
    (4, 'Johan Berg', 'johan.berg@example.com', 'phone', datetime(2022, 6, 30), 0),
    (5, 'Maria Nilsson', 'maria.n@example.com', 'phone', datetime(2025, 8, 11), 0),
    (6, 'Ali Hassan', 'ali.hassan@example.com', 'phone', datetime(2024, 9, 5), 0),
    (7, 'Emma Karlsson', 'emma.k@example.com', 'phone', datetime(2023, 2, 17), 0),
    (8, 'Oskar Persson', 'oskar.p@example.com', 'phone', datetime(2025, 5, 28), 0),
    (9, 'Fatima Yilmaz', 'fatima.y@example.com', 'phone', datetime(2024, 12, 1), 0),
    (10, 'Lukas Ek', 'lukas.ek@example.com', 'phone', datetime(2026, 1, 9), 0)
]

authors = [
    (1, 'F. Scott Fitzgerald'), (2, 'Harper Lee'), (3, 'George Orwell'), (4, 'Jane Austen'),
    (5, 'J.D. Salinger'), (6, 'J.R.R. Tolkien'), (7, 'Ray Bradbury'), (8, 'Charlotte Brontë'),
    (9, 'George Orwell'), (10, 'J.R.R. Tolkien'), (11, 'Aldous Huxley'), (12, 'Paulo Coelho'),
    (13, 'Herman Melville'), (14, 'Leo Tolstoy'), (15, 'Homer'), (16, 'Fyodor Dostoevsky'),
    (17, 'Victor Hugo'), (18, 'Bram Stoker'), (19, 'Stephen King'), (20, 'Stephen King')
]

book_author = [
    (1, 1), (2, 2), (3, 3),(4, 4), (5, 5),
    (6, 6), (7, 7), (8, 8),(9, 9), (10, 10),
    (11, 11), (12, 12), (13, 13),(14, 14), (15, 15),
    (16, 16), (17, 17), (18, 18),(19, 19), (20, 20)
]

loans = [
    (1, 1, 1, datetime(2026,3,1), datetime(2026,3,1)+delta, None),
    (2, 2, 2, datetime(2026,5,1), datetime(2026,5,1)+delta, None),
    (3, 3, 3, datetime(2026,7,1), datetime(2026,7,1)+delta, None),
    (4, 4, 1, datetime(2026,9,1), datetime(2026,9,1)+delta, None),
    (5, 5, 2, datetime(2026,10,1), datetime(2026,10,1)+delta, None),
    (6, 6, 3, datetime(2026,10,10), datetime(2026,10,10)+delta, None)
]

def read_schema() -> list:
    fd = open(schema_path, 'r')
    sql_file = fd.read()
    fd.close()
    return sql_file.split(';')

def db_init(conn):
    ''' run to init and seed bookclub.db '''
    commands = read_schema()
    cursor = conn.cursor()
    for command in commands:
        try:
            cursor.execute(command)
        except:
            print('Command skipped: ')
    cursor.close()
    db_seed_fields(conn)
    conn.commit()

# Incase we need to delete db file before init
def db_delete_file() -> None:
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass

def db_seed_fields(conn) -> None:
    db_insert_many(conn, 'INSERT INTO books (book_id, title, published) VALUES (?, ?, ?)', books)
    db_insert_many(conn, 'INSERT INTO members (member_id, member_name, email, phone, joined, deleted) VALUES (?, ?, ?, ?, ?, ?)', members)
    db_insert_many(conn, 'INSERT INTO authors (author_id, author_name) VALUES (?, ?)', authors)
    db_insert_many(conn, 'INSERT INTO book_author (book_id, author_id) VALUES (?, ?)', book_author)
    db_insert_many(conn, 'INSERT INTO loans (loan_id, member_id, book_id, loan_date, due_date, return_date) VALUES (?, ?, ?, ?, ?, ?)', loans)

''' RUN TO INIT'''
db_init(conn)