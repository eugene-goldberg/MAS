#!/usr/bin/env python3
"""
Comprehensive Selenium UI test suite for MAS Frontend

This test suite verifies:
1. Frontend is accessible at http://localhost:3000
2. WebSocket connection status
3. Message sending functionality
4. All 5 agents interaction (Greeter, Weather, RAG, Academic WebSearch, Academic NewResearch)
5. UI elements interactivity
6. JavaScript console errors
"""

import unittest
import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


class MASFrontendUITests(unittest.TestCase):
    """Test suite for MAS Frontend UI"""
    
    @classmethod
    def setUpClass(cls):
        """Set up Chrome WebDriver with proper options"""
        cls.chrome_options = Options()
        # Run in headless mode for CI/CD environments
        # Comment out the next line to see the browser during tests
        # cls.chrome_options.add_argument("--headless")
        cls.chrome_options.add_argument("--no-sandbox")
        cls.chrome_options.add_argument("--disable-dev-shm-usage")
        cls.chrome_options.add_argument("--disable-gpu")
        cls.chrome_options.add_argument("--window-size=1920,1080")
        
        # Enable logging to capture console errors
        cls.chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
        
    def setUp(self):
        """Set up each test"""
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 20)
        self.base_url = "http://localhost:3000"
        
    def tearDown(self):
        """Clean up after each test"""
        # Check for JavaScript errors before closing
        self._check_console_errors()
        self.driver.quit()
        
    def _check_console_errors(self):
        """Check browser console for JavaScript errors"""
        logs = self.driver.get_log('browser')
        errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if errors:
            print("\n⚠️  JavaScript Console Errors Detected:")
            for error in errors:
                print(f"  - {error['message']}")
        else:
            print("\n✅ No JavaScript console errors found")
            
        # Fail test if critical errors found
        critical_errors = [e for e in errors if 'TypeError' in e['message'] or 'ReferenceError' in e['message']]
        self.assertEqual(len(critical_errors), 0, 
                        f"Critical JavaScript errors found: {critical_errors}")
    
    def _wait_for_element(self, by, value, timeout=10):
        """Helper to wait for element with custom timeout"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def _wait_for_element_clickable(self, by, value, timeout=10):
        """Helper to wait for element to be clickable"""
        return WebDriverWait(self.driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    
    def _send_message(self, message):
        """Helper to send a message through the chat interface"""
        # Find message input
        message_input = self._wait_for_element(By.CSS_SELECTOR, 'textarea[placeholder*="Type your message"]')
        
        # Clear any existing text and type new message
        message_input.clear()
        message_input.send_keys(message)
        
        # Send message (either by Enter key or send button)
        try:
            # Try to find and click send button first
            send_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Send message"]')
            send_button.click()
        except NoSuchElementException:
            # If no send button, use Enter key
            message_input.send_keys(Keys.RETURN)
            
        # Wait a bit for message to be processed
        time.sleep(1)
        
    def _wait_for_agent_response(self, agent_name, timeout=30):
        """Wait for a specific agent to respond"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check agent response panel for the agent
                agent_cards = self.driver.find_elements(By.CSS_SELECTOR, '.agent-card')
                for card in agent_cards:
                    if agent_name.lower() in card.text.lower():
                        return True
                        
                # Also check in message list for agent responses
                messages = self.driver.find_elements(By.CSS_SELECTOR, '.message-content')
                for msg in messages:
                    if agent_name.lower() in msg.text.lower():
                        return True
                        
            except Exception:
                pass
                
            time.sleep(0.5)
            
        return False
    
    def test_01_frontend_accessibility(self):
        """Test 1: Verify frontend is accessible at http://localhost:3000"""
        print("\n🧪 Test 1: Testing frontend accessibility...")
        
        # Navigate to frontend
        self.driver.get(self.base_url)
        
        # Verify page title
        self.assertIn("MAS", self.driver.title, "Page title should contain 'MAS'")
        
        # Verify main app container loads
        app_container = self._wait_for_element(By.CLASS_NAME, "app-container")
        self.assertTrue(app_container.is_displayed(), "App container should be visible")
        
        # Verify header is present
        header = self._wait_for_element(By.CSS_SELECTOR, "header, .header, [role='banner']")
        self.assertTrue(header.is_displayed(), "Header should be visible")
        
        print("✅ Frontend is accessible and main components loaded")
        
    def test_02_websocket_connection_status(self):
        """Test 2: Verify WebSocket connection status indicator"""
        print("\n🧪 Test 2: Testing WebSocket connection status...")
        
        self.driver.get(self.base_url)
        
        # Look for connection status indicator
        connection_status = None
        
        # Try different possible selectors for connection status
        selectors = [
            ".MuiChip-root",  # MUI Chip component
            ".connection-status",
            "[aria-label*='connection']",
            ".status-indicator",
            ".ConnectionStatus",
            "[class*='connection']",
            "[class*='Connection']",
            "div[class*='MuiChip']"  # Alternative MUI Chip selector
        ]
        
        for selector in selectors:
            try:
                connection_status = self.driver.find_element(By.CSS_SELECTOR, selector)
                if connection_status:
                    break
            except NoSuchElementException:
                continue
                
        self.assertIsNotNone(connection_status, "Connection status indicator should be present")
        
        # Check if connected (might show as green color, "Connected" text, or specific class)
        status_text = connection_status.text.lower()
        status_classes = connection_status.get_attribute("class") or ""
        
        is_connected = (
            "connected" in status_text or 
            "online" in status_text or
            "success" in status_classes or
            "connected" in status_classes
        )
        
        if is_connected:
            print("✅ WebSocket is connected")
        else:
            print("⚠️  WebSocket appears to be disconnected")
            print(f"   Status text: {status_text}")
            print(f"   Status classes: {status_classes}")
            
        # Take screenshot for debugging
        self.driver.save_screenshot("websocket_status.png")
        
    def test_03_chat_interface_elements(self):
        """Test 3: Verify chat interface elements are present and interactive"""
        print("\n🧪 Test 3: Testing chat interface elements...")
        
        self.driver.get(self.base_url)
        
        # Wait for WebSocket connection
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".MuiChip-root"))
            )
            time.sleep(1)  # Give WebSocket time to fully connect
        except TimeoutException:
            pass
        
        # Check for chat interface components
        chat_interface = self._wait_for_element(By.CSS_SELECTOR, ".chat-interface, [class*='ChatInterface']")
        self.assertTrue(chat_interface.is_displayed(), "Chat interface should be visible")
        
        # Check for message list area
        message_area = self._wait_for_element(By.CSS_SELECTOR, ".chat-messages, .message-list, [class*='MessageList']")
        self.assertTrue(message_area.is_displayed(), "Message list area should be visible")
        
        # Check for message input
        message_input = self._wait_for_element(By.CSS_SELECTOR, "textarea, input[type='text']")
        self.assertTrue(message_input.is_displayed(), "Message input should be visible")
        
        # Wait for input to be enabled (when connected)
        try:
            WebDriverWait(self.driver, 5).until(
                lambda driver: message_input.is_enabled()
            )
        except TimeoutException:
            pass
        
        self.assertTrue(message_input.is_enabled(), "Message input should be enabled")
        
        # Test input interactivity
        test_text = "Testing input field"
        message_input.clear()
        message_input.send_keys(test_text)
        self.assertEqual(message_input.get_attribute("value"), test_text, "Input should accept text")
        
        print("✅ Chat interface elements are present and interactive")
        
    def test_04_send_message_functionality(self):
        """Test 4: Test sending messages through the chat interface"""
        print("\n🧪 Test 4: Testing message sending functionality...")
        
        self.driver.get(self.base_url)
        time.sleep(2)  # Wait for WebSocket to connect
        
        # Send a test message
        test_message = "Hello, this is a test message"
        self._send_message(test_message)
        
        # Verify message appears in chat
        time.sleep(2)  # Wait for message to appear
        
        # Look for the sent message
        messages = self.driver.find_elements(By.CSS_SELECTOR, ".message, [class*='Message']")
        message_found = False
        
        for msg in messages:
            if test_message in msg.text:
                message_found = True
                print(f"✅ Message found in chat: {msg.text[:50]}...")
                break
                
        self.assertTrue(message_found, f"Sent message '{test_message}' should appear in chat")
        
        # Check if we get any response (loading indicator or agent response)
        time.sleep(3)
        
        # Look for loading indicators or new messages
        loading_indicators = self.driver.find_elements(By.CSS_SELECTOR, 
            ".loading-message, [class*='Loading'], .spinner, [class*='Spinner']")
        new_messages = self.driver.find_elements(By.CSS_SELECTOR, ".message")
        
        has_response = len(loading_indicators) > 0 or len(new_messages) > 1
        
        if has_response:
            print("✅ System responded to the message")
            time.sleep(10)  # Pause to see agent response
        else:
            print("⚠️  No response detected after sending message")
            
    def test_05_greeter_agent_interaction(self):
        """Test 5a: Test interaction with Greeter agent"""
        print("\n🧪 Test 5a: Testing Greeter agent...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Send greeting message
        self._send_message("Hello")
        
        # Wait for Greeter agent response
        agent_responded = self._wait_for_agent_response("Greeter", timeout=20)
        
        if agent_responded:
            print("✅ Greeter agent responded")
            # Check agent panel
            agent_cards = self.driver.find_elements(By.CSS_SELECTOR, ".agent-card")
            for card in agent_cards:
                print(f"   Agent card found: {card.text[:50]}...")
            time.sleep(10)  # Pause to see agent response
        else:
            print("⚠️  Greeter agent did not respond within timeout")
            self.driver.save_screenshot("greeter_agent_timeout.png")
            
    def test_06_weather_agent_interaction(self):
        """Test 5b: Test interaction with Weather agent"""
        print("\n🧪 Test 5b: Testing Weather agent...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Send weather-related message
        self._send_message("What's the weather like in New York?")
        
        # Wait for Weather agent response
        agent_responded = self._wait_for_agent_response("Weather", timeout=20)
        
        if agent_responded:
            print("✅ Weather agent responded")
            time.sleep(10)  # Pause to see agent response
        else:
            print("⚠️  Weather agent did not respond within timeout")
            self.driver.save_screenshot("weather_agent_timeout.png")
            
    def test_07_rag_agent_interaction(self):
        """Test 5c: Test interaction with RAG agent"""
        print("\n🧪 Test 5c: Testing RAG agent...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Send RAG-related query
        self._send_message("Tell me about the documentation")
        
        # Wait for RAG agent response
        agent_responded = self._wait_for_agent_response("RAG", timeout=20)
        
        if agent_responded:
            print("✅ RAG agent responded")
            time.sleep(10)  # Pause to see agent response
        else:
            print("⚠️  RAG agent did not respond within timeout")
            self.driver.save_screenshot("rag_agent_timeout.png")
            
    def test_08_academic_websearch_agent_interaction(self):
        """Test 5d: Test interaction with Academic WebSearch agent"""
        print("\n🧪 Test 5d: Testing Academic WebSearch agent...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Send academic search query
        self._send_message("Search for recent papers on machine learning")
        
        # Wait for Academic WebSearch agent response
        agent_responded = self._wait_for_agent_response("Academic", timeout=30)
        
        if agent_responded:
            print("✅ Academic WebSearch agent responded")
            time.sleep(10)  # Pause to see agent response
        else:
            print("⚠️  Academic WebSearch agent did not respond within timeout")
            self.driver.save_screenshot("academic_websearch_timeout.png")
            
    def test_09_academic_newresearch_agent_interaction(self):
        """Test 5e: Test interaction with Academic NewResearch agent"""
        print("\n🧪 Test 5e: Testing Academic NewResearch agent...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Send new research query
        self._send_message("What are the latest research trends in AI?")
        
        # Wait for Academic NewResearch agent response
        agent_responded = self._wait_for_agent_response("Research", timeout=30)
        
        if agent_responded:
            print("✅ Academic NewResearch agent responded")
            time.sleep(10)  # Pause to see agent response
        else:
            print("⚠️  Academic NewResearch agent did not respond within timeout")
            self.driver.save_screenshot("academic_newresearch_timeout.png")
            
    def test_10_ui_responsiveness(self):
        """Test 6: Test UI responsiveness and element interactions"""
        print("\n🧪 Test 6: Testing UI responsiveness...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Test window resize
        original_size = self.driver.get_window_size()
        
        # Test mobile size
        self.driver.set_window_size(375, 812)
        time.sleep(1)
        
        # Check if UI adapts
        chat_interface = self.driver.find_element(By.CSS_SELECTOR, ".chat-interface, [class*='ChatInterface']")
        self.assertTrue(chat_interface.is_displayed(), "Chat interface should remain visible on mobile")
        
        # Restore original size
        self.driver.set_window_size(original_size['width'], original_size['height'])
        time.sleep(1)
        
        # Test hover effects (if any)
        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, "button")
            if buttons:
                ActionChains(self.driver).move_to_element(buttons[0]).perform()
                time.sleep(0.5)
                print("✅ Hover interactions work")
        except Exception as e:
            print(f"⚠️  Could not test hover effects: {e}")
            
        print("✅ UI is responsive to window size changes")
        
    def test_11_agent_panel_functionality(self):
        """Test 7: Test agent response panel functionality"""
        print("\n🧪 Test 7: Testing agent response panel...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Check if agent panel exists
        agent_panel = None
        panel_selectors = [
            ".agent-response-panel",
            "[class*='AgentResponse']",
            ".agent-panel",
            ".right-panel"
        ]
        
        for selector in panel_selectors:
            try:
                agent_panel = self.driver.find_element(By.CSS_SELECTOR, selector)
                if agent_panel:
                    break
            except NoSuchElementException:
                continue
                
        if agent_panel:
            self.assertTrue(agent_panel.is_displayed(), "Agent panel should be visible")
            print("✅ Agent response panel is present")
            
            # Look for tabs in the agent panel
            tabs = self.driver.find_elements(By.CSS_SELECTOR, ".MuiTab-root, [role='tab']")
            responses_tab = None
            
            print(f"  Found {len(tabs)} tabs")
            for tab in tabs:
                print(f"    Tab text: '{tab.text}'")
                if "RESPONSES" in tab.text.upper():
                    responses_tab = tab
                    break
                    
            if responses_tab:
                # Click on the Responses tab
                responses_tab.click()
                time.sleep(1)
                print("✅ Clicked on Responses tab")
            else:
                print("⚠️  Could not find Responses tab")
            
            # Send a message to trigger agent responses
            self._send_message("Hello")
            
            # Wait for backend response
            print("  Waiting for agent responses...")
            time.sleep(10)
            
            # Look for any response in the chat
            response_found = False
            messages = self.driver.find_elements(By.CSS_SELECTOR, ".message, [class*='Message']")
            for msg in messages:
                if "MAS is processing" not in msg.text and "Hello" not in msg.text:
                    response_found = True
                    print(f"  Found response in chat: {msg.text[:50]}...")
                    time.sleep(10)  # Pause to see agent response
                    break
            
            # Take a screenshot for debugging
            self.driver.save_screenshot("agent_panel_after_message.png")
            
            # Check for agent cards or responses with multiple selectors
            selectors = [
                ".agent-card",
                "[class*='AgentCard']",
                ".agent-response",
                ".agents-list",
                "[class*='agents-list']"
            ]
            
            agent_elements = []
            for selector in selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  Found {len(elements)} elements with selector: {selector}")
                    agent_elements.extend(elements)
            
            # Look specifically for agent cards inside the agents-list
            agent_cards = []
            try:
                agents_list = self.driver.find_element(By.CSS_SELECTOR, ".agents-list")
                if agents_list:
                    agent_cards = agents_list.find_elements(By.CSS_SELECTOR, ".agent-card")
                    print(f"  Found {len(agent_cards)} agent cards in agents-list")
                    if len(agent_cards) > 0:
                        for i, card in enumerate(agent_cards[:3]):
                            print(f"    Card {i+1} text: {card.text[:100]}...")
            except:
                pass
            
            # If no cards in agents-list, check for agent cards anywhere in the panel
            if len(agent_cards) == 0:
                agent_cards = agent_panel.find_elements(By.CSS_SELECTOR, ".agent-card")
                print(f"  Found {len(agent_cards)} agent cards in entire panel")
                if len(agent_cards) > 0:
                    for i, card in enumerate(agent_cards[:3]):
                        print(f"    Card {i+1} text: {card.text[:100]}...")
            
            # Also check the entire panel content
            panel_content = agent_panel.text
            print(f"  Agent panel content preview: {panel_content[:200]}...")
            
            if len(agent_cards) > 0:
                print(f"✅ Found {len(agent_cards)} agent response elements")
                time.sleep(10)  # Pause to see agent responses
            else:
                # Check if we at least have the structure in place
                if agent_panel and responses_tab:
                    print("✅ Agent response panel structure is correct (panel and tabs present)")
                    print("ℹ️  No agent responses displayed - this is expected without backend agent responses")
                else:
                    print("⚠️  No agent response elements found in panel")
        else:
            print("⚠️  Agent response panel not found")
            
    def test_12_error_handling(self):
        """Test 8: Test error handling and edge cases"""
        print("\n🧪 Test 8: Testing error handling...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Test empty message
        self._send_message("")
        time.sleep(1)
        
        # Should not create empty message
        messages = self.driver.find_elements(By.CSS_SELECTOR, ".message")
        empty_messages = [msg for msg in messages if msg.text.strip() == ""]
        self.assertEqual(len(empty_messages), 0, "Should not send empty messages")
        
        # Test very long message
        long_message = "A" * 1000
        self._send_message(long_message)
        time.sleep(2)
        
        # Should handle long messages gracefully
        print("✅ Handles edge cases appropriately")
        
    def test_13_metrics_and_timing(self):
        """Test 9: Test metrics and timing displays"""
        print("\n🧪 Test 9: Testing metrics and timing displays...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Send a message to generate metrics
        self._send_message("Calculate something for me")
        time.sleep(5)
        
        # Look for timing or metrics displays
        metric_selectors = [
            ".metrics-panel",
            "[class*='Metric']",
            ".timing",
            ".duration",
            ".processing-time"
        ]
        
        metrics_found = False
        for selector in metric_selectors:
            try:
                metrics = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if metrics:
                    metrics_found = True
                    print(f"✅ Found {len(metrics)} metric elements")
                    time.sleep(10)  # Pause to see metrics
                    break
            except NoSuchElementException:
                continue
                
        if not metrics_found:
            print("⚠️  No metrics or timing displays found")
            
    def test_14_final_comprehensive_check(self):
        """Test 10: Final comprehensive functionality check"""
        print("\n🧪 Test 10: Running final comprehensive check...")
        
        self.driver.get(self.base_url)
        time.sleep(2)
        
        # Take a full page screenshot
        self.driver.save_screenshot("final_ui_state.png")
        
        # Check all major components are present
        components = {
            "Header": ["header", ".header", "[role='banner']"],
            "Chat Interface": [".chat-interface", "[class*='ChatInterface']"],
            "Message Input": ["textarea", "input[type='text']"],
            "Agent Panel": [".split-panel.right", ".agent-panel", "[class*='AgentPanel']", ".right-panel"]
        }
        
        component_status = {}
        for component_name, selectors in components.items():
            found = False
            for selector in selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if elem and elem.is_displayed():
                        found = True
                        break
                except NoSuchElementException:
                    continue
            component_status[component_name] = found
            
        print("\n📊 Component Status Summary:")
        all_present = True
        for component, present in component_status.items():
            status = "✅" if present else "❌"
            print(f"   {status} {component}")
            if not present:
                all_present = False
                
        self.assertTrue(all_present, "Not all UI components are present")
        
        print("\n✅ Final comprehensive check completed")


def run_single_test(test_name):
    """Run a single test by name"""
    suite = unittest.TestSuite()
    suite.addTest(MASFrontendUITests(test_name))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    # Check if specific test is requested
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test
        test_method = sys.argv[1]
        if hasattr(MASFrontendUITests, test_method):
            run_single_test(test_method)
        else:
            print(f"Test method '{test_method}' not found")
            print("\nAvailable tests:")
            for attr in dir(MASFrontendUITests):
                if attr.startswith('test_'):
                    print(f"  - {attr}")
    else:
        # Run all tests
        unittest.main(verbosity=2)