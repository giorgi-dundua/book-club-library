"""
Lists all books from the catalog

"""
import sqlite3
from database import db_select


def get_books_data() -> list:
    try:
         books_data = db_select(
            """ 
            SELECT b.title, GROUP_CONCAT(a.author_name, ', '), b.published
            FROM books b
            JOIN book_author ba ON b.book_id = ba.book_id
            LEFT JOIN authors a ON ba.author_id = a.author_id
            GROUP BY b.title
            ORDER BY b.title ASC

            """,)
    except sqlite3.Error as e:
        raise print(f"Database error: {e}")

    return books_data

def show_all_books(list_books: list) -> None:
    print("\n--- Shows all books from the catalog ---\n")
    for title, authors, published in list_books:
        print("Book:", title)
        print("Authors:", authors)
        print("Publiched:", published)
        print("-" * 40)




list_books = get_books_data()
show_all_books(list_books)


