from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class EventExtraction(BaseModel):
    description: str = Field(description="Raw description of the event")
    is_calendar_event: bool = Field(description="Whether this text describes a calendar event")
    is_calendar_modify_event: bool = Field(description="Whether this text describes a calendar event that needs to be changed or modified, for example, modify event time or addition of participants")
    is_list_events: bool = Field(description="Whether this text describes a request to list or query calendar events, such as 'show me all my events this week', 'tell me all my meetings with Ethan', or 'list all meetings in the morning'.")
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

class EventConfirmationDraft(BaseModel):
    confirmation_message: str
    calendar_link: Optional[str]
    to_emails: list[str]
    subject: str
    requires_confirmation: bool = True


class ListCalendarEventsFilters(BaseModel):
    """
    Model to represent a request to list or query calendar events.
    Used when the user is not creating or modifying events, but retrieving them.
    """
    description: str = Field(..., description="A cleaned-up version of the user query, e.g., 'List all meetings this week'")

    # Optional filters
    start_time: Optional[datetime] = Field(None, description="Start datetime range to filter events")
    end_time: Optional[datetime] = Field(None, description="End datetime range to filter events")
    participants: Optional[List[str]] = Field(None, description="People to filter events by (e.g., ['ethan@example.com'])")
    time_of_day: Optional[str] = Field(None, description="Time of day filter (e.g., 'morning', 'afternoon', 'evening')")
    keywords: Optional[List[str]] = Field(None, description="Keywords to match in event descriptions or titles")

class CalendarEvent(BaseModel):
    title: str = Field(..., description="Title or summary of the event")
    start_time: datetime = Field(..., description="Start time of the event")
    end_time: datetime = Field(..., description="End time of the event")
    participants: List[str] = Field(..., description="List of participant emails")
    location: Optional[str] = Field(None, description="Location of the event")
    description: Optional[str] = Field(None, description="Optional additional description of the event")

class ListedEvents(BaseModel):
    query_summary: str = Field(..., description="A summary of the user's original query or intent")
    matched_events: List[CalendarEvent] = Field(..., description="List of events that matched the query")

class EventListConfirmation(BaseModel):
    """
    Schema for AI-generated natural language response summarizing a list of matched events.
    """
    message: str = Field(..., description="Natural language summary of the matched calendar events, formatted for user display.")
