from backend import auth, database

def create_test_user():
    print("Creating test user...")
    hashed = auth.get_password_hash("password123")
    
    # Initialize DB (creates tables if not exist)
    database.init_db()
    
    # Check if user exists
    user = database.get_user("user")
    if user:
        print("User 'user' already exists. Updating password...")
        # We need to manually update because create_user doesn't update
        # Using internal session for update
        db = database.SessionLocal()
        try:
            db_user = db.query(database.User).filter(database.User.username == "user").first()
            if db_user:
                db_user.hashed_password = hashed
                db.commit()
        finally:
            db.close()
    else:
        print("Creating user 'user'...")
        database.create_user("user", hashed, role="user")
    

    # Check/Create Admin
    admin = database.get_user("admin")
    if not admin:
        print("Creating admin user...")
        admin_hash = auth.get_password_hash("admin123")
        database.create_user("admin", admin_hash, role="admin")
        print("Admin user created: admin / admin123")
    else:
        print("Admin user already exists.")

    print("Test user ready: user / password123")


if __name__ == "__main__":
    create_test_user()
