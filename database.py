'''
SQLite Database Helpers
'''
import os.path
from sqlite3 import connect, Connection, IntegrityError, Error

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'bookclub.db')


def db_connect() -> Connection:
    conn = connect(db_path)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def db_select(command: str, *args, conn: Connection | None = None) -> list:
    self_connect = conn is None
    if self_connect: conn = db_connect()

    try:
        cursor = conn.cursor()
        cursor.execute(command, sanitize_input(*args))
        return cursor.fetchall()
    finally:
        cursor.close()
        if self_connect: conn.close()


def db_insert(command: str, *args, conn: Connection | None = None):
    self_connect = conn is None
    if self_connect: conn = db_connect()

    try:
        cursor = conn.cursor()
        cursor.execute(command, sanitize_input(*args))
        conn.commit()
    except IntegrityError:
        conn.rollback()
        raise
    finally:
        cursor.close()
        if self_connect: conn.close()


def db_insert_many(command: str, values: list, conn: Connection | None = None):
    self_connect = conn is None
    if self_connect: conn = db_connect()

    try:
        cursor = conn.cursor()
        cursor.executemany(command, values)
        conn.commit()
    except IntegrityError:
        conn.rollback()
        raise
    finally:
        cursor.close()
        if self_connect: conn.close()


def db_update(command: str, *args, conn: Connection | None = None) -> int:
    self_connect = conn is None
    if self_connect: conn = db_connect()

    try:
        cursor = conn.cursor()
        cursor.execute(command, sanitize_input(*args))
        changes = conn.total_changes
        conn.commit()
        return changes
    except IntegrityError:
        conn.rollback()
        raise
    finally:
        cursor.close()
        if self_connect: conn.close()


def db_delete(command: str, *args, conn: Connection | None = None):
    self_connect = conn is None
    if self_connect: conn = db_connect()

    try:
        cursor = conn.cursor()
        cursor.execute(command, sanitize_input(*args))
        conn.commit()
    except IntegrityError:
        conn.rollback()
        raise
    finally:
        cursor.close()
        if self_connect: conn.close()


def sanitize_input(*args) -> tuple:
    return (*args,)


def validate_loan(book_id: int) -> bool:
    ''' validates that there are no active loans on a book '''
    command = 'SELECT * FROM loans WHERE book_id == ? AND return_date IS NULL'
    return not db_select(command, book_id)


def validate_return(member_id: int, book_id: int) -> bool:
    ''' validates that the member has an active loan of the book '''
    command = 'SELECT * FROM loans WHERE member_id == ? AND book_id == ? AND return_date IS NULL'
    return bool(db_select(command, member_id, book_id))


def validate_add_book(title: str, author_name: str) -> bool:
    command =  ('SELECT b.title, a.author_name, b.published FROM books b '
                'JOIN book_author ba ON b.book_id = ba.book_id '
                'JOIN authors a ON ba.author_id = a.author_id '
                'WHERE b.title == ? AND a.author_name == ?')
    return not db_select(command, title, author_name)

 
def validate_add_author(author_name: str) -> bool:
    command = 'SELECT * FROM authors WHERE author_name == ?'
    return not db_select(command, author_name)