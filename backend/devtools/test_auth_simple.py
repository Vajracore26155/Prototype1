#!/usr/bin/env python3
"""Simple auth test"""
import requests

BASE_URL = "http://localhost:8000"

# Register
print("Registering user...")
response = requests.post(f"{BASE_URL}/api/auth/register", json={
    "email": "simple@test.com",
    "username": "simpletest",
    "password": "Test123!",
    "full_name": "Simple Test",
    "organization_name": "Simple Org"
})

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200 or "already exists" in response.text:
    # Login
    print("\nLogging in...")
    response = requests.post(f"{BASE_URL}/api/auth/login", data={
        "username": "simple@test.com",
        "password": "Test123!"
    })
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"✓ Token received: {token[:20]}...")
    else:
        print(f"Response: {response.text}")
