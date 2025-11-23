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
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create sessions table with user_id
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        user_id TEXT,
        title TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
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
    
    # Create settings table for admin configurations
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Set default max_prompts_per_session if not exists
    cursor.execute('''
    INSERT OR IGNORE INTO settings (key, value) VALUES ('max_prompts_per_session', '20')
    ''')
    
    conn.commit()
    conn.close()

def create_session(user_id, title="New Chat"):
    conn = get_db_connection()
    cursor = conn.cursor()
    session_id = str(uuid.uuid4())
    cursor.execute('INSERT INTO sessions (id, user_id, title) VALUES (?, ?, ?)', (session_id, user_id, title))
    conn.commit()
    conn.close()
    return {"id": session_id, "user_id": user_id, "title": title, "created_at": datetime.now().isoformat()}

def get_sessions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM sessions WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions

def delete_session(session_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verify ownership before deleting
    cursor.execute('SELECT id FROM sessions WHERE id = ? AND user_id = ?', (session_id, user_id))
    if not cursor.fetchone():
        conn.close()
        return None # Session not found or not owned by user

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

def create_user(username, hashed_password, role="user"):
    conn = get_db_connection()
    cursor = conn.cursor()
    user_id = str(uuid.uuid4())
    try:
        cursor.execute('INSERT INTO users (id, username, hashed_password, role) VALUES (?, ?, ?, ?)', 
                       (user_id, username, hashed_password, role))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return None
    conn.close()
    return {"id": user_id, "username": username, "role": role}

def get_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_setting(key):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
    result = cursor.fetchone()
    conn.close()
    return result['value'] if result else None

def set_setting(key, value):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO settings (key, value, updated_at) 
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(key) DO UPDATE SET value=?, updated_at=CURRENT_TIMESTAMP
    ''', (key, value, value))
    conn.commit()
    conn.close()
    return {"key": key, "value": value}

def get_all_settings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM settings')
    settings = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return settings
