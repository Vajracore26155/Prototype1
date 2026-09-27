import requests
import json

# Get auth token first (assuming admin login)
login_response = requests.post('http://localhost:8000/api/auth/login', json={
    'email': 'mayankparab4811@gmail.com',
    'password': 'admin123'  # Try common password
})

if login_response.status_code == 200:
    token = login_response.json()['access_token']
    
    # Test get vendor requests
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('http://localhost:8000/api/admin/vendor-requests?status=PENDING', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        requests_list = data.get('data', {}).get('requests', [])
        print(f'Pending requests: {len(requests_list)}')
        for req in requests_list:
            company = req.get('company_name', 'N/A')
            contact = req.get('contact_name', 'N/A')
            request_id = req.get('request_id', 'N/A')
            print(f'  {company} ({contact}) - {request_id}')
    else:
        print(f'Error: {response.status_code} - {response.text}')
else:
    print(f'Login failed: {login_response.status_code} - {login_response.text}')