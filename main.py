from fastapi import FastAPI, HTTPException

from  database import create_book, get_book
from models import BookCreate

app = FastAPI(title="Book Club Library API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/books", status_code=201)
def add_book(book: BookCreate) -> dict:
    """Add a book and its authors to the catalogue."""
    published = f"{book.published_year}-01-01" if book.published_year else None
    book_id = create_book(book.title, book.authors, published)
    return get_book(book_id)


@app.get("/books/{book_id}")
def read_book(book_id: int) -> dict:
    """Show one book with its authors."""
    book = get_book(book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book