import requests
import sys

BASE_URL = "http://localhost:8001"

def register_and_login(username, password, role="user"):
    # Register
    requests.post(f"{BASE_URL}/auth/register", json={"username": username, "password": password, "role": role})
    # Login
    response = requests.post(f"{BASE_URL}/auth/token", data={"username": username, "password": password})
    if response.status_code != 200:
        print(f"Login failed for {username}: {response.text}")
        return None
    return response.json()["access_token"]

def test_isolation():
    print("Testing Session Isolation...")
    
    # Setup User A
    token_a = register_and_login("userA", "passA")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    # User A creates session
    resp = requests.post(f"{BASE_URL}/sessions/", json={"title": "User A Chat"}, headers=headers_a)
    if resp.status_code != 200:
        print(f"Failed to create session for User A: {resp.text}")
        return
    session_a_id = resp.json()["id"]
    print(f"User A created session: {session_a_id}")

    # Setup User B
    token_b = register_and_login("userB", "passB")
    headers_b = {"Authorization": f"Bearer {token_b}"}
    
    # User B lists sessions
    resp = requests.get(f"{BASE_URL}/sessions/", headers=headers_b)
    sessions_b = resp.json()
    if len(sessions_b) == 0:
        print("Success: User B sees 0 sessions.")
    else:
        print(f"Failure: User B sees {len(sessions_b)} sessions (Should be 0).")
        
    # User B tries to delete User A's session
    resp = requests.delete(f"{BASE_URL}/sessions/{session_a_id}", headers=headers_b)
    if resp.status_code == 404:
        print("Success: User B cannot delete User A's session (404 Not Found).")
    else:
        print(f"Failure: User B got {resp.status_code} when deleting User A's session.")

def test_cache_control():
    print("\nTesting Cache Control...")
    
    # Setup Admin
    token_admin = register_and_login("adminUser", "adminPass", role="admin")
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    
    # Set Cache Size to 10MB
    resp = requests.post(f"{BASE_URL}/admin/cache-settings", json={"size_limit_mb": 10}, headers=headers_admin)
    if resp.status_code == 200:
        print("Success: Admin updated cache settings.")
        print(resp.json())
    else:
        print(f"Failure: Admin update failed: {resp.text}")

    # Verify via stats
    resp = requests.get(f"{BASE_URL}/admin/cache-stats", headers=headers_admin)
    stats = resp.json()
    print(f"Cache Stats: {stats}")
    if stats.get("size_limit_bytes") == 10 * 1024 * 1024:
        print("Success: Cache size limit verified in stats.")
    else:
        print(f"Failure: Cache size limit mismatch. Expected {10*1024*1024}, got {stats.get('size_limit_bytes')}")

if __name__ == "__main__":
    try:
        test_isolation()
        test_cache_control()
    except Exception as e:
        print(f"An error occurred: {e}")
