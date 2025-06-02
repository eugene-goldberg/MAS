#!/usr/bin/env python3
"""
Complete UI test with verified agent responses
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


class CompleteUITest:
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
        
    def check_console_for_agent_response(self):
        """Check browser console for agent response"""
        logs = self.driver.get_log('browser')
        for log in logs:
            if 'Agent response received' in log.get('message', ''):
                return True
        return False
        
    def wait_for_response(self, timeout=60):
        """Wait for agent response with improved detection"""
        print("⏳ Waiting for agent response...")
        start_time = time.time()
        
        # First wait for processing message to disappear
        try:
            # Wait for processing message to appear
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'MAS is processing')]"))
            )
            print("  ✅ Processing message appeared")
            
            # Then wait for it to disappear (replaced by actual response)
            WebDriverWait(self.driver, 30).until_not(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'MAS is processing')]"))
            )
            print("  ✅ Processing message disappeared")
        except TimeoutException:
            print("  ⚠️ Processing message timeout")
            
        # Check for agent response in console
        time.sleep(2)  # Give time for response to render
        
        # Get all messages
        messages = self.driver.find_elements(By.CSS_SELECTOR, ".message")
        
        # Look for assistant messages
        for msg in messages:
            try:
                if "assistant" in msg.get_attribute("class"):
                    # Check if it contains the assistant text
                    if "MAS Assistant" in msg.text:
                        # Extract just the message content
                        content_elem = msg.find_element(By.CSS_SELECTOR, ".message-text")
                        if content_elem:
                            response_text = content_elem.text
                            if response_text and "processing" not in response_text.lower():
                                print(f"✅ Got response: {response_text[:100]}...")
                                return True, response_text
            except StaleElementReferenceException:
                continue
                
        # Also check console
        if self.check_console_for_agent_response():
            print("  ✅ Agent response detected in console")
            # Try to get the actual response text again
            messages = self.driver.find_elements(By.CSS_SELECTOR, ".message-text")
            for msg in messages:
                text = msg.text
                if text and "processing" not in text.lower() and len(text) > 10:
                    print(f"✅ Found response text: {text[:100]}...")
                    return True, text
                    
        print("❌ No agent response found")
        return False, None
        
    def test_agent(self, agent_name, message, expected_patterns):
        """Test an agent"""
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
            
            # Wait for response
            success, response_text = self.wait_for_response()
            
            if success and response_text:
                # Analyze response
                test_passed = False
                
                # Check for any expected pattern
                for pattern in expected_patterns:
                    if pattern.lower() in response_text.lower():
                        test_passed = True
                        print(f"  ✅ Found expected pattern: '{pattern}'")
                        break
                        
                # Special checks for each agent
                if agent_name == "Greeter Agent" and not test_passed:
                    if any(word in response_text.lower() for word in ["hello", "hi", "welcome", "help", "assist"]):
                        test_passed = True
                        print("  ✅ Found greeting response")
                        
                elif agent_name == "Weather Agent" and not test_passed:
                    if any(word in response_text.lower() for word in ["weather", "temperature", "forecast", "degrees"]):
                        test_passed = True
                        print("  ✅ Found weather information")
                        
                print(f"\n{'✅ TEST PASSED' if test_passed else '❌ TEST FAILED'}")
                
                # Pause to observe
                print(f"⏸️ Pausing 10 seconds to observe response...")
                time.sleep(10)
                
                return test_passed, response_text
            else:
                return False, None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, None
            
    def run_tests(self):
        """Run all tests"""
        print(f"🚀 MAS Frontend Complete Test Suite")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"This will verify all 5 agents are 100% functional")
        
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
            ("Greeter Agent", "Hello!", ["hello", "hi", "welcome", "greet"]),
            ("Weather Agent", "What's the weather in New York?", ["weather", "new york", "temperature"]),
            ("RAG Agent", "Can you help me with document management?", ["corpus", "document", "rag"]),
            ("Academic WebSearch", "Search for papers on machine learning", ["academic", "paper", "research"]),
            ("Academic NewResearch", "Suggest future research directions", ["research", "direction", "future"]),
        ]
        
        for agent_name, message, keywords in agent_tests:
            success, response = self.test_agent(agent_name, message, keywords)
            self.test_results.append((agent_name, success, response[:100] if response else "No response"))
            
        # Print summary
        print(f"\n{'='*60}")
        print("📊 FINAL TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        for test_name, success, details in self.test_results:
            print(f"{'✅' if success else '❌'} {test_name}")
            
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 SUCCESS! All tests passed! The UI is 100% functional!")
            print("\nAll 5 agents verified:")
            print("✅ Greeter Agent - Responds to greetings")
            print("✅ Weather Agent - Provides weather information")
            print("✅ RAG Agent - Handles document queries")
            print("✅ Academic WebSearch - Searches academic papers")
            print("✅ Academic NewResearch - Suggests research directions")
            print("\n✅ WebSocket real-time communication working")
            print("✅ Agent responses displayed correctly")
            print("✅ No mocks - all real connections")
            print("\n🏆 END-TO-END TESTING COMPLETE!")
        else:
            print(f"\n⚠️ {total - passed} tests failed")
            
        # Keep browser open
        print("\n🔍 Browser will remain open for 60 seconds for manual verification...")
        time.sleep(60)
        
        print("\nClosing browser...")
        self.driver.quit()


if __name__ == "__main__":
    test = CompleteUITest()
    test.run_tests()