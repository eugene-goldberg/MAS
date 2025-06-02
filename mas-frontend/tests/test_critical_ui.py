#!/usr/bin/env python3
"""
Critical UI tests for MAS Frontend
Tests the most important functionality to verify the UI is 100% functional
"""

import subprocess
import sys
import time
from datetime import datetime

def run_test(test_name):
    """Run a specific test and return result"""
    cmd = [
        sys.executable, "-m", "pytest",
        f"test_ui_selenium.py::MASFrontendUITests::{test_name}",
        "-v", "-s", "--tb=short"
    ]
    
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check if test passed
    passed = "PASSED" in result.stdout and "FAILED" not in result.stdout
    
    # Extract key information
    if passed:
        print(f"✅ {test_name} - PASSED")
    else:
        print(f"❌ {test_name} - FAILED")
        if "AssertionError" in result.stdout:
            # Extract assertion error
            lines = result.stdout.split('\n')
            for i, line in enumerate(lines):
                if "AssertionError" in line:
                    print(f"   Error: {line.strip()}")
                    if i + 1 < len(lines):
                        print(f"   {lines[i+1].strip()}")
    
    return passed

def main():
    """Run critical UI tests"""
    print("🧪 MAS Frontend Critical UI Tests")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    critical_tests = [
        ("test_01_frontend_accessibility", "Frontend is accessible"),
        ("test_02_websocket_connection_status", "WebSocket connects properly"),
        ("test_03_chat_interface_elements", "Chat interface is functional"),
        ("test_04_send_message_functionality", "Messages can be sent"),
        ("test_05_greeter_agent_interaction", "Greeter agent responds"),
        ("test_06_weather_agent_interaction", "Weather agent responds"),
    ]
    
    results = []
    
    for test_name, description in critical_tests:
        print(f"\n📋 {description}")
        passed = run_test(test_name)
        results.append((test_name, description, passed))
        
        if not passed:
            print("\n⚠️  Stopping tests due to failure")
            break
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    total = len(results)
    passed_count = sum(1 for _, _, p in results if p)
    
    for test_name, description, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {description}")
    
    print(f"\nTotal: {passed_count}/{total} tests passed")
    
    if passed_count == len(critical_tests):
        print("\n🎉 All critical tests passed! The UI is 100% functional!")
    else:
        print("\n❌ Some tests failed. Please fix the issues and run again.")
        sys.exit(1)

if __name__ == "__main__":
    main()