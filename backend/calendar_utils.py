from dotenv import load_dotenv
import os
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import json

CALENDAR_ID = os.getenv("CALENDAR_ID")

SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")
credentials = service_account.Credentials.from_service_account_info(
    json.loads(SERVICE_ACCOUNT_JSON),
    scopes=["https://www.googleapis.com/auth/calendar"]
)
service = build("calendar", "v3", credentials=credentials)

def get_availability(start: datetime, end: datetime):
    body = {
        "timeMin": start.isoformat(),
        "timeMax": end.isoformat(),
        "items": [{"id": CALENDAR_ID}]
    }
    res = service.freebusy().query(body=body).execute()
    busy = res["calendars"][CALENDAR_ID]["busy"]
    return [] if not busy else busy

def create_event(start: datetime, end: datetime, summary: str, description: str):
    print(f"🗓️ Creating event: {summary} from {start} to {end}")

    assert start.tzinfo is not None, "Start datetime must be timezone-aware"
    assert end.tzinfo is not None, "End datetime must be timezone-aware"

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": start.tzinfo.zone if start.tzinfo else "UTC"
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": end.tzinfo.zone if end.tzinfo else "UTC"
        },
    }

    evt = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    print(f"✅ Event created: {evt.get('htmlLink')}")
    return evt.get("htmlLink")

