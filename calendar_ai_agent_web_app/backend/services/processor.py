from typing import Optional
from langchain_core.messages import HumanMessage
from calendar_ai_agent_web_app.backend.logic.extractor import extract_event_info
from calendar_ai_agent_web_app.backend.logic.parser import parse_calendar_event_details, parse_calendar_modify_details
from calendar_ai_agent_web_app.backend.logic.confirmation import generate_confirmation
from calendar_ai_agent_web_app.backend.logic.calendar import add_calendar_event, update_calendar_event
from calendar_ai_agent_web_app.backend.mail_utils.sender import send_email
from calendar_ai_agent_web_app.backend.schemas.models import EventConfirmation
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.agents.conversation_agent import (
    get_or_create_session_id, graph, get_chat_history
)

def process_calendar_request(user_input: str, participants: list[str]) -> Optional[EventConfirmation]:
    logger.info("Processing calendar request")

    session_id = get_or_create_session_id("ethanchiu940520@gmail.com")

    # Step 1: Use LangGraph agent to get context-aware enriched input
    enriched_input = None
    for event in graph.stream(
        {"messages": [HumanMessage(content=user_input)]},
        config={"configurable": {"session_id": session_id}},
        stream_mode="values",
    ):
        enriched_input = event["messages"][-1].content

    if not enriched_input:
        logger.warning("No valid AI response from LangGraph.")
        return None

    chat_history = get_chat_history(session_id)
    logger.info(f"LangGraph memory for session {session_id}:")

    print("Previous messages:")
    for msg in chat_history.messages:
        print(f"[{msg.type}] {msg.content}")

    # Step 2: Extract event info
    initial_extraction = extract_event_info(enriched_input)
    if (
            not initial_extraction.is_calendar_event
            and not initial_extraction.is_calendar_modify_event
    ) or initial_extraction.confidence_score < 0.7:
        logger.warning(f"Invalid calendar input. Confidence: {initial_extraction.confidence_score}")
        return None

    if initial_extraction.is_calendar_modify_event:
        logger.info("This is a calendar modify event.")

        # Step 3a: Parse, add to calendar, confirm for calendar modify event
        event_details = parse_calendar_modify_details(initial_extraction.description)
        print(event_details)
        participant_list = [email.strip() for email in participants if email.strip()]
        calendar_link = update_calendar_event(event_details, participant_list)
        confirmation = generate_confirmation(event_details, calendar_link)

        send_email(
            to_emails=participant_list,
            subject=event_details.name,
            message=confirmation.confirmation_message,
        )

        return confirmation
    elif initial_extraction.is_calendar_event:
        logger.info("This is a calendar event.")

        # Step 3b: Parse, add to calendar, confirm for calendar event
        event_details = parse_calendar_event_details(initial_extraction.description)
        participant_list = [email.strip() for email in participants if email.strip()]
        calendar_link = add_calendar_event(event_details, participant_list)
        confirmation = generate_confirmation(event_details, calendar_link)

        send_email(
            to_emails=participant_list,
            subject=event_details.name,
            message=confirmation.confirmation_message,
        )

        return confirmation
