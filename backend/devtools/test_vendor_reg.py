import requests
import json

resp = requests.post('http://127.0.0.1:8000/api/vendor/register',
    json={
        'email': 'vendor@test.com',
        'company_name': 'Test Company',
        'contact_name': 'Test Contact',
        'phone': '9876543210',
        'password': 'VendorPass123'
    },
    timeout=5)

print(f'Status: {resp.status_code}')
if resp.status_code in [200, 201]:
    data = resp.json()
    print(f'✓ VENDOR REGISTRATION SUCCESS')
    print(f'  Vendor ID: {data.get("data", {}).get("vendor_id")}')
    print(f'  Message: {data.get("data", {}).get("message")}')
else:
    print(f'Response: {resp.text[:300]}')
