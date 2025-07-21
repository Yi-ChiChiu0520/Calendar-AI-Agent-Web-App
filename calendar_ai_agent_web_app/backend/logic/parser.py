from datetime import datetime
from calendar_ai_agent_web_app.backend.schemas.models import EventDetails
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.config import client, model

def parse_event_details(description: str) -> EventDetails:
    logger.info("Starting event parsing")

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
