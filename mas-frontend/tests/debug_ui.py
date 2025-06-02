#!/usr/bin/env python3
"""
Debug UI to check console logs
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


def debug_ui():
    print("🔍 Starting UI Debug...")
    
    options = Options()
    options.add_argument('--window-size=1920,1080')
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        driver.get("http://localhost:3000")
        time.sleep(3)
        
        # Send a message
        input_field = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "textarea"))
        )
        
        input_field.send_keys("Hello")
        input_field.send_keys(Keys.RETURN)
        
        # Wait a bit
        time.sleep(5)
        
        # Get console logs
        print("\n📋 Console logs:")
        logs = driver.get_log('browser')
        for log in logs:
            print(f"[{log['level']}] {log['message']}")
            
        # Check for messages
        print("\n🔍 Checking for messages in DOM...")
        messages = driver.find_elements(By.CSS_SELECTOR, ".message")
        print(f"Found {len(messages)} messages")
        
        for i, msg in enumerate(messages):
            print(f"\nMessage {i+1}:")
            print(f"  Classes: {msg.get_attribute('class')}")
            print(f"  Text: {msg.text[:100]}...")
            
        # Look for agent response specifically
        print("\n🔍 Looking for agent responses...")
        agent_responses = driver.find_elements(By.CSS_SELECTOR, ".message.assistant")
        print(f"Found {len(agent_responses)} assistant messages")
        
        for i, resp in enumerate(agent_responses):
            print(f"\nAssistant message {i+1}:")
            print(f"  Full text: {resp.text}")
            
        # Check loading message
        loading = driver.find_elements(By.XPATH, "//div[contains(text(), 'MAS is processing')]")
        if loading:
            print("\n⚠️ Loading message still visible!")
            
        # Keep browser open
        print("\n✋ Browser will stay open for 30 seconds...")
        time.sleep(30)
        
    finally:
        driver.quit()
        

if __name__ == "__main__":
    debug_ui()