#!/usr/bin/env python3
import requests
import json
import sqlite3
import time

API_URL = "http://127.0.0.1:8000"
DB_PATH = "./data/sih26155.db"

def get_latest_otp(vendor_email):
    """Get the latest OTP code from database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get vendor
    cursor.execute("SELECT id FROM vendor_users WHERE email = ?", (vendor_email,))
    vendor = cursor.fetchone()
    
    if not vendor:
        conn.close()
        return None
    
    # Get most recent OTP
    cursor.execute("""
        SELECT otp_code, is_used, expires_at
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

print("=" * 70)
print("COMPLETE VENDOR AUTHENTICATION FLOW TEST")
print("=" * 70)
print()

vendor_email = "vendor97269@test.com"

# Step 1: Request OTP
print("Step 1: REQUEST OTP")
print("-" * 70)
print(f"Vendor Email: {vendor_email}")
print()

otp_resp = requests.post(f"{API_URL}/api/vendor/request-otp",
    json={"vendor_email": vendor_email})

if otp_resp.status_code != 200:
    print(f"✗ Failed: {otp_resp.status_code}")
    print(json.dumps(otp_resp.json(), indent=2))
    exit(1)

otp_data = otp_resp.json()
print(f"✓ OTP requested successfully")
print(f"  OTP ID: {otp_data['data']['otp_id']}")
print(f"  Expires: {otp_data['data']['expires_in_minutes']} minutes")
print()

# Wait a moment for database to be written
time.sleep(0.5)

# Get the OTP code from database
otp_code = get_latest_otp(vendor_email)
if not otp_code:
    print("✗ Could not retrieve OTP from database")
    exit(1)

print(f"✓ Retrieved OTP code from database: {otp_code}")
print()

# Step 2: Verify OTP
print("Step 2: VERIFY OTP")
print("-" * 70)
print(f"OTP Code: {otp_code}")
print()

verify_resp = requests.post(f"{API_URL}/api/vendor/verify-otp",
    json={
        "vendor_email": vendor_email,
        "otp_code": otp_code
    })

if verify_resp.status_code != 200:
    print(f"✗ Failed: {verify_resp.status_code}")
    print(json.dumps(verify_resp.json(), indent=2))
    exit(1)

verify_data = verify_resp.json()
session_token = verify_data["data"]["session_token"]
print(f"✓ OTP verified successfully")
print(f"  Session ID: {verify_data['data']['session_id']}")
print(f"  Session Token: {session_token[:30]}...")
print(f"  Valid For: {verify_data['data']['valid_for_hours']} hours")
print()

# Step 3: Set Password
print("Step 3: SET PASSWORD")
print("-" * 70)
new_password = "VendorSecurePass123"
print(f"New Password: {new_password}")
print()

set_pass_resp = requests.post(f"{API_URL}/api/vendor/set-password",
    params={
        "password": new_password,
        "session_token": session_token
    })

if set_pass_resp.status_code != 200:
    print(f"✗ Failed: {set_pass_resp.status_code}")
    print(json.dumps(set_pass_resp.json(), indent=2))
    exit(1)

set_pass_data = set_pass_resp.json()
print(f"✓ Password set successfully")
print(f"  Message: {set_pass_data['data']['message']}")
print()

# Step 4: Vendor Password Login
print("Step 4: VENDOR PASSWORD LOGIN")
print("-" * 70)
print(f"Email: {vendor_email}")
print(f"Password: {new_password}")
print()

login_resp = requests.post(f"{API_URL}/api/vendor/login",
    json={
        "email": vendor_email,
        "password": new_password
    })

if login_resp.status_code != 200:
    print(f"✗ Failed: {login_resp.status_code}")
    print(json.dumps(login_resp.json(), indent=2))
    exit(1)

login_data = login_resp.json()
print(f"✓ Vendor logged in successfully")
print(f"  Vendor ID: {login_data['data']['vendor_id']}")
print(f"  Vendor Name: {login_data['data']['vendor_name']}")
print(f"  Company: {login_data['data']['company_name']}")
print()

print("=" * 70)
print("✓ COMPLETE FLOW TEST PASSED")
print("=" * 70)
