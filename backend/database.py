import sqlite3
import uuid
from datetime import datetime
import os

DB_PATH = "backend/db/chat.db"

def get_db_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create messages table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
    )
    ''')
    
    conn.commit()
    conn.close()

def create_session(title="New Chat"):
    conn = get_db_connection()
    cursor = conn.cursor()
    session_id = str(uuid.uuid4())
    cursor.execute('INSERT INTO sessions (id, title) VALUES (?, ?)', (session_id, title))
    conn.commit()
    conn.close()
    return {"id": session_id, "title": title, "created_at": datetime.now().isoformat()}

def get_sessions():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions ORDER BY created_at DESC')
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions

def delete_session(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Delete messages first (though CASCADE should handle this)
    cursor.execute('DELETE FROM messages WHERE session_id = ?', (session_id,))
    messages_deleted = cursor.rowcount
    # Delete the session
    cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    sessions_deleted = cursor.rowcount
    conn.commit()
    conn.close()
    print(f"Deleted session {session_id}: {sessions_deleted} session(s), {messages_deleted} message(s)")
    return {"sessions_deleted": sessions_deleted, "messages_deleted": messages_deleted}

def update_session_title(session_id, title):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE sessions SET title = ? WHERE id = ?', (title, session_id))
    conn.commit()
    # Fetch the updated session to return all fields
    cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = cursor.fetchone()
    conn.close()
    return dict(session) if session else {"id": session_id, "title": title}

def add_message(session_id, role, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    message_id = str(uuid.uuid4())
    cursor.execute('INSERT INTO messages (id, session_id, role, content) VALUES (?, ?, ?, ?)', 
                   (message_id, session_id, role, content))
    conn.commit()
    conn.close()
    return {"id": message_id, "session_id": session_id, "role": role, "content": content, "created_at": datetime.now().isoformat()}

def get_messages(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC', (session_id,))
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages
