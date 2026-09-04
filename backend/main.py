from __future__ import annotations

import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import (
	ChatRequest,
	ChatResponse,
	BookingRequest,
	BookingResponse,
	CustomerState,
	SiteVisitStatus,
)
from .session import SessionManager, SessionNotFoundError
from .agent import agent
from .booking import simulator
from .analytics import generate_analytics


app = FastAPI(title="AI Real-Estate Chatbot")

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


session_manager = SessionManager()


@app.get("/health")
def health() -> dict:
	return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
	try:
		# ensure session
		sid = session_manager.ensure_session(req.session_id)
		# store user message
		session_manager.add_user_message(sid, req.message)
		history = session_manager.get_history(sid)
		state = session_manager.get_customer_state(sid)

		# Attempt to extract an explicit booking datetime from the latest user message.
		# If present, perform backend booking immediately and only confirm after simulator.book().
		last_user = req.message
		booking_dt = None
		try:
			if hasattr(agent, "llm") and hasattr(agent.llm, "extract_booking_datetime"):
				booking_dt = agent.llm.extract_booking_datetime(agent.system_prompt, last_user)
		except Exception:
			booking_dt = None

		if booking_dt:
			# Build booking request and call simulator
			book_req = BookingRequest(session_id=sid, customer_name=state.name, property_id=None, slot=booking_dt)
			resp = simulator.book(book_req)
			if resp.success:
				# update session and append assistant confirmation
				session_manager.update_customer_state(sid, site_visit_status=SiteVisitStatus.booked)
				session_manager.add_assistant_message(sid, "Your site visit has been successfully booked for the requested date and time. Thank you!")
				return ChatResponse(
					session_id=sid,
					reply="Your site visit has been successfully booked for the requested date and time. Thank you!",
					success=True,
					state=session_manager.get_customer_state(sid),
					messages=session_manager.get_history(sid),
					conversation_ended=True,
				)
			else:
				# booking failed; update state and inform user
				session_manager.update_customer_state(sid, site_visit_status=SiteVisitStatus.booking_failed)
				session_manager.add_assistant_message(sid, f"Booking failed: {resp.message}")
				return ChatResponse(
					session_id=sid,
					reply=f"Booking failed: {resp.message}",
					success=False,
					state=session_manager.get_customer_state(sid),
					messages=session_manager.get_history(sid),
					conversation_ended=False,
				)

		# No booking datetime found; proceed with normal assistant generation
		reply, updated_state = agent.generate(history, state)
		conversation_ended = agent.should_end_conversation(history, updated_state)

		# store assistant message
		session_manager.add_assistant_message(sid, reply)

		# persist state if changed
		if updated_state != state:
			session_manager.update_customer_state(sid, **updated_state.dict())

		# return structured response
		return ChatResponse(
			session_id=sid,
			reply=reply,
			success=True,
			state=updated_state,
			messages=session_manager.get_history(sid),
			conversation_ended=conversation_ended,
		)
	except SessionNotFoundError:
		raise HTTPException(status_code=404, detail="Session not found")
	except Exception:
		# hide internal errors from clients
		raise HTTPException(status_code=500, detail="internal server error")


@app.post("/reset")
def reset(body: dict):
	sid = body.get("session_id")
	if not sid:
		raise HTTPException(status_code=400, detail="session_id required")
	try:
		session_manager.reset_session(sid)
		return {"status": "reset", "session_id": sid}
	except SessionNotFoundError:
		raise HTTPException(status_code=404, detail="Session not found")


@app.post("/book-visit", response_model=BookingResponse)
def book_visit(req: BookingRequest):
	try:
		resp = simulator.book(req)

		# update session site visit status if session provided
		sid = req.session_id
		if sid:
			try:
				if resp.success:
					session_manager.update_customer_state(sid, site_visit_status=SiteVisitStatus.booked)
					# add assistant confirmation message only after successful booking
					session_manager.add_assistant_message(sid, resp.message)
				else:
					session_manager.update_customer_state(sid, site_visit_status=SiteVisitStatus.booking_failed)
			except SessionNotFoundError:
				# ignore session update if session doesn't exist
				pass

		return resp
	except Exception:
		raise HTTPException(status_code=500, detail="internal server error")


@app.post("/analytics")
def analytics_endpoint(body: dict):
	sid = body.get("session_id")
	if not sid:
		raise HTTPException(status_code=400, detail="session_id required")
	try:
		state = session_manager.get_customer_state(sid)
		history = session_manager.get_history(sid)
		a = generate_analytics(state, history)
		return a
	except SessionNotFoundError:
		raise HTTPException(status_code=404, detail="Session not found")
	except Exception:
		raise HTTPException(status_code=500, detail="internal server error")
