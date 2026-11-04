import os

from dotenv import load_dotenv
from fastapi import Header, HTTPException

load_dotenv()


def require_api_key(x_api_key: str | None = Header(default=None)):
    api_key = os.getenv("API_KEY")

    if not api_key or x_api_key != api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
        )
