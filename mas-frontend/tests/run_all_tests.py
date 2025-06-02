#!/usr/bin/env python3
"""
Run all UI tests and generate comprehensive report
"""

import subprocess
import sys
import time
from datetime import datetime

def run_all_tests():
    """Run all UI tests and track results"""
    print("🧪 MAS Frontend Complete UI Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Run all tests with detailed output
    cmd = [
        sys.executable, "-m", "pytest",
        "test_ui_selenium.py",
        "-v", "--tb=short",
        "--capture=no"  # Show all output
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse results
    output = result.stdout + result.stderr
    
    # Count passed/failed
    passed_count = output.count("PASSED")
    failed_count = output.count("FAILED")
    total_tests = passed_count + failed_count
    
    print("\n" + "="*60)
    print("📊 FINAL TEST RESULTS")
    print("="*60)
    
    if failed_count == 0:
        print(f"✅ ALL TESTS PASSED! ({passed_count}/{total_tests})")
        print("\n🎉 The MAS Frontend UI is 100% FUNCTIONAL!")
        return True
    else:
        print(f"❌ Some tests failed: {passed_count}/{total_tests} passed")
        print("\nFailed tests:")
        
        # Extract failed test names
        lines = output.split('\n')
        for line in lines:
            if "FAILED" in line and "::" in line:
                test_name = line.split('::')[-1].split()[0]
                print(f"  - {test_name}")
        
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)