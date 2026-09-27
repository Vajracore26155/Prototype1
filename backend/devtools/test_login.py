import requests
import json

resp = requests.post('http://127.0.0.1:8000/api/auth/login', 
    json={'email': 'mayankparab4811@gmail.com', 'password': 'Admin123'},
    timeout=5)
print(f'Status: {resp.status_code}')
try:
    data = resp.json()
    print(f'Access Token: {data.get("access_token", "MISSING")[:50]}...')
    print(f'User Role: {data.get("role")}')
    print(f'Organization: {data.get("organization")}')
    print('✓ LOGIN SUCCESS')
except Exception as e:
    print(f'Response: {resp.text[:200]}')
    print(f'Error: {e}')
