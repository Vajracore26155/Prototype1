"""
Test all password-related backend endpoints with valid session
"""
import requests
import json
import time

base_url = 'http://127.0.0.1:9000/api'

print("=" * 70)
print("TESTING PASSWORD ENDPOINTS")
print("=" * 70)

# Use the known working session token from earlier
session_token = "554c843a-eae1-487d-b4f3-77bb9bef79fa"
vendor_id = "VND-KINGPML"

# Test 1: GET Profile (to see has_password status)
print("\n[TEST 1] GET /api/vendor/profile/{vendor_id}")
print("-" * 70)
resp = requests.get(
    f'{base_url}/vendor/profile/{vendor_id}',
    headers={'X-Vendor-Session-Token': session_token}
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()['data']
    print(f"✓ Vendor: {data['company_name']}")
    print(f"✓ Email: {data['email']}")
    print(f"✓ Has Password: {data['has_password']}")
    print(f"✓ Username: {data['username']}")
    has_password = data['has_password']
else:
    print(f"✗ Error: {resp.json()}")
    has_password = False

# Test 2: PUT Profile (update profile info)
print("\n[TEST 2] PUT /api/vendor/profile/{vendor_id}")
print("-" * 70)
resp = requests.put(
    f'{base_url}/vendor/profile/{vendor_id}',
    headers={'X-Vendor-Session-Token': session_token},
    json={
        'contact_name': 'Updated Name',
        'phone': '+91-8888888888',
        'username': 'testvendor123'
    }
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"✓ Profile updated successfully")
    print(f"  Response: {json.dumps(resp.json()['data'], indent=4)}")
else:
    print(f"✗ Error: {resp.json()}")

# Test 3: POST set-password (if vendor doesn't have password)
if not has_password:
    print("\n[TEST 3] POST /api/vendor/set-password/{vendor_id}")
    print("-" * 70)
    resp = requests.post(
        f'{base_url}/vendor/set-password/{vendor_id}',
        headers={'X-Vendor-Session-Token': session_token},
        json={
            'username': 'kingvendor',
            'password': 'SecurePass123'
        }
    )
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        print(f"✓ Password set successfully")
        print(f"  Response: {json.dumps(resp.json()['data'], indent=4)}")
    else:
        print(f"✗ Error: {resp.json()}")
else:
    print("\n[TEST 3] SKIPPED - Vendor already has password set")

# Test 4: POST change-password (after setting password)
print("\n[TEST 4] POST /api/vendor/change-password/{vendor_id}")
print("-" * 70)
resp = requests.post(
    f'{base_url}/vendor/change-password/{vendor_id}',
    headers={'X-Vendor-Session-Token': session_token},
    json={
        'current_password': 'SecurePass123',
        'new_password': 'NewSecurePass456'
    }
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    print(f"✓ Password changed successfully")
    print(f"  Response: {json.dumps(resp.json()['data'], indent=4)}")
elif resp.status_code == 401:
    print(f"⚠ Session expired (401) - this is expected for old tokens")
    print(f"  Frontend will handle this by redirecting to login")
else:
    print(f"✗ Error: {resp.json()}")

print("\n" + "=" * 70)
print("ENDPOINT TESTING COMPLETE")
print("=" * 70)
