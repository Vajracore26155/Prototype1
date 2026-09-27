"""
Populate database with existing uploaded files
"""
import os
from pathlib import Path
from datetime import datetime

from app.database import get_db_session, Configuration
from app.storage import UPLOAD_DIR, SANITIZED_DIR, generate_config_id
from app.detection import VendorDetector
from app.security import mask_configuration


def populate_database():
    """Scan uploads directory and add configurations to database"""
    db = get_db_session()
    detector = VendorDetector()
    
    try:
        # Get all uploaded files
        upload_path = Path(UPLOAD_DIR)
        if not upload_path.exists():
            print(f"Upload directory {UPLOAD_DIR} does not exist")
            return
        
        uploaded_files = list(upload_path.glob('*.*'))
        print(f"Found {len(uploaded_files)} uploaded files")
        
        for file_path in uploaded_files:
            # Skip if already in database
            existing = db.query(Configuration).filter(
                Configuration.filename == file_path.name
            ).first()
            
            if existing:
                print(f"Skipping {file_path.name} - already in database")
                continue
            
            print(f"Processing {file_path.name}...")
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                print(f"  Error reading file: {e}")
                continue
            
            # Detect vendor
            vendor_result = detector.detect(content)
            
            # Sanitize content
            masking_result = mask_configuration(content)
            sanitized_content = masking_result.masked_config
            
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
            
            print(f"  ✓ Added {config.config_id} - {config.vendor} ({config.vendor_confidence:.2f})")
        
        print(f"\n✓ Database populated successfully")
        
        # Show summary
        total = db.query(Configuration).count()
        print(f"Total configurations in database: {total}")
        
    except Exception as e:
        print(f"Error populating database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    populate_database()
