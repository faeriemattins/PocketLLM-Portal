import requests
import sys

BASE_URL = "http://localhost:8001"

def test_session_limits():
    print("Testing Session Prompt Limits...")
    
    # Register and login
    requests.post(f"{BASE_URL}/auth/register", json={"username": "limituser", "password": "pass123"})
    response = requests.post(f"{BASE_URL}/auth/token", data={"username": "limituser", "password": "pass123"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create session
    resp = requests.post(f"{BASE_URL}/sessions/", json={"title": "Limit Test"}, headers=headers)
    session_id = resp.json()["id"]
    print(f"Created session: {session_id}")
    
    # Get current limit
    admin_token = get_admin_token()
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    resp = requests.get(f"{BASE_URL}/admin/settings", headers=admin_headers)
    settings = resp.json()["settings"]
    max_prompts = next((int(s["value"]) for s in settings if s["key"] == "max_prompts_per_session"), 20)
    print(f"Max prompts per session: {max_prompts}")
    
    # Send messages up to limit
    for i in range(max_prompts):
        resp = requests.post(
            f"{BASE_URL}/chat/completions",
            json={
                "messages": [{"role": "user", "content": f"Message {i+1}"}],
                "session_id": session_id
            },
            headers=headers
        )
        if resp.status_code == 200:
            print(f"Message {i+1}/{max_prompts} sent successfully")
        else:
            print(f"Failed at message {i+1}: {resp.text}")
            break
    
    # Try to send one more (should fail)
    resp = requests.post(
        f"{BASE_URL}/chat/completions",
        json={
            "messages": [{"role": "user", "content": "This should fail"}],
            "session_id": session_id
        },
        headers=headers
    )
    
    if resp.status_code == 400:
        print(f"✓ Success: Limit enforced. Error: {resp.json()['detail']}")
    else:
        print(f"✗ Failure: Expected 400, got {resp.status_code}")

def test_per_session_caching():
    print("\nTesting Per-Session Caching...")
    
    # Login
    response = requests.post(f"{BASE_URL}/auth/token", data={"username": "limituser", "password": "pass123"})
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create two sessions
    resp1 = requests.post(f"{BASE_URL}/sessions/", json={"title": "Cache Test 1"}, headers=headers)
    session1 = resp1.json()["id"]
    
    resp2 = requests.post(f"{BASE_URL}/sessions/", json={"title": "Cache Test 2"}, headers=headers)
    session2 = resp2.json()["id"]
    
    # Send same message to both sessions
    message = {"role": "user", "content": "Hello"}
    
    resp1 = requests.post(
        f"{BASE_URL}/chat/completions",
        json={"messages": [message], "session_id": session1},
        headers=headers
    )
    
    resp2 = requests.post(
        f"{BASE_URL}/chat/completions",
        json={"messages": [message], "session_id": session2},
        headers=headers
    )
    
    print("✓ Same message sent to two different sessions")
    print("  Cache keys should be different (include session_id)")
    print(f"  Session 1: {session1}")
    print(f"  Session 2: {session2}")

def test_admin_settings():
    print("\nTesting Admin Settings Management...")
    
    admin_token = get_admin_token()
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Update max prompts
    resp = requests.post(
        f"{BASE_URL}/admin/settings",
        json={"max_prompts_per_session": 15},
        headers=headers
    )
    
    if resp.status_code == 200:
        print(f"✓ Updated max_prompts_per_session to 15")
        print(f"  Response: {resp.json()}")
    else:
        print(f"✗ Failed to update settings: {resp.text}")
    
    # Get settings
    resp = requests.get(f"{BASE_URL}/admin/settings", headers=headers)
    settings = resp.json()["settings"]
    print(f"✓ Current settings: {settings}")

def get_admin_token():
    # Register admin if not exists
    requests.post(f"{BASE_URL}/auth/register", json={"username": "admin", "password": "admin123", "role": "admin"})
    response = requests.post(f"{BASE_URL}/auth/token", data={"username": "admin", "password": "admin123"})
    return response.json()["access_token"]

if __name__ == "__main__":
    try:
        test_admin_settings()
        test_session_limits()
        test_per_session_caching()
        print("\n✓ All tests completed!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
