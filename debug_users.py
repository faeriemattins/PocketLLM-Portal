import sqlite3
from backend import auth, database

def debug_users():
    print("Checking users in DB...")
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, hashed_password FROM users")
    users = cursor.fetchall()
    conn.close()
    
    for u in users:
        print(f"User: {u['username']}, Role: {u['role']}")
        
    # Reset admin password
    print("\nResetting admin password to 'admin123'...")
    hashed = auth.get_password_hash("admin123")
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    # Check if admin exists
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if cursor.fetchone():
        cursor.execute("UPDATE users SET hashed_password = ? WHERE username = 'admin'", (hashed,))
        print("Admin password updated.")
    else:
        print("Admin user not found, creating...")
        database.create_user("admin", hashed, role="admin")
        print("Admin user created.")
    conn.commit()
    conn.close()

if __name__ == "__main__":
    debug_users()
