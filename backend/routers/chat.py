from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from backend.model_service import model_service
from backend.cache_manager import cache_manager
from fastapi.responses import StreamingResponse
import json
import hashlib

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7

@router.post("/completions")
async def chat_completions(request: ChatRequest):
    # Simple caching strategy: hash the last user message content
    # In a real app, you'd hash the entire conversation history
    last_message = request.messages[-1].content
    cache_key = hashlib.md5(last_message.encode()).hexdigest()
    
    cached_response = cache_manager.get(cache_key)
    if cached_response:
        # If cached, we stream it back as if it were generated
        # For simplicity in this demo, we'll just yield it in one go or chunks
        def cached_stream():
            yield f"data: {json.dumps({'content': cached_response, 'cached': True})}\n\n"
            yield "data: [DONE]\n\n"
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
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
