#!/usr/bin/env python3
"""
Simple UI test to verify basic message display
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

print("🚀 Simple UI Test - Checking message display")

# Setup browser
options = Options()
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Open the app
    driver.get("http://localhost:3000")
    print("✅ Opened application")
    time.sleep(3)
    
    # Check connection status
    status = driver.find_element(By.CSS_SELECTOR, ".MuiChip-root")
    print(f"📡 Connection status: {status.text}")
    
    # Find and send message
    input_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
    )
    
    test_message = "Hello, test message!"
    input_field.clear()
    input_field.send_keys(test_message)
    print(f"✍️ Typed: '{test_message}'")
    
    input_field.send_keys(Keys.RETURN)
    print("📤 Sent message")
    
    # Wait and check for messages
    time.sleep(3)
    
    # Get all message elements
    messages = driver.find_elements(By.CSS_SELECTOR, ".message")
    print(f"\n📋 Found {len(messages)} message elements")
    
    # Also check for any elements with 'message' in the class
    message_divs = driver.find_elements(By.XPATH, "//div[contains(@class, 'message')]")
    print(f"📋 Found {len(message_divs)} divs with 'message' class")
    
    # Check for specific message content
    all_text = driver.find_element(By.TAG_NAME, "body").text
    if test_message in all_text:
        print(f"✅ User message '{test_message}' is displayed")
    else:
        print(f"❌ User message '{test_message}' NOT found")
        
    # Look for loading or processing message
    if "processing" in all_text.lower():
        print("⏳ Found processing message")
    
    # Wait for any assistant response
    print("\n⏳ Waiting for assistant response...")
    for i in range(20):
        time.sleep(1)
        all_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Check for assistant-related text
        if "MAS Assistant" in all_text:
            print("✅ Found 'MAS Assistant' in page")
            
            # Get the actual response text
            messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'message')]")
            for msg in messages:
                if "MAS Assistant" in msg.text or "assistant" in msg.get_attribute("class"):
                    response = msg.text.replace("MAS Assistant", "").strip()
                    if response and "processing" not in response:
                        print(f"💬 Assistant response: {response[:100]}...")
                        break
            break
    
    # Take screenshot
    driver.save_screenshot("message_display_test.png")
    print("\n📸 Screenshot saved as 'message_display_test.png'")
    
    # Debug: Print page structure
    print("\n🔍 Page structure debug:")
    main_containers = driver.find_elements(By.CSS_SELECTOR, ".chat-interface, .chat-messages, .message-list")
    for container in main_containers:
        classes = container.get_attribute("class")
        print(f"  Container: {classes}")
        children = container.find_elements(By.XPATH, ".//*")
        print(f"    Children: {len(children)}")
    
    print("\n✅ Test complete - keeping browser open for 30 seconds")
    time.sleep(30)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    driver.save_screenshot("error_screenshot.png")
    print("📸 Error screenshot saved")
finally:
    driver.quit()
    print("🏁 Browser closed")