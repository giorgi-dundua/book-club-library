from datetime import date
from sqlite3 import Connection, IntegrityError
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from database import db_connect


class LoanCreate(BaseModel):
    member_id: int
    book_id: int
    loan_date: date
    due_date: date


class LoanReturn(BaseModel):
    return_date: date


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


@app.post("/loans", status_code=201)
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


@app.patch("/loans/{loan_id}/return")
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
