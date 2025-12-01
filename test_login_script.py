import requests

def test_login():
    url = "http://localhost:8000/auth/token"
    # Test with form data (correct)
    try:
        response = requests.post(url, data={"username": "user", "password": "password123"})
        print(f"Form Data Response: {response.status_code}")
        print(response.json())
    except Exception as e:
        print(f"Form Data Error: {e}")

    # Test with JSON (incorrect, to see if this matches user error)
    try:
        response = requests.post(url, json={"username": "user", "password": "password123"})
        print(f"JSON Response: {response.status_code}")
        print(response.text)
    except Exception as e:
        print(f"JSON Error: {e}")

if __name__ == "__main__":
    test_login()
