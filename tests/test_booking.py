from datetime import datetime

from backend.booking import simulator
from backend.models import BookingRequest


def test_booking_success():
    slot = datetime(2026, 10, 5, 11, 0)

    request = BookingRequest(
        session_id="test-session",
        customer_name="Test User",
        property_id="northstar-one",
        slot=slot,
    )

    response = simulator.book(request)

    assert response.success is True
    assert response.booking_id is not None
    assert response.slot == slot
    assert response.message == "Booking confirmed"