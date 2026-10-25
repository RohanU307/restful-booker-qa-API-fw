import threading

import requests

from auth_manager import AuthManager

class APIClient:

#HTTP client with authentication recovery and a single retry.


    AUTH_FAILURE_CODES = {401, 403}

    def __init__(
        self,
        base_url: str,
        timeout: float = 10,
        token_ttl_seconds: float = 300,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self.auth = AuthManager(
            self.base_url,
            timeout=timeout,
            token_ttl_seconds=token_ttl_seconds,
        )

        self._thread_local = threading.local()

    @property
    def session(self):
        """Return the HTTP session associated with the current thread."""
        if not hasattr(self._thread_local, "session"):
            self._thread_local.session = requests.Session()

        return self._thread_local.session

    def _request(
        self,
        method: str,
        path: str,
        *,
        authenticated: bool = False,
        **kwargs,
    ):
        url = f"{self.base_url}{path}"
        headers = dict(kwargs.pop("headers", {}) or {})

        rejected_token = None

        if authenticated:
            rejected_token = self.auth.get_token()
            headers["Cookie"] = f"token={rejected_token}"

        response = self.session.request(
            method,
            url,
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )

        # Retry once after an authentication-related failure.
        if (
            authenticated
            and response.status_code in self.AUTH_FAILURE_CODES
        ):
            new_token = self.auth.refresh_if_current(rejected_token)
            headers["Cookie"] = f"token={new_token}"

            response = self.session.request(
                method,
                url,
                headers=headers,
                timeout=self.timeout,
                **kwargs,
            )

        return response

    def get(self, path, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path, **kwargs):
        return self._request("POST", path, **kwargs)

    def put(self, path, **kwargs):
        return self._request("PUT", path, **kwargs)

    def patch(self, path, **kwargs):
        return self._request("PATCH", path, **kwargs)

    def delete(self, path, **kwargs):
        return self._request("DELETE", path, **kwargs)
