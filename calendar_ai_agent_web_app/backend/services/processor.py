from typing import Optional
from calendar_ai_agent_web_app.backend.logic.extractor import extract_event_info
from calendar_ai_agent_web_app.backend.logic.parser import parse_event_details
from calendar_ai_agent_web_app.backend.logic.confirmation import generate_confirmation
from calendar_ai_agent_web_app.backend.logic.calendar import add_calendar_event
from calendar_ai_agent_web_app.backend.mail_utils.sender import send_email
from calendar_ai_agent_web_app.backend.schemas.models import EventConfirmation
from calendar_ai_agent_web_app.backend.utils.logger import logger


def process_calendar_request(user_input: str, participants: str) -> Optional[EventConfirmation]:
    """
    Handles full event processing pipeline:
    1. Extract event info
    2. Parse event details
    3. Add to calendar
    4. Send confirmation email
    5. Return confirmation response
    """
    logger.info("Processing calendar request")

    initial_extraction = extract_event_info(user_input)
    if not initial_extraction.is_calendar_event or initial_extraction.confidence_score < 0.7:
        logger.warning(f"Invalid calendar input. Confidence: {initial_extraction.confidence_score}")
        return None

    event_details = parse_event_details(initial_extraction.description)

    # Split participants by comma into a clean list
    participant_list = [email.strip() for email in participants if email.strip()]

    calendar_link = add_calendar_event(event_details, participant_list)
    confirmation = generate_confirmation(event_details, calendar_link)

    send_email(
        to_emails=participant_list,
        subject=event_details.name,
        message=confirmation.confirmation_message,
    )

    return confirmation
