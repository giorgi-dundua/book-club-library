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