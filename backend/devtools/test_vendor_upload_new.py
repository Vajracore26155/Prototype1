#!/usr/bin/env python3
"""
Test vendor file upload with a new unique file
"""
import requests
import sys
import tempfile
import os
import time

BASE_URL = "http://localhost:8000/api"

def test_new_vendor_upload():
    print("=== Testing Vendor File Upload (New File) ===")
    
    session_token = "e80bb6a9-1bda-4881-8122-2c6238728503"
    headers = {"X-Vendor-Session-Token": session_token}
    
    # Create a unique test configuration file
    timestamp = str(int(time.time()))
    test_config = f"""version 15.1
hostname TestDevice-{timestamp}
!
interface GigabitEthernet0/1
 ip address 192.168.2.1 255.255.255.0
 no shutdown
!
router ospf 1
 network 192.168.2.0 0.0.0.255 area 0
!
line con 0
 password cisco123
 login
!
end
! Generated at {timestamp}"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
        f.write(test_config)
        temp_file_path = f.name
    
    try:
        print("1. Uploading new unique configuration file...")
        
        with open(temp_file_path, 'rb') as f:
            files = {
                'file': (f'test_config_{timestamp}.cfg', f, 'text/plain')
            }
            data = {
                'device_id': f'TEST-DEVICE-{timestamp}'
            }
            
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
            print(f"   Success: {upload_data.get('success')}")
            print(f"   Duplicate: {upload_data.get('data', {}).get('duplicate', False)}")
            
            if upload_data.get('success') and not upload_data.get('data', {}).get('duplicate', False):
                config_id = upload_data['data']['config_id']
                print(f"   ✅ New file uploaded! Config ID: {config_id}")
                
                # Test upload history
                print("\n2. Checking upload history...")
                response = requests.get(f"{BASE_URL}/vendor/upload/history", headers=headers)
                
                if response.status_code == 200:
                    history = response.json()
                    uploads = history.get('data', {}).get('uploads', [])
                    print(f"   Upload count: {len(uploads)}")
                    
                    if len(uploads) > 0:
                        print("   Recent uploads:")
                        for upload in uploads[:3]:
                            print(f"     - {upload['config_id']}: {upload['filename']}")
                        print("   ✅ Upload history working!")
                        return True
                    else:
                        print("   ❌ No uploads found in history")
                        return False
                else:
                    print(f"   Error getting history: {response.text}")
                    return False
            else:
                print(f"   ❌ Upload failed or was duplicate")
                return False
        else:
            print(f"   Error: {response.text}")
            return False
    
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

if __name__ == "__main__":
    success = test_new_vendor_upload()
    sys.exit(0 if success else 1)