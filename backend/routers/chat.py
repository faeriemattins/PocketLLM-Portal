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
from backend.config import config_manager

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    temperature: Optional[float] = 0.7
    session_id: Optional[str] = None

@router.post("/completions")
async def chat_completions(request: ChatRequest):
    # 1. Check Session Limit
    if request.session_id:
        # Get max prompts setting from ConfigManager (synced with Admin panel)
        max_prompts = config_manager.get("max_prompts", 20)
        
        # Count existing user messages in this session
        messages = database.get_messages(request.session_id)
        existing_user_msgs = sum(1 for m in messages if m['role'] == 'user')
        
        # The current request counts as +1
        total_msgs = existing_user_msgs + 1
        
        print(f"DEBUG: Session {request.session_id} | Existing: {existing_user_msgs} | New Total: {total_msgs} | Limit: {max_prompts}")
        
        if total_msgs > max_prompts:
            print(f"DEBUG: BLOCKED - Limit reached ({total_msgs} > {max_prompts})")
            raise HTTPException(
                status_code=400,
                detail=f"Session has reached maximum of {max_prompts} prompts. Please start a new session."
            )

    # 2. Prepare Cache Key
    # Session-scoped prompt-level caching
    last_user_message = request.messages[-1].content if request.messages else ""
    cache_payload = f"{last_user_message}-{request.temperature}"
    hash_val = hashlib.md5(cache_payload.encode()).hexdigest()
    
    if request.session_id:
        cache_key = f"{request.session_id}:{hash_val}"
    else:
        cache_key = f"global:{hash_val}"

    # 3. Check Cache
    cached_response = cache_manager.get(cache_key)
    if cached_response:
        if request.session_id:
            cache_manager.track_session_cache(request.session_id)
            
        def cached_stream():
            # IMPORTANT: Save user message NOW, after limit check passed
            if request.session_id and request.messages and request.messages[-1].role == "user":
                database.add_message(request.session_id, "user", request.messages[-1].content)
                
            yield f"data: {json.dumps({'content': cached_response, 'cached': True})}\n\n"
            yield "data: [DONE]\n\n"
            
            # Save assistant response
            if request.session_id:
                database.add_message(request.session_id, "assistant", cached_response)
                
        return StreamingResponse(cached_stream(), media_type="text/event-stream")

    # 4. Generate Response
    def generate():
        full_response = ""
        try:
            # IMPORTANT: Save user message NOW, after limit check passed
            if request.session_id and request.messages and request.messages[-1].role == "user":
                database.add_message(request.session_id, "user", request.messages[-1].content)
            
            for chunk in model_service.stream_chat(
                messages=[m.dict() for m in request.messages],
                temperature=request.temperature
            ):
                full_response += chunk
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            # 5. Cache & Cleanup
            # Enforce cache size limit (delete old items if needed)
            cache_manager.check_and_enforce_limit()
            cache_manager.set(cache_key, full_response)
            
            if request.session_id:
                cache_manager.track_session_cache(request.session_id)
                # Cleanup old sessions
                max_cached_sessions = config_manager.get("max_cached_sessions", 10)
                cache_manager.cleanup_old_sessions(max_cached_sessions)
                
                # Save assistant response
                database.add_message(request.session_id, "assistant", full_response)
                
            yield "data: [DONE]\n\n"
        except Exception as e:
            print(f"ERROR in generate: {e}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
