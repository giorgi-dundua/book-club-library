from sqlite3 import Connection, IntegrityError
from sqlite3 import Error as SQLiteError
from typing import Annotated
from datetime import date

from fastapi import Depends, FastAPI, HTTPException

from auth import require_api_key
from database import db_connect
from models import BookCreate, LoanCreate, LoanReturn, MemberUpdate

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
        'overdue_loans': overdue_loans}


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
