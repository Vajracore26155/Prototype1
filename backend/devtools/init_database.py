#!/usr/bin/env python3
"""
Initialize database and populate with existing uploaded files

This script should be run:
1. On first setup
2. After database schema changes
3. When database file is missing or corrupted
"""
import os
import sys
from pathlib import Path

# Ensure we're in the backend directory
backend_dir = Path(__file__).parent
os.chdir(backend_dir)

from app.database import init_db, get_db_session, Configuration
from app.storage import UPLOAD_DIR, SANITIZED_DIR, generate_config_id
from app.detection import VendorDetector
from app.security import mask_configuration
from datetime import datetime


def initialize_and_populate():
    """Initialize database and populate with existing files"""
    
    print("=" * 60)
    print("SIH26155 Database Initialization")
    print("=" * 60)
    
    # Step 1: Initialize database schema
    print("\n[1/2] Initializing database schema...")
    try:
        init_db()
        print("✓ Database schema created")
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        return False
    
    # Step 2: Populate with existing files
    print("\n[2/2] Scanning for existing uploaded files...")
    
    db = get_db_session()
    detector = VendorDetector()
    
    try:
        upload_path = Path(UPLOAD_DIR)
        if not upload_path.exists():
            print(f"✓ No uploads directory found - starting fresh")
            return True
        
        uploaded_files = list(upload_path.glob('*.*'))
        
        if not uploaded_files:
            print(f"✓ No existing files to import")
            return True
        
        print(f"Found {len(uploaded_files)} file(s) in uploads directory")
        
        imported_count = 0
        skipped_count = 0
        
        for file_path in uploaded_files:
            # Check if already in database
            existing = db.query(Configuration).filter(
                Configuration.filename == file_path.name
            ).first()
            
            if existing:
                skipped_count += 1
                print(f"  ⊙ {file_path.name} - already in database")
                continue
            
            print(f"  → {file_path.name}...", end=" ")
            
            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Detect vendor
                vendor_result = detector.detect(content)
                
                # Sanitize content
                masking_result = mask_configuration(content)
                sanitized_content = masking_result.sanitized_content
                
                # Save sanitized file
                sanitized_filename = f"{file_path.stem}_sanitized{file_path.suffix}"
                sanitized_path = Path(SANITIZED_DIR) / sanitized_filename
                sanitized_path.write_text(sanitized_content, encoding='utf-8')
                
                # Get file extension
                file_ext = file_path.suffix.upper().replace('.', '')
                
                # Create configuration record
                config = Configuration(
                    config_id=generate_config_id(),
                    filename=file_path.name,
                    original_filename=file_path.name,
                    file_type=file_ext,
                    status="UPLOADED",
                    vendor=vendor_result['vendor'],
                    vendor_confidence=vendor_result['confidence'],
                    storage_path=str(file_path),
                    sanitized_path=str(sanitized_path),
                    created_at=datetime.fromtimestamp(file_path.stat().st_mtime)
                )
                
                db.add(config)
                db.commit()
                db.refresh(config)
                
                imported_count += 1
                print(f"✓ {config.config_id} ({vendor_result['vendor']})")
                
            except Exception as e:
                print(f"✗ Error: {e}")
                db.rollback()
        
        # Summary
        print(f"\n" + "=" * 60)
        print(f"Database initialization complete!")
        print(f"  • Imported: {imported_count} file(s)")
        print(f"  • Skipped:  {skipped_count} file(s)")
        
        total = db.query(Configuration).count()
        print(f"  • Total configurations in database: {total}")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error during population: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = initialize_and_populate()
    sys.exit(0 if success else 1)
