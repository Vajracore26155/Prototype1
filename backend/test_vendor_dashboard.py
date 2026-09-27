#!/usr/bin/env python3
"""
Test vendor dashboard functionality and file upload
"""
import requests
import sys
import os

BASE_URL = "http://localhost:8000/api"

def test_vendor_dashboard():
    print("=== Testing Vendor Dashboard Functionality ===")
    
    # Use the session token from previous OTP verification
    session_token = "e80bb6a9-1bda-4881-8122-2c6238728503"
    headers = {"X-Vendor-Session-Token": session_token}
    
    print("1. Testing vendor session info...")
    response = requests.get(f"{BASE_URL}/vendor/upload/session", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    vendor_info = response.json()
    print(f"   Vendor: {vendor_info['data']['vendor']['company']} ({vendor_info['data']['vendor']['contact']})")
    
    print("\n2. Testing vendor upload history...")
    response = requests.get(f"{BASE_URL}/vendor/upload/history", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    history = response.json()
    print(f"   Upload count: {len(history.get('data', {}).get('uploads', []))}")
    
    print("\n3. Testing vendor configurations endpoint...")
    response = requests.get(f"{BASE_URL}/vendor/configurations", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    configs = response.json()
    print(f"   Configuration count: {len(configs.get('data', {}).get('configurations', []))}")
    
    print("\n4. Testing vendor audits endpoint...")
    response = requests.get(f"{BASE_URL}/vendor/audits", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        return False
    
    audits = response.json()
    print(f"   Audit count: {len(audits.get('data', {}).get('audits', []))}")
    
    print("\n✅ Vendor dashboard functionality working!")
    return True

if __name__ == "__main__":
    success = test_vendor_dashboard()
    sys.exit(0 if success else 1)