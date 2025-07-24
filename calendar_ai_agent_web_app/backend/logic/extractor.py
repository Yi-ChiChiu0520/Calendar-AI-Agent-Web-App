from datetime import datetime
import json
from openai import OpenAI
from calendar_ai_agent_web_app.backend.schemas.models import EventExtraction
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.config import client, model


def extract_event_info(user_input: str) -> EventExtraction:
    logger.info("Starting event extraction analysis")

    date_context = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    # Prompt with clear roles and example calibration
    messages = [
        {
            "role": "system",
            "content": f"""
                {date_context}
                
                You are an assistant that classifies calendar-related user messages.
                
                You must determine:
                - If the message is about creating a calendar event.
                - If it is about modifying an existing event (rescheduling, renaming, etc.).
                - Provide a cleaned-up summary description.
                - Output only structured JSON with fields:
                  - description: str
                  - is_calendar_event: bool
                  - is_calendar_modify_event: bool
                  - confidence_score: float (0.0 to 1.0)
                
                Be accurate and consistent. Only return the JSON object, no explanation.
                            """
        },
        {"role": "user", "content": "Schedule a call with Alice tomorrow at 3pm."},
        {"role": "assistant", "content": json.dumps({
            "description": "Call with Alice tomorrow at 3pm",
            "is_calendar_event": True,
            "is_calendar_modify_event": False,
            "confidence_score": 0.95
        })},
        {"role": "user", "content": "Change the meeting with Alice to 4pm."},
        {"role": "assistant", "content": json.dumps({
            "description": "Reschedule meeting with Alice to 4pm",
            "is_calendar_event": False,
            "is_calendar_modify_event": True,
            "confidence_score": 0.93
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

        # Heuristic fallback to catch missed modify intent
        if (
            not result.is_calendar_modify_event
            and not result.is_calendar_event
            and "change" in user_input.lower()
            and "to" in user_input.lower()
        ):
            result.is_calendar_modify_event = True
            result.confidence_score = max(result.confidence_score, 0.75)
            logger.warning("LLM failed to mark as modify; heuristic applied.")

        return result

    except Exception as e:
        logger.exception("Failed to extract event info from LLM response")
        return EventExtraction(
            description=user_input,
            is_calendar_event=False,
            is_calendar_modify_event=False,
            confidence_score=0.0
        )
