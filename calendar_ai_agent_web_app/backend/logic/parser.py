from datetime import datetime
from calendar_ai_agent_web_app.backend.schemas.models import EventDetails, EventUpdateDetails
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.config import client, model

def parse_calendar_event_details(description: str) -> EventDetails:
    logger.info("Starting calendar event parsing")

    date_context = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    f"{date_context} Extract detailed event information. Use ISO 8601 format with timezone."
                ),
            },
            {"role": "user", "content": description},
        ],
        response_format=EventDetails,
    )
    return completion.choices[0].message.parsed

def parse_calendar_modify_details(description: str) -> EventUpdateDetails:
    logger.info("Starting calendar modify parsing")

    date_context = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    f"{date_context} Your job is to extract all relevant details to update a calendar event. "
                    "Identify:\n"
                    "- The original date and time (when the meeting was originally scheduled) → `original_date`\n"
                    "- The new date and time (when the meeting should be rescheduled to) → `new_date`\n"
                    "Make sure you don't overwrite the original time. If two time ranges are mentioned, "
                    "use the earlier one as `original_date` and the later one as `new_date`. "
                    "All times should be in ISO 8601 with timezone. Include unchanged fields like name, participants, etc."
                )
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