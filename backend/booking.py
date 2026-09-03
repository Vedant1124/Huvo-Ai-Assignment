from __future__ import annotations

from datetime import datetime
from typing import Optional
import hashlib

from .models import BookingRequest, BookingResponse


class BookingSimulator:
	"""Simple booking simulator that accepts any valid slot.

	This simulator does NOT check real availability — it always returns
	success for a syntactically valid `datetime` slot. This keeps tests
	deterministic and the backend authoritative for confirmations.
	"""

	def _make_booking_id(self, slot: datetime, property_id: Optional[str]) -> str:
		raw = f"{slot.isoformat()}|{property_id or ''}"
		return hashlib.sha1(raw.encode("utf-8")).hexdigest()

	def book(self, request: BookingRequest) -> BookingResponse:
		slot = request.slot
		# Basic validation: slot must be a datetime
		if not isinstance(slot, datetime):
			return BookingResponse(
				success=False,
				message="Invalid slot provided",
				booking_id=None,
				slot=None,
			)

		booking_id = self._make_booking_id(slot, request.property_id)
		return BookingResponse(
			success=True,
			message="Booking confirmed",
			booking_id=booking_id,
			slot=slot,
		)


# convenience single-instance simulator
simulator = BookingSimulator()

