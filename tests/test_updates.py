
from copy import deepcopy

from schemas import validate_booking


def test_put_same_payload_three_times_is_stable(api, booking):
    booking_id, original = booking

    # Preserve an independent copy of the original booking.
    expected_payload = deepcopy(original)
    observed_states = []

    # Send the same PUT payload three times.
    for attempt in range(3):
        response = api.put(
            f"/booking/{booking_id}",
            json=expected_payload,
            authenticated=True,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 200, (
            f"PUT attempt {attempt + 1} failed: "
            f"{response.status_code} {response.text}"
        )

        actual = response.json()

        # Validate the booking structure and date invariants.
        validate_booking(actual)

        # Confirm every field matches the submitted payload.
        assert actual == expected_payload, (
            f"Booking state differs from the expected payload "
            f"after PUT attempt {attempt + 1}.\n"
            f"Expected: {expected_payload}\n"
            f"Actual: {actual}"
        )

        observed_states.append(deepcopy(actual))

    # All three PUT operations should produce the same state.
    assert observed_states[0] == observed_states[1]
    assert observed_states[1] == observed_states[2]

    # Verify the final state persisted on the server.
    final_response = api.get(f"/booking/{booking_id}")

    assert final_response.status_code == 200, (
        f"Final GET failed: "
        f"{final_response.status_code} {final_response.text}"
    )

    final_booking = final_response.json()
    validate_booking(final_booking)

    assert final_booking == expected_payload, (
        f"Final booking state differs from the expected payload.\n"
        f"Expected: {expected_payload}\n"
        f"Actual: {final_booking}"
    )

    print(
        "PUT idempotency verified: three identical updates produced "
        "the same state, and the final state persisted."
    )


def test_patch_changes_only_requested_field(api, booking):
    booking_id, original = booking

    # Read the booking before PATCH.
    before_response = api.get(f"/booking/{booking_id}")

    assert before_response.status_code == 200, (
        f"Initial GET failed: "
        f"{before_response.status_code} {before_response.text}"
    )

    before = before_response.json()
    expected = deepcopy(before)

    # Change only the total price.
    expected["totalprice"] = 600

    response = api.patch(
        f"/booking/{booking_id}",
        json={"totalprice": 600},
        authenticated=True,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200, (
        f"PATCH failed: {response.status_code} {response.text}"
    )

    # Read the booking after PATCH.
    after_response = api.get(f"/booking/{booking_id}")

    assert after_response.status_code == 200, (
        f"Final GET failed: "
        f"{after_response.status_code} {after_response.text}"
    )

    updated = after_response.json()
    validate_booking(updated)

    # Verify that the requested field changed.
    assert updated["totalprice"] == 600

    # Verify every field matches the expected state.
    assert updated == expected, (
        f"PATCH changed unexpected fields.\n"
        f"Expected: {expected}\n"
        f"Actual: {updated}"
    )

    # Explicitly check that all other fields were preserved.
    for field in before:
        if field != "totalprice":
            assert updated[field] == before[field], (
                f"Unexpected change in field '{field}': "
                f"before={before[field]!r}, "
                f"after={updated[field]!r}"
            )

    print(
        "PATCH field preservation verified: totalprice changed to 600 "
        "and all other fields remained unchanged."
    )
