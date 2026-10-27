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


def db_select(query: str) -> None:
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()


def db_insert(command: str, values: tuple) -> None:
    cursor = conn.cursor()
    cursor.execute(command, value)
    cursor.close()
    conn.commit()


def db_insert_many(command: str, values: list) -> None:
    cursor = conn.cursor()
    cursor.executemany(command, values)
    cursor.close()
    conn.commit()


def sanitize_input(*args) -> tuple:
    return (*args,)