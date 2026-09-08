"""
CPCB Browser Debug Script

This script helps debug why the CPCB Angular SPA is not loading properly.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# Add logging preferences
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Navigate to CPCB
    url = "https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/caaqm-comparison-data"
    print(f"Navigating to: {url}")
    driver.get(url)
    
    # Wait for page to load
    print("Waiting for page to load...")
    time.sleep(15)
    
    # Check current URL
    print(f"Current URL: {driver.current_url}")
    
    # Get page source
    page_source = driver.page_source
    print(f"\nPage source length: {len(page_source)}")
    print(f"\nFirst 2000 characters of page source:")
    print(page_source[:2000])
    
    # Check for any error messages
    print("\n\nLooking for error messages...")
    try:
        body = driver.find_element(By.TAG_NAME, "body")
        print(f"Body text: {body.text[:1000]}")
    except Exception as e:
        print(f"Error getting body text: {e}")
    
    # Get browser logs
    print("\n\nBrowser logs (last 20 entries):")
    logs = driver.get_log("performance")
    for log in logs[-20:]:
        print(f"  {log['message'][:200]}")
    
    # Take a screenshot
    driver.save_screenshot("cpcb_debug_screenshot.png")
    print("\nScreenshot saved to cpcb_debug_screenshot.png")
    
finally:
    driver.quit()
    print("\nBrowser closed")