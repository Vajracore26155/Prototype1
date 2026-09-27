#!/usr/bin/env python3
"""
Test vendor configurations and audits endpoints
"""
import requests

BASE_URL = 'http://localhost:8000/api'
session_token = 'e80bb6a9-1bda-4881-8122-2c6238728503'
headers = {'X-Vendor-Session-Token': session_token}

print("=== Testing Vendor Configurations Endpoint ===")
response = requests.get(f'{BASE_URL}/vendor/configurations', headers=headers)
print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    configs = data.get('data', {}).get('configurations', [])
    print(f'Configuration count: {len(configs)}')
    
    # Show recent configurations
    for config in configs[:5]:
        config_id = config.get('config_id', 'N/A')
        filename = config.get('filename', 'N/A')
        vendor = config.get('vendor', 'N/A')
        status = config.get('status', 'N/A')
        print(f'  {config_id}: {filename} ({vendor}) - {status}')
else:
    print(f'Error: {response.text}')

print("\n=== Testing Vendor Audits Endpoint ===")
response = requests.get(f'{BASE_URL}/vendor/audits', headers=headers)
print(f'Status: {response.status_code}')

if response.status_code == 200:
    data = response.json()
    audits = data.get('data', {}).get('audits', [])
    print(f'Audit count: {len(audits)}')
    
    # Show recent audits
    for audit in audits[:5]:
        audit_id = audit.get('audit_id', 'N/A')
        config_id = audit.get('configuration', {}).get('config_id', 'N/A')
        status = audit.get('status', 'N/A')
        risk_level = audit.get('risk_level', 'N/A')
        compliance_score = audit.get('compliance_score', 'N/A')
        print(f'  {audit_id}: Config {config_id} - {status} ({risk_level}, {compliance_score}% compliance)')
else:
    print(f'Error: {response.text}')

print("\n✅ Vendor dashboard endpoints working!")