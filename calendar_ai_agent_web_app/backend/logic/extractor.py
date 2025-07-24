from datetime import datetime
import json
from calendar_ai_agent_web_app.backend.schemas.models import EventExtraction
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.config import client, model


def extract_event_info(user_input: str) -> EventExtraction:
    logger.info("Starting event extraction analysis")

    date_context = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    # Prompt with updated roles and JSON spec
    messages = [
        {
            "role": "system",
            "content": f"""
                {date_context}

                You are an assistant that classifies calendar-related user messages.

                Your job is to identify:
                - Whether the user is creating a new event.
                - Whether they are modifying an existing one (reschedule, rename, cancel).
                - Whether they are asking to list or query calendar events.
                - Generate a short cleaned-up description summarizing the user intent.

                Only return structured JSON with these fields:
                - description: str
                - is_calendar_event: bool (e.g. scheduling "a call with Alice")
                - is_calendar_modify_event: bool (e.g. rescheduling or changing an existing event)
                - is_list_events: bool (e.g. "what meetings do I have this week", or "list all meetings with Ethan")
                - confidence_score: float (between 0.0 and 1.0)

                Be accurate and consistent. Output only a valid JSON object, nothing else.
            """
        },
        {"role": "user", "content": "Schedule a call with Alice tomorrow at 3pm."},
        {"role": "assistant", "content": json.dumps({
            "description": "Schedule call with Alice at 3pm tomorrow",
            "is_calendar_event": True,
            "is_calendar_modify_event": False,
            "is_list_events": False,
            "confidence_score": 0.95
        })},
        {"role": "user", "content": "Change the meeting with Alice to 4pm."},
        {"role": "assistant", "content": json.dumps({
            "description": "Reschedule meeting with Alice to 4pm",
            "is_calendar_event": False,
            "is_calendar_modify_event": True,
            "is_list_events": False,
            "confidence_score": 0.93
        })},
        {"role": "user", "content": "What meetings do I have next week?"},
        {"role": "assistant", "content": json.dumps({
            "description": "List meetings for next week",
            "is_calendar_event": False,
            "is_calendar_modify_event": False,
            "is_list_events": True,
            "confidence_score": 0.92
        })},
        {"role": "user", "content": user_input}
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
        )

        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)
        logger.info(f"Parsed event extraction: {parsed}")

        result = EventExtraction(**parsed)

        # Heuristic fallback for missed modifications
        if (
                not result.is_calendar_modify_event
                and not result.is_calendar_event
                and not result.is_list_events
                and "change" in user_input.lower()
                and "to" in user_input.lower()
        ):
            result.is_calendar_modify_event = True
            result.confidence_score = max(result.confidence_score, 0.75)
            logger.warning("LLM missed modify intent; heuristic applied.")

        return result

    except Exception as e:
        logger.exception("Failed to extract event info from LLM response")
        return EventExtraction(
            description=user_input,
            is_calendar_event=False,
            is_calendar_modify_event=False,
            is_list_events=False,
            confidence_score=0.0
        )
