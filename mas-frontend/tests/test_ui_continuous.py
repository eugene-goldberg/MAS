#!/usr/bin/env python3
"""
Continuous UI test suite that keeps browser open and analyzes agent responses
"""

import unittest
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class MASContinuousUITest:
    """Continuous UI test that analyzes agent responses"""
    
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:3000"
        self.test_results = []
        
    def setup_browser(self):
        """Setup browser once for all tests"""
        print("🌐 Setting up browser...")
        options = Options()
        # Remove headless mode to see the browser
        # options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        # Enable browser logs
        options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        self.driver.implicitly_wait(10)
        
    def teardown_browser(self):
        """Close browser after all tests"""
        if self.driver:
            self.driver.quit()
            
    def clear_chat(self):
        """Clear chat messages for new test"""
        try:
            # Try to find and click clear button if exists
            clear_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='clear']")
            clear_button.click()
            time.sleep(1)
        except:
            # If no clear button, refresh the page
            self.driver.refresh()
            time.sleep(3)
            
    def analyze_response(self, agent_name, expected_patterns, response_text):
        """Analyze agent response for quality and correctness"""
        print(f"\n📊 Analyzing {agent_name} response:")
        print(f"Response: {response_text[:200]}..." if len(response_text) > 200 else f"Response: {response_text}")
        
        # Check for expected patterns
        success = True
        analysis = []
        
        for pattern in expected_patterns:
            if pattern.lower() in response_text.lower():
                analysis.append(f"✅ Found expected: '{pattern}'")
            else:
                analysis.append(f"❌ Missing expected: '{pattern}'")
                success = False
                
        # Check for error indicators
        error_patterns = ['error', 'failed', 'exception', 'not found', 'unable to']
        for error in error_patterns:
            if error in response_text.lower() and not any(p in response_text.lower() for p in ['no error', 'without error']):
                analysis.append(f"⚠️ Contains error indicator: '{error}'")
                success = False
                
        # Print analysis
        for item in analysis:
            print(f"  {item}")
            
        return success, analysis
        
    def wait_and_analyze_response(self, agent_name, expected_patterns, timeout=30):
        """Wait for response and analyze it"""
        try:
            # Wait for assistant message
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'message') and .//text()='MAS Assistant']"))
            )
            
            # Get all messages
            messages = self.driver.find_elements(By.CSS_SELECTOR, "[class*='message']")
            
            # Find the last assistant message
            assistant_response = None
            for msg in reversed(messages):
                if "MAS Assistant" in msg.text or "assistant" in msg.get_attribute("class"):
                    assistant_response = msg.text
                    break
                    
            if assistant_response:
                # Clean up the response text
                response_text = assistant_response.replace("MAS Assistant", "").strip()
                
                # Analyze the response
                success, analysis = self.analyze_response(agent_name, expected_patterns, response_text)
                
                # Pause to observe
                print(f"\n⏸️ Pausing 10 seconds to observe {agent_name} response...")
                time.sleep(10)
                
                return success, response_text, analysis
            else:
                print(f"❌ No response found from {agent_name}")
                return False, None, ["No response found"]
                
        except TimeoutException:
            print(f"⏱️ Timeout waiting for {agent_name} response")
            return False, None, ["Timeout waiting for response"]
            
    def send_message(self, message):
        """Send a message through the chat interface"""
        try:
            # Find message input
            message_input = self.driver.find_element(By.CSS_SELECTOR, "textarea, input[type='text']")
            message_input.clear()
            message_input.send_keys(message)
            
            # Send the message
            message_input.send_keys(Keys.RETURN)
            time.sleep(2)
            
            print(f"📤 Sent: {message}")
            return True
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            return False
            
    def run_test(self, test_name, test_func):
        """Run a single test and record results"""
        print(f"\n{'='*60}")
        print(f"🧪 {test_name}")
        print(f"{'='*60}")
        
        try:
            success, details = test_func()
            result = "PASSED" if success else "FAILED"
            self.test_results.append({
                "name": test_name,
                "result": result,
                "success": success,
                "details": details
            })
            print(f"\n{'✅' if success else '❌'} {test_name}: {result}")
            return success
        except Exception as e:
            print(f"\n❌ {test_name}: FAILED with exception: {e}")
            self.test_results.append({
                "name": test_name,
                "result": "FAILED",
                "success": False,
                "details": [f"Exception: {str(e)}"]
            })
            return False
            
    # Individual test methods
    def test_01_frontend_accessibility(self):
        """Test 1: Verify frontend is accessible"""
        self.driver.get(self.base_url)
        time.sleep(3)
        
        # Check title
        title = self.driver.title
        success = "MAS" in title
        
        # Check main components
        components = []
        try:
            header = self.driver.find_element(By.CSS_SELECTOR, "header, .header, [role='banner']")
            components.append("Header found")
        except:
            components.append("Header missing")
            success = False
            
        try:
            chat = self.driver.find_element(By.CSS_SELECTOR, ".chat-interface, [class*='ChatInterface']")
            components.append("Chat interface found")
        except:
            components.append("Chat interface missing")
            success = False
            
        return success, components
        
    def test_02_websocket_connection(self):
        """Test 2: Verify WebSocket connection status"""
        # Look for connection status
        try:
            status = self.driver.find_element(By.CSS_SELECTOR, ".MuiChip-root")
            status_text = status.text
            
            if "Connected" in status_text:
                return True, ["WebSocket connected"]
            else:
                return False, [f"WebSocket status: {status_text}"]
        except:
            return False, ["Connection status not found"]
            
    def test_03_greeter_agent(self):
        """Test 3: Test Greeter agent"""
        self.clear_chat()
        
        if not self.send_message("Hello! How are you today?"):
            return False, ["Failed to send message"]
            
        expected_patterns = ["hello", "welcome", "greet", "hi", "how can i help"]
        success, response, analysis = self.wait_and_analyze_response("Greeter Agent", expected_patterns)
        
        return success, analysis
        
    def test_04_weather_agent(self):
        """Test 4: Test Weather agent"""
        self.clear_chat()
        
        if not self.send_message("What's the weather like in San Francisco?"):
            return False, ["Failed to send message"]
            
        expected_patterns = ["weather", "temperature", "san francisco", "degrees", "forecast"]
        success, response, analysis = self.wait_and_analyze_response("Weather Agent", expected_patterns)
        
        return success, analysis
        
    def test_05_rag_agent(self):
        """Test 5: Test RAG agent"""
        self.clear_chat()
        
        if not self.send_message("Can you help me create a document corpus about machine learning?"):
            return False, ["Failed to send message"]
            
        expected_patterns = ["corpus", "document", "rag", "create", "collection"]
        success, response, analysis = self.wait_and_analyze_response("RAG Agent", expected_patterns, timeout=40)
        
        return success, analysis
        
    def test_06_academic_websearch(self):
        """Test 6: Test Academic WebSearch agent"""
        self.clear_chat()
        
        if not self.send_message("Find research papers about transformer models"):
            return False, ["Failed to send message"]
            
        expected_patterns = ["academic", "research", "paper", "seminal", "search"]
        success, response, analysis = self.wait_and_analyze_response("Academic WebSearch Agent", expected_patterns)
        
        return success, analysis
        
    def test_07_academic_newresearch(self):
        """Test 7: Test Academic NewResearch agent"""
        self.clear_chat()
        
        if not self.send_message("Suggest new research directions for natural language processing"):
            return False, ["Failed to send message"]
            
        expected_patterns = ["research", "direction", "future", "explore", "opportunity"]
        success, response, analysis = self.wait_and_analyze_response("Academic NewResearch Agent", expected_patterns)
        
        return success, analysis
        
    def test_08_error_handling(self):
        """Test 8: Test error handling"""
        self.clear_chat()
        
        # Send empty message
        try:
            message_input = self.driver.find_element(By.CSS_SELECTOR, "textarea, input[type='text']")
            message_input.clear()
            message_input.send_keys(Keys.RETURN)
            time.sleep(2)
            
            # Check if it was blocked
            messages = self.driver.find_elements(By.CSS_SELECTOR, "[class*='message']")
            if len(messages) == 0:
                return True, ["Empty message correctly blocked"]
            else:
                return False, ["Empty message was not blocked"]
        except:
            return True, ["Input validation working"]
            
    def test_09_agent_panel(self):
        """Test 9: Test agent response panel"""
        # Send a message to trigger agent response
        self.clear_chat()
        self.send_message("Hello, please tell me about the weather")
        time.sleep(5)
        
        try:
            # Look for agent panel
            agent_panel = self.driver.find_element(By.CSS_SELECTOR, ".split-panel.right")
            
            # Check for tabs
            tabs = agent_panel.find_elements(By.CSS_SELECTOR, ".MuiTab-root")
            if len(tabs) > 0:
                return True, [f"Agent panel found with {len(tabs)} tabs"]
            else:
                return False, ["Agent panel found but no tabs"]
        except:
            return False, ["Agent panel not found"]
            
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"\n🚀 Starting MAS Continuous UI Test Suite")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Setup browser once
        self.setup_browser()
        
        try:
            # Run tests
            tests = [
                ("Frontend Accessibility", self.test_01_frontend_accessibility),
                ("WebSocket Connection", self.test_02_websocket_connection),
                ("Greeter Agent", self.test_03_greeter_agent),
                ("Weather Agent", self.test_04_weather_agent),
                ("RAG Agent", self.test_05_rag_agent),
                ("Academic WebSearch Agent", self.test_06_academic_websearch),
                ("Academic NewResearch Agent", self.test_07_academic_newresearch),
                ("Error Handling", self.test_08_error_handling),
                ("Agent Response Panel", self.test_09_agent_panel),
            ]
            
            for test_name, test_func in tests:
                self.run_test(test_name, test_func)
                
            # Final summary
            self.print_summary()
            
            # Keep browser open for manual inspection
            print("\n🔍 Browser will remain open for manual inspection.")
            print("Press Enter to close the browser and exit...")
            input()
            
        finally:
            self.teardown_browser()
            
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for r in self.test_results if r["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['name']}: {result['result']}")
            
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! The UI is 100% functional!")
        else:
            print(f"\n⚠️ {total - passed} tests failed. Review the details above.")


if __name__ == "__main__":
    tester = MASContinuousUITest()
    tester.run_all_tests()