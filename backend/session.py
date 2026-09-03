from __future__ import annotations

import threading
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from .models import ChatMessage, CustomerState, Role


class SessionNotFoundError(KeyError):
	pass


class SessionManager:
	"""In-memory session manager.

	Stores per-session chat history (list of `ChatMessage`) and a `CustomerState`.
	"""

	def __init__(self) -> None:
		self._sessions: Dict[str, Dict] = {}
		self._lock = threading.Lock()

	def create_session(self, session_id: Optional[str] = None) -> str:
		with self._lock:
			sid = session_id or str(uuid.uuid4())
			now = datetime.utcnow()
			self._sessions[sid] = {
				"created_at": now,
				"history": [],  # type: List[ChatMessage]
				"state": CustomerState(),
			}
			return sid

	def get_session(self, session_id: str) -> Dict:
		try:
			return self._sessions[session_id]
		except KeyError:
			raise SessionNotFoundError(f"Session not found: {session_id}")

	def ensure_session(self, session_id: Optional[str]) -> str:
		if session_id and session_id in self._sessions:
			return session_id
		return self.create_session(session_id)

	def add_message(self, session_id: str, role: Role, content: str) -> ChatMessage:
		with self._lock:
			session = self.get_session(session_id)
			msg = ChatMessage(role=role, content=content)
			session["history"].append(msg)
			# update last active
			session["last_active"] = datetime.utcnow()
			return msg

	def add_user_message(self, session_id: str, content: str) -> ChatMessage:
		return self.add_message(session_id, Role.user, content)

	def add_assistant_message(self, session_id: str, content: str) -> ChatMessage:
		return self.add_message(session_id, Role.assistant, content)

	def get_history(self, session_id: str) -> List[ChatMessage]:
		session = self.get_session(session_id)
		return list(session.get("history", []))

	def get_customer_state(self, session_id: str) -> CustomerState:
		session = self.get_session(session_id)
		return session.get("state")

	def update_customer_state(self, session_id: str, **updates) -> CustomerState:
		with self._lock:
			session = self.get_session(session_id)
			state: CustomerState = session.get("state")
			updated = state.copy(update=updates)
			session["state"] = updated
			session["last_active"] = datetime.utcnow()
			return updated

	def reset_session(self, session_id: str) -> None:
		with self._lock:
			if session_id in self._sessions:
				now = datetime.utcnow()
				self._sessions[session_id] = {
					"created_at": now,
					"history": [],
					"state": CustomerState(),
				}
			else:
				raise SessionNotFoundError(session_id)

