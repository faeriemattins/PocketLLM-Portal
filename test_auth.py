import requests
import sys

BASE_URL = "http://localhost:8001"

def test_auth():
    print("Testing Auth Flow...")
    
    # 1. Register User
    username = "testuser"
    password = "testpassword"
    print(f"Registering user '{username}'...")
    response = requests.post(f"{BASE_URL}/auth/register", data={"username": username, "password": password})
    if response.status_code == 200:
        print("Registration successful.")
    elif response.status_code == 400 and "already registered" in response.text:
        print("User already registered.")
    else:
        print(f"Registration failed: {response.status_code} {response.text}")
        return

    # 2. Login
    print("Logging in...")
    response = requests.post(f"{BASE_URL}/auth/token", data={"username": username, "password": password})
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("Login successful. Token received.")
    else:
        print(f"Login failed: {response.status_code} {response.text}")
        return

    # 3. Access Admin Route (Should Fail)
    print("Accessing Admin Route (Should Fail)...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/admin/system-stats", headers=headers)
    if response.status_code == 403:
        print("Admin access denied as expected (403 Forbidden).")
    else:
        print(f"Unexpected status code: {response.status_code} {response.text}")

    # 4. Register Admin (Manual DB manipulation needed for real test, but we can try registering another user)
    # Since we can't easily set role via API, we'll skip positive admin test for now or assume manual DB update.

if __name__ == "__main__":
    try:
        test_auth()
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to backend. Is it running?")
