from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class Role(str, Enum):
	user = "user"
	assistant = "assistant"
	system = "system"


class ChatMessage(BaseModel):
	role: Role
	content: str
	timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
	session_id: Optional[str]
	message: str
	metadata: Optional[Dict[str, Any]] = None


class InterestLevel(str, Enum):
	low = "low"
	medium = "medium"
	high = "high"


class SiteVisitStatus(str, Enum):
	not_requested = "not_requested"
	requested = "requested"
	booked = "booked"
	booking_failed = "booking_failed"


class CustomerState(BaseModel):
	name: Optional[str] = None
	configuration: Optional[str] = None
	budget: Optional[float] = None
	purpose: Optional[str] = None
	timeline: Optional[str] = None
	interest_level: Optional[InterestLevel] = None
	site_visit_status: Optional[SiteVisitStatus] = SiteVisitStatus.not_requested
	follow_up_required: bool = False
	follow_up_preference: Optional[str] = None
	escalation_required: bool = False
	do_not_contact: bool = False


class ChatResponse(BaseModel):
	session_id: Optional[str]
	reply: str
	success: bool = True
	state: CustomerState
	messages: Optional[List[ChatMessage]] = None


class BookingRequest(BaseModel):
	session_id: Optional[str] = None
	customer_name: Optional[str] = None
	property_id: Optional[str] = None
	slot: datetime


class BookingResponse(BaseModel):
	success: bool
	message: str
	booking_id: Optional[str] = None
	slot: Optional[datetime] = None


class Analytics(BaseModel):
	messages_count: int = 0
	bookings_count: int = 0
	last_active: Optional[datetime] = None
	custom: Optional[Dict[str, Any]] = None

