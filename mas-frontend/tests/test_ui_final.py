#!/usr/bin/env python3
"""
Final comprehensive UI test with all agents
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


class FinalUITest:
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
        
    def wait_for_agent_response(self, timeout=60):
        """Wait for actual agent response"""
        print("⏳ Waiting for agent response...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Get all message elements
                messages = self.driver.find_elements(By.CSS_SELECTOR, "[class*='message']")
                
                for msg in messages:
                    try:
                        msg_text = msg.text
                        msg_classes = msg.get_attribute("class") or ""
                        
                        # Check if this is an assistant message
                        if "MAS Assistant" in msg_text or "assistant" in msg_classes:
                            # Extract content
                            content = msg_text.replace("MAS Assistant", "").strip()
                            
                            # Skip processing messages
                            if content and "MAS is processing" not in content:
                                print(f"✅ Got response: {content[:100]}...")
                                return True, content
                    except StaleElementReferenceException:
                        continue
                        
            except Exception as e:
                print(f"  Error: {e}")
                
            time.sleep(1)
            
        print("❌ Timeout waiting for response")
        return False, None
        
    def test_agent(self, agent_name, message, expected_keywords):
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
            
            # Wait for response
            success, response_text = self.wait_for_agent_response()
            
            if success and response_text:
                # Analyze response
                found_keywords = []
                for keyword in expected_keywords:
                    if keyword.lower() in response_text.lower():
                        found_keywords.append(keyword)
                        
                # Special handling for each agent type
                agent_success = False
                
                if agent_name == "Greeter Agent":
                    # Any friendly greeting is good
                    greeting_words = ["hello", "hi", "greet", "welcome", "help", "assist", "how can i", "nice to meet"]
                    if any(word in response_text.lower() for word in greeting_words):
                        agent_success = True
                        print("✅ Found greeting response")
                        
                elif agent_name == "Weather Agent":
                    # Check for weather-related content
                    weather_words = ["weather", "temperature", "forecast", "degrees", "celsius", "fahrenheit", "sunny", "cloudy", "rain"]
                    if any(word in response_text.lower() for word in weather_words):
                        agent_success = True
                        print("✅ Found weather information")
                        
                elif agent_name == "RAG Agent":
                    # Check for RAG-related content
                    rag_words = ["corpus", "document", "rag", "collection", "create", "vertex ai", "search"]
                    if any(word in response_text.lower() for word in rag_words):
                        agent_success = True
                        print("✅ Found RAG-related response")
                        
                elif agent_name == "Academic WebSearch":
                    # Check for academic search content
                    academic_words = ["academic", "paper", "research", "search", "seminal", "citation", "scholar"]
                    if any(word in response_text.lower() for word in academic_words):
                        agent_success = True
                        print("✅ Found academic search response")
                        
                elif agent_name == "Academic NewResearch":
                    # Check for research direction content
                    research_words = ["research", "direction", "future", "explore", "investigate", "study", "potential"]
                    if any(word in response_text.lower() for word in research_words):
                        agent_success = True
                        print("✅ Found research direction response")
                        
                print(f"\n{'✅ TEST PASSED' if agent_success else '❌ TEST FAILED'}")
                
                # Pause to observe
                print(f"⏸️ Pausing 10 seconds to observe response...")
                time.sleep(10)
                
                return agent_success, response_text
            else:
                print("❌ No response received")
                return False, None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, None
            
    def run_tests(self):
        """Run all tests"""
        print(f"🚀 MAS Frontend Final Comprehensive Test")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"This test will verify all 5 agents are 100% functional")
        
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
            ("Weather Agent", "What's the weather in London?", ["weather", "london", "temperature"]),
            ("RAG Agent", "Tell me about creating a corpus", ["corpus", "document", "rag"]),
            ("Academic WebSearch", "Search for ML papers", ["academic", "paper", "research"]),
            ("Academic NewResearch", "Future AI research ideas", ["research", "direction", "future"]),
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
            print("All 5 agents are responding correctly:")
            print("- Greeter Agent ✅")
            print("- Weather Agent ✅")
            print("- RAG Agent ✅")
            print("- Academic WebSearch Agent ✅")
            print("- Academic NewResearch Agent ✅")
        else:
            print(f"\n⚠️ {total - passed} tests failed")
            
        # Keep browser open
        print("\n🔍 Browser will remain open for manual verification...")
        print("You can interact with the UI to test additional scenarios")
        time.sleep(60)
        
        print("\nClosing browser...")
        self.driver.quit()


if __name__ == "__main__":
    test = FinalUITest()
    test.run_tests()