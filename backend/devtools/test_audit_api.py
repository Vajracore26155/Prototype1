#!/usr/bin/env python3
"""
Test the audit API endpoint with authentication
"""
import requests
import json

# First, try to register a test user
register_url = "http://127.0.0.1:8000/api/auth/register"
register_data = {
    "email": "audit_test@test.com",
    "username": "audit_test",
    "password": "test123",
    "full_name": "Audit Test User",
    "organization_name": "Test Organization"
}

print("📝 Registering test user...")
register_response = requests.post(register_url, json=register_data)

if register_response.status_code == 201:
    print("✅ Registration successful!")
elif register_response.status_code == 400:
    print("ℹ️  User already exists, will try to login...")
else:
    print(f"⚠️  Registration status: {register_response.status_code}")

# Login to get token
login_url = "http://127.0.0.1:8000/api/auth/login"
login_data = {
    "email": "audit_test@test.com",
    "password": "test123"
}

print("\n🔐 Logging in...")
login_response = requests.post(login_url, json=login_data)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
user_email = login_response.json()["email"]
print(f"✅ Login successful! User: {user_email}")
print(f"   Token: {token[:30]}...")

# Get configurations
headers = {"Authorization": f"Bearer {token}"}
configs_url = "http://127.0.0.1:8000/api/configurations"

print("\n📋 Fetching configurations...")
configs_response = requests.get(configs_url, headers=headers)

if configs_response.status_code != 200:
    print(f"❌ Failed to get configurations: {configs_response.status_code}")
    print(configs_response.text)
    exit(1)

configs = configs_response.json()["data"]["configurations"]
print(f"✅ Found {len(configs)} configuration(s)")

if not configs:
    print("❌ No configurations available for this user's organization")
    print("   This is normal for a new user - configurations need to be uploaded first")
    exit(0)

# Try to run audit on first config
config_id = configs[0]["config_id"]
filename = configs[0]["filename"]

print(f"\n🚀 Running audit on: {config_id} ({filename})")
audit_url = f"http://127.0.0.1:8000/api/audits/{config_id}/run"

print(f"   POST {audit_url}")
print(f"   Headers: Authorization: Bearer {token[:20]}...")

audit_response = requests.post(audit_url, headers=headers)

print(f"\n📊 Response Status: {audit_response.status_code}")
print(f"Response Body:")
try:
    print(json.dumps(audit_response.json(), indent=2))
except:
    print(audit_response.text)

if audit_response.status_code == 200:
    print("\n✅ Audit completed successfully!")
    audit_data = audit_response.json()["data"]
    print(f"   Audit ID: {audit_data['audit_id']}")
    print(f"   Status: {audit_data['status']}")
    print(f"   Compliance Score: {audit_data['compliance_score']}")
else:
    print(f"\n❌ Audit failed with status {audit_response.status_code}")

