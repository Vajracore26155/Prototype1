#!/usr/bin/env python3
"""
Test complete OTP verification and session creation
"""
import requests
import sys

BASE_URL = "http://localhost:8000/api"

def test_otp_verification():
    print("=== Testing OTP Verification ===")
    
    vendor_email = "palteena08@gmail.com"
    otp_code = "755074"  # From the backend logs
    
    print(f"1. Verifying OTP for: {vendor_email}")
    print(f"   OTP Code: {otp_code}")
    
    response = requests.post(f"{BASE_URL}/vendor/verify-otp", json={
        "vendor_email": vendor_email,
        "otp_code": otp_code
    })
    
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Response: {data}")
        
        if data.get("success"):
            session_token = data["data"]["session_token"]
            session_id = data["data"]["session_id"]
            vendor_id = data["data"]["vendor_id"]
            
            print(f"\n2. Session created successfully!")
            print(f"   Session ID: {session_id}")
            print(f"   Vendor ID: {vendor_id}")
            print(f"   Token: {session_token[:20]}...")
            
            # Test authenticated endpoint
            print(f"\n3. Testing authenticated endpoint...")
            response2 = requests.get(f"{BASE_URL}/vendor/upload/session", headers={
                "X-Vendor-Session-Token": session_token
            })
            
            print(f"   Status: {response2.status_code}")
            if response2.status_code == 200:
                print(f"   Response: {response2.json()}")
                print(f"\n✅ Complete OTP workflow successful!")
                return True
            else:
                print(f"   Error: {response2.text}")
                return False
        else:
            print("   OTP verification failed")
            return False
    else:
        print(f"   Error: {response.text}")
        return False

if __name__ == "__main__":
    success = test_otp_verification()
    sys.exit(0 if success else 1)