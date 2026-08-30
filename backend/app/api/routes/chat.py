import uuid

from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.agent import chat


router = APIRouter(
    prefix="/api/chat",
    tags=["AI Commerce"]
)


class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str


@router.post("/")
def chat_endpoint(request: ChatRequest):

    session_id = request.session_id

    if not session_id:
        session_id = str(uuid.uuid4())

    response = chat(
        session_id=session_id,
        user_message=request.message
    )

    return {
        "session_id": session_id,
        "message": response
    }