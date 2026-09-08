"""
CPCB CAAQMS PM2.5 Browser-Session Acquisition Pipeline (Improved)

This script implements Selenium-based browser automation to acquire
PM2.5 concentration data from CPCB's CAAQMS comparison data interface.

Usage:
    python scripts/cpcb_browser_acquisition.py --test
    python scripts/cpcb_browser_acquisition.py --station site_5453 --start 2026-01-01 --end 2026-01-03
    python scripts/cpcb_browser_acquisition.py --all
"""

import os
import sys
import json
import time
import hashlib
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    StaleElementReferenceException
)
from webdriver_manager.chrome import ChromeDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cpcb_acquisition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
CPCB_URL = "https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/caaqm-comparison-data"
CPCB_HOME = "https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing"
RAW_DATA_DIR = Path("data/raw/air_quality/cpcb_pm25")
STAGING_DIR = Path("data/staging/air_quality/cpcb_pm25")
METADATA_DIR = Path("data/metadata")

# Ahmedabad station mapping (from previous audit)
AHMEDABAD_STATIONS = {
    "site_308": "Maninagar, Ahmedabad - GPCB",
    "site_5449": "Sardar Vallabhbhai Patel Stadium, Ahmedabad - IITM",
    "site_5450": "Gyaspur, Ahmedabad - IITM",
    "site_5451": "Rakhial, Ahmedabad - IITM",
    "site_5452": "Raikhad, Ahmedabad - IITM",
    "site_5453": "Chandkheda, Ahmedabad - IITM",
    "site_5454": "SAC ISRO Bopal, Ahmedabad - IITM",
    "site_5455": "SAC ISRO Satellite, Ahmedabad - IITM",
    "site_5456": "SVPI Airport Hansol, Ahmedabad - IITM"
}

# Rate limiting
MIN_DELAY_SECONDS = 5
MAX_RETRIES = 3
RETRY_BACKOFF = 2


class CPCBBrowserAcquisition:
    """Selenium-based browser automation for CPCB CAAQMS data acquisition."""
    
    def __init__(self, headless: bool = False, download_dir: Optional[Path] = None):
        """Initialize the browser automation.
        
        Args:
            headless: Run browser in headless mode (not recommended for first run)
            download_dir: Directory for downloaded files
        """
        self.headless = headless
        self.download_dir = download_dir or RAW_DATA_DIR
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.driver = None
        self.wait = None
        
    def setup_browser(self) -> webdriver.Chrome:
        """Setup Chrome browser with appropriate options."""
        chrome_options = Options()
        
        # Basic options
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User agent to look like a regular browser
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        # Download preferences
        prefs = {
            "download.default_directory": str(self.download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        if self.headless:
            chrome_options.add_argument("--headless=new")
        
        # Setup ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Anti-detection measures
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        
        # Set page load timeout
        driver.set_page_load_timeout(60)
        
        self.driver = driver
        self.wait = WebDriverWait(driver, 30)
        
        logger.info("Browser setup complete")
        return driver
    
    def navigate_to_comparison_page(self) -> bool:
        """Navigate to CPCB CAAQMS comparison data page."""
        try:
            logger.info(f"Navigating to {CPCB_URL}")
            self.driver.get(CPCB_URL)
            
            # Wait for Angular SPA to load
            logger.info("Waiting for Angular SPA to load...")
            time.sleep(10)
            
            # Check if page loaded correctly
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            # Try to find comparison data elements
            try:
                # Look for state dropdown or any form elements
                self.driver.find_element(By.CSS_SELECTOR, "select, input, button")
                logger.info("Found form elements on page")
                return True
            except NoSuchElementException:
                logger.warning("No form elements found, page may not have loaded")
                
                # Try navigating to home first, then to comparison
                logger.info("Trying alternative navigation...")
                self.driver.get(CPCB_HOME)
                time.sleep(5)
                
                # Look for comparison data link
                try:
                    link = self.driver.find_element(By.PARTIAL_LINK_TEXT, "Comparison")
                    link.click()
                    time.sleep(5)
                    return True
                except NoSuchElementException:
                    logger.error("Could not find comparison data link")
                    return False
            
        except Exception as e:
            logger.error(f"Error navigating to comparison page: {e}")
            return False
    
    def wait_for_angular_load(self) -> bool:
        """Wait for Angular application to fully load."""
        try:
            # Wait for Angular to be ready
            logger.info("Waiting for Angular application to load...")
            
            # Wait for any dropdown or form element
            WebDriverWait(self.driver, 30).until(
                lambda d: d.find_elements(By.TAG_NAME, "select") or 
                          d.find_elements(By.TAG_NAME, "input")
            )
            
            logger.info("Angular application loaded")
            return True
            
        except TimeoutException:
            logger.warning("Timeout waiting for Angular load")
            return False
    
    def select_state(self, state: str = "Gujarat") -> bool:
        """Select state from dropdown."""
        try:
            logger.info(f"Selecting state: {state}")
            
            # Wait for state dropdown
            state_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "state"))
            )
            
            # Select state
            select = Select(state_dropdown)
            select.select_by_visible_text(state)
            
            time.sleep(2)
            logger.info(f"Selected state: {state}")
            return True
            
        except Exception as e:
            logger.error(f"Error selecting state: {e}")
            return False
    
    def select_city(self, city: str = "Ahmedabad") -> bool:
        """Select city from dropdown."""
        try:
            logger.info(f"Selecting city: {city}")
            
            # Wait for city dropdown
            city_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "city"))
            )
            
            # Select city
            select = Select(city_dropdown)
            select.select_by_visible_text(city)
            
            time.sleep(2)
            logger.info(f"Selected city: {city}")
            return True
            
        except Exception as e:
            logger.error(f"Error selecting city: {e}")
            return False
    
    def select_station(self, station_id: str, station_name: str) -> bool:
        """Select station from dropdown."""
        try:
            logger.info(f"Selecting station: {station_name} ({station_id})")
            
            # Wait for station dropdown
            station_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "station"))
            )
            
            # Select station by station_id
            select = Select(station_dropdown)
            select.select_by_visible_text(station_name)
            
            time.sleep(2)
            logger.info(f"Selected station: {station_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error selecting station: {e}")
            return False
    
    def select_parameter(self, parameter: str = "PM2.5") -> bool:
        """Select parameter from dropdown."""
        try:
            logger.info(f"Selecting parameter: {parameter}")
            
            # Wait for parameter dropdown
            param_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "parameter"))
            )
            
            # Select parameter
            select = Select(param_dropdown)
            select.select_by_visible_text(parameter)
            
            time.sleep(2)
            logger.info(f"Selected parameter: {parameter}")
            return True
            
        except Exception as e:
            logger.error(f"Error selecting parameter: {e}")
            return False
    
    def set_date_range(self, start_date: str, end_date: str) -> bool:
        """Set date range for data retrieval.
        
        Args:
            start_date: Start date in DD-MM-YYYY format
            end_date: End date in DD-MM-YYYY format
        """
        try:
            logger.info(f"Setting date range: {start_date} to {end_date}")
            
            # Wait for date fields
            from_date = self.wait.until(
                EC.presence_of_element_located((By.ID, "fromDate"))
            )
            to_date = self.wait.until(
                EC.presence_of_element_located((By.ID, "toDate"))
            )
            
            # Clear and set dates
            from_date.clear()
            from_date.send_keys(start_date)
            
            to_date.clear()
            to_date.send_keys(end_date)
            
            time.sleep(2)
            logger.info(f"Set date range: {start_date} to {end_date}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting date range: {e}")
            return False
    
    def click_submit(self) -> bool:
        """Click submit button to fetch data."""
        try:
            logger.info("Clicking submit button")
            
            # Wait for submit button
            submit_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "submit"))
            )
            
            # Click submit
            submit_button.click()
            
            # Wait for results to load
            time.sleep(5)
            
            logger.info("Submitted request")
            return True
            
        except Exception as e:
            logger.error(f"Error clicking submit: {e}")
            return False
    
    def wait_for_results(self) -> bool:
        """Wait for results table to load."""
        try:
            logger.info("Waiting for results table")
            
            # Wait for table to appear
            table = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.dataTable"))
            )
            
            # Wait for table to have data
            time.sleep(3)
            
            logger.info("Results table loaded")
            return True
            
        except TimeoutException:
            logger.warning("Timeout waiting for results table")
            return False
        except Exception as e:
            logger.error(f"Error waiting for results: {e}")
            return False
    
    def download_excel(self) -> Optional[Path]:
        """Download results as Excel file."""
        try:
            logger.info("Downloading Excel file")
            
            # Find Excel download button
            excel_button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.excel, .fa-file-excel-o"))
            )
            
            # Click download
            excel_button.click()
            
            # Wait for download to complete
            time.sleep(5)
            
            # Find the downloaded file
            downloaded_files = list(self.download_dir.glob("*.xlsx"))
            if downloaded_files:
                latest_file = max(downloaded_files, key=os.path.getctime)
                logger.info(f"Downloaded file: {latest_file}")
                return latest_file
            
            logger.warning("No Excel file found in download directory")
            return None
            
        except Exception as e:
            logger.error(f"Error downloading Excel: {e}")
            return None
    
    def get_station_list(self) -> List[Dict[str, str]]:
        """Get list of stations for Ahmedabad from the page."""
        stations = []
        
        try:
            # Navigate to comparison page
            self.navigate_to_comparison_page()
            
            # Wait for Angular to load
            self.wait_for_angular_load()
            
            # Select state and city
            self.select_state("Gujarat")
            self.select_city("Ahmedabad")
            
            # Wait for station dropdown to populate
            time.sleep(3)
            
            # Get all stations from dropdown
            station_dropdown = self.wait.until(
                EC.presence_of_element_located((By.ID, "station"))
            )
            select = Select(station_dropdown)
            
            for option in select.options:
                if option.text and option.text != "-- Select Station --":
                    station_text = option.text
                    # Try to extract station_id from option value
                    station_id = option.get_attribute("value")
                    
                    stations.append({
                        "station_name": station_text,
                        "station_id": station_id or "unknown"
                    })
            
            logger.info(f"Found {len(stations)} stations")
            return stations
            
        except Exception as e:
            logger.error(f"Error getting station list: {e}")
            return stations
    
    def test_chandkheda(self) -> Dict[str, Any]:
        """Test acquisition with Chandkheda station (site_5453)."""
        logger.info("=" * 70)
        logger.info("TESTING CHANDKHEDA STATION (site_5453)")
        logger.info("=" * 70)
        
        result = {
            "station_id": "site_5453",
            "station_name": "Chandkheda, Ahmedabad - IITM",
            "start_date": "01-01-2026",
            "end_date": "03-01-2026",
            "parameter": "PM2.5",
            "success": False,
            "file_path": None,
            "error": None
        }
        
        try:
            # Setup browser
            self.setup_browser()
            
            # Navigate to page
            if not self.navigate_to_comparison_page():
                result["error"] = "Failed to navigate to comparison page"
                return result
            
            # Wait for Angular to load
            if not self.wait_for_angular_load():
                result["error"] = "Failed to load Angular application"
                return result
            
            # Select state, city, station
            if not self.select_state("Gujarat"):
                result["error"] = "Failed to select state"
                return result
            
            if not self.select_city("Ahmedabad"):
                result["error"] = "Failed to select city"
                return result
            
            if not self.select_station("site_5453", "Chandkheda, Ahmedabad - IITM"):
                result["error"] = "Failed to select station"
                return result
            
            if not self.select_parameter("PM2.5"):
                result["error"] = "Failed to select parameter"
                return result
            
            # Set date range
            if not self.set_date_range("01-01-2026", "03-01-2026"):
                result["error"] = "Failed to set date range"
                return result
            
            # Submit
            if not self.click_submit():
                result["error"] = "Failed to click submit"
                return result
            
            # Wait for results
            if not self.wait_for_results():
                result["error"] = "Failed to get results"
                return result
            
            # Download Excel
            file_path = self.download_excel()
            if file_path:
                result["success"] = True
                result["file_path"] = str(file_path)
                logger.info(f"Test successful: {file_path}")
            else:
                result["error"] = "Failed to download Excel"
            
            return result
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            result["error"] = str(e)
            return result
        
        finally:
            if self.driver:
                self.driver.quit()
    
    def acquire_station_data(self, station_id: str, station_name: str,
                            start_date: str, end_date: str) -> Optional[Path]:
        """Acquire PM2.5 data for a specific station and date range."""
        logger.info(f"Acquiring data for {station_name} ({station_id})")
        
        try:
            # Setup browser if not already
            if not self.driver:
                self.setup_browser()
            
            # Navigate to page
            if not self.navigate_to_comparison_page():
                return None
            
            # Wait for Angular to load
            if not self.wait_for_angular_load():
                return None
            
            # Select state, city, station
            if not self.select_state("Gujarat"):
                return None
            
            if not self.select_city("Ahmedabad"):
                return None
            
            if not self.select_station(station_id, station_name):
                return None
            
            if not self.select_parameter("PM2.5"):
                return None
            
            # Set date range
            if not self.set_date_range(start_date, end_date):
                return None
            
            # Submit
            if not self.click_submit():
                return None
            
            # Wait for results
            if not self.wait_for_results():
                return None
            
            # Download Excel
            return self.download_excel()
            
        except Exception as e:
            logger.error(f"Error acquiring data: {e}")
            return None


def validate_download(file_path: Path, station_id: str) -> Dict[str, Any]:
    """Validate downloaded file contains PM2.5 concentration data."""
    logger.info(f"Validating download: {file_path}")
    
    validation = {
        "file_path": str(file_path),
        "station_id": station_id,
        "valid": False,
        "pm25_column": None,
        "pm25_units": None,
        "row_count": 0,
        "valid_pm25_count": 0,
        "missing_pm25_count": 0,
        "min_pm25": None,
        "max_pm25": None,
        "mean_pm25": None,
        "median_pm25": None,
        "negative_count": 0,
        "error": None
    }
    
    try:
        # Read Excel file
        df = pd.read_excel(file_path)
        validation["row_count"] = len(df)
        
        # Look for PM2.5 column
        pm25_cols = [col for col in df.columns if "PM2.5" in str(col) or "PM25" in str(col)]
        
        if not pm25_cols:
            validation["error"] = "No PM2.5 column found"
            return validation
        
        pm25_col = pm25_cols[0]
        validation["pm25_column"] = pm25_col
        
        # Check for units
        if "µg/m³" in str(pm25_col) or "ug/m3" in str(pm25_col).lower():
            validation["pm25_units"] = "µg/m³"
        else:
            validation["pm25_units"] = "unknown"
        
        # Analyze PM2.5 values
        pm25_values = pd.to_numeric(df[pm25_col], errors="coerce")
        valid_mask = ~pm25_values.isna()
        
        validation["valid_pm25_count"] = valid_mask.sum()
        validation["missing_pm25_count"] = pm25_values.isna().sum()
        
        if valid_mask.sum() > 0:
            validation["min_pm25"] = float(pm25_values.min())
            validation["max_pm25"] = float(pm25_values.max())
            validation["mean_pm25"] = float(pm25_values.mean())
            validation["median_pm25"] = float(pm25_values.median())
            validation["negative_count"] = int((pm25_values < 0).sum())
            
            # Check if values are in valid range (0-500 µg/m³)
            if validation["min_pm25"] >= 0 and validation["max_pm25"] <= 500:
                validation["valid"] = True
                logger.info("Download validation PASSED")
            else:
                validation["error"] = "Values outside valid PM2.5 range (0-500 µg/m³)"
        else:
            validation["error"] = "No valid PM2.5 values"
        
        return validation
        
    except Exception as e:
        validation["error"] = str(e)
        logger.error(f"Validation failed: {e}")
        return validation


def compare_with_existing(new_file: Path, existing_file: Path) -> Dict[str, Any]:
    """Compare new download with existing Chandkheda file."""
    logger.info(f"Comparing with existing file: {existing_file}")
    
    comparison = {
        "new_file": str(new_file),
        "existing_file": str(existing_file),
        "overlapping_timestamps": 0,
        "pm25_agreement": None,
        "missingness_differences": None,
        "schema_differences": None,
        "same_source": None
    }
    
    try:
        # Read both files
        new_df = pd.read_excel(new_file)
        existing_df = pd.read_csv(existing_file)
        
        # Compare schemas
        comparison["schema_differences"] = {
            "new_columns": list(new_df.columns),
            "existing_columns": list(existing_df.columns),
            "new_shape": new_df.shape,
            "existing_shape": existing_df.shape
        }
        
        # Try to find common timestamps
        # This is a simplified comparison - actual implementation would need
        # to handle different timestamp formats
        
        return comparison
        
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        comparison["error"] = str(e)
        return comparison


def create_metadata_files(acquisition_results: List[Dict[str, Any]]):
    """Create required metadata files."""
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create file inventory
    inventory = []
    for result in acquisition_results:
        if result.get("success") and result.get("file_path"):
            file_path = Path(result["file_path"])
            sha256_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
            
            inventory.append({
                "station_id": result["station_id"],
                "station_name": result["station_name"],
                "raw_file": str(file_path),
                "sha256": sha256_hash,
                "source_url": CPCB_URL,
                "retrieval_timestamp": datetime.now().isoformat()
            })
    
    if inventory:
        inventory_df = pd.DataFrame(inventory)
        inventory_df.to_csv(METADATA_DIR / "cpcb_pm25_file_inventory.csv", index=False)
        logger.info(f"Created file inventory with {len(inventory)} records")
    
    # Create acquisition test JSON
    test_result = next((r for r in acquisition_results if r.get("station_id") == "site_5453"), None)
    if test_result:
        with open(METADATA_DIR / "cpcb_pm25_acquisition_test.json", "w") as f:
            json.dump(test_result, f, indent=2)
        logger.info("Created acquisition test JSON")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CPCB CAAQMS PM2.5 Browser Acquisition")
    parser.add_argument("--test", action="store_true", help="Test with Chandkheda station")
    parser.add_argument("--station", type=str, help="Station ID to acquire")
    parser.add_argument("--start", type=str, help="Start date (DD-MM-YYYY)")
    parser.add_argument("--end", type=str, help="End date (DD-MM-YYYY)")
    parser.add_argument("--all", action="store_true", help="Acquire all Ahmedabad stations")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--get-stations", action="store_true", help="Get station list only")
    
    args = parser.parse_args()
    
    # Create directories
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize acquisition
    acquisition = CPCBBrowserAcquisition(headless=args.headless)
    
    if args.get_stations:
        # Get station list
        try:
            acquisition.setup_browser()
            stations = acquisition.get_station_list()
            
            print("\nAhmedabad Stations:")
            print("-" * 50)
            for station in stations:
                print(f"{station['station_id']}: {station['station_name']}")
            
            # Save to metadata
            stations_df = pd.DataFrame(stations)
            stations_df.to_csv(METADATA_DIR / "ahmedabad_cpcb_current_station_inventory.csv", index=False)
            print(f"\nSaved {len(stations)} stations to metadata")
            
        finally:
            if acquisition.driver:
                acquisition.driver.quit()
    
    elif args.test:
        # Test with Chandkheda
        result = acquisition.test_chandkheda()
        
        print("\n" + "=" * 70)
        print("TEST RESULT")
        print("=" * 70)
        print(json.dumps(result, indent=2))
        
        if result["success"]:
            # Validate download
            validation = validate_download(Path(result["file_path"]), result["station_id"])
            print("\n" + "=" * 70)
            print("VALIDATION RESULT")
            print("=" * 70)
            print(json.dumps(validation, indent=2))
            
            # Compare with existing file
            existing_file = Path("raw_data_hourly_chandkheda,_ahmedabad_-_iitm_1H.csv")
            if existing_file.exists():
                comparison = compare_with_existing(Path(result["file_path"]), existing_file)
                print("\n" + "=" * 70)
                print("COMPARISON RESULT")
                print("=" * 70)
                print(json.dumps(comparison, indent=2))
            
            # Create metadata
            create_metadata_files([result])
    
    elif args.station and args.start and args.end:
        # Acquire specific station
        station_name = AHMEDABAD_STATIONS.get(args.station, "Unknown")
        
        result = acquisition.acquire_station_data(
            args.station,
            station_name,
            args.start,
            args.end
        )
        
        if result:
            print(f"\nSuccessfully acquired data: {result}")
        else:
            print("\nFailed to acquire data")
    
    elif args.all:
        # Acquire all stations
        results = []
        
        for station_id, station_name in AHMEDABAD_STATIONS.items():
            logger.info(f"Processing {station_name} ({station_id})")
            
            # Note: In production, you would determine actual date ranges
            # For now, use a default range
            result = acquisition.acquire_station_data(
                station_id,
                station_name,
                "01-01-2026",
                "31-01-2026"
            )
            
            results.append({
                "station_id": station_id,
                "station_name": station_name,
                "success": result is not None,
                "file_path": str(result) if result else None
            })
            
            # Rate limiting
            time.sleep(MIN_DELAY_SECONDS)
        
        # Create metadata
        create_metadata_files(results)
        
        # Print summary
        print("\n" + "=" * 70)
        print("ACQUISITION SUMMARY")
        print("=" * 70)
        successful = sum(1 for r in results if r["success"])
        print(f"Total stations: {len(results)}")
        print(f"Successful: {successful}")
        print(f"Failed: {len(results) - successful}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()