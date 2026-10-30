"""
Search book and show if avaible

"""
import sqlite3
from database import db_select
from string import capwords

def get_book(title: str) -> list:
    #title = 'Pride and Prejudice'

    #book_id = 1

    #result = db_select( "SELECT book_id, title FROM books WHERE book_id = ?", title)
    
    
    try:
        result = db_select(
            """ 
            SELECT b.title, l.return_date
            FROM books b
            LEFT JOIN loans l ON b.book_id = l.book_id
            WHERE b.title = ?
            """, title)
    
    except sqlite3.Error as e:
        raise print(f"Database error: {e}")

    return result


def show_book(book):
    for title, return_date in book:
        if return_date is None:
            status = "Not available"
        else:
            status = "Available"
    
    print("Book found:")
    print(f"{title} - {status}")


def search_book():

    title = capwords(input("Search book by title: ").strip())
    found_book = get_book(title)

    if not found_book:
        print(f"{title} was not found in the catalog.")
    else:
        show_book(found_book)


search_book()