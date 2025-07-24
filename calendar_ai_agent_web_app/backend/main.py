from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from fastapi import Request
from calendar_ai_agent_web_app.backend.services.processor import process_calendar_request
from calendar_ai_agent_web_app.backend.mail_utils.sender import send_email
from calendar_ai_agent_web_app.backend.schemas.models import  EventConfirmationDraft

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
    participants: Optional[List[str]] = []

@app.post("/process")
def process_event(request: CalendarRequest):
    confirmation = process_calendar_request(
        user_input=request.user_input,
        participants=request.participants or []
    )
    if not confirmation:
        return {"error": "Not a valid calendar request."}

    return confirmation.model_dump()


@app.post("/send_confirmation_email")
async def send_confirmation_email(email: EventConfirmationDraft, request: Request):
    body = await request.json()
    print("Received body:", body)
    try:
        send_email(
            to_emails=email.to_emails,
            subject=email.subject,
            message=email.confirmation_message
        )
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))