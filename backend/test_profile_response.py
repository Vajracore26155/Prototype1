"""
Test what the profile endpoint actually returns
"""
import requests
import json
import time

base_url = 'http://127.0.0.1:9000/api'

print("Testing Profile Endpoint Response")
print("=" * 70)

# Step 1: Get OTP and session
print("\n1. Getting fresh OTP...")
resp = requests.post(f'{base_url}/vendor/request-otp', json={'vendor_email': 'kingpml42@gmail.com'})
print(f"   Status: {resp.status_code}")

time.sleep(2)

# Step 2: Get fresh OTP again and verify  
print("\n2. Requesting new OTP...")
resp = requests.post(f'{base_url}/vendor/request-otp', json={'vendor_email': 'kingpml42@gmail.com'})
print(f"   Status: {resp.status_code}")

# For testing, let's check what profile data looks like directly in database
import sqlite3
conn = sqlite3.connect('./data/sih26155.db')
cursor = conn.cursor()

print("\n3. Checking vendor record in database...")
cursor.execute("""
    SELECT id, vendor_id, email, username, company_name, contact_name, phone, 
           email_verified, approval_status, password_hash 
    FROM vendor_users 
    WHERE email = 'kingpml42@gmail.com'
""")
result = cursor.fetchone()

if result:
    fields = ['id', 'vendor_id', 'email', 'username', 'company_name', 'contact_name', 
              'phone', 'email_verified', 'approval_status', 'password_hash']
    print(f"   Record found:")
    for i, field in enumerate(fields):
        print(f"     {field}: {result[i]}")
else:
    print("   No record found!")

conn.close()

print("\n" + "=" * 70)
