#!/usr/bin/env python3
"""
Test vendor file upload functionality
"""
import requests
import sys
import tempfile
import os

BASE_URL = "http://localhost:8000/api"

def test_vendor_upload():
    print("=== Testing Vendor File Upload ===")
    
    # Use the session token from previous OTP verification
    session_token = "e80bb6a9-1bda-4881-8122-2c6238728503"
    headers = {"X-Vendor-Session-Token": session_token}
    
    # Create a test configuration file
    test_config = """version 15.1
hostname TestDevice
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
!
line con 0
 password cisco
 login
!
end"""
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_config)
        temp_file_path = f.name
    
    try:
        print("1. Testing file upload...")
        
        # Test file upload
        with open(temp_file_path, 'rb') as f:
            files = {
                'file': ('test_config.txt', f, 'text/plain')
            }
            data = {
                'device_id': 'TEST-DEVICE-001'
            }
            
            # Remove Content-Type from headers for multipart upload
            upload_headers = {"X-Vendor-Session-Token": session_token}
            
            response = requests.post(
                f"{BASE_URL}/vendor/upload/configuration",
                files=files,
                data=data,
                headers=upload_headers
            )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            upload_data = response.json()
            print(f"   Response: {upload_data}")
            
            if upload_data.get('success'):
                config_id = upload_data['data']['config_id']
                print(f"   ✅ File uploaded successfully! Config ID: {config_id}")
                
                # Test getting upload history after upload
                print("\n2. Checking updated upload history...")
                response = requests.get(f"{BASE_URL}/vendor/upload/history", headers=headers)
                
                if response.status_code == 200:
                    history = response.json()
                    upload_count = len(history.get('data', {}).get('uploads', []))
                    print(f"   Upload count after upload: {upload_count}")
                    
                    if upload_count > 0:
                        print("   ✅ Upload history updated correctly!")
                        return True
                    else:
                        print("   ❌ Upload not reflected in history")
                        return False
                else:
                    print(f"   Error getting history: {response.text}")
                    return False
            else:
                print(f"   ❌ Upload failed: {upload_data}")
                return False
        else:
            print(f"   Error: {response.text}")
            return False
    
    finally:
        # Clean up temp file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    success = test_vendor_upload()
    sys.exit(0 if success else 1)