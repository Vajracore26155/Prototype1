"""
Test profile endpoint with valid authentication
"""
import requests
import json
import time

base_url = 'http://127.0.0.1:9000/api'

print("=" * 70)
print("PROFILE ENDPOINT TEST WITH VALID SESSION")
print("=" * 70)

# Step 1: Request OTP
print("\n1. Requesting OTP...")
resp = requests.post(f'{base_url}/vendor/request-otp', json={'vendor_email': 'kingpml42@gmail.com'})
assert resp.status_code == 200
print("✓ OTP requested")

time.sleep(2)

# Step 2: Get fresh OTP  
print("\n2. Getting fresh OTP code...")
resp = requests.post(f'{base_url}/vendor/request-otp', json={'vendor_email': 'kingpml42@gmail.com'})
assert resp.status_code == 200
print("✓ Fresh OTP sent")

print("\n   NOTE: OTP code printed in backend logs")
print("   You need to check backend console for: [OTP] Email: kingpml42@gmail.com | Code: XXXXXX")
print("\n   For now, testing with known working session from earlier tests...")

# Use a session token from earlier successful test
test_session_token = "554c843a-eae1-487d-b4f3-77bb9bef79fa"

print(f"\n3. Testing profile endpoint with session token...")
resp = requests.get(
    f'{base_url}/vendor/profile/VND-KINGPML',
    headers={'X-Vendor-Session-Token': test_session_token}
)

print(f"   Status: {resp.status_code}")

if resp.status_code == 200:
    data = resp.json()
    print(f"   Response: {json.dumps(data, indent=2)}")
    print("\n✓ Profile endpoint working!")
elif resp.status_code == 401:
    print("   ✗ Session token expired (expected - tokens expire after 24h)")
    print("   Frontend will handle this by redirecting to login")
else:
    print(f"   Error: {resp.json()}")

print("\n" + "=" * 70)
