from datetime import datetime
from calendar_ai_agent_web_app.backend.schemas.models import EventExtraction
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.config import client, model, model_list_event, model_calendar


def extract_event_info(user_input: str) -> EventExtraction:
    logger.info("Starting event extraction analysis")

    date_context = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    messages = [
        {
            "role": "system",
            "content": f"""
{date_context}

You are an assistant that classifies calendar-related user messages.

Your task is to classify whether the user is directly trying to schedule, modify, or list a calendar event. Do not rephrase as "guide user to..." — treat all user inputs as direct commands or requests. Respond only with structured JSON.
1. Creating a new calendar event (e.g. "Schedule meeting with Alice").
2. Modifying an existing calendar event (e.g. "Move call with Bob to 4pm").
3. Listing calendar events (e.g. "What meetings do I have tomorrow?", "Show my calls with Ethan", "Tell me all meetings I have tomorrow.").

Return a JSON object with:
- description: Cleaned-up short summary of intent (str)
- is_calendar_event: bool
- is_calendar_modify_event: bool
- is_list_events: bool
- confidence_score: float (0.0 to 1.0)

Only output JSON. Do not explain.
            """
        },
        {"role": "user", "content": "Tell me all the meetings I have next Tuesday morning with Ethan"},
        {"role": "assistant", "content": EventExtraction(
            description="List meetings for next Tuesday morning with Ethan",
            is_calendar_event=False,
            is_calendar_modify_event=False,
            is_list_events=True,
            confidence_score=0.92
        ).model_dump_json()},
        {"role": "user", "content": "Schedule a call with Alice tomorrow at 3pm."},
        {"role": "assistant", "content": EventExtraction(
            description="Schedule call with Alice at 3pm tomorrow",
            is_calendar_event=True,
            is_calendar_modify_event=False,
            is_list_events=False,
            confidence_score=0.95
        ).model_dump_json()},
        {"role": "user", "content": "Change the meeting with Alice to 4pm."},
        {"role": "assistant", "content": EventExtraction(
            description="Reschedule meeting with Alice to 4pm",
            is_calendar_event=False,
            is_calendar_modify_event=True,
            is_list_events=False,
            confidence_score=0.93
        ).model_dump_json()},
        {"role": "user", "content": "What meetings do I have next week?"},
        {"role": "assistant", "content": EventExtraction(
            description="List meetings for next week",
            is_calendar_event=False,
            is_calendar_modify_event=False,
            is_list_events=True,
            confidence_score=0.92
        ).model_dump_json()},
        {"role": "user", "content": "Tell me all the meetings I have today"},
        {"role": "assistant", "content": EventExtraction(
            description="List meetings for today",
            is_calendar_event=False,
            is_calendar_modify_event=False,
            is_list_events=True,
            confidence_score=0.92
        ).model_dump_json()},
        {"role": "user", "content": user_input}
    ]

    try:
        response = client.beta.chat.completions.parse(
            model=model_calendar,
            messages=messages,
            response_format=EventExtraction
        )

        logger.info(f"Using model: {model_calendar}")

        parsed = response.choices[0].message.parsed
        logger.info(f"Parsed event extraction: {parsed}")

        return parsed

    except Exception as e:
        logger.exception("Failed to extract event info from LLM response")
        return EventExtraction(
            description=user_input,
            is_calendar_event=False,
            is_calendar_modify_event=False,
            is_list_events=False,
            confidence_score=0.0
        )


def extract_list_event_info(user_input: str) -> EventExtraction:
    logger.info("Trying list event extraction with fine tuned model")

    date_context = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    messages = [
        {
            "role": "system",
            "content": f"""
{date_context}

You are an assistant that classifies calendar-related user messages.

Your task is to identify the user's intent and respond with only structured JSON. Classify whether the user is:
1. Creating a new calendar event (e.g. "Schedule meeting with Alice").
2. Modifying an existing calendar event (e.g. "Move call with Bob to 4pm").
3. Listing calendar events (e.g. "What meetings do I have tomorrow?", "Show my calls with Ethan", "Tell me all meetings I have tomorrow.").

Return a JSON object with:
- description: Cleaned-up short summary of intent (str)
- is_calendar_event: bool
- is_calendar_modify_event: bool
- is_list_events: bool
- confidence_score: float (0.0 to 1.0)

Only output JSON. Do not explain.
            """
        },
        {"role": "user", "content": "Tell me all the meetings I have next Tuesday morning with Ethan"},
        {"role": "assistant", "content": EventExtraction(
            description="List meetings for next Tuesday morning with Ethan",
            is_calendar_event=False,
            is_calendar_modify_event=False,
            is_list_events=True,
            confidence_score=0.92
        ).model_dump_json()},
        {"role": "user", "content": "Schedule a call with Alice tomorrow at 3pm."},
        {"role": "assistant", "content": EventExtraction(
            description="Schedule call with Alice at 3pm tomorrow",
            is_calendar_event=True,
            is_calendar_modify_event=False,
            is_list_events=False,
            confidence_score=0.95
        ).model_dump_json()},
        {"role": "user", "content": "Change the meeting with Alice to 4pm."},
        {"role": "assistant", "content": EventExtraction(
            description="Reschedule meeting with Alice to 4pm",
            is_calendar_event=False,
            is_calendar_modify_event=True,
            is_list_events=False,
            confidence_score=0.93
        ).model_dump_json()},
        {"role": "user", "content": "What meetings do I have next week?"},
        {"role": "assistant", "content": EventExtraction(
            description="List meetings for next week",
            is_calendar_event=False,
            is_calendar_modify_event=False,
            is_list_events=True,
            confidence_score=0.92
        ).model_dump_json()},
        {"role": "user", "content": "Tell me all the meetings I have today"},
        {"role": "assistant", "content": EventExtraction(
            description="List meetings for today",
            is_calendar_event=False,
            is_calendar_modify_event=False,
            is_list_events=True,
            confidence_score=0.92
        ).model_dump_json()},
        {"role": "user", "content": user_input}
    ]

    try:
        response = client.beta.chat.completions.parse(
            model=model_list_event,
            messages=messages,
            response_format=EventExtraction
        )

        parsed = response.choices[0].message.parsed
        logger.info(f"Parsed event extraction: {parsed}")

        return parsed

    except Exception as e:
        logger.exception("Failed to extract event info from LLM response")
        return EventExtraction(
            description=user_input,
            is_calendar_event=False,
            is_calendar_modify_event=False,
            is_list_events=False,
            confidence_score=0.0
        )
