from crewai import Agent
from calendar_ai_agent_web_app.backend.schemas.models import EventExtraction


event_classifier = Agent(
    role="EventClassifierAgent",
    goal="Decide whether a message is a calendar event",
    backstory="An AI expert at classifying user intents related to calendar scheduling.",
    reasoning=True,  # Enable reasoning and planning
    max_reasoning_attempts=3,  # Limit reasoning attempts
    max_iter=30,  # Allow more iterations for complex planning
    allow_delegation=False,
    verbose=True,
)