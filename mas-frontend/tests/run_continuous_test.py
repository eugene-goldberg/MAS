#!/usr/bin/env python3
"""
Run continuous UI test with intelligent response analysis
"""

import subprocess
import sys
import os

# Set PYTHONUNBUFFERED to see output in real-time
os.environ['PYTHONUNBUFFERED'] = '1'

print("🚀 Starting MAS Continuous UI Test")
print("=" * 60)
print("This test will:")
print("1. Keep the browser window open throughout all tests")
print("2. Analyze each agent response for correctness")
print("3. Pause 10 seconds after each agent response")
print("4. Show detailed analysis of each response")
print("=" * 60)
print("\nStarting tests...\n")

# Run the continuous test
cmd = [sys.executable, "test_ui_continuous.py"]
subprocess.run(cmd)