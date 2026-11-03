from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoanCreate(BaseModel):
    member_id: int
    book_id: int
    loan_date: date
    due_date: date


class LoanReturn(BaseModel):
    return_date: date


class MemberUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')

    member_name:    str | None = Field(min_length=2, max_length=100, default=None)
    email:          EmailStr | None = Field(max_length=100, default=None)
    phone:          str | None = Field(
        pattern=r'^[\+0-9][0-9\-\(\)\.\ ]{6,25}$',
        min_length=6, 
        max_length=25,
        default=None
        )