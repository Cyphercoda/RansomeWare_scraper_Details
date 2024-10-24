import argparse
import csv
import random
import time
from datetime import datetime
import sys
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import undetected_chromedriver as uc

# Initialize colorama for colored output
init()

# Thread-safe printing
print_lock = threading.Lock()

def safe_print(*args, **kwargs):
    """Thread-safe printing function"""
    with print_lock:
        print(*args, **kwargs)

def random_delay():
    """Add random delay between actions to appear more human-like"""
    time.sleep(random.uniform(2, 4))

def human_like_mouse_movement(actions, element):
    """Simulate more human-like mouse movement"""
    actions.move_by_offset(5, 5)
    actions.move_by_offset(-5, -5)
    actions.move_to_element_with_offset(element, 0, 0)
    actions.pause(random.uniform(0.1, 0.3))
    actions.perform()
    actions.reset_actions()

def setup_selenium():
    """Configure and initialize Undetected ChromeDriver with minimal modifications."""
    options = uc.ChromeOptions()
    
    # Only add essential arguments
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    
    # Initialize undetected chromedriver
    driver = uc.Chrome(options=options)
    
    # Set window size to a standard desktop resolution
    driver.set_window_size(1920, 1080)
    
    return driver

def clean_company_name(name):
    """Clean company name by removing FULL LEAK and extra spaces"""
    if not name:
        return name
        
    # Convert to lower case for comparison
    name_lower = name.lower()
    
    # List of patterns to remove (case insensitive)
    patterns_to_remove = [
        '- full leak',
        '- Full Leak',
        '- FULL LEAK',
        '-full leak',
        '-Full Leak',
        '-FULL LEAK',
        'full leak',
        'full-leak',
        'full_leak',
        'fullleak',
        '[full leak]',
        '(full leak)',
        'leaked',
        'FULL LEAK',
        'FULLLEAK',
        'FullLeak',
        'Full Leak',
        'Full-Leak',
        'Full_Leak',
        '[FULL LEAK]',
        '(FULL LEAK)',
        'LEAKED',
        ' LEAK',
        '.LEAK',
        '_LEAK',
        '-LEAK',
        '- LEAK',
        ' - LEAK',
        '- leaked',
        '- LEAKED'
    ]
    
    # First clean using exact patterns
    cleaned_name = name
    for pattern in patterns_to_remove:
        # Remove pattern with any case
        cleaned_name = cleaned_name.replace(pattern, '')
        cleaned_name = cleaned_name.replace(pattern.lower(), '')
        cleaned_name = cleaned_name.replace(pattern.upper(), '')
        cleaned_name = cleaned_name.replace(pattern.capitalize(), '')
    
    # Remove any extra whitespace and trim
    cleaned_name = " ".join(cleaned_name.split())
    
    # Remove any remaining punctuation at the start/end
    cleaned_name = cleaned_name.strip('[](){} ._-')
    
    # Additional cleanup for any remaining "- " at the start
    cleaned_name = cleaned_name.lstrip('- ')
    
    safe_print(f"{Fore.CYAN}Original name: '{name}'{Style.RESET_ALL}")
    safe_print(f"{Fore.GREEN}Cleaned name: '{cleaned_name}'{Style.RESET_ALL}")
    
    return cleaned_name

def handle_captcha(driver):
    """Handle PerimeterX captcha with more human-like interaction."""
    try:
        # Wait for button with random delay
        button = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "px-captcha-error-button"))
        )
        
        safe_print(f"{Fore.YELLOW}Captcha detected - handling with human-like interaction...{Style.RESET_ALL}")
        
        # Create action chain
        actions = ActionChains(driver)
        
        # Move mouse naturally to button
        human_like_mouse_movement(actions, button)
        
        # Random initial delay before pressing
        time.sleep(random.uniform(0.5, 1.0))
        
        # Press and hold with natural movement
        actions.click_and_hold(button)
        actions.pause(random.uniform(0.1, 0.2))
        
        # Small mouse movements while holding
        for _ in range(3):
            actions.move_by_offset(random.uniform(-2, 2), random.uniform(-2, 2))
            actions.pause(random.uniform(0.1, 0.3))
        
        # Hold for random duration
        actions.pause(random.uniform(4.5, 5.5))
        
        # Release smoothly
        actions.release()
        actions.perform()
        
        # Wait with random delay
        time.sleep(random.uniform(2, 3))
        
        return True
    except Exception as e:
        safe_print(f"{Fore.RED}Error handling captcha: {str(e)}{Style.RESET_ALL}")
        return False

def get_ransomlook_data(driver, start_date, end_date):
    """Fetch data from ransomlook.io between specified dates."""
    safe_print(f"{Fore.CYAN}Fetching data from ransomlook.io for dates between {start_date.date()} and {end_date.date()}...{Style.RESET_ALL}")
    data = []
    page = 1
    has_more_pages = True

    while has_more_pages:
        try:
            url = f"https://www.ransomlook.io/recent?page={page}"
            safe_print(f"{Fore.CYAN}Fetching page {page}...{Style.RESET_ALL}")
            driver.get(url)
            random_delay()
            
            rows = driver.find_elements(By.TAG_NAME, "tr")
            past_date_range = False
            new_entries_found = False
            
            for row in rows[1:]:  # Skip header row
                try:
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if len(cols) >= 3:
                        date_text = cols[0].text.strip()
                        try:
                            entry_date = datetime.strptime(date_text, '%Y-%m-%d')
                            safe_print(f"{Fore.CYAN}Found entry date: {entry_date.date()}{Style.RESET_ALL}")
                            
                            if start_date <= entry_date <= end_date:
                                raw_name = cols[1].text.strip()
                                cleaned_name = clean_company_name(raw_name)
                                safe_print(f"{Fore.GREEN}Adding entry for {date_text}: {cleaned_name} (Original: {raw_name}){Style.RESET_ALL}")
                                
                                data.append({
                                    'date': date_text,
                                    'name': cleaned_name,
                                    'original_name': raw_name,
                                    'group': cols[2].text.strip()
                                })
                                new_entries_found = True
                            elif entry_date < start_date:
                                safe_print(f"{Fore.YELLOW}Date {entry_date.date()} is before start date {start_date.date()}{Style.RESET_ALL}")
                                past_date_range = True
                                break
                            else:
                                safe_print(f"{Fore.YELLOW}Date {entry_date.date()} is outside our range{Style.RESET_ALL}")
                                
                        except ValueError as e:
                            safe_print(f"{Fore.RED}Error parsing date {date_text}: {str(e)}{Style.RESET_ALL}")
                            continue
                            
                except Exception as e:
                    safe_print(f"{Fore.RED}Error processing row: {str(e)}{Style.RESET_ALL}")
                    continue
            
            if past_date_range or not new_entries_found:
                has_more_pages = False
            else:
                try:
                    next_button = driver.find_element(By.CSS_SELECTOR, "[aria-label='Next page']")
                    if not next_button.is_enabled():
                        has_more_pages = False
                    else:
                        page += 1
                except:
                    has_more_pages = False
            
        except Exception as e:
            safe_print(f"{Fore.RED}Error fetching page {page}: {str(e)}{Style.RESET_ALL}")
            has_more_pages = False
    
    safe_print(f"{Fore.GREEN}Found {len(data)} entries within date range{Style.RESET_ALL}")
    return data

def process_company(item, driver_queue):
    """Process a single company using a driver from the pool"""
    driver = None
    try:
        # Get a driver from the pool
        driver = driver_queue.get()
        
        safe_print(f"\n{Fore.CYAN}Processing: {item['name']}...{Style.RESET_ALL}")
        
        # Search and get company details
        search_url = f"https://www.google.com/search?q=zoominfo.com {item['name']}"
        safe_print(f"{Fore.CYAN}Searching: {search_url}{Style.RESET_ALL}")
        
        driver.get(search_url)
        random_delay()
        
        # Scroll behavior
        try:
            for _ in range(random.randint(2, 4)):
                driver.execute_script(f"window.scrollTo(0, {random.randint(100, 500)});")
                time.sleep(random.uniform(0.5, 1.0))
        except Exception:
            pass

        company_prefix = item['name'][:4].lower()
        headings = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "h3"))
        )
        
        matching_link = None
        matching_href = None
        
        for heading in headings:
            try:
                parent = heading.find_element(By.XPATH, "./..")
                if parent.tag_name == 'a':
                    link_text = heading.text.strip().lower()
                    href = parent.get_attribute('href')
                    
                    if ('zoominfo.com' in href) and link_text.startswith(company_prefix):
                        safe_print(f"{Fore.GREEN}Found matching heading: {link_text}{Style.RESET_ALL}")
                        matching_link = parent
                        matching_href = href
                        break
            except Exception:
                continue
        
        if not matching_link:
            result = {
                'Date': item['date'],
                'Name': item['name'],
                'Original_Name': item['original_name'],
                'Group': item['group'],
                'ZoomInfo_Details': 'No matching ZoomInfo page found',
                'Website': 'Not found',
                'Company_Name': 'Not found'
            }
            driver_queue.put(driver)
            return result

        # Try multiple methods to click the link
        click_successful = False
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", matching_link)
            time.sleep(1)
            matching_link.click()
            click_successful = True
        except:
            try:
                driver.execute_script("arguments[0].click();", matching_link)
                click_successful = True
            except:
                try:
                    if matching_href:
                        driver.get(matching_href)
                        click_successful = True
                except:
                    pass

        if not click_successful:
            result = {
                'Date': item['date'],
                'Name': item['name'],
                'Original_Name': item['original_name'],
                'Group': item['group'],
                'ZoomInfo_Details': 'Failed to access ZoomInfo page',
                'Website': 'Not found',
                'Company_Name': 'Not found'
            }
            driver_queue.put(driver)
            return result

        random_delay()

        # Handle captcha if present
        if "Press & Hold to confirm" in driver.page_source:
            handle_captcha(driver)
            random_delay()

        # Extract company information
        company_info = {'details': '', 'website': '', 'company_name': ''}
        
        try:
            company_name_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "company-name"))
            )
            company_info['company_name'] = company_name_element.text
        except:
            company_info['company_name'] = "Not found"

        try:
            company_details = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "company-header-subtitle"))
            )
            company_info['details'] = company_details.text
        except:
            company_info['details'] = "Not found"

        try:
            website_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a.website-link"))
            )
            website_url = website_element.text or website_element.get_attribute('href')
            if website_url.startswith('//'):
                website_url = website_url[2:]
            company_info['website'] = website_url
        except:
            company_info['website'] = "Not found"

        # Print fetched data
        safe_print(f"\n{Fore.GREEN}Fetched Data:{Style.RESET_ALL}")
        safe_print(f"{Fore.YELLOW}Date:{Style.RESET_ALL} {item['date']}")
        safe_print(f"{Fore.YELLOW}Company:{Style.RESET_ALL} {item['name']}")
        safe_print(f"{Fore.YELLOW}Group:{Style.RESET_ALL} {item['group']}")
        safe_print(f"{Fore.YELLOW}Details:{Style.RESET_ALL} {company_info['details']}")
        safe_print(f"{Fore.YELLOW}Website:{Style.RESET_ALL} {company_info['website']}")
        safe_print(f"{Fore.YELLOW}Company Name:{Style.RESET_ALL} {company_info['company_name']}")
        safe_print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")

        result = {
            'Date': item['date'],
            'Name': item['name'],
            'Original_Name': item['original_name'],
            'Group': item['group'],
            'ZoomInfo_Details': company_info['details'],
            'Website': company_info['website'],
            'Company_Name': company_info['company_name']
        }

        # Return driver to the pool
        driver_queue.put(driver)
        return result

    except Exception as e:
        safe_print(f"{Fore.RED}Error processing {item['name']}: {str(e)}{Style.RESET_ALL}")
        if driver:
            driver_queue.put(driver)
        return {
            'Date': item['date'],
            'Name': item['name'],
            'Original_Name': item['original_name'],
            'Group': item['group'],
            'ZoomInfo_Details': f"Error: {str(e)}",
            'Website': 'Not found',
            'Company_Name': 'Not found'
        }

def main():
    try:
        parser = argparse.ArgumentParser(description='Multi-threaded web scraper with website extraction')
        parser.add_argument('--start-date', required=True, help='Start date (YYYY-MM-DD)')
        parser.add_argument('--end-date', required=True, help='End date (YYYY-MM-DD)')
        parser.add_argument('--output-csv', default='company_data.csv', help='Output CSV file name')
        parser.add_argument('--threads', type=int, default=3, help='Number of parallel threads')
        
        args = parser.parse_args()
        
        # Initialize driver pool
        safe_print(f"{Fore.CYAN}Initializing {args.threads} browser instances...{Style.RESET_ALL}")
        driver_queue = Queue()
        for _ in range(args.threads):
            driver = setup_selenium()
            driver_queue.put(driver)
        
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
        end_date = datetime.strptime(args.end_date, '%Y-%m-%d')
        
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        
        # Get initial data using first driver
        initial_driver = driver_queue.get()
        data = get_ransomlook_data(initial_driver, start_date, end_date)
        driver_queue.put(initial_driver)
        
        if not data:
            safe_print(f"{Fore.RED}No data found within the specified date range. Exiting...{Style.RESET_ALL}")
            return
        
        safe_print(f"\n{Fore.GREEN}Processing {len(data)} entries with {args.threads} threads...{Style.RESET_ALL}")
        
        results = []
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            # Submit all tasks
            future_to_item = {
                executor.submit(process_company, item, driver_queue): item 
                for item in data
            }
            
            # Process completed tasks and show progress
            completed = 0
            total = len(future_to_item)
            
            for future in future_to_item:
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    completed += 1
                    safe_print(f"{Fore.CYAN}Progress: {completed}/{total} companies processed{Style.RESET_ALL}")
                except Exception as e:
                    safe_print(f"{Fore.RED}Error processing company: {str(e)}{Style.RESET_ALL}")
        
        # Write results to CSV
        with open(args.output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Date', 'Name', 'Original_Name', 'Group', 'ZoomInfo_Details', 'Website', 'Company_Name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        safe_print(f"\n{Fore.GREEN}Data has been saved to {args.output_csv}{Style.RESET_ALL}")
        safe_print(f"{Fore.GREEN}Successfully processed {len(results)} out of {len(data)} companies{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        safe_print(f"\n{Fore.YELLOW}Script interrupted by user. Saving current progress...{Style.RESET_ALL}")
    except Exception as e:
        safe_print(f"{Fore.RED}Fatal error in main: {str(e)}{Style.RESET_ALL}")
        raise
    finally:
        # Clean up all drivers
        safe_print(f"\n{Fore.CYAN}Cleaning up browser instances...{Style.RESET_ALL}")
        while not driver_queue.empty():
            driver = driver_queue.get()
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    main()