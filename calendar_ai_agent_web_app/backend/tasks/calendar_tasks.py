from crewai import Task
from calendar_ai_agent_web_app.backend.agents.event_classifier import event_classifier
from calendar_ai_agent_web_app.backend.agents.event_parser import event_parser

extract_task = Task(
    description="Classify the user_input as a calendar event and extract basic info.",
    expected_output="Boolean if it's a calendar event, plus short description",
    agent=event_classifier,
    async_execution=False,
    input_vars=["user_input"]  # 👈 REQUIRED
)

parse_details_task = Task(
    description="Parse out the event name, time, location, and participants from the user_input.",
    expected_output="EventDetails object in JSON format",
    agent=event_parser,
    input_vars=["user_input"]  # 👈 REQUIRED
)
