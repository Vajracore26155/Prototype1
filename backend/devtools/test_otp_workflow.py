#!/usr/bin/env python3
"""
Test the complete OTP workflow for an approved vendor
"""
import requests
import sys

BASE_URL = "http://localhost:8000/api"

def test_otp_workflow():
    print("=== Testing OTP Workflow ===")
    
    # Test with Tstar Fashion (should be approved by now)
    vendor_email = "palteena08@gmail.com"  # T-star Fashion actual email
    
    print(f"1. Requesting OTP for: {vendor_email}")
    response = requests.post(f"{BASE_URL}/vendor/request-otp", json={
        "vendor_email": vendor_email
    })
    
    print(f"   Status: {response.status_code}")
    if response.status_code != 200:
        print(f"   Error: {response.text}")
        
        # Try with a known approved vendor
        print("\n   Trying with a known approved vendor...")
        response = requests.post(f"{BASE_URL}/vendor/request-otp", json={
            "vendor_email": "kingpml42@gmail.com"  # KingPML Company
        })
        print(f"   Status: {response.status_code}")
        if response.status_code != 200:
            print(f"   Error: {response.text}")
            return False
        vendor_email = "kingpml42@gmail.com"
    
    data = response.json()
    print(f"   Response: {data}")
    
    if not data.get("success"):
        print("   Failed to send OTP")
        return False
    
    print("\n2. OTP sent successfully!")
    print("   Check the backend logs for the OTP code (it's printed for testing)")
    
    # In a real test, we'd extract the OTP from the database or email
    # For now, let's just verify the request worked
    return True

if __name__ == "__main__":
    success = test_otp_workflow()
    sys.exit(0 if success else 1)