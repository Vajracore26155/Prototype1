"""
Get a valid session token for testing
"""
import requests
import json
import time

base_url = 'http://127.0.0.1:9000/api'

# Request OTP
print("Requesting OTP...")
resp = requests.post(f'{base_url}/vendor/request-otp', json={'vendor_email': 'kingpml42@gmail.com'})
print(f"Status: {resp.status_code}")

time.sleep(1)

# Get new OTP
print("\nRequesting fresh OTP...")
resp = requests.post(f'{base_url}/vendor/request-otp', json={'vendor_email': 'kingpml42@gmail.com'})
print(f"Status: {resp.status_code}")

print("\nSaved output to logs. Check backend console for [OTP] line to get the code.")
