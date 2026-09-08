"""
CPCB Menu Interaction Test

Test interacting with the CPCB menu to find comparison data.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
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
    # Navigate to CPCB home page
    print("Navigating to CPCB home page...")
    driver.get("https://airquality.cpcb.gov.in/ccr/")
    
    # Wait for page to load
    print("Waiting for page to load...")
    time.sleep(15)
    
    print(f"Current URL: {driver.current_url}")
    
    # Look for "Data" menu
    print("\nLooking for 'Data' menu...")
    data_menu = driver.find_elements(By.XPATH, "//*[contains(text(), 'Data')]")
    print(f"Found {len(data_menu)} elements containing 'Data'")
    
    for item in data_menu:
        try:
            print(f"  Tag: {item.tag_name}, Text: {item.text.strip()[:50]}")
            
            # Try to hover over the menu
            actions = ActionChains(driver)
            actions.move_to_element(item).perform()
            time.sleep(2)
            
            # Look for dropdown items
            dropdown_items = driver.find_elements(By.CSS_SELECTOR, ".dropdown-menu a, .nav-dropdown a, [class*='dropdown'] a")
            print(f"  Found {len(dropdown_items)} dropdown items")
            
            for dropdown in dropdown_items[:10]:
                try:
                    text = dropdown.text.strip()
                    href = dropdown.get_attribute("href")
                    if text:
                        print(f"    {text}: {href}")
                except:
                    pass
            
            break  # Process only the first Data menu
            
        except Exception as e:
            print(f"  Error: {e}")
    
    # Take screenshot
    driver.save_screenshot("cpcb_menu_test.png")
    print("\nScreenshot saved to cpcb_menu_test.png")
    
finally:
    driver.quit()
    print("\nBrowser closed")