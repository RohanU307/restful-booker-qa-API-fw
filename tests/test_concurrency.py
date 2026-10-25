from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier
from time import time_ns

from schemas import validate_booking


def test_two_threads_update_same_booking(api, booking):
    """
    Submit two conflicting PUT requests concurrently to the same booking.

    Verify:
    - Both threads are coordinated using a barrier.
    - Request initiation timestamps are recorded.
    - HTTP responses are captured.
    - The final booking matches one complete submitted payload.
    - No unexpected partial payload merge is present.
    """

    booking_id, original_payload = booking

    # Prepare two complete, conflicting booking payloads.
    payload_a = deepcopy(original_payload)
    payload_a["firstname"] = "ConcurrentUserA"
    payload_a["lastname"] = "ThreadA"
    payload_a["totalprice"] = 610

    payload_b = deepcopy(original_payload)
    payload_b["firstname"] = "ConcurrentUserB"
    payload_b["lastname"] = "ThreadB"
    payload_b["totalprice"] = 820

    # Each worker waits until both threads are ready.
    start_barrier = Barrier(2)

    def update_booking(payload, thread_name):
        start_barrier.wait(timeout=10)

        # Record the time immediately before submitting the request.
        started_at_ns = time_ns()

        response = api.put(
            f"/booking/{booking_id}",
            json=payload,
            authenticated=True,
            headers={"Content-Type": "application/json"},
        )

        return {
            "thread": thread_name,
            "started_at_ns": started_at_ns,
            "status_code": response.status_code,
            "response_text": response.text,
            "response_json": (
                response.json()
                if response.headers.get("Content-Type", "").startswith(
                    "application/json"
                )
                else None
            ),
        }

    # Execute both updates using separate worker threads.
    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(
            update_booking,
            payload_a,
            "Thread A",
        )

        future_b = executor.submit(
            update_booking,
            payload_b,
            "Thread B",
        )

        result_a = future_a.result(timeout=30)
        result_b = future_b.result(timeout=30)

    # Display evidence from both concurrent requests.
    print("\n--- Concurrent Update Results ---")

    for result in (result_a, result_b):
        print(
            f"{result['thread']}: "
            f"HTTP {result['status_code']}, "
            f"started_at_ns={result['started_at_ns']}"
        )
        print(f"Response: {result['response_text']}")

    start_difference_ns = abs(
        result_a["started_at_ns"] - result_b["started_at_ns"]
    )

    print(
        "Difference between recorded request initiation times: "
        f"{start_difference_ns:,} nanoseconds"
    )

    print(
        "Difference between recorded initiation times: "
        f"{start_difference_ns / 1_000_000:.3f} milliseconds"
    )

    # The standard successful outcome for this API is HTTP 200.
    # If this fails, inspect the response to determine whether the
    # sandbox returned an authentication, missing-record, or server error.
    assert result_a["status_code"] == 200, (
        f"Thread A update failed: HTTP {result_a['status_code']}; "
        f"response={result_a['response_text']}"
    )

    assert result_b["status_code"] == 200, (
        f"Thread B update failed: HTTP {result_b['status_code']}; "
        f"response={result_b['response_text']}"
    )

    # Retrieve the final state after both requests have completed.
    final_response = api.get(f"/booking/{booking_id}")

    assert final_response.status_code == 200, (
        f"Unable to retrieve final booking state: "
        f"HTTP {final_response.status_code}; "
        f"response={final_response.text}"
    )

    final_booking = final_response.json()

    # Validate the structure and business invariants of the final state.
    validate_booking(final_booking)

    # The final state must match one of the two complete payloads.
    # A mixture of Thread A and Thread B fields is not acceptable.
    assert final_booking == payload_a or final_booking == payload_b, (
        "Unexpected final booking state detected. "
        "The final record does not match either complete submitted payload. "
        f"\nThread A payload: {payload_a}"
        f"\nThread B payload: {payload_b}"
        f"\nFinal booking: {final_booking}"
    )

    print("\n--- Final Booking State ---")
    print(final_booking)

    if final_booking == payload_a:
        print("Observed outcome: Thread A's complete payload persisted.")
    else:
        print("Observed outcome: Thread B's complete payload persisted.")

    print(
        "Data integrity verified: the final booking matches one complete "
        "submitted payload without unexpected partial field merging."
    )