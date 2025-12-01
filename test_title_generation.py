import requests
import sys

BASE_URL = "http://127.0.0.1:8001"

def test_title_generation():
    # 1. Login as admin (or user)
    print("Logging in...")
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code != 200:
            print(f"Login failed: {response.status_code}")
            return
        token = response.json()["access_token"]
    except Exception as e:
        print(f"Login error: {e}")
        return

    # 2. Create a session
    print("Creating session...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(f"{BASE_URL}/sessions/", json={"title": "Test Session"}, headers=headers)
        if response.status_code != 200:
            print(f"Create session failed: {response.status_code}")
            return
        session_id = response.json()["id"]
        print(f"Session created: {session_id}")
    except Exception as e:
        print(f"Create session error: {e}")
        return

    # 3. Generate Title
    print("Generating title...")
    try:
        response = requests.post(f"{BASE_URL}/sessions/{session_id}/title", 
                                 json={"user_message": "How do I make a cake?"}, 
                                 headers=headers)
        
        if response.status_code == 200:
            print(f"Title generated successfully: {response.json()['title']}")
        else:
            print(f"Title generation failed: {response.status_code}")
            print(f"Response text: {response.text}")
    except Exception as e:
        print(f"Title generation error: {e}")
    print("Test finished.")

if __name__ == "__main__":
    test_title_generation()
