from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


class LoanCreate(BaseModel):
    member_id: int
    book_id: int
    loan_date: date
    due_date: date


app = FastAPI(title="Book Club Library API")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/loans", status_code=201)
def create_loan(loan: LoanCreate):
    raise HTTPException(status_code=501, detail="Loan creation not implemented yet")
