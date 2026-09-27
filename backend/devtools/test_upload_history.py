#!/usr/bin/env python3
import requests

BASE_URL = 'http://localhost:8000/api'
session_token = 'e80bb6a9-1bda-4881-8122-2c6238728503'
headers = {'X-Vendor-Session-Token': session_token}

response = requests.get(f'{BASE_URL}/vendor/upload/history', headers=headers)
print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    uploads = data.get('data', {}).get('uploads', [])
    print(f'Upload count: {len(uploads)}')
    
    for upload in uploads:
        config_id = upload.get('config_id', 'N/A')
        filename = upload.get('filename', 'N/A')
        status = upload.get('status', 'N/A')
        print(f'  {config_id}: {filename} - {status}')
else:
    print(f'Error: {response.text}')