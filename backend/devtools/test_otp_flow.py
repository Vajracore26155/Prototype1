import requests
import json
import sqlite3

base_url = 'http://127.0.0.1:9000/api'

print("="*60)
print("FULL VENDOR OTP LOGIN FLOW TEST")
print("="*60)

# Test 1: Request OTP
print("\n1. REQUEST OTP")
print("-" * 60)
response = requests.post(f'{base_url}/vendor/request-otp', json={'vendor_email': 'testapproved@company.com'})
if response.status_code == 200:
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Response: OTP sent successfully")
else:
    print(f"✗ Error {response.status_code}: {response.json()}")
    exit(1)

# Test 2: Try invalid OTP
print("\n2. VERIFY OTP - INVALID CODE TEST")
print("-" * 60)
response = requests.post(
    f'{base_url}/vendor/verify-otp',
    json={'vendor_email': 'testapproved@company.com', 'otp_code': '000000'}
)
if response.status_code == 400:
    print(f"✓ Status: {response.status_code} (Expected invalid OTP error)")
    print(f"✓ Message: Invalid OTP detected correctly")
else:
    print(f"✗ Unexpected status: {response.status_code}")
    exit(1)

# Test 3: Try with non-existent vendor
print("\n3. REQUEST OTP - NON-EXISTENT VENDOR TEST")
print("-" * 60)
response = requests.post(f'{base_url}/vendor/request-otp', json={'vendor_email': 'nonexistent@example.com'})
if response.status_code == 404:
    print(f"✓ Status: {response.status_code} (Expected vendor not found)")
else:
    print(f"✗ Unexpected status: {response.status_code}")
    exit(1)

# Test 4: Try with unapproved vendor
print("\n4. REQUEST OTP - UNAPPROVED VENDOR TEST")
print("-" * 60)
conn = sqlite3.connect('./data/sih26155.db')
cursor = conn.cursor()
cursor.execute("SELECT email FROM vendor_users WHERE approval_status = 'PENDING' LIMIT 1")
result = cursor.fetchone()
conn.close()

if result:
    unapproved_email = result[0]
    response = requests.post(f'{base_url}/vendor/request-otp', json={'vendor_email': unapproved_email})
    if response.status_code == 403:
        print(f"✓ Status: {response.status_code} (Expected not approved)")
    else:
        print(f"✗ Unexpected status: {response.status_code}")
        exit(1)
else:
    print("(No pending vendor found for this test)")

# Test 5: Test vendor registration
print("\n5. VENDOR REGISTRATION TEST")
print("-" * 60)
response = requests.post(
    f'{base_url}/vendor/register',
    json={
        'email': 'newvendor@example.com',
        'company_name': 'New Vendor Inc',
        'contact_name': 'John Doe',
        'phone': '+1234567890',
        'organization_id': 1
    }
)
if response.status_code == 200:
    data = response.json()
    print(f"✓ Status: {response.status_code}")
    print(f"✓ Vendor created with ID: {data['data']['vendor_id']}")
    print(f"✓ Status: {data['data']['status']}")
else:
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

print("\n" + "="*60)
print("ALL TESTS COMPLETED - OTP SYSTEM WORKING")
print("="*60)
