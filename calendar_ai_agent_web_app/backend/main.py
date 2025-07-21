from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from calendar_ai_agent_web_app.backend.services.processor import process_calendar_request

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CalendarRequest(BaseModel):
    user_input: str
    participants: List[str]


@app.post("/process")
def process_event(request: CalendarRequest):
    confirmation = process_calendar_request(
        user_input=request.user_input,
        participants=request.participants
    )
    if not confirmation:
        return {"error": "Not a valid calendar request."}

    return {
        "confirmation_message": confirmation.confirmation_message,
        "calendar_link": confirmation.calendar_link
    }