#!/usr/bin/env python3
"""
Fix organization assignment for existing configurations
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.database.models import Configuration, Organization, User

def fix_organizations():
    """Assign all configurations to existing organizations"""
    db: Session = SessionLocal()
    
    try:
        # Get all organizations
        orgs = db.query(Organization).all()
        print(f"✓ Found {len(orgs)} organization(s)")
        
        for org in orgs:
            print(f"  - {org.name} (ID: {org.id})")
        
        if not orgs:
            print("❌ No organizations found!")
            return
        
        # Get the first organization (most likely the one users belong to)
        default_org = orgs[0]
        print(f"\n✓ Using organization: {default_org.name} (ID: {default_org.id})")
        
        # Get all configurations without organization
        configs_without_org = db.query(Configuration).filter(
            (Configuration.organization_id == None) | (Configuration.organization_id == 0)
        ).all()
        
        print(f"✓ Found {len(configs_without_org)} configurations without organization")
        
        if configs_without_org:
            # Assign them to the default organization
            for config in configs_without_org:
                config.organization_id = default_org.id
                print(f"  - Assigned {config.config_id} ({config.original_filename}) to {default_org.name}")
            
            db.commit()
            print(f"\n✅ Successfully assigned {len(configs_without_org)} configurations to {default_org.name}")
        else:
            print("\n✓ All configurations already have an organization assigned")
        
        # Verify
        user = db.query(User).first()
        if user:
            user_configs = db.query(Configuration).filter(
                Configuration.organization_id == user.organization_id
            ).all()
            print(f"\n✓ User {user.email} can now access {len(user_configs)} configuration(s)")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Fix Organization Assignment")
    print("=" * 60)
    print()
    fix_organizations()
    print()
