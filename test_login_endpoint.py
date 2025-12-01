import urllib.request
import urllib.parse
import json

def test_login():
    url = "http://localhost:8000/auth/token"
    data = urllib.parse.urlencode({
        "username": "admin",
        "password": "admin123"
    }).encode("utf-8")
    
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    
    try:
        with urllib.request.urlopen(req) as response:
            print(f"Status: {response.status}")
            print(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        print(f"Error: {e}")
        if hasattr(e, 'read'):
            print(e.read().decode("utf-8"))

if __name__ == "__main__":
    test_login()
