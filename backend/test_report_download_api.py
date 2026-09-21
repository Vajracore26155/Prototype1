#!/usr/bin/env python3
"""
Test the report download API endpoint with authentication
"""
import requests
import json

# Register/Login
register_url = "http://127.0.0.1:8000/api/auth/register"
register_data = {
    "email": "report_test@test.com",
    "username": "report_test",
    "password": "test123",
    "full_name": "Report Test User",
    "organization_name": "Test Org"
}

print("📝 Registering test user...")
register_response = requests.post(register_url, json=register_data)

# Login
login_url = "http://127.0.0.1:8000/api/auth/login"
login_data = {
    "email": "mayankparab4811@gmail.com",
    "password": "Mayank@05"
}

print("🔐 Logging in...")
login_response = requests.post(login_url, json=login_data)

if login_response.status_code != 200:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["access_token"]
print(f"✅ Login successful!")

# Get audits
headers = {"Authorization": f"Bearer {token}"}
audits_url = "http://127.0.0.1:8000/api/audits/list"

print("\n📋 Fetching audits...")
audits_response = requests.get(audits_url, headers=headers, params={"limit": 5})

if audits_response.status_code != 200:
    print(f"⚠️  Failed to get audits: {audits_response.status_code}")
    print(audits_response.text)
    # Try to get from configurations instead
    print("\nTrying to run a new audit...")
    configs_response = requests.get("http://127.0.0.1:8000/api/configurations", headers=headers)
    if configs_response.status_code == 200 and configs_response.json()["data"]["configurations"]:
        config_id = configs_response.json()["data"]["configurations"][0]["config_id"]
        print(f"Running audit on config: {config_id}")
        run_response = requests.post(f"http://127.0.0.1:8000/api/audits/{config_id}/run", headers=headers)
        if run_response.status_code == 200:
            audit_id = run_response.json()["data"]["audit_id"]
            print(f"✅ Audit created: {audit_id}")
        else:
            print(f"❌ Failed to run audit: {run_response.status_code}")
            print(run_response.text)
            exit(1)
    else:
        print("❌ No configurations available")
        exit(1)
else:
    audits = audits_response.json()["data"]["audits"]
    if not audits:
        print("❌ No audits available")
        exit(1)
    audit_id = audits[0]["audit_id"]
    print(f"✅ Found {len(audits)} audit(s)")
    print(f"   Using: {audit_id}")

# Try to download report
print(f"\n📥 Downloading report for audit: {audit_id}")
report_url = f"http://127.0.0.1:8000/api/audits/{audit_id}/report"

print(f"   GET {report_url}")
print(f"   Headers: Authorization: Bearer {token[:20]}...")

report_response = requests.get(report_url, headers=headers)

print(f"\n📊 Response Status: {report_response.status_code}")
print(f"   Content-Type: {report_response.headers.get('content-type')}")
print(f"   Content-Length: {report_response.headers.get('content-length', 'Unknown')}")

if report_response.status_code == 200:
    # Save the PDF
    output_file = f"downloaded_report_{audit_id}.pdf"
    with open(output_file, 'wb') as f:
        f.write(report_response.content)
    
    print(f"\n✅ Report downloaded successfully!")
    print(f"   File size: {len(report_response.content):,} bytes")
    print(f"   Saved to: {output_file}")
else:
    print(f"\n❌ Report download failed!")
    print(f"Response Body:")
    try:
        print(json.dumps(report_response.json(), indent=2))
    except:
        print(report_response.text)
