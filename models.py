from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class LoanCreate(BaseModel):
    member_id: int
    book_id: int
    loan_date: date
    due_date: date


class LoanReturn(BaseModel):
    return_date: date


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    authors: list[str] = Field(min_length=1)
    published_year: int | None = Field(default=None, ge=1, le=9999)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Book title cannot be empty")
        return value

    @field_validator("authors")
    @classmethod
    def validate_authors(cls, values: list[str]) -> list[str]:
        cleaned = []
        seen = set()

        for author in values:
            author = author.strip()

            if not author:
                raise ValueError("Author name cannot be empty")

            if author.casefold() not in seen:
                cleaned.append(author)
                seen.add(author.casefold())

        if not cleaned:
            raise ValueError("At least one author is required")

        return cleaned


class BulkBookCreate(BaseModel):
    books: list[BookCreate] = Field(min_length=1, max_length=100)


class MemberUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    member_name: str | None = Field(min_length=2, max_length=100, default=None)
    email: EmailStr | None = Field(max_length=100, default=None)
    phone: str | None = Field(
        pattern=r"^[\+0-9][0-9\-\(\)\.\ ]{6,25}$",
        min_length=6,
        max_length=25,
        default=None,
    )
