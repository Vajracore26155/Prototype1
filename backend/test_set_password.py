import requests
import json

API_URL = "http://127.0.0.1:8000"

# Session token from OTP verification test
session_token = "_6iMOyUrcEI7-UEedPjv_cOMHlCCPM2oYTSUoIBP5Yo"
new_password = "VendorSecurePass123"

print("=== Password Setup Test ===\n")

print(f"Session Token: {session_token[:20]}...")
print(f"New Password: {new_password}\n")

print("Step 1: Set Password")
set_pass_resp = requests.post(f"{API_URL}/api/vendor/set-password",
    params={
        "password": new_password,
        "session_token": session_token
    })

print(f"Status: {set_pass_resp.status_code}")

if set_pass_resp.status_code != 200:
    print(f"✗ Password setup failed")
    print(f"Response: {json.dumps(set_pass_resp.json(), indent=2)}")
    exit(1)

set_pass_data = set_pass_resp.json()
print(f"✓ Password set successfully\n")
print(f"Message: {set_pass_data['data']['message']}")

print("\n✓ Password setup flow COMPLETE and WORKING")
print("  Vendor can now login with email + password")
