import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


class LibraryApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = os.getenv("API_KEY")

    def _request(
        self, method: str, path: str, *, authenticated: bool = False, **kwargs
    ) -> Any:
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
            if response.status_code == 204:
                return None
            return response.json()
        except requests.exceptions.Timeout as error:
            raise LibraryApiError("The request took too long") from error
        except requests.exceptions.ConnectionError as error:
            raise LibraryApiError("Could not connect to the server") from error
        except requests.exceptions.JSONDecodeError as error:
            raise LibraryApiError("The response was not valid JSON") from error
        except requests.exceptions.HTTPError as error:
            error_response = error.response
            if error_response is None:
                raise LibraryApiError(f"HTTP error occurred: {error}") from error
            error_msg = f"API returned HTTP {error_response.status_code}"
            try:
                json_msg = error_response.json()
                if isinstance(json_msg, dict):
                    msg = json_msg.get("detail")
                    if isinstance(msg, str) and msg.strip():
                        error_msg = msg
            except requests.exceptions.JSONDecodeError:
                pass
            raise LibraryApiError(error_msg) from error
        except requests.exceptions.RequestException as error:
            raise LibraryApiError("The API request failed") from error

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

    def get_book(self, book_id: int) -> dict:
        return self._request("GET", f"/books/{book_id}")

    def get_books(self, search: str | None = None) -> list[dict]:
        params = {"search": search} if search else {}
        return self._request("GET", "/books", params=params)

    def patch_book(self, book_id: int, changes: dict) -> dict:
        return self._request(
            "PATCH", f"/books/{book_id}", authenticated=True, json=changes
        )

    def delete_book(self, book_id: int) -> None:
        return self._request("DELETE", f"/books/{book_id}", authenticated=True)

    def get_members_personal_data(self) -> dict:
        return self._request("GET", "/members/personal", authenticated=True)

    def get_member_personal_data(self, member_id: int) -> dict:
        return self._request(
            "GET", f"/members/{member_id}/personal", authenticated=True
        )


class LibraryApiError(Exception):
    pass
