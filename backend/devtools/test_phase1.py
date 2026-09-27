"""
Phase 1 verification script
Tests that the foundation is working correctly
"""
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.database import init_db, get_db_session, Configuration
from app.storage import generate_config_id, validate_filename, validate_file_size

print("=" * 60)
print("PHASE 1 VERIFICATION TEST")
print("=" * 60)

# Test 1: Database initialization
print("\n[Test 1] Database Initialization...")
try:
    init_db()
    print("✓ Database initialized successfully")
except Exception as e:
    print(f"✗ Database initialization failed: {e}")
    sys.exit(1)

# Test 2: Database session
print("\n[Test 2] Database Session...")
try:
    db = get_db_session()
    count = db.query(Configuration).count()
    print(f"✓ Database session working (found {count} configurations)")
    db.close()
except Exception as e:
    print(f"✗ Database session failed: {e}")
    sys.exit(1)

# Test 3: ID generation
print("\n[Test 3] ID Generation...")
try:
    config_id = generate_config_id()
    assert config_id.startswith("CFG-"), "Config ID should start with CFG-"
    print(f"✓ Generated config ID: {config_id}")
except Exception as e:
    print(f"✗ ID generation failed: {e}")
    sys.exit(1)

# Test 4: File validation
print("\n[Test 4] File Validation...")
try:
    assert validate_filename("config.cfg") == True, "Should accept .cfg"
    assert validate_filename("config.conf") == True, "Should accept .conf"
    assert validate_filename("config.txt") == True, "Should accept .txt"
    assert validate_filename("config.json") == True, "Should accept .json"
    assert validate_filename("config.exe") == False, "Should reject .exe"
    assert validate_filename("../etc/passwd") == False, "Should reject path traversal"
    print("✓ Filename validation working correctly")
except Exception as e:
    print(f"✗ Filename validation failed: {e}")
    sys.exit(1)

# Test 5: File size validation
print("\n[Test 5] File Size Validation...")
try:
    assert validate_file_size(1000) == True, "Should accept small files"
    assert validate_file_size(10 * 1024 * 1024) == True, "Should accept 10MB"
    assert validate_file_size(20 * 1024 * 1024) == False, "Should reject >10MB"
    print("✓ File size validation working correctly")
except Exception as e:
    print(f"✗ File size validation failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ ALL PHASE 1 TESTS PASSED!")
print("=" * 60)
print("\nPhase 1 Foundation is ready.")
print("Backend components verified:")
print("  • Database models and initialization")
print("  • File storage utilities")
print("  • ID generation")
print("  • Input validation")
print("\nNext: Run 'python app/main.py' to start the API server")
print("=" * 60)
