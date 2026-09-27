import requests
import random

email = f"vendor{random.randint(10000,99999)}@test.com"

resp = requests.post('http://127.0.0.1:8000/api/vendor/register',
    json={
        'email': email,
        'company_name': f'Test Corp {random.randint(1000,9999)}',
        'contact_name': 'John Doe',
        'phone': '9876543210',
        'password': 'VendorPass123'
    },
    timeout=5)

print(f'Status: {resp.status_code}')
if resp.status_code in [200, 201]:
    data = resp.json()
    print(f'✓ VENDOR REGISTRATION SUCCESS')
    print(f'  Email: {email}')
    vendor_id = data.get("data", {}).get("vendor_id")
    print(f'  Vendor ID: {vendor_id}')
else:
    print(f'Response: {resp.text[:300]}')
