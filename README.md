# Chat-n-Schedule 📅

An AI-powered chat assistant that books meetings on Google Calendar through natural conversation. Tell it when you're free (or ask it to check), and it'll find availability and create the event for you — no forms, just chat.

## How it works

- **Frontend** — a [Streamlit](https://streamlit.io/) chat UI that sends your messages to the backend and displays the assistant's replies.
- **Backend** — a [FastAPI](https://fastapi.tiangolo.com/) server that runs a [LangGraph](https://www.langchain.com/langgraph) agent powered by Google's Gemini model.
- **Agent** — the agent has two tools at its disposal:
  - `check_availability` — checks the Google Calendar for busy/free time in a given window.
  - `book_event` — creates a new event on the calendar.
- **Calendar integration** — a Google service account authenticates with the Calendar API to read free/busy data and create events.
- **Date parsing** — natural-language date/time expressions (e.g. "tomorrow at 3pm") are parsed with `dateparser`, timezone-aware, using the user's browser timezone (detected automatically on the frontend).
- The backend also tracks conversational "slots" (like the timezone or details mentioned earlier) across turns, so the agent remembers context as the conversation continues.

## Project structure

```
chat-n-schedule/
├── backend/
│   ├── main.py            # FastAPI app, exposes POST /chat
│   ├── agent.py           # LangGraph agent, tools, and conversation logic
│   ├── calendar_utils.py  # Google Calendar API integration (free/busy, create event)
│   └── date_utils.py      # Natural-language date/time parsing
├── frontend/
│   └── app.py             # Streamlit chat interface
├── requirements.txt
└── .gitignore
```

## Prerequisites

- Python 3.10+
- A [Google Cloud service account](https://cloud.google.com/iam/docs/service-account-overview) with the Calendar API enabled, and access granted to the calendar you want to manage
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/)

## Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/bhawna1224/chat-n-schedule.git
   cd chat-n-schedule
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create a `.env` file inside `backend/` with:

   ```env
   GEMINI_API_KEY=your_gemini_api_key
   CALENDAR_ID=your_google_calendar_id
   SERVICE_ACCOUNT_JSON={"type": "service_account", ...}
   ```

   - `GEMINI_API_KEY` — your Gemini API key.
   - `CALENDAR_ID` — the ID of the Google Calendar to check/book against (usually your Gmail address, or a shared calendar's ID).
   - `SERVICE_ACCOUNT_JSON` — the full contents of your Google service account JSON key, as a single-line string.

   Make sure the service account has been shared with the target calendar (with "Make changes to events" permission).

4. **Run the backend**

   ```bash
   cd backend
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

5. **Run the frontend**

   In a separate terminal:

   ```bash
   cd frontend
   streamlit run app.py
   ```

   > Note: the frontend currently points at a deployed backend URL (`https://chat-n-schedule.onrender.com/chat`). If you're running the backend locally, update the URL in `frontend/app.py` to `http://localhost:8000/chat`.

## Usage

Once both servers are running, open the Streamlit app in your browser and start chatting, for example:

- "Am I free tomorrow between 2pm and 4pm?"
- "Book a call with Alex on Friday at 10am for 30 minutes"

The assistant will check your calendar, ask for any missing details, and confirm once the event is booked — with a link to the created event.



