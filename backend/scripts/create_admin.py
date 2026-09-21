#!/usr/bin/env python3
"""
Create initial admin user for Tatva Security Platform

Usage:
    python scripts/create_admin.py

This script creates a default admin user if no users exist in the database.
For production, change the default password immediately after first login.
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine
from app.database.models import Base, User, Organization
from app.auth.security import get_password_hash
from app.auth.permissions import Role
from datetime import datetime


def create_initial_admin():
    """Create initial admin user and organization"""
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Check if any users exist
        existing_users = db.query(User).count()
        
        if existing_users > 0:
            print("❌ Users already exist in the database.")
            print("   Use the register endpoint to create new users.")
            return False
        
        print("🚀 Creating initial admin user and organization...")
        
        # Create default organization
        org = Organization(
            org_id="ORG-000001",
            name="Tatva Security Platform",
            slug="tatva-security",
            status="ACTIVE",
            created_at=datetime.utcnow()
        )
        db.add(org)
        db.flush()
        
        print(f"✓ Created organization: {org.name} (ID: {org.org_id})")
        
        # Create admin user
        admin_email = "admin@tatva.security"
        admin_password = "admin123"  # Change this in production!
        
        admin_user = User(
            user_id="USR-000001",
            email=admin_email,
            username="admin",
            hashed_password=get_password_hash(admin_password),
            full_name="System Administrator",
            organization_id=org.id,
            role=Role.SUPER_ADMIN.value,
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        db.add(admin_user)
        db.commit()
        
        print(f"✓ Created admin user: {admin_user.full_name}")
        print()
        print("=" * 60)
        print("✅ INITIAL ADMIN USER CREATED SUCCESSFULLY")
        print("=" * 60)
        print()
        print("Login Credentials:")
        print(f"  Email:    {admin_email}")
        print(f"  Password: {admin_password}")
        print()
        print("⚠️  IMPORTANT: Change the default password immediately!")
        print()
        print("Access the application at: http://localhost:5173/login")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {str(e)}")
        return False
        
    finally:
        db.close()


if __name__ == "__main__":
    print()
    print("=" * 60)
    print("Tatva Security Platform - Admin User Setup")
    print("=" * 60)
    print()
    
    success = create_initial_admin()
    
    sys.exit(0 if success else 1)
