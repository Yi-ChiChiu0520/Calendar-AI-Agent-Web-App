from crewai import Agent
from datetime import datetime

from calendar_ai_agent_web_app.backend.schemas.models import EventDetails
from calendar_ai_agent_web_app.backend.utils.logger import logger
from calendar_ai_agent_web_app.backend.config import client, model

# Define the CrewAI Agent
event_parser = Agent(
    role="EventParserAgent",
    goal="Decide whether a message is a calendar event and extract all related details.",
    backstory="An AI expert trained to identify user intent and extract structured event information like name, time, location, and participants from raw text.",
    reasoning=True,  # Enable reasoning and planning
    max_reasoning_attempts=3,  # Limit reasoning attempts
    max_iter=30,  # Allow more iterations for complex planning
    allow_delegation=False,
    verbose=True,
)

# Define the agent's core function
def parse_event_details(description: str) -> EventDetails:
    logger.info("Starting event parsing")

    date_context = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content":(
                    f"{date_context} Extract detailed event information such as:\n"
                    "- name\n"
                    "- description\n"
                    "- date (full ISO 8601 with timezone)\n"
                    "- duration_minutes (integer)\n"
                    "- location\n"
                    "- participants (list of names)\n\n"
                    "Respond strictly in JSON format matching the following structure:\n"
                    "{"
                    "  \"name\": str,\n"
                    "  \"description\": str,\n"
                    "  \"date\": str,\n"
                    "  \"duration_minutes\": int,\n"
                    "  \"location\": str,\n"
                    "  \"participants\": [str, ...]\n"
                    "}"
                ),
            },
            {"role": "user", "content": description},
        ],
        response_format=EventDetails,
    )

    parsed_result = completion.choices[0].message.parsed

    logger.info(f"Parsed event: Name={parsed_result.name}, Date={parsed_result.date}, Duration={parsed_result.duration_minutes} mins")
    logger.info(f"Participants: {', '.join(parsed_result.participants)}")

    return parsed_result
