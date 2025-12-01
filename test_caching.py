import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

# Login as admin
print("Logging in...")
login_data = {
    "username": "admin",
    "password": "admin123"
}
response = requests.post(f"{BASE_URL}/auth/token", data=login_data)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Test 1: Send identical request twice
print("\n=== Test 1: Identical Requests ===")
messages = [{"role": "user", "content": "Say exactly: Testing cache"}]
payload = {
    "messages": messages,
    "temperature": 0.7
}

print("Request 1 (should generate)...")
start = time.time()
r1 = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers, stream=True)
response1 = ""
for line in r1.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data_str = line_str[6:]
            if data_str != '[DONE]':
                try:
                    data = json.loads(data_str)
                    if 'content' in data:
                        response1 += data['content']
                except:
                    pass
time1 = time.time() - start
print(f"Response: {response1[:50]}...")
print(f"Time: {time1:.2f}s")

print("\nRequest 2 (should be cached)...")
start = time.time()
r2 = requests.post(f"{BASE_URL}/chat/completions", json=payload, headers=headers, stream=True)
response2 = ""
cached = False
for line in r2.iter_lines():
    if line:
        line_str = line.decode('utf-8')
        if line_str.startswith('data: '):
            data_str = line_str[6:]
            if data_str != '[DONE]':
                try:
                    data = json.loads(data_str)
                    if 'content' in data:
                        response2 += data['content']
                    if 'cached' in data:
                        cached = True
                except:
                    pass
time2 = time.time() - start
print(f"Response: {response2[:50]}...")
print(f"Time: {time2:.2f}s")
print(f"Cached: {cached}")
print(f"Responses match: {response1 == response2}")

# Check cache
print("\n=== Checking Cache ===")
cache_items = requests.get(f"{BASE_URL}/admin/cache-items", headers=headers).json()
print(f"Total cache items: {len(cache_items)}")
for item in cache_items[-3:]:
    print(f"Key: {item['key'][:50]}...")
    print(f"  Access count: {item['access_count']}")
