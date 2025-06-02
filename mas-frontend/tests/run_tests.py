#!/usr/bin/env python3
"""
Helper script to run MAS Frontend UI tests with proper setup and error handling
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path


def check_chrome_installed():
    """Check if Chrome is installed"""
    try:
        # Try to find Chrome
        if sys.platform == "darwin":  # macOS
            chrome_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Chromium.app/Contents/MacOS/Chromium"
            ]
        elif sys.platform.startswith("linux"):
            chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium"
            ]
        elif sys.platform == "win32":
            chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
            ]
        else:
            chrome_paths = []
            
        for path in chrome_paths:
            if os.path.exists(path):
                print(f"✅ Chrome found at: {path}")
                return True
                
        print("❌ Chrome not found. Please install Google Chrome.")
        return False
        
    except Exception as e:
        print(f"❌ Error checking for Chrome: {e}")
        return False


def check_frontend_running(url="http://localhost:3000", timeout=5):
    """Check if frontend is accessible"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ Frontend is accessible at {url}")
            return True
        else:
            print(f"❌ Frontend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to frontend at {url}")
        print("   Make sure the frontend is running with: npm start")
        return False
    except Exception as e:
        print(f"❌ Error checking frontend: {e}")
        return False


def check_backend_running(url="http://localhost:8000", timeout=5):
    """Check if backend is accessible"""
    try:
        # Try health endpoint or root
        for endpoint in ["/health", "/api/health", "/"]:
            try:
                response = requests.get(f"{url}{endpoint}", timeout=timeout)
                if response.status_code in [200, 404]:  # 404 means server is up but endpoint doesn't exist
                    print(f"✅ Backend appears to be running at {url}")
                    return True
            except:
                continue
                
        print(f"⚠️  Backend may not be running at {url}")
        print("   Make sure the backend is running")
        return True  # Don't fail, as WebSocket might be on different port
        
    except Exception as e:
        print(f"⚠️  Could not verify backend: {e}")
        return True  # Don't fail the test


def install_dependencies():
    """Install required Python packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def run_tests(specific_test=None):
    """Run the Selenium tests"""
    print("\n🚀 Running Selenium UI tests...")
    
    cmd = [sys.executable, "test_ui_selenium.py"]
    if specific_test:
        cmd.append(specific_test)
        
    try:
        result = subprocess.run(cmd, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def main():
    """Main entry point"""
    print("🧪 MAS Frontend UI Test Runner")
    print("=" * 50)
    
    # Change to tests directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check prerequisites
    checks = [
        ("Chrome Browser", check_chrome_installed),
        ("Frontend Service", check_frontend_running),
        ("Backend Service", check_backend_running),
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        if not check_func():
            all_passed = False
            
    if not all_passed:
        print("\n⚠️  Some prerequisites are not met.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            print("Exiting...")
            sys.exit(1)
            
    # Install dependencies if needed
    try:
        import selenium
        print("\n✅ Selenium is already installed")
    except ImportError:
        if not install_dependencies():
            print("❌ Failed to install dependencies")
            sys.exit(1)
            
    # Run tests
    print("\n" + "=" * 50)
    
    # Check if specific test requested
    specific_test = None
    if len(sys.argv) > 1:
        specific_test = sys.argv[1]
        print(f"Running specific test: {specific_test}")
    else:
        print("Running all tests...")
        
    success = run_tests(specific_test)
    
    if success:
        print("\n✅ All tests completed successfully!")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        print("\n💡 Tips for debugging:")
        print("   - Check screenshots in the tests directory")
        print("   - Ensure all services are running properly")
        print("   - Run specific tests to isolate issues")
        print("   - Check browser console for JavaScript errors")
        
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()