from schemas import validate_booking


def test_create_and_read_booking(api, booking):
    booking_id, expected = booking
    response = api.get(f"/booking/{booking_id}")
    assert response.status_code == 200
    actual = response.json()
    validate_booking(actual)
    assert actual["firstname"] == expected["firstname"]
    assert actual["lastname"] == expected["lastname"]


def test_missing_booking_returns_not_found(api):
    response = api.get("/booking/999999999")
    assert response.status_code == 404
