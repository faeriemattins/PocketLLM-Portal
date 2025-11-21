from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import chat, admin
import uvicorn
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI(title="PocketLLM Portal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/cache")
async def get_cache():
    db_path = "cache/cache.db"
    if not os.path.exists(db_path):
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value, store_time, access_count FROM Cache")
        rows = cursor.fetchall()
        conn.close()
        
        cache_data = []
        for row in rows:
            cache_data.append({
                "key": row[0],
                "value": row[1],
                "store_time": row[2],
                "access_count": row[3]
            })
        return cache_data
    except Exception as e:
        print(f"Error reading cache: {e}")
        return []

@app.get("/")
def read_root():
    return {"message": "PocketLLM Portal Backend is running"}

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
