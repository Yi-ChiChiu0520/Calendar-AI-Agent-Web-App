from datetime import datetime
from calendar_ai_agent_web_app.backend.schemas.models import EventDetails, EventUpdateDetails, ListCalendarEventsFilters
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.config import client, model
from zoneinfo import ZoneInfo

def parse_calendar_event_details(description: str) -> EventDetails:
    logger.info("Starting calendar event parsing")

    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    date_context = f"Today is {now.strftime('%A, %B %d, %Y')}."

    system_prompt = (
        f"{date_context} Your task is to extract detailed information about a new calendar event.\n\n"
        "- Interpret relative time references (e.g., 'next Monday', 'this Friday') accurately.\n"
        "- Assume:\n"
        "  • 'this week' means from today up to this Saturday.\n"
        "  • 'next' refers to the week **starting from this upcoming Sunday**.\n"
        "- ⏰ All time references (e.g., '3pm–4pm') are in the **America/Los_Angeles** time zone unless otherwise stated.\n"
        "- All times must be returned in ISO 8601 format **with timezone** (America/Los_Angeles).\n"
        "- Include fields: name, description, location (if available), date/time, duration in minutes, participants.\n"
        "- Return output as a strict JSON object matching the EventDetails schema."
    )

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": description}
        ],
        response_format=EventDetails
    )

    return completion.choices[0].message.parsed

def parse_calendar_modify_details(description: str) -> EventUpdateDetails:
    logger.info("Starting calendar modify parsing")

    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    date_context = (
        f"Today is {now.strftime('%A, %B %d, %Y')}.\n"
        "The calendar week runs from Sunday to Saturday.\n"
        "- 'This [weekday]' refers to the upcoming [weekday] within this week (before the coming Saturday).\n"
        "- 'Next [weekday]' refers to the [weekday] in the following week, starting the next Sunday.\n"
        "- ⏰ All time references like '8am–9am' are in **America/Los_Angeles** timezone by default.\n"
        "- Always use ISO 8601 format with timezone for all datetime fields.\n"
    )

    system_prompt = (
        f"{date_context}\n"
        "Your job is to extract all relevant details to update a calendar event.\n"
        "Identify:\n"
        "- The original date and time (when the meeting was originally scheduled) → `original_date`\n"
        "- The new date and time (when the meeting should be rescheduled to) → `new_date`\n"
        "If two time ranges are mentioned, treat the earlier one as `original_date` and the later one as `new_date`.\n"
        "Also include unchanged fields like `name`, `description`, `location`, `participants`, and `duration_minutes` if possible."
    )

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": "Reschedule the meeting with Ethan to discuss the project roadmap from next Wednesday 8–9am to next Friday 7–8am."
            },
            {
                "role": "assistant",
                "content": (
                    '{"name": "Project Roadmap Discussion with Ethan", '
                    '"description": "Discuss the project roadmap with Ethan.", '
                    '"location": "Company Meeting Room A", '
                    '"original_date": "2025-07-30T08:00:00-04:00", '
                    '"new_date": "2025-08-01T07:00:00-04:00", '
                    '"duration_minutes": 60, '
                    '"participants": ["ethan@example.com"]}'
                )
            },
            {
                "role": "user",
                "content": description
            },
        ],
        response_format=EventUpdateDetails
    )

    return completion.choices[0].message.parsed

def parse_list_calendar_events(description: str) -> ListCalendarEventsFilters:
    logger.info("Starting list calendar events parsing")

    now = datetime.now(ZoneInfo("America/Los_Angeles"))
    date_context = f"Today is {now.strftime('%A, %B, %d, %Y')}"

    completion = client.beta.chat.completions.parse(
        model = model,
        messages = [
            {
                "role": "system",
                "content": (
                    f"{date_context}\n"
                    "You are a calendar assistant that extracts filters for listing existing events — NOT creating or editing them.\n\n"
                    "Your goal is to extract:\n"
                    "- A cleaned-up description summarizing the user's request.\n"
                    "- Optional structured fields:\n"
                    "   - 'start_time' and 'end_time': ISO 8601 datetimes in America/Los_Angeles time.\n"
                    "   - 'participants': names or emails mentioned.\n"
                    "   - 'time_of_day': 'morning', 'afternoon', or 'evening'.\n"
                    "   - 'keywords': event-related words (e.g., 'meeting', 'call', etc.)\n\n"
                    "Use today's actual date from context. Only return structured JSON. Do not explain."
                )
            },
            {
                "role":"user",
                "content": "Show me all meetings with Ethan next week in the morning"
            },
            {
                "role": "assistant",
                "content": (
                    '{'
                    '"description": "List all meetings with Ethan next week in the morning", '
                    '"start_time": "2025-07-29T00:00:00-07:00", '
                    '"end_time": "2025-08-02T23:59:59-07:00", '
                    '"participants": ["Ethan"], '
                    '"time_of_day": "morning", '
                    '"keywords": ["meeting"]'
                    '}'
                )
            },
            {
                "role": "user",
                "content": "Show me all meetings with chiuetha@usc.edu today"
            },
            {
                "role": "assistant",
                "content": (
                    '{'
                    '"description": "List all meetings with Ethan today", '
                    '"start_time": "2025-07-25T00:00:00-07:00", '
                    '"end_time": "2025-07-25T23:59:59-07:00", '
                    '"participants": ["chiuetha@usc.edu"], '
                    '"keywords": ["meeting"]'
                    '}'
                )
            },
            {
                "role": "user",
                "content": "Tell me all meetings I had yesterday"
            },
            {
                "role": "assistant",
                "content": (
                    '{'
                    '"description": "List all meetings from yesterday", '
                    '"start_time": "2025-07-24T00:00:00-07:00", '
                    '"end_time": "2025-07-24T23:59:59-07:00", '
                    '"participants": ["Ethan"], '
                    '"time_of_day": "morning", '
                    '"keywords": ["meeting"]'
                    '}'
                )
            },
            {
                "role": "user",
                "content": description
            }
        ],
        response_format=ListCalendarEventsFilters
    )
    print(completion.choices[0].message.parsed)

    return completion.choices[0].message.parsed
