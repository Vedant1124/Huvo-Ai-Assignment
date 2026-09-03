from __future__ import annotations

from typing import Dict, Any, Optional

from .models import CustomerState


def generate_analytics(state: CustomerState, history: Optional[list] = None) -> Dict[str, Any]:
    """Return structured analytics from a completed conversation.

    Use `null` (None) for unavailable values and never invent values.
    """
    def none_if_missing(value):
        return value if value is not None else None

    analytics = {
        "lead_summary": None,
        "configuration": none_if_missing(state.configuration),
        "budget": none_if_missing(state.budget),
        "purpose": none_if_missing(state.purpose),
        "timeline": none_if_missing(state.timeline),
        "interest_level": none_if_missing(getattr(state.interest_level, "value", state.interest_level)),
        "site_visit_status": none_if_missing(getattr(state.site_visit_status, "value", state.site_visit_status)),
        "follow_up_required": none_if_missing(state.follow_up_required),
        "follow_up_preference": none_if_missing(state.follow_up_preference),
        "escalation_required": none_if_missing(state.escalation_required),
        "do_not_contact": none_if_missing(state.do_not_contact),
    }

    # Build a conservative lead summary from known state fields only.
    parts = []
    if state.name:
        parts.append(f"name: {state.name}")
    if state.purpose:
        parts.append(f"purpose: {state.purpose}")
    if state.budget is not None:
        parts.append(f"budget: {state.budget}")
    if state.timeline:
        parts.append(f"timeline: {state.timeline}")
    if state.interest_level is not None:
        parts.append(f"interest_level: {getattr(state.interest_level, 'value', state.interest_level)}")

    analytics["lead_summary"] = "; ".join(parts) if parts else None

    return analytics
# analytics helpers (placeholder)
