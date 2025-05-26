import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

class OdishaRERAScraper:
    def __init__(self, headless=True):
        self.setup_driver(headless)
        self.projects_data = []
        
    def setup_driver(self, headless):
        """Setup Chrome WebDriver with options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            print("Chrome WebDriver initialized successfully")
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            raise
    
    def extract_basic_project_info(self, card):
        """Extract basic project information from project card"""
        try:
            project_data = {}
            
            # Project Name - from h5.card-title
            try:
                name_element = card.find_element(By.CSS_SELECTOR, "h5.card-title")
                project_data['Project Name'] = name_element.text.strip()
            except:
                project_data['Project Name'] = "N/A"
            
            # Promoter Name - from small tag after project name
            try:
                promoter_element = card.find_element(By.CSS_SELECTOR, "small")
                promoter_text = promoter_element.text.strip()
                if promoter_text.startswith("by "):
                    project_data['Promoter Name'] = promoter_text[3:]  # Remove "by " prefix
                else:
                    project_data['Promoter Name'] = promoter_text
            except:
                project_data['Promoter Name'] = "N/A"
            
            # RERA Registration Number - from span.fw-bold
            try:
                rera_element = card.find_element(By.CSS_SELECTOR, "span.fw-bold")
                project_data['Rera Regd. No'] = rera_element.text.strip()
            except:
                project_data['Rera Regd. No'] = "N/A"
            
            # Extract Address from the project details section
            try:
                # Look for the Address label and get the corresponding strong element
                address_elements = card.find_elements(By.XPATH, ".//label[contains(text(), 'Address')]/following-sibling::strong")
                if address_elements:
                    project_data['Project Address'] = address_elements[0].text.strip()
                else:
                    project_data['Project Address'] = "N/A"
            except:
                project_data['Project Address'] = "N/A"
            
            # Extract Project Type
            try:
                type_elements = card.find_elements(By.XPATH, ".//label[contains(text(), 'Project Type')]/following-sibling::strong")
                if type_elements:
                    project_data['Project Type'] = type_elements[0].text.strip()
                else:
                    project_data['Project Type'] = "N/A"
            except:
                project_data['Project Type'] = "N/A"
            
            # Extract Started From date
            try:
                start_elements = card.find_elements(By.XPATH, ".//label[contains(text(), 'Started From')]/following-sibling::strong")
                if start_elements:
                    project_data['Started From'] = start_elements[0].text.strip()
                else:
                    project_data['Started From'] = "N/A"
            except:
                project_data['Started From'] = "N/A"
            
            # Extract Possession by date
            try:
                possession_elements = card.find_elements(By.XPATH, ".//label[contains(text(), 'Possession by')]/following-sibling::strong")
                if possession_elements:
                    project_data['Possession by'] = possession_elements[0].text.strip()
                else:
                    project_data['Possession by'] = "N/A"
            except:
                project_data['Possession by'] = "N/A"
            
            # Extract Units information
            try:
                units_element = card.find_element(By.CSS_SELECTOR, ".apartment-unit strong")
                project_data['Units'] = units_element.text.strip()
            except:
                project_data['Units'] = "N/A"
            
            # Initialize fields that need to be extracted from detail page
            # GST No.
            
            return project_data
            
        except Exception as e:
            print(f"Error extracting basic project info: {e}")
            return None
    def extract_promoter_details(self, project_data):
        try:
            promoter_details = self.driver.find_elements(By.XPATH, ".//a[contains(text(),'Promoter Details')]")
            if promoter_details:
                print("Promoter Details link found, clicking to extract GST No. and Address...")
                print(promoter_details)
                #  promoter_details[0].click()
                promoter_tab = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Promoter Details')]"))
                )
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", promoter_tab)
                promoter_tab.click()
                print("Clicked 'Promoter Details' tab.")
                self.wait_for_loader_to_disappear()
                promoter_card = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".promoter.mb-4"))
                )
            else:
                print("Promoter Details link not found, skipping GST No. and Address extraction.")
            print("Extracting GST No. and Address of the Promoter...")
            promoter_card = self.driver.find_element(By.CSS_SELECTOR, ".promoter.mb-4")
            print("Promoter card found, extracting details...")
            try:
                print("Gst No. extraction will be done on detail page")
                gst_elem = WebDriverWait(promoter_card, 10).until(
                    EC.presence_of_element_located((By.XPATH, ".//label[contains(text(), 'GST No.')]/parent::div/strong"))
                )
                print("GST No. element found, waiting for text to be non-empty...")

                # Wait until text is non-empty
                self.wait.until(lambda d: gst_elem.text.strip() != "")
                print("GST No. text is non-empty, extracting...")
                gst = gst_elem.text.strip()
                project_data['GST No.'] = gst
            except:
                project_data['GST No.'] = "N/A"

            # Registered Office Address
            try:
                print("Extracting Registered Office Address...")
                # addr_div = promoter_card.find_elements(By.XPATH, "//label[contains(text(), 'Registered Office Address')]/following-sibling::strong").text
                addr = WebDriverWait(promoter_card, 10).until(
                    EC.presence_of_element_located((By.XPATH, ".//label[contains(text(), 'Registered Office Address')]/following-sibling::strong"))
                )
                print("addr element found, waiting for text to be non-empty...")

                # Wait until text is non-empty
                self.wait.until(lambda d: addr.text.strip() != "")
                print("addr text is non-empty, extracting...")
                address = addr.text.strip()
                # address = addr_div.text.replace("Registered Office Address", "").strip()
                project_data['Address of the Promoter'] = address
            except:
                project_data['Address of the Promoter'] = "N/A"
        except:
            print("Promoter card not found, skipping details extraction.")
            project_data['GST No.'] = "N/A"
            project_data['Address of the Promoter'] = "N/A"
        return project_data

    def scrape_projects(self):
        """Scrape the first 6 projects from ORERA website - basic info only"""
        data = []
        try:
            print("Navigating to ORERA projects page...")
            self.driver.get("https://rera.odisha.gov.in/projects")
            
            # Wait for page to load
            time.sleep(5)
            
            # Wait for project cards to load
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card.project-card")))
            
        
            for i in range(6):
                print(f"Scraping project {i+1}/6...")
                
                try:
                    project_cards = self.driver.find_elements(By.CSS_SELECTOR, ".card.project-card")
                    if len(project_cards) <= i:
                        print("Not enough project cards found.")
                        break
                    # Scroll the card into view
                    card = project_cards[i]
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                    time.sleep(1)

                    project_data = self.extract_basic_project_info(card)
                    view_button = card.find_element(By.XPATH, ".//a[contains(text(),'View Details')]")
                    
                    view_button.click()
                    print("Clicked on View Details button, waiting for details page to load...")
                    print("Navigated to details page.")

                    project_data = self.extract_promoter_details(project_data)

                    self.driver.back()
                    self.dismiss_popup()
                    
                    if project_data:
                        print(f"Project data extracted: {project_data}")
                        data.append(project_data)
                        self.save_to_json(project_data)
                        print(f"✓ Successfully scraped project: {project_data.get('Project Name', 'Unknown')}")
                    
                    # Small delay between projects
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error scraping project {i}: {e}")
                    continue
                
                if i >= 6:
                    print("Reached the limit of 6 projects, stopping further scraping.")
                    break
                # break added for testing purposes
        
        except Exception as e:
            print(f"Error during scraping: {e}")
            return []

        finally:
            print("Scraping completed. Saving results...", data)
            self.save_to_json(data)


    def wait_for_loader_to_disappear(self, timeout=10):
        #wait for animations
        try:
            WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ngx-overlay"))
            )
            time.sleep(0.5)  
        except TimeoutException:
            print("Loader did not disappear in time.")
    
    def save_to_json(self, projects, filename="orera_projects.json"):
        """Save scraped data to JSON file"""
        if not projects:
            print("No data to save")
            return
        try:
            print("Saving data to JSON...")
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(projects, f, indent=2, ensure_ascii=False)
            print(f"Data saved to {filename}")
        except Exception as e:
            print(f"Error saving to JSON: {e}")
    
    def display_results(self):
        """Display scraped results in a formatted way"""
        if not self.projects_data:
            print("No data to display")
            return
        
        print("\n" + "="*80)
        print("ORERA PROJECTS SCRAPING RESULTS")
        print("="*80)
        
        for i, project in enumerate(self.projects_data, 1):
            print(f"\nProject {i}:")
            print("-" * 40)
            for key, value in project.items():
                print(f"{key}: {value}")
            print("-" * 40)
    
    def cleanup(self):
        """Close the webdriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            print("WebDriver closed")

    def dismiss_popup(self):
        try:
                        print("Checking for popup...")
                        ok_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".swal2-confirm"))
                        )
                        print("Popup detected. Clicking OK to dismiss it.")
                        ok_button.click()
                        # Optional: wait for popup to fully disappear
                        WebDriverWait(self.driver, 5).until_not(
                            EC.presence_of_element_located((By.CLASS_NAME, "swal2-popup"))
                        )
                        print("Popup dismissed.")
        except TimeoutException:
                        print("No popup appeared after going back.")
        except Exception as e:
                        print(f"Unexpected error while handling popup: {e}")

def main():
    print("ORERA Projects Scraper")
    print("="*60)
    print("Target: First 6 projects with basic information")
    print("\nNote: This scraper requires ChromeDriver to be installed and in PATH")
    print("Install with: pip install selenium pandas")
    print("\n" + "-"*60)
    
    scraper = OdishaRERAScraper(headless=False)  # Set to True for headless mode
    
    try:
        # Scrape the projects (basic info only)
        results = scraper.scrape_projects()
        
        if results:
            scraper.display_results()
            
            
            print(f"\nSuccessfully scraped {len(results)} projects!")
    
    except Exception as e:
        print(f"Scraping failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure ChromeDriver is installed: https://chromedriver.chromium.org/")
        print("2. Check if the website is accessible")
        print("3. Website structure might have changed")
    
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()