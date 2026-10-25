import pytest

from api_client import APIClient
from config import BASE_URL, REQUEST_TIMEOUT_SECONDS
from data_factory import booking_payload

@pytest.fixture
def api():

    return APIClient(
        BASE_URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
        )

@pytest.fixture
def booking(api):

    payload = booking_payload()

    response = api.post("/booking", json=payload)

    assert response.status_code == 200, (
        f"Booking creation failed: "
        f"HTTP {response.status_code} — {response.text}"
        )

    booking_id = response.json().get("bookingid")

    assert booking_id is not None, (
        "Booking creation succeeded but the response "
        "did not contain a bookingid."
        )

    yield booking_id, payload

# Another user may delete the booking before fixture teardown.
    try:
        delete_response = api.delete(
            f"/booking/{booking_id}",
            authenticated=True,
            )

        if delete_response.status_code == 201:
            print(f"Booking {booking_id} deleted successfully.")

        elif delete_response.status_code == 404:
            print(f"Booking {booking_id} was already deleted.")

        else:
            print(
                f"Cleanup warning for booking {booking_id}: "
                f"HTTP {delete_response.status_code} — "
                f"{delete_response.text}"
                )

    except Exception as exc:
        print(f"Cleanup failed for booking {booking_id}: {exc}")
