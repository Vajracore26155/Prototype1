#!/usr/bin/env python3
"""
Complete Test Suite Runner
Runs all phase tests in sequence to verify the entire system
"""
import subprocess
import sys
from pathlib import Path

def run_test(phase_num: int, test_file: str) -> bool:
    """Run a single test file"""
    print(f"\n{'='*70}")
    print(f"Running Phase {phase_num}: {test_file}")
    print('='*70)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=Path(__file__).parent,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Phase {phase_num} PASSED")
            return True
        else:
            print(f"❌ Phase {phase_num} FAILED")
            return False
    except Exception as e:
        print(f"❌ Phase {phase_num} ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SIH26155 COMPLETE TEST SUITE")
    print("="*70)
    
    tests = [
        (1, "test_phase1.py", "Foundation"),
        (2, "test_phase2.py", "Security & Detection"),
        (3, "test_phase3.py", "Cisco End-to-End"),
        (4, "test_phase4.py", "Fortinet Normalization"),
        (5, "test_phase5.py", "Adaptive AI"),
        (6, "test_phase6.py", "Frontend Integration"),
    ]
    
    results = []
    for phase_num, test_file, description in tests:
        passed = run_test(phase_num, test_file)
        results.append((phase_num, description, passed))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for phase_num, description, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"Phase {phase_num} ({description}): {status}")
    
    passed_count = sum(1 for _, _, p in results if p)
    total_count = len(results)
    
    print("\n" + "="*70)
    if passed_count == total_count:
        print(f"🎉 ALL TESTS PASSED ({passed_count}/{total_count})")
        print("="*70)
        print("\nSIH26155 Prototype: READY FOR DEMO ✅")
        print("\nNext Steps:")
        print("1. Start backend: cd backend && python -m uvicorn app.main:app --reload")
        print("2. Start frontend: cd frontend && npm run dev")
        print("3. Open browser: http://localhost:5173")
        print("4. Upload demo configs from demo_configs/ folder")
        return 0
    else:
        print(f"⚠️  SOME TESTS FAILED ({passed_count}/{total_count} passed)")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
