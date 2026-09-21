import requests
import json
import random

API_URL = "http://127.0.0.1:8000"

# Step 1: Register a fresh vendor
print("=== Step 1: Register Fresh Vendor ===")
email = f"vendor{random.randint(10000,99999)}@test.com"
reg_resp = requests.post(f"{API_URL}/api/vendor/register",
    json={
        'email': email,
        'company_name': f'Test Corp {random.randint(1000,9999)}',
        'contact_name': 'Jane Smith',
        'phone': '9876543210',
        'password': 'VendorPass123'
    })

if reg_resp.status_code != 200:
    print(f"✗ Registration failed: {reg_resp.text}")
    exit(1)

reg_data = reg_resp.json()
vendor_id = reg_data.get("data", {}).get("vendor_id")
print(f"✓ Vendor registered: {email}")
print(f"  Vendor ID: {vendor_id}")

# Step 2: Admin Login
print("\n=== Step 2: Admin Login ===")
login_resp = requests.post(f"{API_URL}/api/auth/login",
    json={"email": "mayankparab4811@gmail.com", "password": "Admin123"})

if login_resp.status_code != 200:
    print(f"✗ Admin login failed")
    exit(1)

login_data = login_resp.json()
admin_token = login_data.get("access_token")
print(f"✓ Admin logged in")

# Step 3: Get pending requests
print("\n=== Step 3: Get Pending Requests ===")
headers = {"Authorization": f"Bearer {admin_token}"}
requests_resp = requests.get(f"{API_URL}/api/admin/vendor-requests",
    headers=headers)

requests_data = requests_resp.json()
pending = requests_data.get("data", {}).get("requests", [])

# Find our newly registered vendor
our_request = None
for req in pending:
    if req["vendor_email"] == email:
        our_request = req
        break

if not our_request:
    print(f"✗ Could not find our vendor in pending requests")
    exit(1)

request_id = our_request["request_id"]
print(f"✓ Found pending request: {request_id}")

# Step 4: Approve the vendor
print(f"\n=== Step 4: Approve Vendor ===")
print("(Check backend logs for approval email)")
approve_resp = requests.post(
    f"{API_URL}/api/admin/vendor-requests/{request_id}/decide",
    json={"approved": True, "notes": "Approved for testing"},
    headers=headers)

if approve_resp.status_code != 200:
    print(f"✗ Approval failed: {approve_resp.text}")
    exit(1)

approve_data = approve_resp.json()
print(f"✓ Vendor approved successfully")
print(f"  Decision: {approve_data['data']['decision']}")
print(f"  Message: {approve_data['data']['message']}")

print("\n✓ TEST COMPLETE - Check backend console for approval email")
