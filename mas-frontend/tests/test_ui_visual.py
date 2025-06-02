#!/usr/bin/env python3
"""
Visual UI test that shows agent responses and pauses for observation
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


class VisualUITest:
    def __init__(self):
        self.base_url = "http://localhost:3000"
        self.driver = None
        
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
        
    def test_agent(self, agent_name, message, expected_keywords):
        """Test an agent and pause to show response"""
        print(f"\n{'='*60}")
        print(f"🧪 Testing {agent_name}")
        print(f"📤 Sending: {message}")
        print(f"{'='*60}")
        
        # Clear and send message
        try:
            # Wait for input field to be ready
            input_field = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
            )
            
            # Clear field and wait a bit
            input_field.clear()
            time.sleep(0.5)
            
            # Send message
            input_field.send_keys(message)
            input_field.send_keys(Keys.RETURN)
            
            # Wait for response
            print("⏳ Waiting for response...")
            
            # Wait for processing message to appear and then disappear
            try:
                # First wait for processing message
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'MAS is processing')]"))
                )
                print("  Processing message appeared...")
                
                # Then wait for it to be replaced by actual response
                # Wait for a message that doesn't contain "processing"
                WebDriverWait(self.driver, 40).until(
                    lambda driver: any(
                        "MAS Assistant" in msg.text and "processing" not in msg.text 
                        for msg in driver.find_elements(By.CSS_SELECTOR, "[class*='message']")
                    )
                )
                print("  Agent response received...")
            except TimeoutException:
                print("  No processing message seen, checking for direct response...")
            
            # Get the response - wait a bit more for full render
            time.sleep(3)
            messages = self.driver.find_elements(By.CSS_SELECTOR, "[class*='message']")
            
            response_text = None
            # Look for the last assistant message that's not the processing message
            for msg in reversed(messages):
                if ("assistant" in msg.get_attribute("class") or "MAS Assistant" in msg.text) and "processing" not in msg.text:
                    response_text = msg.text.replace("MAS Assistant", "").strip()
                    if response_text and response_text != "MAS is processing your request...":
                        break
                    
            if response_text:
                print(f"\n📥 Response received:")
                print(f"{'-'*60}")
                print(response_text[:500] + "..." if len(response_text) > 500 else response_text)
                print(f"{'-'*60}")
                
                # Analyze response
                found_keywords = []
                missing_keywords = []
                
                for keyword in expected_keywords:
                    if keyword.lower() in response_text.lower():
                        found_keywords.append(keyword)
                    else:
                        missing_keywords.append(keyword)
                        
                print(f"\n✅ Found keywords: {', '.join(found_keywords) if found_keywords else 'None'}")
                if missing_keywords:
                    print(f"❌ Missing keywords: {', '.join(missing_keywords)}")
                    
                success = len(found_keywords) > 0
                print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")
                
                # Pause to observe
                print(f"\n⏸️  Pausing 10 seconds to observe {agent_name} response...")
                print("👀 Please check the browser window to see the full response")
                time.sleep(10)
                
                return success
            else:
                print("❌ No response received")
                return False
                
        except TimeoutException:
            print("⏱️ Timeout - no response received within 30 seconds")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False
            
    def run_tests(self):
        """Run all tests sequentially in the same browser"""
        print(f"🚀 MAS Frontend Visual Test Suite")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.setup_browser()
        self.driver.get(self.base_url)
        time.sleep(3)
        
        results = []
        
        # Test 1: Check connection
        print("\n🔌 Checking WebSocket connection...")
        try:
            status = self.driver.find_element(By.CSS_SELECTOR, ".MuiChip-root")
            if "Connected" in status.text:
                print("✅ WebSocket connected")
                results.append(("WebSocket Connection", True))
            else:
                print(f"❌ WebSocket status: {status.text}")
                results.append(("WebSocket Connection", False))
        except:
            print("❌ Connection status not found")
            results.append(("WebSocket Connection", False))
            
        # Test agents
        agent_tests = [
            ("Greeter Agent", "Hello! How are you today?", ["hello", "hi", "welcome", "greet"]),
            ("Weather Agent", "What's the weather in Tokyo?", ["weather", "tokyo", "temperature", "degrees"]),
            ("RAG Agent", "Can you help me create a document corpus?", ["corpus", "document", "rag", "create"]),
            ("Academic WebSearch", "Find papers about transformers", ["academic", "paper", "research", "seminal"]),
            ("Academic NewResearch", "Suggest research directions for NLP", ["research", "direction", "future", "explore"]),
        ]
        
        for agent_name, message, keywords in agent_tests:
            success = self.test_agent(agent_name, message, keywords)
            results.append((agent_name, success))
            
        # Print summary
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        for test_name, success in results:
            print(f"{'✅' if success else '❌'} {test_name}")
            
        print(f"\nTotal: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! The UI is 100% functional!")
        else:
            print(f"\n⚠️ {total - passed} tests failed")
            
        print("\n🔍 Browser will remain open for 30 seconds for manual inspection...")
        print("You can check the browser window to see the current state")
        time.sleep(30)
        
        print("\nClosing browser...")
        self.driver.quit()


if __name__ == "__main__":
    test = VisualUITest()
    test.run_tests()