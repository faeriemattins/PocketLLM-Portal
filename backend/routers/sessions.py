from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend import database

router = APIRouter()

class Session(BaseModel):
    id: str
    title: str
    created_at: str

class CreateSessionRequest(BaseModel):
    title: Optional[str] = "New Chat"

class Message(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: str

class AddMessageRequest(BaseModel):
    role: str
    content: str

@router.post("/", response_model=Session)
def create_session(request: CreateSessionRequest):
    return database.create_session(request.title)

@router.get("/", response_model=List[Session])
def list_sessions():
    return database.get_sessions()

@router.delete("/{session_id}")
def delete_session(session_id: str):
    database.delete_session(session_id)
    return {"status": "success"}

@router.get("/{session_id}/messages", response_model=List[Message])
def get_session_messages(session_id: str):
    return database.get_messages(session_id)

@router.post("/{session_id}/messages", response_model=Message)
def add_message(session_id: str, request: AddMessageRequest):
    return database.add_message(session_id, request.role, request.content)

class GenerateTitleRequest(BaseModel):
    user_message: str

@router.post("/{session_id}/title", response_model=Session)
def generate_session_title(session_id: str, request: GenerateTitleRequest):
    from backend.model_service import model_service
    title = model_service.generate_title(request.user_message)
    return database.update_session_title(session_id, title)
