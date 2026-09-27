#!/usr/bin/env python3
"""
Complete End-to-End Test:
1. Register new vendor
2. Admin approves vendor
3. Vendor requests OTP
4. Vendor verifies OTP
5. Vendor sets password
6. Vendor logs in with password
"""
import requests
import json
import sqlite3
import time
import random

API_URL = "http://127.0.0.1:8000"
DB_PATH = "./data/sih26155.db"
ADMIN_EMAIL = "mayankparab4811@gmail.com"
ADMIN_PASSWORD = "Admin123"

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

print("=" * 80)
print("COMPLETE END-TO-END VENDOR FLOW TEST")
print("=" * 80)
print()

# Generate fresh vendor email
vendor_email = f"e2e_vendor_{random.randint(100000, 999999)}@test.com"
vendor_password = "TempVendorPass123"
new_password = "FinalVendorPass456"

print("🔹 PHASE 1: VENDOR REGISTRATION")
print("-" * 80)
print(f"Vendor Email: {vendor_email}")
print(f"Temp Password: {vendor_password}")
print()

# Step 1: Register vendor
reg_resp = requests.post(f"{API_URL}/api/vendor/register",
    json={
        'email': vendor_email,
        'company_name': f'E2E Test Corp {random.randint(1000,9999)}',
        'contact_name': 'Test Contact',
        'phone': '9876543210',
        'password': vendor_password
    })

if reg_resp.status_code != 200:
    print(f"✗ Registration failed: {reg_resp.status_code}")
    print(json.dumps(reg_resp.json(), indent=2))
    exit(1)

reg_data = reg_resp.json()
vendor_id = reg_data.get("data", {}).get("vendor_id")
print(f"✓ Vendor registered")
print(f"  Vendor ID: {vendor_id}")
print(f"  Status: PENDING (awaiting admin approval)")
print()

print("🔹 PHASE 2: ADMIN APPROVAL")
print("-" * 80)

# Step 2: Admin login
admin_login = requests.post(f"{API_URL}/api/auth/login",
    json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})

if admin_login.status_code != 200:
    print(f"✗ Admin login failed")
    exit(1)

admin_token = admin_login.json()["access_token"]
print(f"✓ Admin logged in")
print()

# Step 3: Get pending requests
headers = {"Authorization": f"Bearer {admin_token}"}
pending_resp = requests.get(f"{API_URL}/api/admin/vendor-requests", headers=headers)
pending_data = pending_resp.json()

# Find our vendor request
our_request = None
for req in pending_data.get("data", {}).get("requests", []):
    if req["vendor_email"] == vendor_email:
        our_request = req
        break

if not our_request:
    print(f"✗ Could not find vendor request")
    exit(1)

request_id = our_request["request_id"]
print(f"✓ Found pending request: {request_id}")
print()

# Step 4: Admin approves vendor
approve_resp = requests.post(
    f"{API_URL}/api/admin/vendor-requests/{request_id}/decide",
    json={"approved": True, "notes": "E2E test approval"},
    headers=headers)

if approve_resp.status_code != 200:
    print(f"✗ Approval failed: {approve_resp.status_code}")
    print(json.dumps(approve_resp.json(), indent=2))
    exit(1)

approve_data = approve_resp.json()
print(f"✓ Vendor approved by admin")
print(f"  Decision: {approve_data['data']['decision']}")
print()

print("🔹 PHASE 3: OTP-BASED LOGIN & PASSWORD SETUP")
print("-" * 80)

# Step 5: Request OTP
otp_resp = requests.post(f"{API_URL}/api/vendor/request-otp",
    json={"vendor_email": vendor_email})

if otp_resp.status_code != 200:
    print(f"✗ OTP request failed: {otp_resp.status_code}")
    print(json.dumps(otp_resp.json(), indent=2))
    exit(1)

otp_data = otp_resp.json()
print(f"✓ OTP requested")
print(f"  OTP ID: {otp_data['data']['otp_id']}")
print(f"  Expires in: {otp_data['data']['expires_in_minutes']} minutes")
print()

# Step 6: Get OTP code from database
time.sleep(0.5)
otp_code = get_latest_otp(vendor_email)
if not otp_code:
    print("✗ Could not retrieve OTP from database")
    exit(1)

print(f"✓ OTP code retrieved: {otp_code}")
print()

# Step 7: Verify OTP
verify_resp = requests.post(f"{API_URL}/api/vendor/verify-otp",
    json={
        "vendor_email": vendor_email,
        "otp_code": otp_code
    })

if verify_resp.status_code != 200:
    print(f"✗ OTP verification failed: {verify_resp.status_code}")
    print(json.dumps(verify_resp.json(), indent=2))
    exit(1)

verify_data = verify_resp.json()
session_token = verify_data["data"]["session_token"]
print(f"✓ OTP verified successfully")
print(f"  Session ID: {verify_data['data']['session_id']}")
print(f"  Session valid for: {verify_data['data']['valid_for_hours']} hours")
print()

# Step 8: Set password
set_pass_resp = requests.post(f"{API_URL}/api/vendor/set-password",
    params={
        "password": new_password,
        "session_token": session_token
    })

if set_pass_resp.status_code != 200:
    print(f"✗ Password setup failed: {set_pass_resp.status_code}")
    print(json.dumps(set_pass_resp.json(), indent=2))
    exit(1)

print(f"✓ Password set successfully")
print(f"  New password: {new_password}")
print()

print("🔹 PHASE 4: SUBSEQUENT LOGIN (PASSWORD)")
print("-" * 80)

# Step 9: Vendor password login
login_resp = requests.post(f"{API_URL}/api/vendor/login",
    json={
        "email": vendor_email,
        "password": new_password
    })

if login_resp.status_code != 200:
    print(f"✗ Password login failed: {login_resp.status_code}")
    print(json.dumps(login_resp.json(), indent=2))
    exit(1)

login_data = login_resp.json()
print(f"✓ Vendor logged in with password")
print(f"  Vendor ID: {login_data['data']['vendor_id']}")
print(f"  Vendor Name: {login_data['data']['vendor_name']}")
print(f"  Company: {login_data['data']['company_name']}")
print(f"  Session valid for: {login_data['data']['valid_for_hours']} hours")
print()

print("=" * 80)
print("✓✓✓ COMPLETE END-TO-END FLOW TEST PASSED ✓✓✓")
print("=" * 80)
print()
print("Summary:")
print("  1. Vendor registration: ✓")
print("  2. Admin approval: ✓")
print("  3. OTP request: ✓")
print("  4. OTP verification: ✓")
print("  5. Password setup: ✓")
print("  6. Subsequent login: ✓")
