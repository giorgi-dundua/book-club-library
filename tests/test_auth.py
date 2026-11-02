import pytest
from fastapi import HTTPException

from auth import require_api_key


@pytest.mark.parametrize(
    "configured_key, supplied_key, expected_status",
    [
        ("secret", "secret", 200),
        ("secret", "wrong", 401),
        ("secret", None, 401),
        (None, "secret", 401),
    ],
)
def test_api_key(monkeypatch, configured_key, supplied_key, expected_status):
    if configured_key is None:
        monkeypatch.delenv("API_KEY", raising=False)
    else:
        monkeypatch.setenv("API_KEY", configured_key)

    if expected_status == 200:
        require_api_key(supplied_key)
    else:
        with pytest.raises(HTTPException) as exc:
            require_api_key(supplied_key)

        assert exc.value.status_code == expected_status
