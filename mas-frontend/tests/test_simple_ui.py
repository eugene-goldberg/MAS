#!/usr/bin/env python3
"""
Simple UI test to check if agent responses are being displayed
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

print("🚀 Simple Agent Response Test")
print("="*60)

# Setup browser
options = Options()
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

try:
    # Open app
    driver.get("http://localhost:3000")
    print("✅ Opened application")
    time.sleep(3)
    
    # Check connection
    status = driver.find_element(By.CSS_SELECTOR, ".MuiChip-root")
    print(f"📡 Connection: {status.text}")
    
    # Send simple greeting
    input_field = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
    )
    
    input_field.clear()
    input_field.send_keys("Hello")
    input_field.send_keys(Keys.RETURN)
    print("📤 Sent: 'Hello'")
    
    # Wait and check for changes
    print("\n⏳ Monitoring for responses...")
    
    for i in range(60):  # 60 seconds max
        time.sleep(1)
        
        # Get all text on page
        body_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Check for processing message
        if i == 2 and "MAS is processing" in body_text:
            print("✅ Processing message appeared")
            
        # Look for any response that's not processing
        messages = driver.find_elements(By.XPATH, "//div[contains(@class, 'message')]")
        
        for msg in messages:
            msg_text = msg.text
            # Skip user messages and processing messages
            if msg_text and "Hello" not in msg_text and "processing" not in msg_text:
                if "MAS Assistant" in msg_text or len(msg_text) > 20:
                    print(f"\n🎉 Found response: {msg_text[:100]}...")
                    
                    # Take screenshot
                    driver.save_screenshot("agent_response_found.png")
                    print("📸 Screenshot saved")
                    
                    # Keep browser open to see result
                    print("\n✅ Test successful - agent responded!")
                    print("Browser will stay open for 30 seconds...")
                    time.sleep(30)
                    driver.quit()
                    exit(0)
                    
        if i % 10 == 0 and i > 0:
            print(f"  Still waiting... ({i}s)")
            
    # If we get here, no response was found
    print("\n❌ No agent response found after 60 seconds")
    driver.save_screenshot("no_response_timeout.png")
    print("📸 Timeout screenshot saved")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    driver.save_screenshot("error.png")
finally:
    print("\nClosing browser...")
    driver.quit()