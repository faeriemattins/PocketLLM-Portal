from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
import psutil
import os
from backend.cache_manager import cache_manager
from backend.model_service import model_service
from backend.config import config_manager
from backend import auth

router = APIRouter()

async def get_current_admin_user(current_user: auth.TokenData = Depends(auth.get_current_user)):
    # In a real app, we'd fetch the user from DB to check role, but for JWT we encoded it
    # However, our TokenData only has username. Let's fetch user to be safe.
    from backend import database
    user = database.get_user(current_user.username)
    if not user or user['role'] != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user

class SessionConfig(BaseModel):
    max_prompts: int

class CacheSessionConfig(BaseModel):
    max_cached_sessions: int

class ModelSelection(BaseModel):
    model_filename: str

class CacheSettings(BaseModel):
    size_limit_mb: int

class AppSettings(BaseModel):
    max_prompts_per_session: int = None

@router.get("/system-stats")
def get_system_stats(current_user: dict = Depends(get_current_admin_user)):
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
        "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2)
    }

@router.get("/cache-stats")
def get_cache_stats(current_user: dict = Depends(get_current_admin_user)):
    return cache_manager.stats()

@router.get("/cache-items")
def get_cache_items(current_user: dict = Depends(get_current_admin_user)):
    return cache_manager.get_all_items()

@router.post("/clear-cache")
def clear_cache(current_user: dict = Depends(get_current_admin_user)):
    cache_manager.clear()
    return {"status": "Cache cleared"}

@router.get("/session-config")
def get_session_config(current_user: dict = Depends(get_current_admin_user)):
    return {"max_prompts": config_manager.get("max_prompts", 20)}

@router.post("/session-config")
def set_session_config(config: SessionConfig, current_user: dict = Depends(get_current_admin_user)):
    config_manager.set("max_prompts", config.max_prompts)
    return {"status": "Session config updated", "max_prompts": config.max_prompts}

@router.get("/cache-session-config")
def get_cache_session_config(current_user: dict = Depends(get_current_admin_user)):
    return {"max_cached_sessions": config_manager.get("max_cached_sessions", 10)}

@router.post("/cache-session-config")
def set_cache_session_config(config: CacheSessionConfig, current_user: dict = Depends(get_current_admin_user)):
    config_manager.set("max_cached_sessions", config.max_cached_sessions)
    return {"status": "Cache session config updated", "max_cached_sessions": config.max_cached_sessions}

@router.get("/models")
def list_models(current_user: dict = Depends(get_current_admin_user)):
    return {
        "models": model_service.list_models(),
        "current_model": os.path.basename(model_service.current_model_path)
    }

@router.post("/models/select")
def select_model(selection: ModelSelection, current_user: dict = Depends(get_current_admin_user)):
    try:
        model_service.set_model(selection.model_filename)
        return {"status": "Model changed", "current_model": selection.model_filename}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache-settings")
def update_cache_settings(settings: CacheSettings, current_user: dict = Depends(get_current_admin_user)):
    # Convert MB to Bytes
    size_bytes = settings.size_limit_mb * 1024 * 1024
    cache_manager.set_size_limit(size_bytes)
    return {"status": "updated", "new_limit_bytes": size_bytes}

@router.get("/settings")
def get_settings(current_user: dict = Depends(get_current_admin_user)):
    from backend import database
    settings = database.get_all_settings()
    return {"settings": settings}

@router.post("/settings")
def update_settings(settings: AppSettings, current_user: dict = Depends(get_current_admin_user)):
    from backend import database
    updated = []
    
    if settings.max_prompts_per_session is not None:
        result = database.set_setting('max_prompts_per_session', str(settings.max_prompts_per_session))
        updated.append(result)
    
    return {"status": "updated", "settings": updated}
