"""Pydantic models for the Book Club Library API."""
from pydantic import BaseModel, Field, field_validator


class BookCreate(BaseModel):
    """Data a volunteer sends to add a book."""

    title: str = Field(max_length=300)
    authors: list[str] = Field(min_length=1)
    published_year: int | None = Field(default=None, ge=1000, le=2100)

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("title must not be empty")
        return value

    @field_validator("authors")
    @classmethod
    def authors_not_blank(cls, names: list[str]) -> list[str]:
        cleaned = [name.strip() for name in names]
        if any(not name for name in cleaned):
            raise ValueError("author names must not be empty")
        return cleaned