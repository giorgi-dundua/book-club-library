from datetime import date

from pydantic import BaseModel


class LoanCreate(BaseModel):
    member_id: int
    book_id: int
    loan_date: date
    due_date: date


class LoanReturn(BaseModel):
    return_date: date


class MemberUpdate(BaseModel):
    member_name:    str | None = None
    email:          str | None = None
    phone:          str | None = None