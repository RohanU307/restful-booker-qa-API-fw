from datetime import date, timedelta
from uuid import uuid4


def booking_payload():
    """Create unique booking data with valid, future check-in/check-out dates."""
    checkin = date.today() + timedelta(days=30)
    checkout = checkin + timedelta(days=3)
    suffix = uuid4().hex[:8]
    return {
        "firstname": f"Test{suffix}",
        "lastname": "Guest",
        "totalprice": 450,
        "depositpaid": True,
        "bookingdates": {
            "checkin": checkin.isoformat(),
            "checkout": checkout.isoformat(),
        },
        "additionalneeds": "Breakfast",
    }


def changed_payload(original, *, totalprice=None):
    payload = dict(original)
    payload["bookingdates"] = dict(original["bookingdates"])
    if totalprice is not None:
        payload["totalprice"] = totalprice
    return payload

def create_booking(api, payload):
    """Create a booking and return its ID."""

    response = api.post(
        "/booking",
        json=payload
    )

    assert response.status_code == 200, (
        f"Booking creation failed: "
        f"{response.status_code} {response.text}"
    )

    booking_id = response.json().get("bookingid")

    assert booking_id is not None, (
        "Booking creation response did not contain bookingid"
    )

    return booking_id
