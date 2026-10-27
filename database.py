'''
SQLite Database Helpers
'''
import os.path
from sqlite3 import connect

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'bookclub.db')

def db_connect(init=False) -> Connection:
    '''init param for writing bookclub.db from Schema'''
    conn = connect(db_path)
    if init: db_init(conn, read_schema())
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def db_insert_many(conn, command, values):
    cursor = conn.cursor()
    cursor.executemany(command, values)
    cursor.close()
    conn.commit()

def sanitize_input(*args) -> tuple:
    return (*args,)