#!/usr/bin/env python3
"""
Quick test to verify UI loads without compilation errors
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def test_ui_loads():
    print("🔍 Testing UI loads without compilation errors...")
    
    options = Options()
    options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        driver.get("http://localhost:3000")
        time.sleep(3)
        
        # Check for compilation error overlay
        try:
            error_overlay = driver.find_element(By.XPATH, "//div[contains(text(), 'Compiled with problems')]")
            if error_overlay:
                print("❌ Compilation error overlay found!")
                # Get the error text
                error_text = driver.find_element(By.TAG_NAME, "body").text
                print(f"Error: {error_text[:500]}...")
                return False
        except:
            print("✅ No compilation error overlay found")
        
        # Check for the chat interface
        try:
            chat_header = driver.find_element(By.XPATH, "//h6[contains(text(), 'MAS Chat')]")
            if chat_header:
                print("✅ Chat interface loaded successfully")
            
            # Check for connection status
            status = driver.find_element(By.CSS_SELECTOR, ".MuiChip-root")
            print(f"✅ Connection status: {status.text}")
            
            # Check for the input field
            input_field = driver.find_element(By.CSS_SELECTOR, "textarea")
            if input_field:
                print("✅ Chat input field present")
                
            print("\n🎉 UI loaded successfully without compilation errors!")
            return True
            
        except Exception as e:
            print(f"❌ Error checking UI elements: {e}")
            return False
            
    finally:
        print("\n⏸️ Keeping browser open for 10 seconds...")
        time.sleep(10)
        driver.quit()


if __name__ == "__main__":
    success = test_ui_loads()
    exit(0 if success else 1)