"""
CPCB Browser Navigation Test

Test different navigation approaches to find the comparison data page.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Try navigating to home page first
    print("Step 1: Navigating to CPCB home page...")
    driver.get("https://airquality.cpcb.gov.in/ccr/")
    time.sleep(10)
    
    print(f"Current URL: {driver.current_url}")
    
    # Look for navigation links
    print("\nStep 2: Looking for navigation links...")
    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"Found {len(links)} links")
    
    for link in links[:20]:  # Show first 20 links
        try:
            href = link.get_attribute("href")
            text = link.text.strip()
            if text and href:
                print(f"  {text}: {href}")
        except:
            pass
    
    # Look for any Angular components
    print("\nStep 3: Looking for Angular components...")
    angular_elements = driver.find_elements(By.CSS_SELECTOR, "[ng-controller], [ng-app], app-root, router-outlet")
    print(f"Found {len(angular_elements)} Angular elements")
    
    # Try to find comparison data link
    print("\nStep 4: Looking for comparison data link...")
    comparison_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Comparison")
    print(f"Found {len(comparison_links)} comparison links")
    
    for link in comparison_links:
        print(f"  Link text: {link.text}")
        print(f"  Link href: {link.get_attribute('href')}")
    
    # Try to find data menu
    print("\nStep 5: Looking for data menu...")
    menu_items = driver.find_elements(By.CSS_SELECTOR, ".nav-item, .menu-item, [class*='menu']")
    print(f"Found {len(menu_items)} menu items")
    
    for item in menu_items[:10]:
        try:
            print(f"  {item.text.strip()}")
        except:
            pass
    
    # Take screenshot
    driver.save_screenshot("cpcb_navigation_test.png")
    print("\nScreenshot saved to cpcb_navigation_test.png")
    
finally:
    driver.quit()
    print("\nBrowser closed")