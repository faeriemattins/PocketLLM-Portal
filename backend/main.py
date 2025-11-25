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
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
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
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user['username'], "role": user['role']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
def read_root():
    return {"message": "PocketLLM Portal Backend is running"}

@app.on_event("startup")
async def startup_event():
    # Create default admin user
    try:
        hashed_pwd = auth.get_password_hash("admin123")
        database.create_user("admin", hashed_pwd, role="admin")
        print("Default admin user created/verified: admin/admin123")
    except Exception:
        pass # User likely exists

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8001, reload=True)
