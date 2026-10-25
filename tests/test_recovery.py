from data_factory import booking_payload, create_booking
from recovery import ensure_booking_exists


def test_recreate_booking_if_deleted(api):
    # Step 1: Generate unique booking data
    payload = booking_payload()

    # Step 2: Create the original booking
    original_id = create_booking(api, payload)

    replacement_id = None

    try:
        # Step 3: Simulate another user deleting the booking
        delete_response = api.delete(
            f"/booking/{original_id}",
            authenticated=True
        )

        assert delete_response.status_code in (201, 404), (
            f"Unexpected deletion response: "
            f"{delete_response.status_code} "
            f"{delete_response.text}"
        )

        # Step 4: Check whether the booking exists.
        # If missing, the recovery helper creates a replacement.
        replacement_id = ensure_booking_exists(
            api,
            original_id,
            payload
        )

        # Step 5: Verify that recovery returned a new booking ID
        assert replacement_id != original_id, (
            "Expected a new booking ID after the original was deleted"
        )

        # Step 6: Retrieve the replacement booking
        response = api.get(
            f"/booking/{replacement_id}"
        )

        assert response.status_code == 200

        actual = response.json()

        # Step 7: Verify the recovered booking's data
        assert actual["firstname"] == payload["firstname"]
        assert actual["lastname"] == payload["lastname"]
        assert actual["totalprice"] == payload["totalprice"]
        assert actual["bookingdates"] == payload["bookingdates"]

        print(
            f"Recovery successful: original booking "
            f"{original_id}, replacement booking {replacement_id}"
        )

    finally:
        # Step 8: Attempt to clean up the replacement booking
        if replacement_id is not None:
            api.delete(
                f"/booking/{replacement_id}",
                authenticated=True
            )