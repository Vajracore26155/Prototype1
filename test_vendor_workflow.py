#!/usr/bin/env python3
"""
Test script for complete vendor upload workflow
Tests: Login → Upload → Configuration → Audit → Report Download
"""

import requests
import json
import time
import io

# Configuration
BASE_URL = "http://localhost:8000/api"
VENDOR_EMAIL = "kingmp142@gmail.com"  # EnhanceMagic - has password
VENDOR_PASSWORD = "Enhanced@123"  # We'll need to set this

def test_vendor_login():
    """Test vendor password login"""
    print("1. Testing vendor login...")
    
    response = requests.post(f"{BASE_URL}/vendor/login", json={
        "email": VENDOR_EMAIL,
        "password": VENDOR_PASSWORD
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            token = data["data"]["session_token"]
            print(f"✅ Login successful! Session token: {token[:20]}...")
            return token
        else:
            print(f"❌ Login failed: {data.get('error', {}).get('message', 'Unknown error')}")
            return None
    else:
        print(f"❌ Login request failed: {response.status_code}")
        return None

def test_vendor_upload(token):
    """Test vendor file upload"""
    print("\n2. Testing vendor file upload...")
    
    # Create test configuration content
    config_content = """
! Cisco Configuration Test
hostname test-router-vendor
!
interface GigabitEthernet0/0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
enable secret cisco123
username admin password admin123
!
snmp-server community public RO
!
end
"""
    
    files = {
        'file': ('test_cisco_config.cfg', config_content, 'text/plain')
    }
    
    headers = {
        'X-Vendor-Session-Token': token
    }
    
    response = requests.post(f"{BASE_URL}/vendor/upload/configuration", 
                           files=files, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            config_id = data["data"]["config_id"]
            audit_id = data["data"].get("audit", {}).get("audit_id")
            print(f"✅ Upload successful! Config ID: {config_id}")
            if audit_id:
                print(f"✅ Auto-audit completed! Audit ID: {audit_id}")
            return config_id, audit_id
        else:
            print(f"❌ Upload failed: {data.get('error', {}).get('message', 'Unknown error')}")
            return None, None
    else:
        print(f"❌ Upload request failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None, None

def test_get_configurations(token):
    """Test getting vendor configurations"""
    print("\n3. Testing get configurations...")
    
    headers = {
        'X-Vendor-Session-Token': token
    }
    
    response = requests.get(f"{BASE_URL}/vendor/configurations", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            configs = data["data"]["configurations"]
            print(f"✅ Found {len(configs)} configurations")
            for config in configs[:3]:  # Show first 3
                print(f"  - {config['config_id']}: {config['filename']}")
            return configs
        else:
            print(f"❌ Get configurations failed: {data}")
            return []
    else:
        print(f"❌ Get configurations request failed: {response.status_code}")
        return []

def test_get_audits(token):
    """Test getting vendor audits"""
    print("\n4. Testing get audits...")
    
    headers = {
        'X-Vendor-Session-Token': token
    }
    
    response = requests.get(f"{BASE_URL}/vendor/audits", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            audits = data["data"]["audits"]
            print(f"✅ Found {len(audits)} audits")
            for audit in audits[:3]:  # Show first 3
                print(f"  - {audit['audit_id']}: {audit['status']} ({audit['compliance_score']}%)")
            return audits
        else:
            print(f"❌ Get audits failed: {data}")
            return []
    else:
        print(f"❌ Get audits request failed: {response.status_code}")
        return []

def test_run_manual_audit(token, config_id):
    """Test manual audit execution"""
    print(f"\n5. Testing manual audit for config {config_id}...")
    
    headers = {
        'X-Vendor-Session-Token': token
    }
    
    response = requests.post(f"{BASE_URL}/vendor/audit/{config_id}", 
                           json={}, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            audit_id = data["data"]["audit_id"]
            compliance = data["data"]["compliance_score"]
            risk_level = data["data"]["risk_level"]
            print(f"✅ Manual audit successful!")
            print(f"  - Audit ID: {audit_id}")
            print(f"  - Compliance: {compliance}%")
            print(f"  - Risk Level: {risk_level}")
            return audit_id
        else:
            print(f"❌ Manual audit failed: {data.get('error', {}).get('message', 'Unknown error')}")
            return None
    else:
        print(f"❌ Manual audit request failed: {response.status_code}")
        return None

def test_download_report(token, audit_id):
    """Test PDF report download"""
    print(f"\n6. Testing PDF report download for audit {audit_id}...")
    
    headers = {
        'X-Vendor-Session-Token': token
    }
    
    response = requests.get(f"{BASE_URL}/vendor/audit/{audit_id}/report", 
                          headers=headers)
    
    if response.status_code == 200:
        print(f"✅ Report download successful!")
        print(f"  - Content type: {response.headers.get('Content-Type', 'unknown')}")
        print(f"  - Content length: {len(response.content)} bytes")
        
        # Save the PDF for verification
        with open(f"vendor_report_{audit_id}.pdf", "wb") as f:
            f.write(response.content)
        print(f"  - Saved as: vendor_report_{audit_id}.pdf")
        return True
    else:
        print(f"❌ Report download failed: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        return False

def main():
    """Run complete vendor workflow test"""
    print("🚀 Starting Complete Vendor Workflow Test")
    print("=" * 50)
    
    # Step 1: Login
    token = test_vendor_login()
    if not token:
        print("\n❌ Cannot proceed without login token")
        return
    
    # Step 2: Upload file
    config_id, auto_audit_id = test_vendor_upload(token)
    if not config_id:
        print("\n❌ Cannot proceed without successful upload")
        return
    
    # Step 3: Get configurations
    configs = test_get_configurations(token)
    
    # Step 4: Get audits
    audits = test_get_audits(token)
    
    # Step 5: Manual audit (if auto-audit didn't happen)
    manual_audit_id = None
    if not auto_audit_id:
        manual_audit_id = test_run_manual_audit(token, config_id)
    
    # Step 6: Download report
    audit_id_for_report = auto_audit_id or manual_audit_id
    if audit_id_for_report:
        test_download_report(token, audit_id_for_report)
    else:
        print("\n❌ No audit ID available for report download")
    
    print("\n" + "=" * 50)
    print("🎉 Vendor Workflow Test Complete!")
    print(f"✅ Login: {'✓' if token else '✗'}")
    print(f"✅ Upload: {'✓' if config_id else '✗'}")
    print(f"✅ Auto-audit: {'✓' if auto_audit_id else '✗'}")
    print(f"✅ Manual audit: {'✓' if manual_audit_id else 'N/A'}")
    print(f"✅ Report download: {'✓' if (auto_audit_id or manual_audit_id) else '✗'}")

if __name__ == "__main__":
    main()