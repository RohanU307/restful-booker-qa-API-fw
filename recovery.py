from data_factory import create_booking


def ensure_booking_exists(api, booking_id, payload):
    """Return an existing booking ID or recreate a missing booking."""

    response = api.get(f"/booking/{booking_id}")

    if response.status_code == 200:
        return booking_id

    if response.status_code == 404:
        print(
            f"Booking {booking_id} is missing. "
            "Recreating the prerequisite booking."
        )

        new_booking_id = create_booking(api, payload)

        print(f"Replacement booking created: {new_booking_id}")

        return new_booking_id

    raise RuntimeError(
        f"Unable to verify booking {booking_id}: "
        f"HTTP {response.status_code} — {response.text}"
    )

def update_booking_safely(
    api,
    booking_id,
    original_payload,
    updated_payload
):
    """Update a booking and recover if it disappears."""

    booking_id = ensure_booking_exists(
        api,
        booking_id,
        original_payload
    )

    response = api.put(
        f"/booking/{booking_id}",
        json=updated_payload,
        authenticated=True
    )

    if response.status_code == 404:
        print(
            f"Booking {booking_id} disappeared during update. "
            "Recreating the prerequisite."
        )

        booking_id = create_booking(
            api,
            original_payload
        )

        response = api.put(
            f"/booking/{booking_id}",
            json=updated_payload,
            authenticated=True
        )

    assert response.status_code == 200, (
        f"Booking update failed: "
        f"{response.status_code} {response.text}"
    )

    return booking_id, response.json()