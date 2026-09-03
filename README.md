# Northstar Homes AI Sales Assistant

An AI-powered conversational sales assistant for Northstar Homes.

The assistant is designed to have natural conversations with prospective customers, understand their requirements, qualify leads, answer property-related questions using only verified information, and help interested customers arrange a site visit.

---

## Features

- Natural conversational sales interaction
- English, Hindi and Hinglish support
- Conversation memory
- Customer qualification
- Budget and configuration understanding
- Objection handling
- Site-visit booking simulation
- Booking success handling
- Booking failure handling
- Human escalation
- Do-not-contact handling
- Contact-later handling
- Anti-hallucination rules
- Lead analytics after conversation
- Simple web-based chat interface
- FastAPI backend

---

## Project Structure

```text
northstar-ai-agent/
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── agent.py
│   ├── models.py
│   ├── session.py
│   ├── booking.py
│   └── analytics.py
│
├── prompts/
│   └── system_prompt.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── tests/
│   ├── test_agent.py
│   ├── test_booking.py
│   └── test_cases.md
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Property Information

The assistant currently has the following verified project information:

- **Company:** Northstar Homes
- **Project:** Northstar One
- **Location:** Sector 79, Gurugram
- **2 BHK:** ₹1.35 crore onwards
- **3 BHK:** ₹1.75 crore onwards

The assistant must not invent additional property information such as discounts, amenities, availability, floor plans, possession dates, or other unsupported details.

---

# How to Run the Bot

## Prerequisites

Make sure the following are installed:

- Python 3.11 or compatible Python 3 version
- VS Code
- VS Code Live Server extension
- A Groq API key

---

## 1. Clone the Repository

```bash
git clone <your-github-repository-url>
cd northstar-ai-agent
```

If the repository is already downloaded, simply open the project folder in VS Code and open a terminal in the project root.

---

## 2. Create a Virtual Environment

For Windows:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
venv\Scripts\activate
```

After activation, the terminal should show something similar to:

```text
(venv)
```

---

## 3. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt
```

The project uses:

- FastAPI
- Uvicorn
- Pydantic
- Groq
- python-dotenv
- pytest

---

## 4. Configure Environment Variables

Create a `.env` file in the project root.

Use `.env.example` as the template.

Example:

```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=your_groq_model
```

Replace the placeholder values with your own Groq API credentials.

**Do not commit `.env` or any API key to GitHub.**

---

## 5. Start the Backend

From the project root, make sure the virtual environment is activated and run:

```bash
uvicorn backend.main:app --reload
```

The FastAPI backend will run at:

```text
http://127.0.0.1:8000
```

Keep this terminal running while using the frontend.

---

## 6. Check Backend Health

Open the following URL in a browser:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## 7. Start the Frontend

The frontend is designed to be run using the VS Code **Live Server** extension.

### Using Live Server

1. Open the project in VS Code.
2. Open `frontend/index.html`.
3. Right-click inside the file.
4. Select **Open with Live Server**.

The frontend will typically open at:

```text
http://127.0.0.1:5500/frontend/index.html
```

or:

```text
http://localhost:5500/frontend/index.html
```

Depending on the Live Server configuration, the exact URL may vary slightly.

The frontend communicates with the FastAPI backend running on:

```text
http://localhost:8000
```

### Running the Application

Both servers should be running:

```text
Frontend:
http://localhost:5500

Backend:
http://localhost:8000
```

Use the frontend URL to interact with the AI sales assistant.

---

# API Endpoints

The backend exposes the following main endpoints.

---

## Health Check

```http
GET /health
```

Checks whether the backend is running.

Example:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

## Chat

```http
POST /chat
```

Used to send customer messages to the AI assistant.

Example request:

```json
{
  "session_id": "your-session-id",
  "message": "I am looking for a 2 BHK"
}
```

The backend maintains the conversation using the session ID.

---

## Reset Conversation

```http
POST /reset
```

Resets a conversation session.

Example request:

```json
{
  "session_id": "your-session-id"
}
```

---

## Book Site Visit

```http
POST /book-visit
```

Used to simulate a site-visit booking.

Example request:

```json
{
  "session_id": "your-session-id",
  "customer_name": "Test User",
  "property_id": "northstar-one",
  "slot": "2026-10-05T11:00:00"
}
```

The booking response indicates whether the booking was successful.

The assistant only confirms a site visit after receiving a successful booking result.

---

## Analytics

```http
POST /analytics
```

Generates lead analytics for a conversation.

Example request:

```json
{
  "session_id": "your-session-id"
}
```

Analytics can include:

- Lead summary
- Configuration
- Budget
- Purpose
- Timeline
- Interest level
- Site-visit status
- Follow-up requirement
- Follow-up preference
- Escalation requirement
- Do-not-contact status

---

# Running Tests

The project uses `pytest` for automated testing.

Make sure the virtual environment is activated.

From the project root, run:

```bash
python -m pytest -v
```

Current automated tests cover:

- Do-not-contact behaviour
- Human escalation behaviour
- Successful site-visit booking

Example:

```text
tests/test_agent.py::test_agent_respects_do_not_contact PASSED
tests/test_agent.py::test_agent_respects_escalation PASSED
tests/test_booking.py::test_booking_success PASSED

3 passed
```

Additional manual test scenarios are documented in:

```text
tests/test_cases.md
```

The manual test cases cover:

- Basic property qualification
- Budget handling
- Hinglish conversation
- Hindi conversation
- Conversation memory
- Site-visit booking
- Booking failure
- Not interested customers
- Busy customers
- Do-not-contact requests
- Human escalation
- Unknown property information
- Unsupported requests
- Proper conversation ending

---

# Key Assumptions

1. Northstar One is the only property currently available to the assistant.

2. The following property information is considered verified:
   - Project: Northstar One
   - Location: Sector 79, Gurugram
   - 2 BHK starting at ₹1.35 crore onwards
   - 3 BHK starting at ₹1.75 crore onwards

3. The site-visit booking system is simulated and does not connect to a real CRM, inventory system, or property-management system.

4. Customer information is maintained within the current conversation session.

5. The assistant only confirms a site visit after the booking mechanism returns a successful result.

6. The assistant must not invent unavailable property information.

7. Human escalation is represented through application state and the assistant response rather than an actual external phone call or CRM action.

8. Contact-later requests are stored as customer state and are not treated as actual scheduled calls unless an external system confirms the action.

9. The frontend is intended to be run locally using VS Code Live Server.

---

# Known Limitations

- Property information is intentionally limited because there is no real Northstar Homes property database connected.
- Site-visit booking is simulated.
- There is no real CRM integration.
- There is no real property inventory integration.
- There is no real phone-call or voice integration.
- Human escalation does not actually contact a sales representative.
- Follow-up requests are not connected to a real reminder or calling system.
- The assistant cannot reliably answer property questions for which verified information is unavailable.
- Analytics are generated from information captured during the conversation.
- Some analytics fields may remain empty if the customer does not provide the corresponding information.
- The application requires a valid Groq API key to generate AI responses.

---

# Prompt Engineering

The main system prompt is stored separately in:

```text
prompts/system_prompt.txt
```

The system prompt defines:

- Assistant role
- Verified property information
- Conversation objectives
- Customer qualification
- Conversation memory
- English, Hindi and Hinglish behaviour
- Anti-hallucination rules
- Pricing rules
- Objection handling
- Busy customer handling
- Do-not-contact behaviour
- Contact-later behaviour
- Site-visit booking
- Booking failure handling
- Human escalation
- Conversation ending
- Response style

Keeping the system prompt in a separate file makes it easier to improve the agent's behaviour without changing the backend implementation.

---

# Architecture

```text
                    ┌─────────────────────┐
                    │    Web Frontend     │
                    │    HTML/CSS/JS      │
                    │    Live Server      │
                    │      :5500          │
                    └──────────┬──────────┘
                               │
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    │      main.py        │
                    │      :8000          │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Agent         │
                    │      agent.py       │
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
          ┌──────────────────┐   ┌──────────────────┐
          │ System Prompt    │   │ Conversation      │
          │ system_prompt    │   │ Memory / State   │
          │ .txt             │   │                  │
          └──────────────────┘   └──────────────────┘
                    │
                    ▼
              ┌───────────┐
              │ Groq LLM  │
              └───────────┘


Additional Backend Components:

booking.py    → Site-visit booking simulation
analytics.py  → Lead analytics
session.py    → Conversation/session state
models.py     → Pydantic request/response models
```

---

# AI Tools Used

## ChatGPT

Used during development for:

- Understanding assignment requirements
- Designing the conversational agent architecture
- Prompt engineering
- Debugging
- Improving multilingual and Hinglish behaviour
- Designing test cases
- Reviewing edge cases
- Documentation

## Groq API

Used as the LLM provider for the conversational AI agent.

The application sends the system prompt, conversation history and relevant customer state to the configured Groq model.

---

# Security

API credentials are stored using environment variables.

The `.env` file should never be committed to Git.

The repository contains `.env.example` with placeholder values only.

---

# Example Conversation

```text
Customer:
I want a 3 BHK.

Assistant:
Sure. 3 BHK starts at ₹1.75 crore onwards.
What budget range are you considering?

Customer:
Around 2 crore.

Assistant:
Got it. Are you looking for the property for self-use
or as an investment?

Customer:
For self-use.

Assistant:
Understood. Would you like to arrange a site visit?
```

The assistant uses information already provided by the customer instead of repeatedly asking the same questions.

---

# Project Goal

The goal of the assistant is not to aggressively push a sale.

It is designed to:

1. Understand the customer's requirements.
2. Provide accurate and verified information.
3. Qualify genuine interest.
4. Handle objections naturally.
5. Help arrange a site visit.
6. Respect customer preferences.
7. Escalate when human assistance is required.
8. Maintain conversation context.
9. Avoid making unsupported claims.