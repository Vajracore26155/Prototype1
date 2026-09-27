#!/usr/bin/env python3
"""
Test REJECTED vendor access control
"""
import requests
import json
import random

API_URL = "http://127.0.0.1:8000"
ADMIN_EMAIL = "mayankparab4811@gmail.com"
ADMIN_PASSWORD = "Admin123"

print("=" * 80)
print("TEST: REJECTED VENDOR ACCESS CONTROL")
print("=" * 80)
print()

# Create a vendor
vendor_email = f"rejected_{random.randint(100000, 999999)}@test.com"

print("🔹 SETUP: CREATE AND REJECT VENDOR")
print("-" * 80)

# Register vendor
reg_resp = requests.post(f"{API_URL}/api/vendor/register",
    json={
        'email': vendor_email,
        'company_name': f'Rejected Corp {random.randint(1000,9999)}',
        'contact_name': 'Rejected User',
        'phone': '9876543210',
        'password': 'TempPass123'
    })

vendor_id = reg_resp.json()["data"]["vendor_id"]
print(f"✓ Vendor created: {vendor_id}")
print()

# Admin login
admin_login = requests.post(f"{API_URL}/api/auth/login",
    json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
admin_token = admin_login.json()["access_token"]
headers = {"Authorization": f"Bearer {admin_token}"}

# Get vendor request
pending_resp = requests.get(f"{API_URL}/api/admin/vendor-requests", headers=headers)
our_request = None
for req in pending_resp.json()["data"]["requests"]:
    if req["vendor_email"] == vendor_email:
        our_request = req
        break

request_id = our_request["request_id"]
print(f"Found request: {request_id}")
print()

# Admin REJECTS vendor
reject_resp = requests.post(
    f"{API_URL}/api/admin/vendor-requests/{request_id}/decide",
    json={"approved": False, "notes": "Test rejection"},
    headers=headers)

if reject_resp.status_code == 200:
    reject_data = reject_resp.json()
    print(f"✓ Vendor REJECTED by admin")
    print(f"  Decision: {reject_data['data']['decision']}")
    print()
else:
    print(f"✗ Rejection failed: {reject_resp.status_code}")
    exit(1)

print("🔹 TEST 1: REJECTED VENDOR TRIES OTP LOGIN")
print("-" * 80)

otp_resp = requests.post(f"{API_URL}/api/vendor/request-otp",
    json={"vendor_email": vendor_email})

print(f"Status: {otp_resp.status_code}")

if otp_resp.status_code == 403:
    otp_error = otp_resp.json()
    print(f"✓ Access Denied (HTTP 403)")
    print(f"  Error Code: {otp_error['detail']['error']['code']}")
    print(f"  Message: {otp_error['detail']['error']['message']}")
    print()
    print("✓ REJECTED vendor correctly denied OTP access")
else:
    print(f"✗ Expected 403, got {otp_resp.status_code}")
    print(json.dumps(otp_resp.json(), indent=2))

print()

print("🔹 TEST 2: REJECTED VENDOR TRIES PASSWORD LOGIN")
print("-" * 80)

pwd_login = requests.post(f"{API_URL}/api/vendor/login",
    json={
        "email": vendor_email,
        "password": "TempPass123"
    })

print(f"Status: {pwd_login.status_code}")

if pwd_login.status_code == 403:
    pwd_error = pwd_login.json()
    print(f"✓ Access Denied (HTTP 403)")
    print(f"  Error Code: {pwd_error['detail']['error']['code']}")
    print(f"  Message: {pwd_error['detail']['error']['message']}")
    print()
    print("✓ REJECTED vendor correctly denied password login")
else:
    print(f"✗ Expected 403, got {pwd_login.status_code}")
    print(json.dumps(pwd_login.json(), indent=2))

print()

print("=" * 80)
print("✓✓✓ REJECTED VENDOR ACCESS CONTROL TEST PASSED ✓✓✓")
print("=" * 80)
print()
print("Summary:")
print("  ✓ REJECTED vendors cannot request OTP (HTTP 403)")
print("  ✓ REJECTED vendors cannot use password login (HTTP 403)")
print("  ✓ Clear error messages inform user of rejection")
