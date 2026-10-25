
from data_factory import booking_payload, create_booking
from recovery import update_booking_safely


def test_update_recovers_if_booking_is_deleted(api):
    # Step 1: Create a booking
    original_payload = booking_payload()
    original_id = create_booking(api, original_payload)

    replacement_id = None

    try:
        # Step 2: Simulate another user deleting the booking
        delete_response = api.delete(
            f"/booking/{original_id}",
            authenticated=True
        )

        assert delete_response.status_code in (201, 404), (
            f"Unexpected delete response: "
            f"{delete_response.status_code} {delete_response.text}"
        )

        # Step 3: Prepare an updated payload
        updated_payload = dict(original_payload)
        updated_payload["bookingdates"] = dict(
            original_payload["bookingdates"]
        )
        updated_payload["totalprice"] = 999

        # Step 4: Attempt the update with recovery enabled
        replacement_id, update_response = update_booking_safely(
            api,
            original_id,
            original_payload,
            updated_payload
        )

        # Step 5: Verify that a replacement booking was created
        assert replacement_id != original_id, (
            "Expected recovery to create a replacement booking"
        )

        # Step 6: Verify the updated price
        assert update_response["totalprice"] == 999

        # Step 7: Confirm the replacement exists on the server
        get_response = api.get(f"/booking/{replacement_id}")

        assert get_response.status_code == 200
        assert get_response.json()["totalprice"] == 999

        print(
            f"Update recovery successful: "
            f"original ID={original_id}, "
            f"replacement ID={replacement_id}"
        )

    finally:
        # Step 8: Clean up the replacement booking
        if replacement_id is not None:
            api.delete(
                f"/booking/{replacement_id}",
                authenticated=True
            )

