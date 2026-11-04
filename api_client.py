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

        try:
            response = requests.request(
                method,
                f"{self.base_url}{path}",
                headers=headers,
                timeout=timeout,
                **kwargs,
            )

            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout as error:
            raise LibraryApiError("The request took too long.") from error
        except requests.exceptions.ConnectionError as error:
            raise LibraryApiError("Could not connect to the server") from error
        except requests.exceptions.JSONDecodeError as error:
            raise LibraryApiError("The response was not valid JSON") from error
        except requests.exceptions.HTTPError as error:
            status = error.response.status_code
            raise LibraryApiError(f"API returned HTTP {status}") from error
        except requests.exceptions.RequestException as error:
            raise LibraryApiError("The API request failed.") from error

    def check_health(self) -> dict:
        return self._request("GET", "/health")

    def create_book(
        self, title: str, authors: list[str], published_year: int | None = None
    ) -> dict:
        return self._request(
            "POST",
            "/books",
            json={"title": title, "authors": authors, "published_year": published_year},
            authenticated=True,
        )

    def get_most_borrowed_books(self) -> list[dict]:
        return self._request("GET", "/statistics/most-borrowed")

    def get_never_borrowed_books(self) -> list[dict]:
        return self._request("GET", "/books/never-borrowed")


class LibraryApiError(Exception):
    pass
