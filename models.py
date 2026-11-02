from datetime import date

from pydantic import BaseModel


class LoanCreate(BaseModel):
    member_id: int
    book_id: int
    loan_date: date
    due_date: date


class LoanReturn(BaseModel):
    return_date: date
