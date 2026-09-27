"""
Full vendor OTP login flow test
Tests the complete end-to-end workflow
"""
import requests
import json

base_url = 'http://127.0.0.1:9000/api'

print("="*70)
print("FULL VENDOR OTP FLOW TEST - END-TO-END")
print("="*70)

# Step 1: Request OTP
print("\n[STEP 1] Request OTP")
print("-" * 70)
response = requests.post(
    f'{base_url}/vendor/request-otp',
    json={'vendor_email': 'kingpml42@gmail.com'}
)
print(f"✓ Status: {response.status_code}")
print(f"✓ Response: {json.dumps(response.json(), indent=2)}")

# Step 2: Verify OTP with correct code
print("\n[STEP 2] Verify OTP with code 175158")
print("-" * 70)
response = requests.post(
    f'{base_url}/vendor/verify-otp',
    json={
        'vendor_email': 'kingpml42@gmail.com',
        'otp_code': '175158'
    }
)
print(f"✓ Status: {response.status_code}")
data = response.json()
print(f"✓ Response: {json.dumps(data, indent=2)}")

if not data.get('success'):
    print("✗ FAILED - OTP verification returned success: false")
    exit(1)

session_token = data['data']['session_token']
print(f"\n✓ Session token received: {session_token}")

# Step 3: Get vendor session info (authenticated request)
print("\n[STEP 3] Get Vendor Session Info (authenticated)")
print("-" * 70)
response = requests.get(
    f'{base_url}/vendor/upload/session',
    headers={'X-Vendor-Session-Token': session_token}
)
print(f"✓ Status: {response.status_code}")
session_data = response.json()
print(f"✓ Response: {json.dumps(session_data, indent=2)}")

if not session_data.get('success'):
    print("✗ FAILED - Could not retrieve session info")
    exit(1)

# Step 4: Get vendor upload history (authenticated request)
print("\n[STEP 4] Get Vendor Upload History (authenticated)")
print("-" * 70)
response = requests.get(
    f'{base_url}/vendor/upload/history',
    headers={'X-Vendor-Session-Token': session_token}
)
print(f"✓ Status: {response.status_code}")
history_data = response.json()
print(f"✓ Response: {json.dumps(history_data, indent=2)}")

if not history_data.get('success'):
    print("✗ FAILED - Could not retrieve upload history")
    exit(1)

# Step 5: Test invalid session token
print("\n[STEP 5] Test Invalid Session Token")
print("-" * 70)
response = requests.get(
    f'{base_url}/vendor/upload/session',
    headers={'X-Vendor-Session-Token': 'invalid-token-12345'}
)
print(f"✓ Status: {response.status_code} (Should be 401)")
if response.status_code != 401:
    print(f"✗ FAILED - Expected 401 but got {response.status_code}")
    exit(1)
print(f"✓ Error response: {response.json()['detail']['error']['message']}")

print("\n" + "="*70)
print("✓ ALL TESTS PASSED - VENDOR OTP FLOW IS FULLY WORKING")
print("="*70)
print("\nThe vendor can now:")
print("  1. Request OTP by email")
print("  2. Verify OTP and get session token")
print("  3. Access authenticated endpoints with the session token")
print("  4. View session information")
print("  5. View upload history")
print("\nThe frontend should now display the vendor dashboard correctly!")
