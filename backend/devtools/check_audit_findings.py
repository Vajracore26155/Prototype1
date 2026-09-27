#!/usr/bin/env python3
"""
Check what's actually stored in the audit and findings tables
"""
from app.database import get_db_session, Audit, Finding, Configuration

def check_audit_data():
    print("=== Checking Audit Data in Database ===")
    
    with get_db_session() as db:
        # Check recent audits
        audits = db.query(Audit).order_by(Audit.started_at.desc()).limit(5).all()
        
        print(f"Found {len(audits)} recent audits:")
        
        for audit in audits:
            print(f"\nAudit: {audit.audit_id}")
            print(f"  Status: {audit.status}")
            print(f"  Risk Level: {audit.risk_level}")
            print(f"  Compliance: {audit.compliance_score}%")
            print(f"  Passed: {audit.passed_count}")
            print(f"  Failed: {audit.failed_count}")
            print(f"  Warnings: {audit.warning_count}")
            print(f"  Started: {audit.started_at}")
            print(f"  Completed: {audit.completed_at}")
            
            # Get configuration
            config = db.query(Configuration).filter(Configuration.id == audit.configuration_id).first()
            if config:
                print(f"  Config: {config.config_id} - {config.original_filename}")
                print(f"  Vendor: {config.vendor}")
            
            # Check findings for this audit
            findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
            print(f"  Findings in DB: {len(findings)}")
            
            if findings:
                for i, finding in enumerate(findings[:3]):  # Show first 3
                    print(f"    {i+1}. {finding.severity}: {finding.title}")
                    print(f"       Status: {finding.status}")
                    print(f"       Rule: {finding.rule_id}")
                    print(f"       Description: {finding.description[:100] if finding.description else 'N/A'}...")
            else:
                print("    No findings found in database!")
                
                # This might indicate the audit ran but didn't create findings
                # Let's check if there should be findings by looking at the audit status
                if audit.compliance_score == 0 and audit.failed_count == 0:
                    print("    → This suggests either no rules were applied or all tests passed")
                elif audit.failed_count > 0:
                    print("    → This is strange - audit shows failures but no findings in DB")

if __name__ == "__main__":
    check_audit_data()