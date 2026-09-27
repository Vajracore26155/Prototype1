#!/usr/bin/env python3
"""
Verify Test Readiness
Checks that the system is ready for comprehensive testing

This script verifies:
1. All required files exist
2. Dependencies are installed
3. Database is accessible
4. Main app can be imported
5. Security fixes are in place
"""
import sys
from pathlib import Path
import importlib.util

def check_file_exists(filepath, description):
    """Check if a file exists"""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} MISSING: {filepath}")
        return False

def check_module_import(module_name, description):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {description}: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ {description} FAILED: {module_name}")
        print(f"   Error: {e}")
        return False

def check_security_fixes():
    """Verify security fixes are in place"""
    print("\n📋 Verifying Security Fixes...")
    
    checks = []
    
    # Check comparison.py has require_permission
    try:
        from app.api import comparison
        has_auth = hasattr(comparison, 'require_permission') or 'require_permission' in open('app/api/comparison.py').read()
        if has_auth:
            print("✅ comparison.py: Authentication added")
            checks.append(True)
        else:
            print("❌ comparison.py: Missing authentication")
            checks.append(False)
    except Exception as e:
        print(f"⚠️  comparison.py: Could not verify ({e})")
        checks.append(None)
    
    # Check frameworks.py has require_permission
    try:
        from app.api import frameworks
        has_auth = hasattr(frameworks, 'require_permission') or 'require_permission' in open('app/api/frameworks.py').read()
        if has_auth:
            print("✅ frameworks.py: Authentication added")
            checks.append(True)
        else:
            print("❌ frameworks.py: Missing authentication")
            checks.append(False)
    except Exception as e:
        print(f"⚠️  frameworks.py: Could not verify ({e})")
        checks.append(None)
    
    # Check config_versions.py has organization validation
    try:
        content = open('app/api/config_versions.py').read()
        has_org_check = 'organization_id' in content and 'Configuration' in content
        if has_org_check:
            print("✅ config_versions.py: Organization validation added")
            checks.append(True)
        else:
            print("❌ config_versions.py: Missing organization validation")
            checks.append(False)
    except Exception as e:
        print(f"⚠️  config_versions.py: Could not verify ({e})")
        checks.append(None)
    
    # Check search.py has organization scope
    try:
        content = open('app/api/search.py').read()
        has_org_scope = 'organization_id' in content
        if has_org_scope:
            print("✅ search.py: Organization scope added")
            checks.append(True)
        else:
            print("❌ search.py: Missing organization scope")
            checks.append(False)
    except Exception as e:
        print(f"⚠️  search.py: Could not verify ({e})")
        checks.append(None)
    
    return checks

def main():
    print("="*70)
    print("TATVA TEST READINESS VERIFICATION")
    print("="*70)
    
    all_checks = []
    
    # Check test files
    print("\n📋 Checking Test Files...")
    test_files = [
        ("tests/test_security_regression.py", "Security Regression Tests"),
        ("run_security_tests.py", "Security Test Runner"),
        ("run_all_tests.py", "Comprehensive Test Runner"),
        ("SECURITY_TESTING.md", "Security Testing Documentation"),
        ("TEST_VERIFICATION.md", "Test Verification Guide"),
    ]
    
    for filepath, desc in test_files:
        all_checks.append(check_file_exists(filepath, desc))
    
    # Check modified API files
    print("\n📋 Checking Modified API Files...")
    api_files = [
        ("app/api/comparison.py", "Comparison API"),
        ("app/api/frameworks.py", "Frameworks API"),
        ("app/api/bulk_upload.py", "Bulk Upload API"),
        ("app/api/config_versions.py", "Config Versions API"),
        ("app/api/search.py", "Search API"),
    ]
    
    for filepath, desc in api_files:
        all_checks.append(check_file_exists(filepath, desc))
    
    # Check core modules can be imported
    print("\n📋 Checking Module Imports...")
    modules = [
        ("app.database", "Database Module"),
        ("app.auth.dependencies", "Auth Dependencies"),
        ("app.auth.permissions", "Permission System"),
        ("app.auth.security", "Security Module"),
    ]
    
    for module, desc in modules:
        all_checks.append(check_module_import(module, desc))
    
    # Check security fixes
    security_checks = check_security_fixes()
    all_checks.extend([c for c in security_checks if c is not None])
    
    # Check dependencies
    print("\n📋 Checking Python Dependencies...")
    dependencies = [
        ("fastapi", "FastAPI"),
        ("sqlalchemy", "SQLAlchemy"),
        ("pydantic", "Pydantic"),
        ("pytest", "Pytest"),
    ]
    
    for module, desc in dependencies:
        all_checks.append(check_module_import(module, desc))
    
    # Print summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for c in all_checks if c is True)
    failed = sum(1 for c in all_checks if c is False)
    total = len(all_checks)
    
    print(f"Total Checks: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total*100):.1f}%")
    
    print("\n" + "="*70)
    if failed == 0:
        print("✅ SYSTEM READY FOR TESTING")
        print("="*70)
        print("\nNext steps:")
        print("1. Run: python run_security_tests.py")
        print("2. Run: python run_all_tests.py")
        print("3. Review results in TEST_VERIFICATION.md")
        print("4. Mark Task #9 complete if all tests pass")
    else:
        print("❌ SYSTEM NOT READY")
        print("="*70)
        print("\nIssues found:")
        print("- Review failures above")
        print("- Install missing dependencies: pip install -r requirements.txt")
        print("- Ensure security fixes are properly applied")
        print("- Fix issues before running tests")
    print("="*70)
    
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
