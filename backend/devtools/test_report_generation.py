#!/usr/bin/env python3
"""
Test report generation for different vendor audits
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.database.models import Audit, Configuration
from app.api.audit import generate_audit_report

def test_report_generation():
    """Test report generation for various audits"""
    db: Session = SessionLocal()
    
    try:
        # Get all audits
        audits = db.query(Audit).all()
        
        if not audits:
            print("❌ No audits found in database")
            print("   Please run an audit first")
            return
        
        print(f"✓ Found {len(audits)} audit(s) in database\n")
        
        # Test report generation for each audit
        for audit in audits[:5]:  # Test first 5
            config = db.query(Configuration).filter(
                Configuration.id == audit.configuration_id
            ).first()
            
            vendor = config.vendor if config else "Unknown"
            filename = config.original_filename if config else "Unknown"
            
            print(f"Testing report for: {audit.audit_id}")
            print(f"  Configuration: {filename}")
            print(f"  Vendor: {vendor}")
            print(f"  Status: {audit.status}")
            
            try:
                # Try to generate report
                pdf_buffer = generate_audit_report(audit.audit_id, db)
                pdf_size = len(pdf_buffer.getvalue())
                
                print(f"  ✅ Report generated successfully! Size: {pdf_size:,} bytes")
                
                # Save to file for testing
                output_file = f"test_report_{audit.audit_id}_{vendor}.pdf"
                with open(output_file, 'wb') as f:
                    f.write(pdf_buffer.getvalue())
                print(f"  📄 Saved to: {output_file}\n")
                
            except Exception as e:
                print(f"  ❌ Error generating report: {str(e)}")
                import traceback
                traceback.print_exc()
                print()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Test Report Generation for Different Vendors")
    print("=" * 60)
    print()
    test_report_generation()
