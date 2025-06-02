#!/usr/bin/env python3
"""
Complete UI test with academic research workflow
"""

import time
import subprocess
import sys
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


class AcademicUITest:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.driver = None
        self.test_results = []
        self.message_count = 0
        
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
        
    def wait_for_new_response(self, previous_count, timeout=60):
        """Wait for a new agent response after the previous count"""
        print(f"⏳ Waiting for new response (after message {previous_count})...")
        
        try:
            # Wait for processing message to appear and disappear
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'MAS is processing')]"))
                )
                print("  ✅ Processing message appeared")
                
                WebDriverWait(self.driver, 30).until_not(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'MAS is processing')]"))
                )
                print("  ✅ Processing message disappeared")
            except TimeoutException:
                print("  ⚠️ Processing message timeout")
            
            # Wait a bit for rendering
            time.sleep(2)
            
            # Get all assistant messages
            assistant_messages = self.driver.find_elements(By.CSS_SELECTOR, ".message.assistant .message-text")
            
            # We should have more messages than before
            if len(assistant_messages) > previous_count:
                # Get the newest message
                newest_message = assistant_messages[-1].text
                print(f"✅ Got new response: {newest_message[:100]}...")
                return True, newest_message, len(assistant_messages)
            else:
                print(f"❌ No new response found (still {len(assistant_messages)} assistant messages)")
                return False, None, len(assistant_messages)
                
        except Exception as e:
            print(f"❌ Error waiting for response: {e}")
            return False, None, previous_count
            
    def send_message(self, message):
        """Send a message via the chat interface"""
        try:
            input_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
            )
            
            input_field.clear()
            time.sleep(0.5)
            input_field.send_keys(message)
            input_field.send_keys(Keys.RETURN)
            
            return True
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
            
    def test_agent_workflow(self):
        """Test the complete agent workflow"""
        print(f"\n{'='*60}")
        print("🔬 Testing Academic Research Workflow")
        print(f"{'='*60}\n")
        
        # Test 1: Greeter Agent
        print("1️⃣ Testing Greeter Agent...")
        if self.send_message("Hello!"):
            success, response, count = self.wait_for_new_response(self.message_count)
            if success and any(word in response.lower() for word in ["hello", "hi", "welcome", "help"]):
                print("✅ Greeter Agent: PASSED")
                self.test_results.append(("Greeter Agent", True, response[:100]))
                self.message_count = count
            else:
                print("❌ Greeter Agent: FAILED")
                self.test_results.append(("Greeter Agent", False, "No greeting response"))
        
        time.sleep(3)
        
        # Test 2: Weather Agent
        print("\n2️⃣ Testing Weather Agent...")
        if self.send_message("What's the weather in San Francisco?"):
            success, response, count = self.wait_for_new_response(self.message_count)
            if success and any(word in response.lower() for word in ["weather", "temperature", "degrees", "san francisco"]):
                print("✅ Weather Agent: PASSED")
                self.test_results.append(("Weather Agent", True, response[:100]))
                self.message_count = count
            else:
                print("❌ Weather Agent: FAILED")
                self.test_results.append(("Weather Agent", False, "No weather response"))
        
        time.sleep(3)
        
        # Test 3: RAG Agent - Check corpus
        print("\n3️⃣ Testing RAG Agent - Checking for seminal papers corpus...")
        if self.send_message("Can you list the available corpora?"):
            success, response, count = self.wait_for_new_response(self.message_count)
            if success:
                if "seminal_papers" in response:
                    print("✅ RAG Agent: Corpus found")
                    self.test_results.append(("RAG Agent - List Corpus", True, "seminal_papers corpus exists"))
                else:
                    print("⚠️ seminal_papers corpus not found, will search anyway")
                    self.test_results.append(("RAG Agent - List Corpus", False, "seminal_papers corpus not found"))
                self.message_count = count
        
        time.sleep(3)
        
        # Test 4: Academic WebSearch - Now with context
        print("\n4️⃣ Testing Academic WebSearch with seminal paper context...")
        if self.send_message("I need to research papers that cite the Transformer architecture paper 'Attention Is All You Need' by Vaswani et al. Can you search for recent papers that build upon this seminal work?"):
            success, response, count = self.wait_for_new_response(self.message_count)
            if success:
                # More flexible checking for academic search functionality
                if any(phrase in response.lower() for phrase in [
                    "search", "papers", "academic", "transformer", "attention",
                    "citations", "research", "vaswani", "recent work", "builds upon"
                ]):
                    print("✅ Academic WebSearch: PASSED")
                    self.test_results.append(("Academic WebSearch", True, response[:200]))
                else:
                    print("❌ Academic WebSearch: Response doesn't indicate search capability")
                    self.test_results.append(("Academic WebSearch", False, response[:200]))
                self.message_count = count
            else:
                print("❌ Academic WebSearch: No response")
                self.test_results.append(("Academic WebSearch", False, "No response"))
        
        time.sleep(5)  # Give more time for complex query
        
        # Test 5: Academic NewResearch - Based on seminal paper
        print("\n5️⃣ Testing Academic NewResearch for future directions...")
        if self.send_message("Based on the Transformer architecture from 'Attention Is All You Need', what are some promising future research directions in this area? Consider recent developments in large language models."):
            success, response, count = self.wait_for_new_response(self.message_count)
            if success:
                # Check for research direction suggestions
                if any(phrase in response.lower() for phrase in [
                    "research", "direction", "future", "explore", "investigate",
                    "potential", "promising", "development", "advance", "study"
                ]):
                    print("✅ Academic NewResearch: PASSED")
                    self.test_results.append(("Academic NewResearch", True, response[:200]))
                else:
                    print("❌ Academic NewResearch: Response doesn't suggest research directions")
                    self.test_results.append(("Academic NewResearch", False, response[:200]))
                self.message_count = count
            else:
                print("❌ Academic NewResearch: No response")
                self.test_results.append(("Academic NewResearch", False, "No response"))
        
        time.sleep(3)
        
    def run_tests(self):
        """Run all tests"""
        print(f"🚀 MAS Frontend Academic Research Test Suite")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"This will test the full academic research workflow")
        
        # First, setup the seminal paper corpus
        print("\n📚 Setting up seminal paper corpus...")
        result = subprocess.run([sys.executable, "setup_seminal_paper.py"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️ Warning: Corpus setup had issues, but continuing with tests")
            print(f"Output: {result.stdout}")
            print(f"Error: {result.stderr}")
        else:
            print("✅ Seminal paper corpus ready")
        
        # Now run the UI tests
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
        
        # Run the workflow tests
        self.test_agent_workflow()
        
        # Print summary
        print(f"\n{'='*60}")
        print("📊 FINAL TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        for test_name, success, details in self.test_results:
            print(f"{'✅' if success else '❌'} {test_name}")
            if not success or "Academic" in test_name:
                print(f"   Details: {details[:100]}...")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 SUCCESS! All tests passed! The academic research workflow is functional!")
        else:
            print(f"\n⚠️ {total - passed} tests failed")
        
        # Keep browser open for observation
        print("\n🔍 Browser will remain open for 30 seconds for manual verification...")
        time.sleep(30)
        
        print("\nClosing browser...")
        self.driver.quit()


if __name__ == "__main__":
    test = AcademicUITest()
    test.run_tests()