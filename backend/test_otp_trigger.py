#!/usr/bin/env python3
import requests
import json

API_URL = "http://127.0.0.1:8003"  # Use port 8003 where backend is running

print("=" * 80)
print("Testing OTP Email Sending")
print("=" * 80)
print()

# Use an approved vendor
vendor_email = "e2e_vendor_199372@test.com"

print(f"Requesting OTP for: {vendor_email}")
print()

otp_resp = requests.post(f"{API_URL}/api/vendor/request-otp",
    json={"vendor_email": vendor_email})

print(f"Status: {otp_resp.status_code}")

if otp_resp.status_code == 200:
    print("✅ OTP Request Successful")
    otp_data = otp_resp.json()
    print(f"  OTP ID: {otp_data['data']['otp_id']}")
    print()
    print("Check backend console for email status message!")
else:
    print(f"❌ Request failed")
    print(json.dumps(otp_resp.json(), indent=2))
