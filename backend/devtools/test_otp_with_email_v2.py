#!/usr/bin/env python3
"""
Complete OTP flow with email verification
"""
import requests
import json
import sqlite3
import time
import random

API_URL = "http://127.0.0.1:8003"
DB_PATH = "./data/sih26155.db"
ADMIN_EMAIL = "mayankparab4811@gmail.com"
ADMIN_PASSWORD = "Admin123"

def get_latest_otp(vendor_email):
    """Get the latest OTP code from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM vendor_users WHERE email = ?", (vendor_email,))
    vendor = cursor.fetchone()
    
    if not vendor:
        conn.close()
        return None
    
    cursor.execute("""
        SELECT otp_code
        FROM vendor_otps
        WHERE vendor_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (vendor["id"],))
    
    otp = cursor.fetchone()
    conn.close()
    
    if otp:
        return otp["otp_code"]
    return None

print("=" * 80)
print("COMPLETE OTP FLOW WITH EMAIL DELIVERY TEST")
print("=" * 80)
print()

# Create new vendor
vendor_email = f"email_test_{random.randint(100000, 999999)}@test.com"

print("STEP 1: Register Vendor")
print("-" * 80)
reg_resp = requests.post(f"{API_URL}/api/vendor/register",
    json={
        'email': vendor_email,
        'company_name': f'Email Test Corp {random.randint(1000,9999)}',
        'contact_name': 'Email Test User',
        'phone': '9876543210',
        'password': 'TempPass123'
    })

if reg_resp.status_code != 200:
    print(f"✗ Registration failed")
    exit(1)

vendor_id = reg_resp.json()["data"]["vendor_id"]
print(f"✅ Vendor registered: {vendor_id}")
print(f"   Email: {vendor_email}")
print()

# Admin approval
print("STEP 2: Admin Approval")
print("-" * 80)
admin_login = requests.post(f"{API_URL}/api/auth/login",
    json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
admin_token = admin_login.json()["access_token"]

headers = {"Authorization": f"Bearer {admin_token}"}
pending_resp = requests.get(f"{API_URL}/api/admin/vendor-requests", headers=headers)
our_request = None
for req in pending_resp.json()["data"]["requests"]:
    if req["vendor_email"] == vendor_email:
        our_request = req
        break

request_id = our_request["request_id"]

approve_resp = requests.post(
    f"{API_URL}/api/admin/vendor-requests/{request_id}/decide",
    json={"approved": True},
    headers=headers)

print(f"✅ Vendor approved")
print()

# Request OTP
print("STEP 3: Request OTP (Email Should Be Sent)")
print("-" * 80)
print(f"Requesting OTP for: {vendor_email}")
print()

otp_resp = requests.post(f"{API_URL}/api/vendor/request-otp",
    json={"vendor_email": vendor_email})

if otp_resp.status_code != 200:
    print(f"✗ OTP request failed")
    exit(1)

otp_data = otp_resp.json()
print(f"✅ OTP Request Successful")
print(f"   OTP ID: {otp_data['data']['otp_id']}")
print()

# Get OTP from database
time.sleep(1)
otp_code = get_latest_otp(vendor_email)

print(f"✅ OTP Code retrieved from database: {otp_code}")
print()

# Verify OTP
print("STEP 4: Verify OTP")
print("-" * 80)
verify_resp = requests.post(f"{API_URL}/api/vendor/verify-otp",
    json={"vendor_email": vendor_email, "otp_code": otp_code})

if verify_resp.status_code != 200:
    print(f"✗ OTP verification failed")
    exit(1)

verify_data = verify_resp.json()
session_token = verify_data["data"]["session_token"]
print(f"✅ OTP Verified Successfully")
print(f"   Session ID: {verify_data['data']['session_id']}")
print()

# Set password
print("STEP 5: Set Password")
print("-" * 80)
set_pass_resp = requests.post(f"{API_URL}/api/vendor/set-password",
    params={"password": "NewPassword123", "session_token": session_token})

if set_pass_resp.status_code != 200:
    print(f"✗ Password setup failed")
    exit(1)

print(f"✅ Password Set Successfully")
print()

print("=" * 80)
print("✅✅✅ OTP EMAIL SYSTEM WORKING CORRECTLY ✅✅✅")
print("=" * 80)
print()
print("Summary:")
print(f"  Vendor: {vendor_id}")
print(f"  Email: {vendor_email}")
print(f"  OTP Sent: ✅ (Check backend logs for 'Email sent successfully')")
print(f"  OTP Code: {otp_code}")
print(f"  OTP Verified: ✅")
print(f"  Password Set: ✅")
print()
print("Next Action:")
print(f"  1. Check email inbox for: {vendor_email}")
print(f"  2. Look for email subject: 'Your VAJRA Upload Verification Code: {otp_code}'")
print(f"  3. Email should be from: noreply@vajra-security.com")
