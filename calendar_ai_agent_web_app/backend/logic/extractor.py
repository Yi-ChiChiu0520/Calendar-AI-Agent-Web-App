# from datetime import datetime
# import json
# from calendar_ai_agent_web_app.backend.schemas.models import EventExtraction
# from calendar_ai_agent_web_app.backend.utils.logger import logger
# from calendar_ai_agent_web_app.backend.config import client_llama, model_llama, client, model
#
#
# def extract_event_info(user_input: str) -> EventExtraction:
#     logger.info("Starting event extraction analysis")
#
#     date_context = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
#
#     # Few-shot examples
#     few_shot_messages = [
#         {"role": "system", "content": f"""
# {date_context}
#
# You are an assistant that classifies calendar-related user messages.
#
# Your task is to identify the user's intent and respond with only structured JSON. Classify whether the user is:
# 1. Creating a new calendar event (e.g. "Schedule meeting with Alice").
# 2. Modifying an existing calendar event (e.g. "Move call with Bob to 4pm").
# 3. Listing calendar events, examples of listing calendar events include:
# - "What meetings do I have [today/tomorrow/next week]?"
# - "Show me all my calls with Alice."
# - "List all the events I have this afternoon."
#
# These are classified as: is_list_events=True
#
# Return a JSON object with:
# - description: Cleaned-up short summary of intent (str)
# - is_calendar_event: bool
# - is_calendar_modify_event: bool
# - is_list_events: bool
# - confidence_score: float (0.0 to 1.0)
#
# Only output JSON. Do not explain.
#         """},
#         {"role": "user", "content": "Tell me all the meetings I have today"},
#         {"role": "assistant", "content": json.dumps({
#             "description": "List meetings for today",
#             "is_calendar_event": False,
#             "is_calendar_modify_event": False,
#             "is_list_events": True,
#             "confidence_score": 0.92
#         })},
#         {"role": "user", "content": "Schedule a call with Alice tomorrow at 3pm."},
#         {"role": "assistant", "content": json.dumps({
#             "description": "Schedule call with Alice at 3pm tomorrow",
#             "is_calendar_event": True,
#             "is_calendar_modify_event": False,
#             "is_list_events": False,
#             "confidence_score": 0.95
#         })},
#         {"role": "user", "content": "Change the meeting with Alice to 4pm."},
#         {"role": "assistant", "content": json.dumps({
#             "description": "Reschedule meeting with Alice to 4pm",
#             "is_calendar_event": False,
#             "is_calendar_modify_event": True,
#             "is_list_events": False,
#             "confidence_score": 0.93
#         })},
#         {"role": "user", "content": user_input}
#     ]
#
#     try:
#         response = client_llama.chat(model=model_llama, messages=few_shot_messages)
#         content = response['message']['content'].strip()
#
#         logger.info(f"Raw response from LLaMA: {content}")
#
#         try:
#             parsed_json = json.loads(content)
#         except json.JSONDecodeError:
#             logger.error(f"Invalid JSON from LLaMA: {content}")
#             raise
#
#         parsed = EventExtraction(**parsed_json)
#         logger.info(f"Parsed event extraction: {parsed}")
#         return parsed
#
#     except Exception as e:
#         logger.exception("Failed to extract event info from LLM response")
#         return EventExtraction(
#             description=user_input,
#             is_calendar_event=False,
#             is_calendar_modify_event=False,
#             is_list_events=False,
#             confidence_score=0.0
#         )

from datetime import datetime
from calendar_ai_agent_web_app.backend.schemas.models import EventExtraction
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.config import client, model, model_fine_tuned


def extract_event_info(user_input: str) -> EventExtraction:
    logger.info("Starting event extraction analysis")

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
            model=model,
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
            model=model_fine_tuned,
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
