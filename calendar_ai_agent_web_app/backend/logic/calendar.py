from datetime import datetime, timedelta
import os
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.schemas.models import EventDetails
from calendar_ai_agent_web_app.backend.constants import SCOPES
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def add_calendar_event(event_details: EventDetails, emails: list[str]) -> str:
    logger.info("Adding event to Google Calendar")

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials.json")

            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        start_time = event_details.date
        duration = event_details.duration_minutes

        start_dt = datetime.fromisoformat(start_time)
        end_dt = start_dt + timedelta(minutes=duration)

        event = {
            "summary": event_details.name,
            "location": event_details.location,
            "description": event_details.description,
            "colorId": 5,
            "start": {
                "dateTime": start_dt.isoformat(),
            },
            "end": {
                "dateTime": end_dt.isoformat(),
            },
            "attendees": [{"email": email} for email in emails],
            "reminders": {
              "useDefault": True,
            },
        }

        event = service.events().insert(calendarId="primary", body=event).execute()

        print("Start datetime:", start_dt.isoformat())
        print("End datetime:", end_dt.isoformat())

        print(f"Event created {event.get('htmlLink')}")
        return event.get('htmlLink')

    except HttpError as error:
        print("An error occurred:", error)
