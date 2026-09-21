#!/usr/bin/env python3
"""
Run Security Regression Tests

This script runs all security regression tests to verify:
1. Unauthenticated endpoints are protected
2. IDOR vulnerabilities are fixed
3. Organization isolation is enforced
4. Search is properly scoped
5. Resource assignment is correct

Usage:
    python run_security_tests.py
    
Options:
    --verbose     Show detailed test output
    --fail-fast   Stop on first failure
    --coverage    Generate coverage report
"""
import sys
import subprocess
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Run security regression tests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fail-fast", "-x", action="store_true", help="Stop on first failure")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--html", action="store_true", help="Generate HTML report")
    
    args = parser.parse_args()
    
    # Build pytest command
    cmd = ["pytest", "tests/test_security_regression.py"]
    
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-v")  # Always verbose for security tests
    
    if args.fail_fast:
        cmd.append("-x")
    
    if args.coverage:
        cmd.extend(["--cov=app", "--cov-report=term-missing"])
        if args.html:
            cmd.append("--cov-report=html")
    
    # Add color and short traceback
    cmd.extend(["--color=yes", "--tb=short"])
    
    print("=" * 70)
    print("SECURITY REGRESSION TEST SUITE")
    print("=" * 70)
    print(f"Running: {' '.join(cmd)}")
    print("=" * 70)
    print()
    
    # Run tests
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    print()
    print("=" * 70)
    if result.returncode == 0:
        print("✅ ALL SECURITY TESTS PASSED")
        print("=" * 70)
        print()
        print("Security verification complete:")
        print("  ✅ Unauthenticated endpoints protected")
        print("  ✅ IDOR vulnerabilities fixed")
        print("  ✅ Organization isolation enforced")
        print("  ✅ Cross-org data access prevented")
        print("  ✅ Resource assignment correct")
    else:
        print("❌ SECURITY TESTS FAILED")
        print("=" * 70)
        print()
        print("CRITICAL: Security vulnerabilities detected or tests incomplete!")
        print("Review failures above and fix before proceeding.")
    print("=" * 70)
    
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
