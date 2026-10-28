'''
SQLite Database Helpers
'''
import os.path
from sqlite3 import connect, Connection, IntegrityError

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
    try: cursor.execute(command, sanitize_input(*args))
    except IntegrityError as e: print('Integrity error occured: ', e)
    cursor.close()
    conn.commit()

def db_insert_many(command: str, values: list) -> None:
    cursor = conn.cursor()
    try: cursor.executemany(command, values)
    except IntegrityError as e: print('Integrity error occured: ', e)
    cursor.close()
    conn.commit()

def db_update(command: str, *args) -> int:
    cursor = conn.cursor()
    try: cursor.execute(command, sanitize_input(*args))
    except IntegrityError as e: print('Integrity error occured: ', e)
    changes = conn.total_changes
    cursor.close()
    conn.commit()
    return changes

def db_delete(command: str, *args) -> None:
    cursor = conn.cursor()
    cursor.execute(command, sanitize_input(*args))
    cursor.close()
    conn.commit()

def sanitize_input(*args) -> tuple:
    return (*args,)

def validate_loan(book_id: int) -> bool:
    command = 'SELECT * FROM loans WHERE book_id == ? AND return_date IS NULL'
    return not db_select(command, book_id)

def validate_return(member_id: int, book_id: int) -> bool:
    command = 'SELECT * FROM loans WHERE member_id == ? AND book_id == ? AND return_date IS NULL'
    return not not db_select(command, member_id, book_id) #cheeky not not

def validate_add_book(title: str, author_name: str) -> bool:
    command =  ('SELECT b.title, a.author_name, b.published FROM books b '
                'JOIN book_author ba ON b.book_id = ba.book_id '
                'JOIN authors a ON ba.author_id = a.author_id '
                'WHERE b.title == ? AND a.author_name == ?')
    return not db_select(command, title, author_name)
    
def validate_add_author(author_name: str) -> bool:
    command = 'SELECT * FROM authors WHERE author_name == ?'
    return not db_select(command, author_name)