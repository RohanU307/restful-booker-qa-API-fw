
import threading
import time

import requests


class AuthManager:
    """
    Thread-safe token manager for the Restful Booker demo API.

    TOKEN_TTL_SECONDS controls how long the client caches a token.
    It is a local cache policy, not a verified server-side expiry value.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 10,
        token_ttl_seconds: float = 300,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.token_ttl_seconds = token_ttl_seconds

        self._token = None
        self._token_created_at = None
        self._lock = threading.Lock()

    def _is_token_usable(self) -> bool:
        """Return whether a cached token is within its local cache lifetime."""

        if not self._token or self._token_created_at is None:
            return False

        age = time.monotonic() - self._token_created_at

        return age < self.token_ttl_seconds

    def _generate_token(self) -> str:
        """Authenticate and store a newly generated token."""

        response = requests.post(
            f"{self.base_url}/auth",
            json={
                "username": "admin",
                "password": "password123",
            },
            timeout=self.timeout,
        )

        response.raise_for_status()

        token = response.json().get("token")

        if not token:
            raise RuntimeError(
                f"Auth response did not contain a token: {response.text}"
            )

        self._token = token
        self._token_created_at = time.monotonic()

        return token

    def get_token(self, force_refresh: bool = False) -> str:
        """
        Return a usable cached token or generate a new one.

        The lock ensures concurrent callers do not generate multiple
        tokens when the cache is empty or expired.
        """

        if not force_refresh and self._is_token_usable():
            return self._token

        with self._lock:
            # Check again because another thread may have refreshed it.
            if not force_refresh and self._is_token_usable():
                return self._token

            return self._generate_token()

    def refresh_if_current(self, rejected_token: str) -> str:
        """
        Refresh a rejected token only if it is still the cached token.

        If another thread has already replaced the rejected token,
        reuse the newer token instead of authenticating again.
        """

        with self._lock:
            if (
                self._token
                and self._token != rejected_token
                and self._is_token_usable()
            ):
                return self._token

            return self._generate_token()



    def invalidate(self):
        """Clear the cached token and its local creation timestamp."""
        with self._lock:
            self._token = None
            self._token_created_at = None
