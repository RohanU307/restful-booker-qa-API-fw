
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

from auth_manager import AuthManager


def test_token_is_cached():
    manager = AuthManager(
        "https://restful-booker.herokuapp.com"
    )

    mock_response = Mock()
    mock_response.json.return_value = {"token": "test-token-123"}
    mock_response.raise_for_status.return_value = None

    with patch("auth_manager.requests.post", return_value=mock_response) as mock_post:
        first_token = manager.get_token()
        second_token = manager.get_token()

        assert first_token == "test-token-123"
        assert second_token == "test-token-123"

        # Only one login request should be made because the token is cached.
        assert mock_post.call_count == 1

    print("Token caching verified: only one login request was made.")


def test_concurrent_token_generation():
    manager = AuthManager(
        "https://restful-booker.herokuapp.com"
    )

    mock_response = Mock()
    mock_response.json.return_value = {"token": "shared-test-token"}
    mock_response.raise_for_status.return_value = None

    with patch("auth_manager.requests.post", return_value=mock_response) as mock_post:
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = [
                pool.submit(manager.get_token)
                for _ in range(5)
            ]

            tokens = [
                future.result(timeout=10)
                for future in futures
            ]

        assert all(token == "shared-test-token" for token in tokens)

        # The lock should prevent five simultaneous login requests.
        assert mock_post.call_count == 1

    print(
        "Concurrent token generation verified: "
        "five callers received the same cached token."
    )

def test_invalidated_token_is_regenerated():
    manager = AuthManager(
        "https://restful-booker.herokuapp.com"
    )

    first_response = Mock()
    first_response.json.return_value = {"token": "old-token"}
    first_response.raise_for_status.return_value = None

    second_response = Mock()
    second_response.json.return_value = {"token": "new-token"}
    second_response.raise_for_status.return_value = None

    with patch(
        "auth_manager.requests.post",
        side_effect=[first_response, second_response]
    ) as mock_post:

        # First request generates a token.
        first_token = manager.get_token()
        assert first_token == "old-token"

        # Invalidate the cached token.
        manager.invalidate()

        # Next request should generate a replacement token.
        second_token = manager.get_token()
        assert second_token == "new-token"

        # Confirm that authentication was requested twice.
        assert mock_post.call_count == 2

    print(
        "Token invalidation verified: "
        "the old token was replaced with a new token."
    )

def test_simultaneous_refresh_reuses_new_token():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    import time

    manager = AuthManager(
        "https://restful-booker.herokuapp.com"
    )

    # Simulate an already-cached token that the server rejected.
    manager._token = "old-token"

    barrier = Barrier(2)

    mock_response = Mock()
    mock_response.json.return_value = {"token": "new-token"}
    mock_response.raise_for_status.return_value = None

    def refresh():
        barrier.wait(timeout=5)
        return manager.refresh_if_current("old-token")

    with patch(
        "auth_manager.requests.post",
        return_value=mock_response
    ) as mock_post:

        with ThreadPoolExecutor(max_workers=2) as pool:
            future_a = pool.submit(refresh)
            future_b = pool.submit(refresh)

            token_a = future_a.result(timeout=10)
            token_b = future_b.result(timeout=10)

        assert token_a == "new-token"
        assert token_b == "new-token"

        # Only one replacement token should be generated.
        assert mock_post.call_count == 1

    print(
        "Simultaneous refresh verified: "
        "both threads reused the same replacement token."
    )

def test_expired_cached_token_is_regenerated():
    from unittest.mock import Mock, patch
    from auth_manager import AuthManager

    manager = AuthManager(
        "https://restful-booker.herokuapp.com",
        token_ttl_seconds=60,
    )

    first_response = Mock()
    first_response.json.return_value = {"token": "first-token"}
    first_response.text = '{"token": "first-token"}'

    second_response = Mock()
    second_response.json.return_value = {"token": "second-token"}
    second_response.text = '{"token": "second-token"}'

    with patch(
        "auth_manager.requests.post",
        side_effect=[first_response, second_response],
    ) as mock_post:

        first_token = manager.get_token()
        assert first_token == "first-token"

        # Simulate expiration of the local token cache.
        manager._token_created_at -= 61

        second_token = manager.get_token()

        assert second_token == "second-token"
        assert mock_post.call_count == 2

    print("Token expiration and regeneration verified.")