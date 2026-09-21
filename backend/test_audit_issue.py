#!/usr/bin/env python3
"""
Test audit execution to debug the issue
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.database.models import Configuration, User
from app.findings import run_configuration_audit

def test_audit():
    """Test running an audit"""
    db: Session = SessionLocal()
    
    try:
        # Get the first configuration
        config = db.query(Configuration).first()
        
        if not config:
            print("❌ No configurations found in database")
            return
        
        print(f"✓ Found configuration: {config.config_id}")
        print(f"  Filename: {config.original_filename}")
        print(f"  Vendor: {config.vendor}")
        print(f"  Status: {config.status}")
        print(f"  File path: {config.sanitized_path}")
        
        # Check if file exists
        if not os.path.exists(config.sanitized_path):
            print(f"❌ Configuration file not found: {config.sanitized_path}")
            return
        
        print(f"✓ Configuration file exists")
        
        # Try to run audit
        print(f"\n🚀 Running audit...")
        audit = run_configuration_audit(config.config_id)
        
        print(f"\n✅ Audit completed successfully!")
        print(f"  Audit ID: {audit.audit_id}")
        print(f"  Status: {audit.status}")
        print(f"  Compliance Score: {audit.compliance_score}")
        print(f"  Risk Score: {audit.risk_score}")
        print(f"  Risk Level: {audit.risk_level}")
        print(f"  Passed: {audit.passed_count}")
        print(f"  Failed: {audit.failed_count}")
        print(f"  Warnings: {audit.warning_count}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_audit()
