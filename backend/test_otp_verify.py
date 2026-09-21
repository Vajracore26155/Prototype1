import requests
import json

API_URL = "http://127.0.0.1:8000"

# OTP from console logs
vendor_email = "vendor97269@test.com"
otp_code = "517064"  # From backend console output

print("=== OTP Verification Test ===\n")

print(f"Vendor Email: {vendor_email}")
print(f"OTP Code: {otp_code}\n")

print("Step 1: Verify OTP")
verify_resp = requests.post(f"{API_URL}/api/vendor/verify-otp",
    json={
        "vendor_email": vendor_email,
        "otp_code": otp_code
    })

print(f"Status: {verify_resp.status_code}")

if verify_resp.status_code != 200:
    print(f"✗ OTP verification failed")
    print(f"Response: {json.dumps(verify_resp.json(), indent=2)}")
    exit(1)

verify_data = verify_resp.json()
print(f"✓ OTP verified successfully\n")

# Extract session details
session_data = verify_data.get("data", {})
print("Session Created:")
print(f"  Session ID: {session_data.get('session_id')}")
print(f"  Session Token: {session_data.get('session_token')[:20]}...")
print(f"  Vendor ID: {session_data.get('vendor_id')}")
print(f"  Vendor Name: {session_data.get('vendor_name')}")
print(f"  Company: {session_data.get('company_name')}")
print(f"  Organization ID: {session_data.get('organization_id')}")
print(f"  Expires At: {session_data.get('expires_at')}")
print(f"  Valid For: {session_data.get('valid_for_hours')} hours")
print(f"  Message: {session_data.get('message')}")

print("\n✓ OTP verification flow COMPLETE and WORKING")
