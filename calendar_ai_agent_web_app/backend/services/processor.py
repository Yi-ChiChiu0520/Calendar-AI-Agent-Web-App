from typing import Optional, Union
from langchain_core.messages import HumanMessage
from calendar_ai_agent_web_app.backend.logic.extractor import extract_event_info, extract_list_event_info
from calendar_ai_agent_web_app.backend.logic.parser import parse_calendar_event_details, parse_calendar_modify_details, parse_list_calendar_events
from calendar_ai_agent_web_app.backend.logic.confirmation import generate_confirmation, generate_modify_confirmation, generate_matched_calendar_events_message
from calendar_ai_agent_web_app.backend.logic.calendar import add_calendar_event, update_calendar_event, get_calendar_events
from calendar_ai_agent_web_app.backend.schemas.models import  EventConfirmationDraft, EventListConfirmation
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.agents.conversation_agent import (
    get_or_create_session_id, graph, get_chat_history
)

def process_calendar_request(user_input: str, participants: list[str]) ->  Optional[Union[EventConfirmationDraft, EventListConfirmation]]:
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

    # Step 2: Extract event info
    initial_extraction = extract_event_info(enriched_input)
    if (
            not initial_extraction.is_calendar_event
            and not initial_extraction.is_calendar_modify_event
            and not initial_extraction.is_list_events
    ) or initial_extraction.confidence_score < 0.7:

        # Fallback to list event-specific extraction
        initial_extraction = extract_list_event_info(enriched_input)

        if(not initial_extraction.is_calendar_event
            and not initial_extraction.is_calendar_modify_event
            and not initial_extraction.is_list_events
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
        confirmation = generate_modify_confirmation(event_details, calendar_link)

        return EventConfirmationDraft(
            confirmation_message=confirmation.confirmation_message,
            calendar_link=confirmation.calendar_link,
            to_emails=participant_list,
            subject=event_details.name,
            requires_confirmation=True
        )
    elif initial_extraction.is_calendar_event:
        logger.info("This is a calendar event.")

        # Step 3b: Parse, add to calendar, confirm for calendar event
        event_details = parse_calendar_event_details(initial_extraction.description)
        participant_list = [email.strip() for email in participants if email.strip()]
        calendar_link = add_calendar_event(event_details, participant_list)
        confirmation = generate_confirmation(event_details, calendar_link)

        return EventConfirmationDraft(
            confirmation_message=confirmation.confirmation_message,
            calendar_link=confirmation.calendar_link,
            to_emails=participant_list,
            subject=event_details.name,
            requires_confirmation=True
        )
    else:
        list_calender_events_filters = parse_list_calendar_events(initial_extraction.description)
        matched_events = get_calendar_events(list_calender_events_filters)
        matched_events_confirmation_message = generate_matched_calendar_events_message(matched_events)

        return EventListConfirmation(
            message=matched_events_confirmation_message.message
        )

