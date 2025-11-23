from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import chat, admin, sessions
import uvicorn
from pydantic import BaseModel
import sqlite3
import os
from backend.database import init_db

app = FastAPI(title="PocketLLM Portal")

# Initialize database
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(sessions.router, prefix="/sessions", tags=["sessions"])

from backend import auth, database
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

@app.post("/auth/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    # We use form_data.username and form_data.password for simplicity with OAuth2 standard
    user = database.get_user(form_data.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = auth.get_password_hash(form_data.password)
    database.create_user(form_data.username, hashed_password)
    return {"message": "User created successfully"}

@app.post("/auth/token", response_model=auth.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = database.get_user(form_data.username)
    if not user or not auth.verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value, store_time, access_count FROM Cache")
        rows = cursor.fetchall()
        conn.close()
        
        cache_data = []
        for row in rows:
            key = row[0]
            value = row[1]
            
            # Handle binary keys
            if isinstance(key, bytes):
                try:
                    key = key.decode('utf-8')
                except:
                    key = str(key)
            
            # Handle binary values (likely pickled)
            if isinstance(value, bytes):
                try:
                    # Try to decode as utf-8 first (in case it's just a string)
                    value = value.decode('utf-8')
                except:
                    # If binary/pickled, just show representation
                    value = f"<Binary Data: {len(value)} bytes>"

            cache_data.append({
                "key": key,
                "value": value,
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
