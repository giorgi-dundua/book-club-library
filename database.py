'''
SQLite Database Helpers
'''
import os.path
from sqlite3 import connect

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'bookclub.db')
schema_path = os.path.join(base_dir, 'schema.sql')


def db_connect(init=False) -> Connection:
    '''init param for writing bookclub.db from Schema'''
    if init: db_init()
    conn = connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def read_schema():
    fd = open(schema_path, 'r')
    sql_file = fd.read()
    fd.close()
    return sql_file.split(';')

def db_init(conn):
    for command in read_schema():
        try:
            conn.execute(command)
        except OperationalError, msg:
            print("Command skipped: ", msg)

def sanitize_input(*args) -> tuple:
    return (*args,)