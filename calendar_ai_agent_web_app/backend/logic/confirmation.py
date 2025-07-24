from calendar_ai_agent_web_app.backend.schemas.models import EventConfirmation, EventDetails, EventUpdateDetails
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.config import client, model

def generate_confirmation(event_details: EventDetails, calendar_link: str) -> EventConfirmation:
    logger.info("Generating confirmation message")

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": f"Generate a confirmation email. Sign off as Susie. Include this calendar link: {calendar_link}"},
            {"role": "user", "content": str(event_details.model_dump())},
        ],
        response_format=EventConfirmation,
    )
    return completion.choices[0].message.parsed


def generate_modify_confirmation(event_details: EventUpdateDetails, calendar_link: str) -> EventConfirmation:
    logger.info("Generating modify confirmation message")

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": f"Generate a calendar event modified confirmation email. Sign off as Susie. Include this calendar link: {calendar_link}"},
            {"role": "user", "content": str(event_details.model_dump())},
        ],
        response_format=EventConfirmation,
    )
    return completion.choices[0].message.parsed
