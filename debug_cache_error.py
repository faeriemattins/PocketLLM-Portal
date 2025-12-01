import requests
import sys

BASE_URL = "http://127.0.0.1:8001"

def test_login_and_cache():
    # 1. Login
    print("Attempting login as user...")
    try:
        response = requests.post(f"{BASE_URL}/auth/token", data={
            "username": "user",
            "password": "password123"
        })
        if response.status_code != 200:
            print(f"Login failed: {response.status_code} {response.text}")
            return
        
        token = response.json()["access_token"]
        print("Login successful.")
    except Exception as e:
        print(f"Login exception: {e}")
        return

    # 2. Fetch Cache Items
    print("Fetching cache items...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/admin/cache-items", headers=headers)
        
        if response.status_code != 200:
            print(f"Cache fetch failed: {response.status_code} {response.text}")
        else:
            data = response.json()
            print(f"Cache fetch successful. Items count: {len(data)}")
            # print(data) # Uncomment if needed
    except Exception as e:
        print(f"Cache fetch exception: {e}")

if __name__ == "__main__":
    test_login_and_cache()
