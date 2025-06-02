#!/usr/bin/env python3
"""
Complete academic research workflow test with proper context
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


class CompleteAcademicTest:
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
                print(f"✅ Got new response: {newest_message[:150]}...")
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
            
    def test_complete_workflow(self):
        """Test the complete academic research workflow"""
        print(f"\n{'='*60}")
        print("🔬 Testing Complete Academic Research Workflow")
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
        
        time.sleep(2)
        
        # Test 2: Weather Agent
        print("\n2️⃣ Testing Weather Agent...")
        if self.send_message("What's the weather in New York?"):
            success, response, count = self.wait_for_new_response(self.message_count)
            if success and any(word in response.lower() for word in ["weather", "temperature", "degrees", "new york"]):
                print("✅ Weather Agent: PASSED")
                self.test_results.append(("Weather Agent", True, response[:100]))
                self.message_count = count
            else:
                print("❌ Weather Agent: FAILED")
                self.test_results.append(("Weather Agent", False, "No weather response"))
        
        time.sleep(2)
        
        # Test 3: First, query the existing corpus to get context
        print("\n3️⃣ Getting seminal paper context from corpus...")
        if self.send_message("Can you search the seminal_papers corpus and tell me about the Transformer paper by Vaswani et al?"):
            success, response, count = self.wait_for_new_response(self.message_count)
            if success and "attention is all you need" in response.lower():
                print("✅ RAG Agent: Found transformer paper in corpus")
                self.test_results.append(("RAG Agent - Query Corpus", True, "Found transformer paper"))
                self.message_count = count
            else:
                print("⚠️ RAG Agent: Transformer paper not clearly identified")
                self.test_results.append(("RAG Agent - Query Corpus", False, response[:100] if response else "No response"))
        
        time.sleep(3)
        
        # Test 4: Now search for papers citing it - using the corpus context
        print("\n4️⃣ Testing Academic WebSearch with corpus context...")
        if self.send_message("Now that we have the Transformer paper from the corpus, can you search for recent papers that cite and build upon this work? Focus on papers about large language models."):
            success, response, count = self.wait_for_new_response(self.message_count, timeout=90)
            if success:
                # Check if it's attempting to search or giving meaningful response
                if any(phrase in response.lower() for phrase in [
                    "search", "papers", "citing", "transformer", "language models",
                    "bert", "gpt", "recent", "research", "found"
                ]) and "workflow" not in response.lower():
                    print("✅ Academic WebSearch: Searching for citing papers")
                    self.test_results.append(("Academic WebSearch", True, response[:200]))
                else:
                    print("❌ Academic WebSearch: Still asking for workflow")
                    self.test_results.append(("Academic WebSearch", False, response[:200]))
                self.message_count = count
            else:
                print("❌ Academic WebSearch: No response")
                self.test_results.append(("Academic WebSearch", False, "No response"))
        
        time.sleep(5)
        
        # Test 5: Suggest future research based on the seminal paper
        print("\n5️⃣ Testing Academic NewResearch based on corpus paper...")
        if self.send_message("Given the Transformer architecture from the seminal_papers corpus and its impact on NLP, what are promising future research directions? Consider efficiency, multimodality, and reasoning capabilities."):
            success, response, count = self.wait_for_new_response(self.message_count, timeout=90)
            if success:
                # Check for actual research suggestions
                if any(phrase in response.lower() for phrase in [
                    "efficiency", "multimodal", "reasoning", "research direction",
                    "future", "explore", "investigate", "potential", "promising",
                    "improvement", "advance", "develop", "scale"
                ]) and "workflow" not in response.lower():
                    print("✅ Academic NewResearch: Provided research directions")
                    self.test_results.append(("Academic NewResearch", True, response[:200]))
                else:
                    print("❌ Academic NewResearch: Still asking for workflow")
                    self.test_results.append(("Academic NewResearch", False, response[:200]))
                self.message_count = count
            else:
                print("❌ Academic NewResearch: No response")
                self.test_results.append(("Academic NewResearch", False, "No response"))
        
        time.sleep(3)
        
        # Test 6: Try a more direct approach with the academic agent
        print("\n6️⃣ Testing direct academic research query...")
        if self.send_message("Using the Transformer paper from seminal_papers corpus as the seminal work, analyze recent developments in transformer-based models and suggest research gaps."):
            success, response, count = self.wait_for_new_response(self.message_count, timeout=90)
            if success:
                print(f"Response preview: {response[:300]}...")
                self.test_results.append(("Direct Academic Query", True, response[:200]))
                self.message_count = count
        
        time.sleep(2)
        
    def run_tests(self):
        """Run all tests"""
        print(f"🚀 MAS Frontend Complete Academic Research Test")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Testing full academic workflow with corpus context")
        
        # Setup corpus
        print("\n📚 Setting up seminal paper corpus...")
        result = subprocess.run([sys.executable, "setup_corpus_websocket.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Seminal paper corpus ready")
        else:
            print("⚠️ Corpus setup had issues")
            print(f"Output: {result.stdout}")
        
        # Run UI tests
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
        
        # Run workflow tests
        self.test_complete_workflow()
        
        # Print summary
        print(f"\n{'='*60}")
        print("📊 FINAL TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        for test_name, success, details in self.test_results:
            print(f"{'✅' if success else '❌'} {test_name}")
            if "Academic" in test_name or "Direct" in test_name:
                print(f"   Response: {details}")
        
        print(f"\nTotal: {passed}/{total} tests passed")
        
        # Analysis
        print("\n📋 Academic Agent Analysis:")
        academic_tests = [r for n, s, r in self.test_results if "Academic" in n or "Direct" in n]
        if academic_tests:
            print("The academic agents responded with:")
            for i, response in enumerate(academic_tests, 1):
                print(f"{i}. {response[:150]}...")
        
        # Keep browser open
        print("\n🔍 Browser will remain open for 60 seconds for manual verification...")
        print("Try manually asking about the Transformer paper research directions!")
        time.sleep(60)
        
        print("\nClosing browser...")
        self.driver.quit()


if __name__ == "__main__":
    test = CompleteAcademicTest()
    test.run_tests()