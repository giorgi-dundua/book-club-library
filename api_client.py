import requests


class LibraryApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, **kwargs):
        response = requests.request(
            method, f"{self.base_url}{path}", timeout=5, **kwargs
        )

        response.raise_for_status()
        return response.json()

    def check_health(self) -> dict:
        return self._request("GET", "/health")
