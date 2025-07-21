from typing import Optional
from pydantic import BaseModel, Field

class EventExtraction(BaseModel):
    description: str = Field(description="Raw description of the event")
    is_calendar_event: bool = Field(description="Whether this text describes a calendar event")
    confidence_score: float = Field(description="Confidence score between 0 and 1")

class EventDetails(BaseModel):
    name: str = Field(description="Name of the event")
    description: str = Field(description="Description of the event")
    location: str = Field(description="Location of the event")
    date: str = Field(description="ISO 8601 datetime")
    duration_minutes: int = Field(description="Duration in minutes")
    participants: list[str] = Field(description="List of participants")

class EventConfirmation(BaseModel):
    confirmation_message: str = Field(description="Natural language confirmation")
    calendar_link: Optional[str] = Field(description="Calendar link")
