from typing import Optional
from pydantic import BaseModel, Field

class EventExtraction(BaseModel):
    description: str = Field(description="Raw description of the event")
    is_calendar_event: bool = Field(description="Whether this text describes a calendar event")
    is_calendar_modify_event: bool = Field(description="Whether this text describes a calendar event that needs to be changed or modified, for example, modify event time or addition of participants")
    confidence_score: float = Field(description="Confidence score between 0 and 1")

class EventDetails(BaseModel):
    name: str = Field(description="Name of the event")
    description: str = Field(description="Description of the event")
    location: str = Field(description="Location of the event")
    date: str = Field(description="ISO 8601 datetime")
    duration_minutes: int = Field(description="Duration in minutes")
    participants: list[str] = Field(description="List of participants")

class EventUpdateDetails(BaseModel):
    name: str = Field(description="Name of the event to update.")
    description: str = Field(description="Updated description or agenda of the event.")
    location: str = Field(description="Updated location of the event.")
    original_date: str = Field(description="Original datetime of the event to identify the event to update (ISO 8601 format with timezone).")
    new_date: str = Field(description="New datetime to update the event to (ISO 8601 format with timezone).")
    duration_minutes: int = Field(description="Updated duration of the event in minutes.")
    participants: list[str] = Field(description="Updated list of participant email addresses.")

class EventConfirmation(BaseModel):
    confirmation_message: str = Field(description="Natural language confirmation")
    calendar_link: Optional[str] = Field(description="Calendar link")
