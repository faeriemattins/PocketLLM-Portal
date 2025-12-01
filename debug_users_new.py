from backend import database

def list_users():
    db = database.SessionLocal()
    try:
        users = db.query(database.User).all()
        print(f"Found {len(users)} users:")
        for u in users:
            print(f"- {u.username} (Role: {u.role})")
    finally:
        db.close()

if __name__ == "__main__":
    list_users()
