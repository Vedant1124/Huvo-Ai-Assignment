from __future__ import annotations

import os
import json
from typing import List, Tuple, Optional, Dict
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables from .env before reading GROQ_API_KEY / GROQ_MODEL
load_dotenv()

from groq import Groq

from .models import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    CustomerState,
    Role,
    InterestLevel,
    SiteVisitStatus,
)


class SimpleGroqClient:
    """Wrapper around the official Groq client.

    Uses `GROQ_API_KEY` and `GROQ_MODEL` from environment variables.
    """

    def __init__(self) -> None:
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "groq-model")
        self.client: Optional[Groq] = None
        # store recent user messages seen during generate() calls
        self._recent_user_messages: List[str] = []
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception:
                self.client = None

    def generate(self, system_prompt: str, history: List[ChatMessage], state: CustomerState) -> str:
        if not self.client:
            raise RuntimeError("Groq client not configured")

        # Build messages payload: system prompt then conversation history
        messages = [{"role": "system", "content": system_prompt}]
        # append current state as a system note (JSON) to give the model context
        try:
            state_json = json.dumps(state.dict(), default=str)
            messages.append({"role": "system", "content": f"CURRENT_CUSTOMER_STATE: {state_json}"})
        except Exception:
            pass

        # store recent user messages for possible later extraction calls
        try:
            self._recent_user_messages = [m.content for m in history if m.role == Role.user]
        except Exception:
            self._recent_user_messages = []

        for m in history:
            messages.append({"role": m.role.value, "content": m.content})

        # Call Groq chat completions API
        try:
            resp = self.client.chat.completions.create(model=self.model, messages=messages)
            # Best-effort extraction of text
            if hasattr(resp, "choices") and resp.choices:
                choice = resp.choices[0]
                # many SDKs put text under message->content
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    return str(choice.message.content)
                # or under text
                if hasattr(choice, "text"):
                    return str(choice.text)
            # Fallback: try dict-like
            try:
                j = dict(resp)
                if "choices" in j and j["choices"]:
                    c = j["choices"][0]
                    if isinstance(c, dict) and "message" in c and "content" in c["message"]:
                        return str(c["message"]["content"]) 
                    if isinstance(c, dict) and "text" in c:
                        return str(c["text"])
            except Exception:
                pass

            # If nothing matched, raise to trigger clean error handling
            raise RuntimeError("unexpected Groq response format")
        except Exception as exc:
            # Bubble up as runtime error for caller to handle gracefully
            raise RuntimeError(f"Groq API error: {exc}") from exc

    def extract_json(self, system_prompt: str, user_text: str, state: CustomerState) -> Optional[Dict]:
        """Ask Groq to extract structured JSON for CustomerState fields from a single user message.

        Returns a dict of extracted fields (only those explicitly present), or None on error.
        """
        if not self.client:
            raise RuntimeError("Groq client not configured")

        instruction = (
            "You are a JSON extractor. Given the following single USER message, return a JSON object "
            "containing ONLY the fields explicitly provided by the user. Do not infer or add any fields. "
            "Fields: name (string), configuration (string, e.g. '2 BHK'), budget (number, in INR or absolute), "
            "purpose ('buy'|'rent'), timeline (string), interest_level ('low'|'medium'|'high'), "
            "site_visit_status ('not_requested'|'requested'|'booked'|'booking_failed'), "
            "follow_up_required (boolean), follow_up_preference (string), escalation_required (boolean), "
            "do_not_contact (boolean). Return STRICTLY valid JSON (object) and nothing else."
        )
        # Combine recent user messages (if any) with the current user_text so the model
        # can reason across messages (date in earlier user message + time in later one).
        combined_user_text = None
        try:
            combined_list = list(self._recent_user_messages) if hasattr(self, "_recent_user_messages") else []
            # append the latest user_text if not already present as last
            if not combined_list or combined_list[-1] != user_text:
                combined_list.append(user_text)
            combined_user_text = "\n".join(combined_list)
        except Exception:
            combined_user_text = user_text

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"EXTRACTION_INSTRUCTION: {instruction}"},
            {"role": "user", "content": combined_user_text},
        ]

        try:
            resp = self.client.chat.completions.create(model=self.model, messages=messages)
            # Extract text
            text = None
            if hasattr(resp, "choices") and resp.choices:
                c = resp.choices[0]
                if hasattr(c, "message") and hasattr(c.message, "content"):
                    text = str(c.message.content)
                elif hasattr(c, "text"):
                    text = str(c.text)
            if text is None:
                try:
                    jd = dict(resp)
                    if "choices" in jd and jd["choices"]:
                        c = jd["choices"][0]
                        if isinstance(c, dict) and "message" in c and "content" in c["message"]:
                            text = str(c["message"]["content"])
                        elif isinstance(c, dict) and "text" in c:
                            text = str(c["text"])
                except Exception:
                    pass

            if not text:
                return None

            # Find JSON object in text
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return None
            json_text = text[start : end + 1]
            parsed = json.loads(json_text)
            if not isinstance(parsed, dict):
                return None

            # Validate with Pydantic CustomerState: only include keys that were present
            try:
                validated = CustomerState.parse_obj(parsed)
            except Exception:
                return None

            updates: Dict = {}
            for k in parsed.keys():
                if hasattr(validated, k):
                    updates[k] = getattr(validated, k)

            return updates
        except Exception:
            return None

    def extract_booking_datetime(self, system_prompt: str, user_text: str) -> Optional[datetime]:
        """Ask Groq to extract an explicit booking datetime from a single user message.

        Returns a timezone-naive `datetime` (best-effort) if the user explicitly provided
        a date/time; otherwise returns None. The LLM is instructed to return an ISO8601
        datetime string in JSON under key `booking_datetime` when present.
        """
        if not self.client:
            raise RuntimeError("Groq client not configured")

        instruction = (
            "Given the single USER message, return a JSON object with only the key 'booking_datetime' "
            "with an ISO-8601 datetime string value (e.g. '2026-09-03T15:00:00') if and only if the user "
            "explicitly provided a date and/or time for a site visit. If the user did NOT provide an explicit "
            "datetime, return an empty JSON object {}. Do NOT infer or guess datetimes. Return strictly valid JSON."
        )

        # Combine recent user messages with the current one so date and time split across
        # multiple user messages can be considered. Only user messages are used.
        try:
            combined_list = list(self._recent_user_messages) if hasattr(self, "_recent_user_messages") else []
            if not combined_list or combined_list[-1] != user_text:
                combined_list.append(user_text)
            combined_user_text = "\n".join(combined_list)
        except Exception:
            combined_user_text = user_text

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"EXTRACTION_INSTRUCTION: {instruction}"},
            {"role": "user", "content": combined_user_text},
        ]

        try:
            resp = self.client.chat.completions.create(model=self.model, messages=messages)
            text = None
            if hasattr(resp, "choices") and resp.choices:
                c = resp.choices[0]
                if hasattr(c, "message") and hasattr(c.message, "content"):
                    text = str(c.message.content)
                elif hasattr(c, "text"):
                    text = str(c.text)
            if text is None:
                try:
                    jd = dict(resp)
                    if "choices" in jd and jd["choices"]:
                        c = jd["choices"][0]
                        if isinstance(c, dict) and "message" in c and "content" in c["message"]:
                            text = str(c["message"]["content"])
                        elif isinstance(c, dict) and "text" in c:
                            text = str(c["text"])
                except Exception:
                    pass

            if not text:
                return None

            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1 or end <= start:
                return None
            json_text = text[start : end + 1]
            parsed = json.loads(json_text)
            if not isinstance(parsed, dict):
                return None

            dt_str = parsed.get("booking_datetime")
            if not dt_str:
                return None

            # Try several parse strategies; prefer ISO8601
            try:
                # fromisoformat supports 'YYYY-MM-DDTHH:MM:SS' optionally with timezone
                dt = datetime.fromisoformat(dt_str)
                # drop tzinfo to keep naive datetime
                if dt.tzinfo is not None:
                    dt = dt.replace(tzinfo=None)
                return dt
            except Exception:
                pass

            # try common formats
            fmts = [
                "%Y-%m-%d %H:%M",
                "%d-%m-%Y %H:%M",
                "%d/%m/%Y %H:%M",
                "%d %b %Y %H:%M",
                "%d %B %Y %H:%M",
                "%Y-%m-%d",
                "%d-%m-%Y",
                "%d/%m/%Y",
            ]
            for f in fmts:
                try:
                    dt = datetime.strptime(dt_str, f)
                    return dt
                except Exception:
                    continue

            return None
        except Exception:
            return None


def _load_system_prompt() -> str:
    here = os.path.dirname(__file__)
    prompt_path = os.path.normpath(os.path.join(here, "..", "prompts", "system_prompt.txt"))
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return "You are a helpful assistant for a real-estate sales chatbot. Do not invent property information. Respect do-not-contact and escalation flags."  # fallback


class Agent:
    def __init__(self) -> None:
        self.llm = SimpleGroqClient()
        self.system_prompt = _load_system_prompt()

    def _is_human_escalation_request(self, history: List[ChatMessage]) -> bool:
        last_user = None
        for message in reversed(history):
            if message.role == Role.user:
                last_user = message.content
                break
        if not last_user:
            return False

        text = last_user.lower()
        english = [
            "talk to a human",
            "talk to human",
            "talk to sales rep",
            "speak to a human",
            "speak to human",
            "speak to sales rep",
            "connect me with a human",
            "connect me with sales rep",
            "sales representative",
            "sales rep",
            "customer care",
            "customer support",
            "agent",
            "human sales",
            "human representative",
            "representative",
            "connect with team",
            "talk to team",
            "need a human",
            "need sales",
            "connect with sales",
            "someone from sales",
            "human executive",
            "sales executive",
            "talk to someone",
        ]
        hindi = [
            "human se baat karna hai",
            "sales rep se baat",
            "agent se connect",
            "sales representative se connect",
            "sales rep se milna hai",
            "human representative",
            "team se baat",
            "customer care",
            "human se connect",
            "sales executive",
            "ek agent",
            "ek sales rep",
            "agent chahiye",
            "human chahiye",
            "representative chahiye",
            "sales team",
            "team se connect",
            "rozn se contact",
        ]
        hinglish = [
            "human se connect",
            "sales rep se connect",
            "agent se connect",
            "human ko call",
            "sales rep chahiye",
            "agent chahiye",
            "team se connect karna hai",
            "rep se baat karni hai",
            "human se talk",
            "sales rep se talk",
            "agent se baat",
            "human representative chahiye",
            "sales executive chahiye",
            "human sales rep",
            "agent please",
        ]
        any_terms = english + hindi + hinglish
        return any(term in text for term in any_terms)

    def generate(self, history: List[ChatMessage], state: CustomerState) -> Tuple[str, CustomerState]:
        """Generate assistant response and optionally update state.

        Uses Groq for generation. On API errors returns a safe error message.
        """
        last_user = None
        for message in reversed(history):
            if message.role == Role.user:
                last_user = message.content
                break

        if self._is_human_escalation_request(history):
            updated_state = state.copy(update={"escalation_required": True})
            return ("Sure, our team will contact you soon. Thanks for your time and for speaking with Northstar Homes!", updated_state)

        # Respect do_not_contact: refuse to respond with contact attempts
        if state.do_not_contact:
            return ("The customer has requested not to be contacted. I will not send messages.", state)

        # Respect escalation flag
        if state.escalation_required:
            return ("Sure, our team will contact you soon. Thanks for your time and for speaking with Northstar Homes!", state)

        # Call LLM (Groq). Handle API errors cleanly.
        try:
            reply = self.llm.generate(self.system_prompt, history, state)
        except Exception as exc:
            print(f"Groq error: {exc}")
            reply = "Sorry, I'm temporarily unable to respond. Please try again later."

        # Extract customer information from the last user message only using Groq extraction.
        updated_state = state
        try:
            if last_user:
                updates = self.llm.extract_json(self.system_prompt, last_user, state)
                if updates:
                    updated_state = state.copy(update=updates)
        except Exception as exc:
            # keep existing state on extraction errors
            print(f"Groq extraction error: {exc}")

        return (reply, updated_state)
    


agent = Agent()
# agent module (placeholder)
