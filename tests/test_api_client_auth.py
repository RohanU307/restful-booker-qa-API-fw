
from unittest.mock import Mock, patch

from api_client import APIClient


def test_api_client_refreshes_token_after_401():
    client = APIClient(
        "https://restful-booker.herokuapp.com"
    )

    unauthorized_response = Mock()
    unauthorized_response.status_code = 401
    unauthorized_response.text = "Unauthorized"

    success_response = Mock()
    success_response.status_code = 200
    success_response.text = '{"ok": true}'

    captured_headers = []

    def fake_request(method, url, **kwargs):
        # Save a snapshot of the headers at request time.
        captured_headers.append(dict(kwargs["headers"]))

        if len(captured_headers) == 1:
            return unauthorized_response

        return success_response

    with patch.object(
        client.auth,
        "get_token",
        return_value="old-token"
    ), patch.object(
        client.auth,
        "refresh_if_current",
        return_value="new-token"
    ) as mock_refresh, patch.object(
        client.session,
        "request",
        side_effect=fake_request
    ) as mock_request:

        response = client.get(
            "/booking/1",
            authenticated=True
        )

        assert response.status_code == 200

        mock_refresh.assert_called_once_with("old-token")
        assert mock_request.call_count == 2

        # Verify the first request used the old token.
        assert captured_headers[0]["Cookie"] == "token=old-token"

        # Verify the retry used the new token.
        assert captured_headers[1]["Cookie"] == "token=new-token"

    print(
        "Authentication recovery verified: "
        "401 received, token refreshed, and request retried successfully."
    )

def test_api_client_refreshes_token_after_403():
    from unittest.mock import Mock, patch

    from api_client import APIClient

    client = APIClient("https://restful-booker.herokuapp.com")

    forbidden_response = Mock()
    forbidden_response.status_code = 403
    forbidden_response.text = "Forbidden"

    success_response = Mock()
    success_response.status_code = 200
    success_response.text = '{"ok": true}'

    captured_headers = []

    def fake_request(method, url, **kwargs):
        captured_headers.append(dict(kwargs["headers"]))

        if len(captured_headers) == 1:
            return forbidden_response

        return success_response

    with (
        patch.object(
            client.auth,
            "get_token",
            return_value="old-token",
        ),
        patch.object(
            client.auth,
            "refresh_if_current",
            return_value="new-token",
        ) as mock_refresh,
        patch.object(
            client.session,
            "request",
            side_effect=fake_request,
        ) as mock_request,
    ):
        response = client.get(
            "/booking/1",
            authenticated=True,
        )

    assert response.status_code == 200
    assert mock_request.call_count == 2

    mock_refresh.assert_called_once_with("old-token")

    assert captured_headers[0]["Cookie"] == "token=old-token"
    assert captured_headers[1]["Cookie"] == "token=new-token"

    print("HTTP 403 recovery verified.")

def test_api_client_does_not_retry_authentication_indefinitely():
    from unittest.mock import Mock, patch

    from api_client import APIClient

    client = APIClient("https://restful-booker.herokuapp.com")

    unauthorized_response = Mock()
    unauthorized_response.status_code = 401
    unauthorized_response.text = "Unauthorized"

    with (
        patch.object(
            client.auth,
            "get_token",
            return_value="old-token",
        ),
        patch.object(
            client.auth,
            "refresh_if_current",
            return_value="new-token",
        ) as mock_refresh,
        patch.object(
            client.session,
            "request",
            return_value=unauthorized_response,
        ) as mock_request,
    ):
        response = client.get(
            "/booking/1",
            authenticated=True,
        )

    assert response.status_code == 401
    assert mock_request.call_count == 2
    mock_refresh.assert_called_once_with("old-token")

    print("Single-retry limit verified.")