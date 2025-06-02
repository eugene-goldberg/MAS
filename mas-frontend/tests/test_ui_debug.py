#!/usr/bin/env python3
"""
Debug UI test to check console logs and network activity
"""

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json


class DebugUITest:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.driver = None
        
    def setup_browser(self):
        """Setup browser with debug logging"""
        print("🌐 Opening browser with debug logging...")
        options = Options()
        options.add_argument('--window-size=1920,1080')
        
        # Enable all logging
        options.set_capability('goog:loggingPrefs', {
            'browser': 'ALL',
            'driver': 'ALL',
            'performance': 'ALL'
        })
        
        # Enable network logging
        options.add_argument('--enable-logging')
        options.add_argument('--v=1')
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.implicitly_wait(10)
        
    def check_console_logs(self):
        """Print browser console logs"""
        logs = self.driver.get_log('browser')
        if logs:
            print("\n📋 Browser Console Logs:")
            for log in logs:
                level = log.get('level', 'INFO')
                message = log.get('message', '')
                # Parse out the actual message from Chrome's format
                if '"' in message:
                    try:
                        # Extract the JSON part
                        start = message.find('{')
                        if start > 0:
                            json_str = message[start:]
                            data = json.loads(json_str)
                            message = data.get('message', message)
                    except:
                        pass
                print(f"  [{level}] {message}")
        else:
            print("\n📋 No new console logs")
            
    def check_network_activity(self):
        """Check network activity via performance logs"""
        try:
            logs = self.driver.get_log('performance')
            ws_messages = []
            
            for log in logs:
                message = json.loads(log['message'])
                method = message['message'].get('method', '')
                
                # Look for WebSocket messages
                if 'WebSocket' in method:
                    ws_messages.append(message['message'])
                    
            if ws_messages:
                print("\n🌐 WebSocket Activity:")
                for msg in ws_messages[-10:]:  # Last 10 messages
                    print(f"  {msg.get('method', 'Unknown')}: {msg.get('params', {})}")
        except Exception as e:
            print(f"\n❌ Could not check network activity: {e}")
            
    def test_single_message(self):
        """Test sending a single message and debug the response"""
        print(f"\n🚀 Debug UI Test")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.setup_browser()
        self.driver.get(self.base_url)
        print("\n⏳ Waiting for page to load...")
        time.sleep(3)
        
        # Check initial console logs
        self.check_console_logs()
        
        # Test 1: Check connection
        print("\n🔌 Checking WebSocket connection...")
        try:
            status = self.driver.find_element(By.CSS_SELECTOR, ".MuiChip-root")
            print(f"✅ Connection status: {status.text}")
        except:
            print("❌ Connection status not found")
            
        # Check console after connection
        self.check_console_logs()
        
        # Test 2: Send a simple message
        print("\n📤 Sending test message...")
        try:
            # Wait for input to be ready
            input_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
            )
            
            # Send message
            test_message = "Hello"
            input_field.clear()
            input_field.send_keys(test_message)
            
            print(f"  Typed: '{test_message}'")
            self.check_console_logs()
            
            input_field.send_keys(Keys.RETURN)
            print("  Sent message")
            
            # Wait a bit and check logs
            time.sleep(2)
            self.check_console_logs()
            
            # Wait for any response
            print("\n⏳ Waiting for response...")
            for i in range(30):  # 30 seconds max
                time.sleep(1)
                
                # Check for new messages
                messages = self.driver.find_elements(By.CSS_SELECTOR, "[class*='message']")
                assistant_messages = [
                    msg for msg in messages 
                    if "assistant" in msg.get_attribute("class") or "MAS Assistant" in msg.text
                ]
                
                if len(assistant_messages) > 0:
                    last_msg = assistant_messages[-1].text
                    if "processing" not in last_msg:
                        print(f"\n✅ Got response: {last_msg[:100]}...")
                        break
                        
                if i % 5 == 0:
                    print(f"  Still waiting... ({i}s)")
                    self.check_console_logs()
                    self.check_network_activity()
                    
        except Exception as e:
            print(f"\n❌ Error during test: {e}")
            import traceback
            traceback.print_exc()
            
        # Final console check
        print("\n📋 Final console check:")
        self.check_console_logs()
        
        # Keep browser open for manual inspection
        print("\n🔍 Browser will remain open for 60 seconds for manual inspection...")
        print("Check the browser console (F12) for more details")
        time.sleep(60)
        
        print("\nClosing browser...")
        self.driver.quit()


if __name__ == "__main__":
    test = DebugUITest()
    test.test_single_message()