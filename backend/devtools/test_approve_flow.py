import requests
import json

API_URL = "http://127.0.0.1:8000"

# Step 1: Admin Login
print("=== Step 1: Admin Login ===")
login_resp = requests.post(f"{API_URL}/api/auth/login",
    json={"email": "mayankparab4811@gmail.com", "password": "Admin123"})
print(f"Status: {login_resp.status_code}")
if login_resp.status_code != 200:
    print(f"Error: {login_resp.text}")
    exit(1)

login_data = login_resp.json()
admin_token = login_data.get("access_token")
print(f"✓ Admin token obtained")

# Step 2: Check pending vendor requests
print("\n=== Step 2: Get Pending Requests ===")
headers = {"Authorization": f"Bearer {admin_token}"}
requests_resp = requests.get(f"{API_URL}/api/admin/vendor-requests",
    headers=headers)
print(f"Status: {requests_resp.status_code}")
print(f"Response: {json.dumps(requests_resp.json(), indent=2)[:500]}")

requests_data = requests_resp.json()
if not requests_data.get("success"):
    print("✗ Failed to get requests")
    exit(1)

pending = requests_data.get("data", {}).get("requests", [])
if not pending:
    print("No pending requests to approve")
    exit(1)

request_id = pending[0]["request_id"]
vendor_id = pending[0]["vendor_id"]
print(f"✓ Found pending request: {request_id} for vendor {vendor_id}")

# Step 3: Approve the vendor
print(f"\n=== Step 3: Approve Vendor (Request ID: {request_id}) ===")
approve_resp = requests.post(
    f"{API_URL}/api/admin/vendor-requests/{request_id}/decide",
    json={"approved": True, "notes": "Approved for testing"},
    headers=headers)
print(f"Status: {approve_resp.status_code}")
print(f"Response: {json.dumps(approve_resp.json(), indent=2)}")

if approve_resp.status_code == 200:
    print("✓ APPROVAL SUCCESSFUL")
else:
    print(f"✗ APPROVAL FAILED")
    print(f"Error details: {approve_resp.text}")
