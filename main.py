from datetime import date
from sqlite3 import Connection
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from database import db_connect


class LoanCreate(BaseModel):
    member_id: int
    book_id: int
    loan_date: date
    due_date: date


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

    cursor = conn.execute(
        "INSERT INTO loans (member_id, book_id, loan_date, due_date) VALUES (?, ?, ?, ?)",
        (
            loan.member_id,
            loan.book_id,
            loan.loan_date.isoformat(),
            loan.due_date.isoformat(),
        ),
    )
    conn.commit()
    return {"loan_id": cursor.lastrowid}
