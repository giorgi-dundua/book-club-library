import os

import requests
from dotenv import load_dotenv

load_dotenv()


class LibraryApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = os.getenv("API_KEY")

    def _request(
        self, method: str, path: str, *, authenticated: bool = False, **kwargs
    ):
        headers = kwargs.pop("headers", {})
        timeout = kwargs.pop("timeout", 5)

        if authenticated:
            if not self.api_key:
                raise LibraryApiError("API_KEY is not configured.")
            headers["X-API-Key"] = self.api_key

        response = requests.request(
            method, f"{self.base_url}{path}", headers=headers, timeout=timeout, **kwargs
        )

        response.raise_for_status()
        return response.json()

    def check_health(self) -> dict:
        return self._request("GET", "/health")

    def create_book(self, title: str, authors: list[str]) -> dict:
        return self._request(
            "POST",
            "/books",
            json={"title": title, "authors": authors},
            authenticated=True,
        )


class LibraryApiError(Exception):
    pass
