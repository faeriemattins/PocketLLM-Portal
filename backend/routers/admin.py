from fastapi import APIRouter
import psutil
from backend.cache_manager import cache_manager

router = APIRouter()

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
