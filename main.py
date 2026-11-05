from sqlite3 import Connection, IntegrityError
from sqlite3 import Error as SQLiteError
from typing import Annotated
from datetime import date

from fastapi import Depends, FastAPI, HTTPException

from auth import require_api_key
from database import (
    db_connect,
    get_book,
    get_book_loan_statistics,
    get_never_borrowed_books,
)
from models import (
    BookCreate,
    BookPatch,
    BookUpdate,
    LoanCreate,
    LoanReturn,
    MemberUpdate,
)

app = FastAPI(title="Book Club Library API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


def get_db():
    conn = db_connect()
    try:
        yield conn
    finally:
        conn.close()


@app.get("/books/never-borrowed")
def read_never_borrowed_books(conn: Annotated[Connection, Depends(get_db)]):
    book_rows = get_never_borrowed_books(conn)
    keys = ["book_id", "title"]
    return [dict(zip(keys, row)) for row in book_rows]


def insert_book(conn: Connection, book: BookCreate) -> dict:
    published = (
        f"{book.published_year}-01-01" if book.published_year is not None else None
    )

    cursor = conn.execute(
        "INSERT INTO books (title, published) VALUES (?, ?)",
        (book.title, published),
    )

    book_id = cursor.lastrowid

    for author_name in book.authors:
        author = conn.execute(
            """
            SELECT author_id
            FROM authors
            WHERE LOWER(author_name) = LOWER(?)
            ORDER BY author_id
            LIMIT 1
            """,
            (author_name,),
        ).fetchone()

        if author is None:
            author_cursor = conn.execute(
                "INSERT INTO authors (author_name) VALUES (?)",
                (author_name,),
            )
            author_id = author_cursor.lastrowid
        else:
            author_id = author[0]

        conn.execute(
            """
            INSERT INTO book_author (book_id, author_id)
            VALUES (?, ?)
            """,
            (book_id, author_id),
        )

    return {
        "book_id": book_id,
        "title": book.title,
        "authors": book.authors,
        "published": published,
    }


def save_book_update(
    book_id: int,
    title: str,
    authors: list[str],
    published_year: int | None,
    conn: Connection,
) -> dict:
    """Save complete book information in SQLite."""

    existing_book = conn.execute(
        "SELECT book_id FROM books WHERE book_id = ?",
        (book_id,),
    ).fetchone()

    if existing_book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    published = f"{published_year}-01-01" if published_year is not None else None

    try:
        # Update the main book information.
        conn.execute(
            """
            UPDATE books
            SET title = ?, published = ?
            WHERE book_id = ?
            """,
            (title, published, book_id),
        )

        # Remove the old author relationships.
        conn.execute(
            "DELETE FROM book_author WHERE book_id = ?",
            (book_id,),
        )

        # Connect the book to its corrected authors.
        for author_name in authors:
            author = conn.execute(
                """
                SELECT author_id
                FROM authors
                WHERE LOWER(author_name) = LOWER(?)
                LIMIT 1
                """,
                (author_name,),
            ).fetchone()

            if author is None:
                cursor = conn.execute(
                    "INSERT INTO authors (author_name) VALUES (?)",
                    (author_name,),
                )
                author_id = cursor.lastrowid
            else:
                author_id = author[0]

            conn.execute(
                """
                INSERT INTO book_author (book_id, author_id)
                VALUES (?, ?)
                """,
                (book_id, author_id),
            )

        # Save all changes together.
        conn.commit()

    except IntegrityError as error:
        conn.rollback()
        print("DATABASE ERROR:", repr(error))

        raise HTTPException(
            status_code=409,
            detail="Book update conflicts with database constraints",
        ) from error

    except SQLiteError as error:
        conn.rollback()
        print("DATABASE ERROR:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="Internal database error",
        ) from error

    return {
        "book_id": book_id,
        "title": title,
        "authors": authors,
        "published": published,
    }


@app.put("/books/{book_id}", dependencies=[Depends(require_api_key)])
def replace_book(
    book_id: int,
    data: BookUpdate,
    conn: Annotated[Connection, Depends(get_db)],
):
    return save_book_update(
        book_id=book_id,
        title=data.title,
        authors=data.authors,
        published_year=data.published_year,
        conn=conn,
    )


@app.patch("/books/{book_id}", dependencies=[Depends(require_api_key)])
def patch_book(
    book_id: int,
    data: BookPatch,
    conn: Annotated[Connection, Depends(get_db)],
):
    # Find the current book.
    current_book = conn.execute(
        """
        SELECT title, published
        FROM books
        WHERE book_id = ?
        """,
        (book_id,),
    ).fetchone()

    if current_book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found",
        )

    # Find the current authors.
    current_authors = conn.execute(
        """
        SELECT a.author_name
        FROM authors a
        JOIN book_author ba ON a.author_id = ba.author_id
        WHERE ba.book_id = ?
        ORDER BY a.author_id
        """,
        (book_id,),
    ).fetchall()

    authors = [row[0] for row in current_authors]

    # Get only the fields supplied by the volunteer.
    changes = data.model_dump(exclude_unset=True)

    if not changes:
        raise HTTPException(
            status_code=422,
            detail="At least one field must be provided",
        )

    if "title" in changes and changes["title"] is None:
        raise HTTPException(
            status_code=422,
            detail="Title cannot be null",
        )

    if "authors" in changes and changes["authors"] is None:
        raise HTTPException(
            status_code=422,
            detail="Authors cannot be null",
        )

    # Keep existing values for fields not supplied.
    title = changes.get("title", current_book[0])

    published_year = int(current_book[1][:4]) if current_book[1] is not None else None

    published_year = changes.get(
        "published_year",
        published_year,
    )

    authors = changes.get("authors", authors)

    # Save the complete updated information.
    return save_book_update(
        book_id=book_id,
        title=title,
        authors=authors,
        published_year=published_year,
        conn=conn,
    )


@app.post("/books", dependencies=[Depends(require_api_key)], status_code=201)
def create_books(
    data: BookCreate | list[BookCreate],
    conn: Annotated[Connection, Depends(get_db)],
):
    books = data if isinstance(data, list) else [data]

    if not books:
        raise HTTPException(
            status_code=422,
            detail="At least one book is required",
        )

    if len(books) > 100:
        raise HTTPException(
            status_code=422,
            detail="Maximum 100 books can be added at once",
        )

    try:
        results = [insert_book(conn, book) for book in books]
        conn.commit()

        return {
            "message": "Books added successfully",
            "count": len(results),
            "books": results,
        }

    except IntegrityError as error:
        conn.rollback()
        print("DATABASE ERROR:", repr(error))

        raise HTTPException(
            status_code=409,
            detail="Internal database error",
        ) from error

    except SQLiteError as error:
        conn.rollback()
        print("DATABASE ERROR:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="Internal database error",
        ) from error

        
@app.get("/books/{book_id}")
def read_book(
    book_id: int,
    conn: Annotated[Connection, Depends(get_db)],
) -> dict:
    """Show one book with its authors."""
    book = get_book(conn, book_id)

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    return book


@app.get('/loans', dependencies=[Depends(require_api_key)])
def get_loans(conn: Annotated[Connection, Depends(get_db)]):
    active_loans = conn.execute(
        '''
        SELECT b.title, m.member_name, l.due_date, 
        l.loan_id, l.member_id, l.book_id 
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        JOIN members m ON l.member_id = m.member_id
        WHERE l.return_date IS NULL
        '''
    ).fetchall()

    if not active_loans:
        raise HTTPException(status_code=404, detail="No loans found")

    count = len(active_loans)
    loans = []
    overdue_loans = []

    for loan in active_loans:
        ids = dict(zip(
            ('loan_id', 'member_id', 'book_id'),
            loan[-3:]
        ))
        data = dict(zip(
            ('book', 'member', 'due_date', 'id_info'),
            (*loan[:3],ids)
        ))
        if data.get('due_date') < date.today().isoformat():
            overdue_loans.append(data)
        loans.append(data)

    overdue_loans.sort(key=lambda x: x.get('due_date'))

    return {
        'count': count,
        'active_loans': loans, 
        'overdue_loans': overdue_loans
    }


@app.post("/loans", dependencies=[Depends(require_api_key)], status_code=201)
def create_loan(loan: LoanCreate, conn: Annotated[Connection, Depends(get_db)]):
    member = conn.execute(
        "SELECT 1 FROM members WHERE member_id = ?",
        (loan.member_id,),
    ).fetchone()
    book = conn.execute(
        "SELECT 1 FROM books WHERE book_id = ?",
        (loan.book_id,),
    ).fetchone()
    active_loan = conn.execute(
        "SELECT 1 FROM loans WHERE book_id = ? AND return_date IS NULL LIMIT 1",
        (loan.book_id,),
    ).fetchone()

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    if active_loan is not None:
        raise HTTPException(status_code=409, detail="Book is already borrowed")

    try:
        cursor = conn.execute(
            "INSERT INTO loans (member_id, book_id, loan_date, due_date) "
            "VALUES (?, ?, ?, ?)",
            (
                loan.member_id,
                loan.book_id,
                loan.loan_date.isoformat(),
                loan.due_date.isoformat(),
            ),
        )
        conn.commit()

    except IntegrityError as error:
        conn.rollback()

        if (
            error.sqlite_errorname == "SQLITE_CONSTRAINT_UNIQUE"
            and "loans.book_id" in str(error)
        ):
            raise HTTPException(
                status_code=409,
                detail="Book is already borrowed",
            ) from error

        raise

    return {"loan_id": cursor.lastrowid}


@app.patch("/loans/{loan_id}/return", dependencies=[Depends(require_api_key)])
def return_loan(
    loan_id: int, loan: LoanReturn, conn: Annotated[Connection, Depends(get_db)]
):
    cursor = conn.execute(
        "UPDATE loans SET return_date = ? WHERE loan_id = ? AND return_date IS NULL",
        (loan.return_date.isoformat(), loan_id),
    )

    if cursor.rowcount == 0:
        existing_loan = conn.execute(
            "SELECT 1 FROM loans WHERE loan_id = ?", (loan_id,)
        ).fetchone()
        if existing_loan is None:
            raise HTTPException(status_code=404, detail="Loan not found")
        raise HTTPException(status_code=409, detail="Loan was already returned")

    conn.commit()

    return {
        "loan_id": loan_id,
        "return_date": loan.return_date.isoformat(),
    }


@app.patch("/members/{member_id}", dependencies=[Depends(require_api_key)])
def update_member(
    member_id: int, changes: MemberUpdate, conn: Annotated[Connection, Depends(get_db)]
):
    member = conn.execute(
        "SELECT member_name, email, phone, deleted from members "
        "WHERE member_id = ? AND deleted = 0",
        (member_id,),
    ).fetchone()

    if member is None:
        raise HTTPException(status_code=404, detail="Member not found")

    current_values = dict(zip(("member_name", "email", "phone"), member))
    changes_values = changes.model_dump(exclude_unset=True)

    if all(current_values.get(key) == val for key, val in changes_values.items()):
        return {"message": "No changes"}

    changes_placeholders = ", ".join([key + " = ?" for key in changes_values])

    try:
        conn.execute(
            "UPDATE OR IGNORE members SET " + changes_placeholders + " "
            "WHERE member_id = ?",
            (
                *changes_values.values(),
                member_id,
            ),
        )
        updated_member = conn.execute(
            "SELECT * from members WHERE member_id = ?", (member_id,)
        ).fetchone()

        conn.commit()

    except IntegrityError:
        conn.rollback()
        raise

    return dict(
        zip(
            ("member_id", "member_name", "email", "phone", "joined", "deleted"),
            updated_member,
        )
    )


@app.get('/members/{member_id}/loans', dependencies=[Depends(require_api_key)])
def get_member_loans(member_id: int, conn: Annotated[Connection, Depends(get_db)]):
    active_loans = conn.execute(
        '''
        SELECT b.title, m.member_name, l.due_date, 
        l.loan_id, l.member_id, l.book_id 
        FROM loans l
        JOIN books b ON l.book_id = b.book_id
        JOIN members m ON l.member_id = m.member_id
        WHERE l.return_date IS NULL 
        AND l.member_id = ?
        ''',
        (member_id,)
    ).fetchall()

    if not active_loans:
        raise HTTPException(status_code=404, detail="No loans found")

    count = len(active_loans)
    loans = []
    overdue_loans = []

    for loan in active_loans:
        ids = dict(zip(
            ('loan_id', 'member_id', 'book_id'),
            loan[-3:]
        ))
        data = dict(zip(
            ('book', 'member', 'due_date', 'id_info'),
            (*loan[:3],ids)
        ))
        if data.get('due_date') < date.today().isoformat():
            overdue_loans.append(data)
        loans.append(data)

    overdue_loans.sort(key=lambda x: x.get('due_date'))

    return {
        'member_id': member_id,
        'count': count,
        'active_loans': loans, 
        'overdue_loans': overdue_loans}
@app.get("/statistics/most-borrowed")
def read_book_loan_statistics(conn: Annotated[Connection, Depends(get_db)]):
    book_rows = get_book_loan_statistics(conn)
    keys = ["book_id", "title", "total_loans"]
    return [dict(zip(keys, row)) for row in book_rows]
