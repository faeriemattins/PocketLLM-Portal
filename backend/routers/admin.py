from fastapi import APIRouter, HTTPException
import psutil
import os
from backend.cache_manager import cache_manager
from backend.model_service import model_service
from pydantic import BaseModel

router = APIRouter()

from backend.config import config_manager

class SessionConfig(BaseModel):
    max_prompts: int

class CacheSessionConfig(BaseModel):
    max_cached_sessions: int

class ModelSelection(BaseModel):
    model_filename: str

@router.get("/system-stats")
def get_system_stats():
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2)
    }

@router.get("/cache-stats")
def get_cache_stats():
    return cache_manager.stats()

@router.post("/clear-cache")
def clear_cache():
    cache_manager.clear()
    return {"status": "Cache cleared"}

@router.get("/session-config")
def get_session_config():
    return {"max_prompts": config_manager.get("max_prompts", 20)}

@router.post("/session-config")
def set_session_config(config: SessionConfig):
    config_manager.set("max_prompts", config.max_prompts)
    return {"status": "Session config updated", "max_prompts": config.max_prompts}

@router.get("/cache-session-config")
def get_cache_session_config():
    return {"max_cached_sessions": config_manager.get("max_cached_sessions", 10)}

@router.post("/cache-session-config")
def set_cache_session_config(config: CacheSessionConfig):
    config_manager.set("max_cached_sessions", config.max_cached_sessions)
    return {"status": "Cache session config updated", "max_cached_sessions": config.max_cached_sessions}

@router.get("/models")
def list_models():
    return {
        "models": model_service.list_models(),
        "current_model": os.path.basename(model_service.current_model_path)
    }

@router.post("/models/select")
def select_model(selection: ModelSelection):
    try:
        model_service.set_model(selection.model_filename)
        return {"status": "Model changed", "current_model": selection.model_filename}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
