from datetime import datetime, timedelta
import os
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.schemas.models import EventDetails, EventUpdateDetails, ListCalendarEventsFilters, ListedEvents, CalendarEvent
from calendar_ai_agent_web_app.backend.constants import SCOPES
import os.path
from zoneinfo import ZoneInfo  # built-in in Python 3.9+
from typing import Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from calendar_ai_agent_web_app.backend.config import client, model

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

        start_dt = datetime.fromisoformat(start_time).replace(tzinfo=ZoneInfo("America/Los_Angeles"))  # or your actual timezone
        end_dt = start_dt + timedelta(minutes=duration)

        event = {
            "summary": event_details.name,
            "location": event_details.location,
            "description": event_details.description,
            "colorId": 5,
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": "America/Los_Angeles"

            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": "America/Los_Angeles"

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

def update_calendar_event(event_details: EventUpdateDetails, emails: list[str]) -> str:
    logger.info("Updating event in Google Calendar")

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

        if not event_details.original_date:
            logger.error("Missing original_date — cannot find existing event to update.")
            return ""

        original_start_dt = datetime.fromisoformat(event_details.original_date)
        original_end_dt = original_start_dt + timedelta(minutes=event_details.duration_minutes)

        new_start_dt = datetime.fromisoformat(event_details.new_date)
        new_end_dt = new_start_dt + timedelta(minutes=event_details.duration_minutes)

        time_min = original_start_dt - timedelta(minutes=10)
        time_max = original_end_dt + timedelta(minutes=10)

        logger.info(f"Searching for events between {time_min} and {time_max}")

        events_result = service.events().list(
            calendarId="primary",
            timeMin=time_min.astimezone().isoformat(),
            timeMax=time_max.astimezone().isoformat(),
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        if not events:
            logger.warning("No matching event found to update.")
            return ""

        event = events[0]
        event_id = event["id"]

        # Update event details
        event["summary"] = event_details.name
        event["location"] = event_details.location
        event["description"] = event_details.description
        event["start"] = {
            "dateTime": new_start_dt.isoformat(),
            "timeZone": "America/Los_Angeles"
        }
        event["end"] = {
            "dateTime": new_end_dt.isoformat(),
            "timeZone": "America/Los_Angeles"
        }
        event["attendees"] = [{"email": email} for email in emails]
        event["reminders"] = {"useDefault": True}

        updated_event = service.events().update(
            calendarId="primary", eventId=event_id, body=event
        ).execute()

        logger.info(f"Event updated: {updated_event.get('htmlLink')}")
        return updated_event.get("htmlLink")

    except HttpError as error:
        logger.error(f"An error occurred during event update: {error}")
        return ""

def get_calendar_events(filters: ListCalendarEventsFilters) -> ListedEvents:
    logger.info("Fetching events from Google Calendar")

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

        # Default time window: today to 1 week later if not specified
        start_time = filters.start_time or datetime.now().astimezone()
        end_time = filters.end_time or (start_time + timedelta(days=7))

        logger.info(f"Querying events from {start_time} to {end_time}")

        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_time.isoformat(),
            timeMax=end_time.isoformat(),
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        logger.info(f"Found {len(events)} events")
        print(events)

        matched = filter_events_with_llm(events, filters)

        print(matched)

        return matched

    except HttpError as error:
        logger.error(f"Error fetching events: {error}")
        return ListedEvents(query_summary=filters.description, matched_events=[])

def filter_events_with_llm(events: list[dict], filters: ListCalendarEventsFilters) -> Optional[ListedEvents]:
    logger.info("Filtering events using LLM")

    try:
        system_prompt = (
            "You are a helpful assistant that filters calendar events based on a user's intent. "
            "Return only the list of events that match the user's filter as a JSON list. "
            "Use exact structure of the input events. No explanations."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"User's filter: {filters.model_dump()}"},
            {"role": "user", "content": f"Events to filter: {events}"},
        ]

        response = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            response_format=ListedEvents,
        )

        parsed_events = response.choices[0].message.parsed
        return parsed_events

    except Exception as e:
        logger.exception("LLM filtering failed")
        return []