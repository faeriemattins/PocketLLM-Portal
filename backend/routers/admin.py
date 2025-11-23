from fastapi import APIRouter, HTTPException
import psutil
import os
from backend.cache_manager import cache_manager
from backend.model_service import model_service
from pydantic import BaseModel

router = APIRouter()

class CacheConfig(BaseModel):
    size_limit_mb: int

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

@router.get("/cache-config")
def get_cache_config():
    limit = cache_manager.get_size_limit()
    # Convert bytes to MB for frontend
    limit_mb = int(limit / (1024 * 1024)) if limit else 0
    return {"size_limit_mb": limit_mb}

@router.post("/cache-config")
def set_cache_config(config: CacheConfig):
    # Convert MB to bytes
    size_bytes = config.size_limit_mb * 1024 * 1024
    cache_manager.set_size_limit(size_bytes)
    return {"status": "Cache size limit updated", "size_limit_mb": config.size_limit_mb}

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
