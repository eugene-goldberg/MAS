#!/usr/bin/env python3
"""
Quick debug script to identify specific UI issues in MAS Frontend
This script provides detailed diagnostics about what's broken
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def setup_driver(headless=False):
    """Set up Chrome driver"""
    options = Options()
    if headless:
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    return driver


def diagnose_ui_issues():
    """Run diagnostics to identify UI issues"""
    driver = setup_driver(headless=False)  # Run with visible browser for debugging
    issues = []
    
    try:
        print("\n🔍 MAS Frontend UI Diagnostics")
        print("=" * 60)
        
        # 1. Check if page loads
        print("\n1️⃣ Checking page load...")
        driver.get("http://localhost:3000")
        time.sleep(3)
        
        # Check page title
        title = driver.title
        print(f"   Page title: '{title}'")
        if not title:
            issues.append("Page has no title - might not be loading correctly")
            
        # Check for React root
        try:
            root = driver.find_element(By.ID, "root")
            if root:
                print("   ✅ React root element found")
                # Check if it has content
                if not root.text.strip() and not root.find_elements(By.XPATH, ".//*"):
                    issues.append("React root is empty - app might not be mounting")
            else:
                issues.append("No React root element found")
        except NoSuchElementException:
            issues.append("React root element (#root) not found")
            
        # 2. Check for JavaScript errors
        print("\n2️⃣ Checking for JavaScript errors...")
        logs = driver.get_log('browser')
        js_errors = [log for log in logs if log['level'] == 'SEVERE']
        
        if js_errors:
            issues.append(f"Found {len(js_errors)} JavaScript errors")
            for error in js_errors[:5]:  # Show first 5 errors
                print(f"   ❌ JS Error: {error['message']}")
        else:
            print("   ✅ No JavaScript errors detected")
            
        # 3. Check main components
        print("\n3️⃣ Checking main UI components...")
        
        components_to_check = [
            ("App Container", [".app-container", "#app", "[class*='App']"]),
            ("Header", ["header", ".header", "[class*='Header']"]),
            ("Chat Interface", [".chat-interface", "[class*='ChatInterface']", ".chat"]),
            ("Message Input", ["textarea", "input[type='text']", "[class*='MessageInput']"]),
            ("Connection Status", [".connection-status", "[class*='Connection']", ".status"]),
            ("Agent Panel", [".agent-panel", "[class*='AgentPanel']", ".agents"])
        ]
        
        for component_name, selectors in components_to_check:
            found = False
            found_selector = None
            
            for selector in selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        found = True
                        found_selector = selector
                        # Check if visible
                        visible_count = sum(1 for e in elements if e.is_displayed())
                        print(f"   {'✅' if visible_count > 0 else '⚠️'} {component_name}: Found {len(elements)} element(s) with '{selector}', {visible_count} visible")
                        break
                except Exception:
                    continue
                    
            if not found:
                issues.append(f"{component_name} not found with any selector: {selectors}")
                print(f"   ❌ {component_name}: Not found")
                
        # 4. Check WebSocket connection
        print("\n4️⃣ Checking WebSocket connection...")
        
        # Look for any WebSocket-related indicators
        ws_indicators = driver.find_elements(By.XPATH, "//*[contains(@class, 'connect') or contains(@class, 'status') or contains(text(), 'Connected') or contains(text(), 'Disconnected')]")
        
        if ws_indicators:
            print(f"   Found {len(ws_indicators)} potential WebSocket indicators:")
            for indicator in ws_indicators[:3]:
                text = indicator.text.strip()
                classes = indicator.get_attribute("class")
                if text or classes:
                    print(f"     - Text: '{text}', Classes: '{classes}'")
        else:
            issues.append("No WebSocket connection indicators found")
            
        # 5. Check network requests
        print("\n5️⃣ Checking network activity...")
        
        # Execute JavaScript to check for fetch/XHR activity
        network_check = driver.execute_script("""
            return {
                hasWebSocket: typeof WebSocket !== 'undefined',
                fetchDefined: typeof fetch !== 'undefined',
                performance: window.performance.getEntriesByType('resource').length
            }
        """)
        
        print(f"   WebSocket available: {network_check['hasWebSocket']}")
        print(f"   Fetch API available: {network_check['fetchDefined']}")
        print(f"   Network requests made: {network_check['performance']}")
        
        # 6. Check React DevTools
        print("\n6️⃣ Checking React presence...")
        
        react_check = driver.execute_script("""
            return {
                hasReact: typeof React !== 'undefined',
                hasReactDOM: typeof ReactDOM !== 'undefined',
                reactVersion: typeof React !== 'undefined' ? React.version : null,
                hasReactDevTools: '__REACT_DEVTOOLS_GLOBAL_HOOK__' in window
            }
        """)
        
        if react_check['hasReact']:
            print(f"   ✅ React detected (version: {react_check['reactVersion']})")
        else:
            issues.append("React not detected in global scope")
            
        # 7. Try to interact with the UI
        print("\n7️⃣ Testing UI interactions...")
        
        try:
            # Find and click on any input
            inputs = driver.find_elements(By.CSS_SELECTOR, "input, textarea")
            if inputs:
                input_elem = inputs[0]
                input_elem.click()
                input_elem.send_keys("Test")
                value = input_elem.get_attribute("value")
                if value == "Test":
                    print("   ✅ Input field accepts text")
                else:
                    issues.append("Input field doesn't retain typed text")
            else:
                issues.append("No input fields found")
        except Exception as e:
            issues.append(f"Cannot interact with input fields: {e}")
            
        # 8. Take diagnostic screenshots
        print("\n8️⃣ Taking diagnostic screenshots...")
        
        # Full page screenshot
        driver.save_screenshot("diagnostic_full_page.png")
        print("   📸 Saved: diagnostic_full_page.png")
        
        # Try to screenshot specific elements
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            body.screenshot("diagnostic_body_content.png")
            print("   📸 Saved: diagnostic_body_content.png")
        except Exception:
            pass
            
        # Get page source for analysis
        with open("diagnostic_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("   📄 Saved: diagnostic_page_source.html")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        if issues:
            print(f"\n❌ Found {len(issues)} issues:\n")
            for i, issue in enumerate(issues, 1):
                print(f"{i}. {issue}")
                
            print("\n💡 Recommendations:")
            
            if any("React root is empty" in issue for issue in issues):
                print("   - Check if React app is building correctly")
                print("   - Look for build errors in npm/yarn output")
                print("   - Verify webpack/build configuration")
                
            if any("JavaScript errors" in issue for issue in issues):
                print("   - Fix JavaScript errors first - they may block rendering")
                print("   - Check browser console for detailed error messages")
                
            if any("WebSocket" in issue for issue in issues):
                print("   - Verify WebSocket server is running")
                print("   - Check WebSocket endpoint configuration")
                print("   - Look for CORS issues")
                
        else:
            print("\n✅ No major issues detected!")
            print("   The UI appears to be loading correctly.")
            
    except Exception as e:
        print(f"\n❌ Diagnostic failed with error: {e}")
        
    finally:
        print("\n🏁 Diagnostics complete. Check screenshots and HTML source for details.")
        driver.quit()


if __name__ == "__main__":
    diagnose_ui_issues()