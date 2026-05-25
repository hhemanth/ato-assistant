import os

from fastapi import APIRouter, Request
from langsmith import traceable
from pydantic import BaseModel
from supabase import create_client, Client

router = APIRouter()

_supabase: Client = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


class FeedbackRequest(BaseModel):
    user_query: str
    response: str


@router.post("/feedback", status_code=204)
@traceable(name="feedback")
async def submit_feedback(request: Request, body: FeedbackRequest) -> None:
    _supabase.table("feedback").insert(
        {"user_query": body.user_query, "response": body.response}
    ).execute()
