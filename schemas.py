from datetime import date
from jsonschema import validate

BOOKING_SCHEMA = {
    "type": "object",
    "required": [
        "firstname", "lastname", "totalprice", "depositpaid",
        "bookingdates", "additionalneeds"
    ],
    "properties": {
        "firstname": {"type": "string", "minLength": 1},
        "lastname": {"type": "string", "minLength": 1},
        "totalprice": {"type": "integer", "minimum": 0},
        "depositpaid": {"type": "boolean"},
        "bookingdates": {
            "type": "object",
            "required": ["checkin", "checkout"],
            "properties": {
                "checkin": {"type": "string", "format": "date"},
                "checkout": {"type": "string", "format": "date"}
            },
            "additionalProperties": True
        },
        "additionalneeds": {"type": "string"}
    },
    "additionalProperties": True
}


def validate_booking(booking):
    validate(instance=booking, schema=BOOKING_SCHEMA)
    checkin = date.fromisoformat(booking["bookingdates"]["checkin"])
    checkout = date.fromisoformat(booking["bookingdates"]["checkout"])
    assert checkout > checkin, "checkout must be later than checkin"
