from datetime import datetime
from calendar_ai_agent_web_app.backend.schemas.models import EventExtraction
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.config import client, model

def extract_event_info(user_input: str) -> EventExtraction:
    logger.info("Starting event extraction analysis")

    date_context = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": f"{date_context} Analyze if the text describes a calendar event."},
            {"role": "user", "content": user_input},
        ],
        response_format=EventExtraction,
    )
    return completion.choices[0].message.parsed
