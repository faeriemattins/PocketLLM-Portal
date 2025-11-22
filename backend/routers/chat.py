from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.model_service import model_service
from backend.cache_manager import cache_manager
from fastapi.responses import StreamingResponse
import json
import hashlib

router = APIRouter()

from backend import database

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7
    session_id: Optional[str] = None

@router.post("/completions")
async def chat_completions(request: ChatRequest):
    # Simple caching strategy: hash the last user message content
    # In a real app, you'd hash the entire conversation history
    last_message = request.messages[-1].content
    cache_key = hashlib.md5(last_message.encode()).hexdigest()
    
    # If session_id is provided, save the user message
    if request.session_id:
        # We assume the last message in request.messages is the new user message
        # In a robust app, we might want to be more explicit, but this works for now
        if request.messages[-1].role == "user":
             database.add_message(request.session_id, "user", request.messages[-1].content)

    cached_response = cache_manager.get(cache_key)
    if cached_response:
        # If cached, we stream it back as if it were generated
        # For simplicity in this demo, we'll just yield it in one go or chunks
        def cached_stream():
            yield f"data: {json.dumps({'content': cached_response, 'cached': True})}\n\n"
            yield "data: [DONE]\n\n"
            
            # If session_id is provided, save the cached assistant response too
            if request.session_id:
                database.add_message(request.session_id, "assistant", cached_response)
                
        return StreamingResponse(cached_stream(), media_type="text/event-stream")

    def generate():
        full_response = ""
        try:
            for chunk in model_service.stream_chat(
                messages=[m.dict() for m in request.messages],
                temperature=request.temperature
            ):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            # Cache the full response
            cache_manager.set(cache_key, full_response)
            
            # If session_id is provided, save the assistant response
            if request.session_id:
                database.add_message(request.session_id, "assistant", full_response)
                
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
