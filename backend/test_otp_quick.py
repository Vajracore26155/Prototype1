import requests
import json

response = requests.post(
    'http://127.0.0.1:9000/api/vendor/verify-otp',
    json={'vendor_email': 'kingpml42@gmail.com', 'otp_code': '721007'}
)

print(f'Status: {response.status_code}')
data = response.json()
if response.status_code == 200:
    print(f'✓ OTP verified successfully')
    session_token = data["data"]["session_token"]
    print(f'✓ Session token: {session_token}')
    print(f'✓ Vendor ID: {data["data"]["vendor_id"]}')
    
    # Now test getting session info
    print("\n" + "="*60)
    print("Testing authenticated endpoint...")
    response2 = requests.get(
        'http://127.0.0.1:9000/api/vendor/upload/session',
        headers={'X-Vendor-Session-Token': session_token}
    )
    print(f'Status: {response2.status_code}')
    print(json.dumps(response2.json(), indent=2))
else:
    print(f'Error: {data["detail"]["error"]["message"]}')
