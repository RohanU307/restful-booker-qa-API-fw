from data_factory import booking_payload
from schemas import validate_booking


def test_date_and_schema_invariants(api, booking):
    booking_id, _ = booking
    response = api.get(f"/booking/{booking_id}")
    assert response.status_code == 200
    validate_booking(response.json())



def test_duplicate_date_range_behavior_is_recorded(api, booking):
    """
    Investigate duplicate date-range behavior.

    The public sandbox may accept overlapping bookings.
    Cleanup is best-effort so a transient network failure during
    DELETE does not obscure the main test result.
    """
    import requests

    booking_id, payload = booking

    duplicate = dict(payload)
    duplicate["bookingdates"] = dict(payload["bookingdates"])

    response = api.post("/booking", json=duplicate)

    assert response.status_code in (200, 400, 409), (
        f"Unexpected duplicate-booking response: "
        f"{response.status_code} {response.text}"
    )

    if response.status_code == 200:
        duplicate_id = response.json().get("bookingid")

        assert duplicate_id is not None, (
            "Duplicate booking was accepted, but bookingid was missing."
        )

        print(
            "Sandbox accepted overlapping/duplicate date payload; "
            f"original booking={booking_id}, "
            f"second booking={duplicate_id}. "
            "No room-level conflict validation was observed."
        )

        try:
            cleanup = api.delete(
                f"/booking/{duplicate_id}",
                authenticated=True,
            )

            if cleanup.status_code == 201:
                print(
                    f"Duplicate booking {duplicate_id} "
                    "deleted successfully."
                )

            elif cleanup.status_code == 404:
                print(
                    f"Duplicate booking {duplicate_id} "
                    "was already deleted."
                )

            else:
                print(
                    f"Cleanup warning for duplicate booking "
                    f"{duplicate_id}: HTTP {cleanup.status_code}"
                )

        except requests.RequestException as exc:
            print(
                f"Transient cleanup network error for booking "
                f"{duplicate_id}: {exc}"
            )

            print(
                "Cleanup did not complete during this attempt. "
                "The booking may still exist in the shared sandbox."
            )

    elif response.status_code in (400, 409):
        print(
            "Sandbox rejected the duplicate date payload with "
            f"HTTP {response.status_code}."
        )




from copy import deepcopy
from api_client import APIClient
from config import BASE_URL, REQUEST_TIMEOUT_SECONDS
from data_factory import booking_payload
from schemas import validate_booking


def test_duplicate_booking_from_independent_client():
    """
    Attempt to create two bookings with identical dates using
    independent API client instances.

    Restful Booker does not expose room IDs or distinct user
    identities for booking creation, so this test documents
    actual sandbox behavior rather than assuming conflict rejection.
    """

    client_a = APIClient(BASE_URL, REQUEST_TIMEOUT_SECONDS)
    client_b = APIClient(BASE_URL, REQUEST_TIMEOUT_SECONDS)

    payload_a = booking_payload()
    payload_b = deepcopy(payload_a)

    created_booking_ids = []

    try:
        # First booking
        response_a = client_a.post(
            "/booking",
            json=payload_a,
        )

        assert response_a.status_code == 200, (
            f"First booking creation failed: "
            f"{response_a.status_code} {response_a.text}"
        )

        booking_id_a = response_a.json()["bookingid"]
        created_booking_ids.append(booking_id_a)

        print(f"\nFirst booking created: {booking_id_a}")

        # Second booking with the same date range
        response_b = client_b.post(
            "/booking",
            json=payload_b,
        )

        print(
            f"Duplicate booking response: "
            f"HTTP {response_b.status_code}"
        )

        print(f"Response body: {response_b.text}")

        if response_b.status_code in (400, 409):
            print(
                "Sandbox rejected the duplicate booking "
                "with a validation/conflict response."
            )

        elif response_b.status_code == 200:
            booking_id_b = response_b.json()["bookingid"]
            created_booking_ids.append(booking_id_b)

            assert booking_id_b != booking_id_a, (
                "The duplicate creation returned the same booking ID."
            )

            duplicate_booking = response_b.json()["booking"]

            validate_booking(duplicate_booking)

            assert duplicate_booking == payload_b, (
                "Duplicate booking payload was unexpectedly modified."
            )

            print(
                "Sandbox accepted the duplicate date range. "
                "No room-level conflict validation was observed."
            )

        else:
            raise AssertionError(
                "Unexpected response during duplicate booking creation: "
                f"HTTP {response_b.status_code} {response_b.text}"
            )

    finally:
        # Cleanup both bookings, even if an assertion fails.
        for booking_id in created_booking_ids:
            try:
                response = client_a.delete(
                    f"/booking/{booking_id}",
                    authenticated=True,
                )

                if response.status_code == 201:
                    print(f"Booking {booking_id} deleted successfully.")

                elif response.status_code == 404:
                    print(
                        f"Booking {booking_id} was already deleted."
                    )

                else:
                    print(
                        f"Cleanup warning for booking {booking_id}: "
                        f"HTTP {response.status_code}"
                    )

            except Exception as exc:
                print(
                    f"Cleanup warning for booking {booking_id}: {exc}"
                )