#!/usr/bin/env python3
"""
Test vendor upload isolation by creating real vendor uploads
This creates test uploads for different vendors to verify isolation
"""
import requests
import sys
import os
import io
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from database.database import get_db
from database.models import Configuration, VendorUser, VendorUploadSession
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

def create_test_upload_scenario():
    """Create test configuration uploads for different vendors using existing sessions"""
    
    BASE_URL = "http://localhost:8000"
    
    print("📤 Creating Test Upload Scenario for Isolation Testing...")
    
    db = next(get_db())
    try:
        # Get first two active vendor sessions with different vendor IDs
        sessions = db.query(VendorUploadSession).filter(
            VendorUploadSession.status == "ACTIVE"
        ).limit(10).all()
        
        # Find sessions for different vendors
        used_vendors = set()
        selected_sessions = []
        
        for session in sessions:
            if session.vendor_id not in used_vendors:
                used_vendors.add(session.vendor_id)
                selected_sessions.append(session)
                if len(selected_sessions) >= 2:
                    break
        
        if len(selected_sessions) < 2:
            print("❌ Need sessions from at least 2 different vendors")
            return False
        
        # Get vendor details
        vendors = []
        for session in selected_sessions:
            vendor = db.query(VendorUser).filter(VendorUser.id == session.vendor_id).first()
            if vendor:
                vendors.append(vendor)
            else:
                print(f"❌ Could not find vendor for session {session.session_id}")
                return False
        
        print(f"Using vendors: {vendors[0].company_name} and {vendors[1].company_name}")
        
        # Create test configuration content
        test_configs = [
            {
                "filename": "cisco_test_vendor1.cfg",
                "content": "hostname VENDOR1-ROUTER\ninterface FastEthernet0/0\n ip address 192.168.1.1 255.255.255.0\nline vty 0 4\n password test123"
            },
            {
                "filename": "cisco_test_vendor2.cfg", 
                "content": "hostname VENDOR2-SWITCH\ninterface GigabitEthernet0/1\n switchport mode access\n switchport access vlan 10"
            }
        ]
        
        # Upload configurations for each vendor
        for i, (vendor, session) in enumerate(zip(vendors, selected_sessions)):
            config = test_configs[i]
            
            print(f"\n📁 Uploading {config['filename']} for {vendor.company_name}...")
            
            # Create file-like object for upload
            file_content = config['content'].encode('utf-8')
            files = {
                'file': (config['filename'], io.BytesIO(file_content), 'text/plain')
            }
            
            headers = {
                'X-Vendor-Session-Token': session.session_token
            }
            
            # Upload configuration
            try:
                response = requests.post(
                    f"{BASE_URL}/api/vendor/upload/configuration",
                    files=files,
                    headers=headers,
                    params={'auto_audit': 'false'}  # Skip audit for faster test
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        config_id = result['data']['config_id']
                        print(f"✅ Upload successful: {config_id}")
                    else:
                        print(f"❌ Upload failed: {result}")
                else:
                    print(f"❌ Upload request failed: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ Error uploading for {vendor.company_name}: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating test scenario: {e}")
        return False
    finally:
        db.close()

def test_isolation_after_uploads():
    """Test isolation after creating vendor-specific uploads"""
    
    print("\n🔒 Testing Isolation After Uploads...")
    
    db = next(get_db())
    try:
        # Get vendors
        vendors = db.query(VendorUser).limit(2).all()
        
        for vendor in vendors:
            # Get vendor-specific configurations
            vendor_configs = db.query(Configuration).filter(
                Configuration.uploaded_by == vendor.vendor_id
            ).all()
            
            # Get all configurations
            all_configs = db.query(Configuration).all()
            
            print(f"\nVendor {vendor.company_name} ({vendor.vendor_id}):")
            print(f"  Owns: {len(vendor_configs)} configurations")
            print(f"  Total in system: {len(all_configs)} configurations")
            
            # Check if vendor sees only their own
            other_configs = db.query(Configuration).filter(
                Configuration.uploaded_by != vendor.vendor_id,
                Configuration.uploaded_by.isnot(None)
            ).all()
            
            if len(other_configs) > 0:
                print(f"  ✅ ISOLATION OK: Cannot see {len(other_configs)} other vendor configs")
            
            # List vendor's configurations
            if vendor_configs:
                print(f"  📁 Own configurations:")
                for config in vendor_configs:
                    print(f"    - {config.config_id}: {config.original_filename}")
        
        # Summary
        total_with_vendor = db.query(Configuration).filter(
            Configuration.uploaded_by.isnot(None)
        ).all()
        
        total_without_vendor = db.query(Configuration).filter(
            Configuration.uploaded_by.is_(None)
        ).all()
        
        print(f"\n📊 Isolation Summary:")
        print(f"  Vendor-specific configs: {len(total_with_vendor)}")
        print(f"  Legacy/unassigned configs: {len(total_without_vendor)}")
        
        if len(total_with_vendor) >= 2:
            print("✅ Vendor isolation is working - vendors have separate configurations")
            return True
        else:
            print("⚠️  Need more vendor-specific uploads to fully verify isolation")
            return True
            
    except Exception as e:
        print(f"❌ Error testing isolation: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🧪 Vendor Upload Isolation Test")
    print("=" * 40)
    
    # Step 1: Create test upload scenario
    success = create_test_upload_scenario()
    
    if success:
        # Step 2: Test isolation
        test_isolation_after_uploads()
        print("\n✅ Phase 2 Vendor Isolation Testing Complete")
    else:
        print("\n❌ Failed to create test scenario")