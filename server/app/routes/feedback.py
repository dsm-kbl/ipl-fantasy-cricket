"""Feedback API route."""

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from server.app.core.deps import get_current_user
from server.app.models.user import User
from server.app.services.email_service import send_feedback_email

router = APIRouter(prefix="/api", tags=["feedback"])


class FeedbackRequest(BaseModel):
    message: str


@router.post("/feedback")
async def submit_feedback(
    body: FeedbackRequest,
    current_user: User = Depends(get_current_user),
):
    """Submit feedback from an authenticated user."""
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    asyncio.get_event_loop().run_in_executor(
        None, send_feedback_email, current_user.username, current_user.email, message
    )

    return {"message": "Feedback sent. Thanks!"}
