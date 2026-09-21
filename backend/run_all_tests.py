#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
Runs all tests and verifies Tatva still works after security fixes

This script:
1. Runs existing phase tests (Phase 1-7)
2. Runs security regression tests
3. Runs integration tests
4. Generates summary report

Usage:
    python run_all_tests.py
    python run_all_tests.py --skip-security  # Skip security tests
    python run_all_tests.py --phase 4        # Run specific phase only
"""
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

class TestRunner:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.results = {}
        self.total_passed = 0
        self.total_failed = 0
        self.start_time = datetime.now()
        
    def run_test_suite(self, name, command):
        """Run a test suite and capture results"""
        print(f"\n{'='*70}")
        print(f"Running: {name}")
        print(f"Command: {' '.join(command)}")
        print(f"{'='*70}\n")
        
        result = subprocess.run(
            command,
            cwd=Path(__file__).parent,
            capture_output=not self.verbose,
            text=True
        )
        
        self.results[name] = {
            "passed": result.returncode == 0,
            "return_code": result.returncode
        }
        
        if result.returncode == 0:
            self.total_passed += 1
            print(f"✅ {name}: PASSED")
        else:
            self.total_failed += 1
            print(f"❌ {name}: FAILED (exit code: {result.returncode})")
            if not self.verbose and result.stdout:
                print(f"\nOutput:\n{result.stdout}")
            if result.stderr:
                print(f"\nErrors:\n{result.stderr}")
        
        return result.returncode == 0
    
    def print_summary(self):
        """Print test execution summary"""
        elapsed = datetime.now() - self.start_time
        
        print("\n" + "="*70)
        print("TEST EXECUTION SUMMARY")
        print("="*70)
        print(f"Execution Time: {elapsed.total_seconds():.2f}s")
        print(f"Total Suites: {len(self.results)}")
        print(f"Passed: {self.total_passed}")
        print(f"Failed: {self.total_failed}")
        print("="*70)
        
        print("\nDetailed Results:")
        for name, result in self.results.items():
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"  {status} - {name}")
        
        print("\n" + "="*70)
        if self.total_failed == 0:
            print("🎉 ALL TESTS PASSED!")
            print("="*70)
            print("\n✅ Security fixes verified")
            print("✅ Tatva functionality preserved")
            print("✅ No regressions detected")
            print("\nSystem is ready for vendor onboarding features (Tasks #10-18)")
        else:
            print("⚠️  SOME TESTS FAILED")
            print("="*70)
            print("\n❌ Review failures above")
            print("❌ Fix issues before proceeding")
            print("\nDo NOT proceed with new features until all tests pass!")
        print("="*70)
        
        return self.total_failed == 0


def main():
    parser = argparse.ArgumentParser(description="Run comprehensive test suite")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--skip-security", action="store_true", help="Skip security tests")
    parser.add_argument("--skip-phase", action="store_true", help="Skip phase tests")
    parser.add_argument("--skip-integration", action="store_true", help="Skip integration tests")
    parser.add_argument("--phase", type=int, help="Run specific phase only (1-7)")
    parser.add_argument("--fast", action="store_true", help="Fail fast - stop on first failure")
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    
    print("="*70)
    print("TATVA COMPREHENSIVE TEST SUITE")
    print("Testing security fixes and system functionality")
    print("="*70)
    
    all_passed = True
    
    # Security regression tests (CRITICAL)
    if not args.skip_security:
        print("\n📋 PHASE: SECURITY REGRESSION TESTS")
        passed = runner.run_test_suite(
            "Security Regression Tests",
            ["pytest", "tests/test_security_regression.py", "-v", "--tb=short"]
        )
        if not passed and args.fast:
            print("\n⚠️  Fast fail enabled. Stopping due to security test failure.")
            runner.print_summary()
            sys.exit(1)
        all_passed = all_passed and passed
    
    # Phase tests
    if not args.skip_phase:
        phases = [args.phase] if args.phase else range(1, 8)
        
        for phase in phases:
            test_file = f"test_phase{phase}.py"
            test_path = Path(__file__).parent / test_file
            
            if test_path.exists():
                print(f"\n📋 PHASE {phase} TESTS")
                passed = runner.run_test_suite(
                    f"Phase {phase} Tests",
                    ["python", test_file]
                )
                if not passed and args.fast:
                    print(f"\n⚠️  Fast fail enabled. Stopping due to Phase {phase} failure.")
                    runner.print_summary()
                    sys.exit(1)
                all_passed = all_passed and passed
            else:
                print(f"\n⚠️  Skipping Phase {phase} - {test_file} not found")
        
        # Complete phase tests
        complete_tests = [
            ("test_phase5_complete.py", "Phase 5 Complete"),
            ("test_phase6_complete.py", "Phase 6 Complete"),
        ]
        
        for test_file, name in complete_tests:
            test_path = Path(__file__).parent / test_file
            if test_path.exists() and (not args.phase or args.phase in [5, 6]):
                print(f"\n📋 {name.upper()} TESTS")
                passed = runner.run_test_suite(
                    name,
                    ["python", test_file]
                )
                if not passed and args.fast:
                    print(f"\n⚠️  Fast fail enabled. Stopping due to {name} failure.")
                    runner.print_summary()
                    sys.exit(1)
                all_passed = all_passed and passed
    
    # Integration tests
    if not args.skip_integration:
        integration_tests = [
            ("tests/test_api_integration.py", "API Integration"),
            ("tests/test_auth.py", "Authentication"),
            ("tests/test_compliance_engine.py", "Compliance Engine"),
            ("tests/test_drift_detection.py", "Drift Detection"),
            ("tests/test_adaptive_learning.py", "Adaptive Learning"),
        ]
        
        print("\n📋 INTEGRATION TESTS")
        for test_file, name in integration_tests:
            test_path = Path(__file__).parent / test_file
            if test_path.exists():
                passed = runner.run_test_suite(
                    name,
                    ["pytest", test_file, "-v", "--tb=short"]
                )
                if not passed and args.fast:
                    print(f"\n⚠️  Fast fail enabled. Stopping due to {name} failure.")
                    runner.print_summary()
                    sys.exit(1)
                all_passed = all_passed and passed
    
    # Print summary
    success = runner.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
