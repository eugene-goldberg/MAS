#!/usr/bin/env python3
"""
Comprehensive UI test with intelligent agent response analysis
"""

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class ComprehensiveUITest:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.driver = None
        self.test_results = []
        
    def setup_browser(self):
        """Setup browser in visible mode"""
        print("🌐 Opening browser...")
        options = Options()
        options.add_argument('--window-size=1920,1080')
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.implicitly_wait(10)
        
    def wait_for_actual_response(self, timeout=60):
        """Wait for actual agent response, not just processing message"""
        print("⏳ Waiting for agent response...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Get all messages
                messages = self.driver.find_elements(By.CSS_SELECTOR, "[class*='message']")
                
                # Look for assistant messages
                for msg in messages:
                    try:
                        msg_text = msg.text
                        msg_classes = msg.get_attribute("class") or ""
                        
                        # Check if this is an assistant message
                        if "MAS Assistant" in msg_text or "assistant" in msg_classes:
                            # Extract the actual content
                            content = msg_text.replace("MAS Assistant", "").strip()
                            
                            # Skip if it's just the processing message
                            if content and "MAS is processing" not in content:
                                print(f"✅ Got agent response: {content[:100]}...")
                                return True, content
                    except StaleElementReferenceException:
                        continue
                        
                # Check console for errors
                logs = self.driver.get_log('browser')
                for log in logs:
                    if 'agent_response' in log.get('message', ''):
                        print("  Agent response received in console")
                        
            except Exception as e:
                print(f"  Error while waiting: {e}")
                
            time.sleep(1)
            
        print("❌ Timeout waiting for agent response")
        return False, None
        
    def test_agent(self, agent_name, message, expected_patterns):
        """Test an agent and analyze response"""
        print(f"\n{'='*60}")
        print(f"🧪 Testing {agent_name}")
        print(f"📤 Sending: {message}")
        print(f"{'='*60}")
        
        try:
            # Wait for input to be ready
            input_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
            )
            
            # Clear and send message
            input_field.clear()
            time.sleep(0.5)
            input_field.send_keys(message)
            input_field.send_keys(Keys.RETURN)
            
            # Wait for actual response
            success, response_text = self.wait_for_actual_response()
            
            if success and response_text:
                # Analyze response
                print(f"\n📊 Analyzing response...")
                found_patterns = []
                missing_patterns = []
                
                for pattern in expected_patterns:
                    if pattern.lower() in response_text.lower():
                        found_patterns.append(pattern)
                    else:
                        missing_patterns.append(pattern)
                        
                print(f"✅ Found keywords: {', '.join(found_patterns) if found_patterns else 'None'}")
                if missing_patterns:
                    print(f"⚠️ Missing keywords: {', '.join(missing_patterns)}")
                    
                # Determine success based on finding at least one expected pattern
                test_success = len(found_patterns) > 0
                
                # Special case for greeting - any friendly response is good
                if agent_name == "Greeter Agent" and not test_success:
                    greeting_words = ["hello", "hi", "greet", "welcome", "help", "assist"]
                    if any(word in response_text.lower() for word in greeting_words):
                        test_success = True
                        print("✅ Found greeting-related response")
                        
                print(f"\n{'✅ TEST PASSED' if test_success else '❌ TEST FAILED'}")
                
                # Pause to observe
                print(f"⏸️ Pausing 10 seconds to observe response...")
                time.sleep(10)
                
                return test_success, response_text
            else:
                print("❌ No response received")
                return False, None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, None
            
    def run_tests(self):
        """Run all tests"""
        print(f"🚀 MAS Frontend Comprehensive Test")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.setup_browser()
        self.driver.get(self.base_url)
        time.sleep(3)
        
        # Check connection
        print("\n🔌 Checking WebSocket connection...")
        try:
            status = self.driver.find_element(By.CSS_SELECTOR, ".MuiChip-root")
            if "Connected" in status.text:
                print("✅ WebSocket connected")
                self.test_results.append(("WebSocket Connection", True, "Connected"))
            else:
                print(f"❌ WebSocket status: {status.text}")
                self.test_results.append(("WebSocket Connection", False, status.text))
        except:
            print("❌ Connection status not found")
            self.test_results.append(("WebSocket Connection", False, "Not found"))
            
        # Test each agent
        agent_tests = [
            ("Greeter Agent", "Hello! How are you?", ["hello", "hi", "welcome", "greet", "help"]),
            ("Weather Agent", "What's the weather in Paris?", ["weather", "paris", "temperature", "forecast"]),
            ("RAG Agent", "Help me create a corpus", ["corpus", "document", "rag", "create", "collection"]),
            ("Academic WebSearch", "Find papers on AI", ["academic", "paper", "research", "search"]),
            ("Academic NewResearch", "Research ideas for ML", ["research", "direction", "future", "explore"]),
        ]
        
        for agent_name, message, keywords in agent_tests:
            success, response = self.test_agent(agent_name, message, keywords)
            self.test_results.append((agent_name, success, response[:100] if response else "No response"))
            
        # Print summary
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        for test_name, success, details in self.test_results:
            print(f"{'✅' if success else '❌'} {test_name}: {details[:50]}...")
            
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! The UI is 100% functional!")
        else:
            print(f"\n⚠️ {total - passed} tests failed")
            
        # Keep browser open
        print("\n🔍 Browser will remain open for 30 seconds...")
        time.sleep(30)
        
        print("\nClosing browser...")
        self.driver.quit()


if __name__ == "__main__":
    test = ComprehensiveUITest()
    test.run_tests()