import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as undetec
import os
from selenium.webdriver.common.action_chains import ActionChains
import shutil
import subprocess
import logging
from datetime import datetime
import json

FIXED_PROXY = "http://103.214.8.89:10000"

USER_AGENTS = [
    # Desktop user agents
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Mobile user agents
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36"
]

SEARCH_KEYWORDS = [
    "vpsx.me", "vpsx.me review", "vpsx.me proxy", "vpsx.me là gì", "vpsx.me tốc độ", "vpsx.me giá rẻ",
    "vpsx hosting", "vpsx server", "vpsx proxy vietnam", "vpsx vps", "vpsx.me đánh giá",
    "vpsx.me chất lượng", "vpsx.me dịch vụ", "vpsx.me hỗ trợ", "vpsx proxy service"
]

SEARCH_ENGINES = {
    "google": {
        "url": "https://www.google.com",
        "search_box": 'input[name="q"]',
        "search_button": 'input[type="submit"]'
    },
    "bing": {
        "url": "https://www.bing.com",
        "search_box": 'input[name="q"]',
        "search_button": 'input[type="submit"]'
    },
    "coccoc": {
        "url": "https://coccoc.com",
        "search_box": 'input[name="query"]',
        "search_button": 'button[type="submit"]'
    }
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traffic_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Traffic statistics
traffic_stats = {
    "total_visits": 0,
    "direct_visits": 0,
    "search_visits": 0,
    "successful_visits": 0,
    "failed_visits": 0,
    "search_engines_used": {"google": 0, "bing": 0, "coccoc": 0},
    "start_time": datetime.now()
}

# Khởi tạo trình duyệt với proxy

def get_driver(proxy=None):
    chrome_options = Options()
    
    # Tạo profile mới cho mỗi lần chạy
    profile_id = random.randint(100000, 999999)
    profile_dir = os.path.abspath(f"profiles/profile_{profile_id}")
    os.makedirs(profile_dir, exist_ok=True)
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    
    # Random user-agent
    user_agent = random.choice(USER_AGENTS)
    chrome_options.add_argument(f'--user-agent={user_agent}')
    
    # Random window size based on user agent type
    if "Mobile" in user_agent or "iPhone" in user_agent or "Android" in user_agent:
        # Mobile sizes
        w = random.randint(360, 414)
        h = random.randint(640, 896)
    else:
        # Desktop sizes
        w = random.randint(1024, 1920)
        h = random.randint(768, 1080)
    
    chrome_options.add_argument(f'--window-size={w},{h}')
    
    # Additional options to avoid detection
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--allow-running-insecure-content')
    chrome_options.add_argument('--disable-extensions')
    
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    
    try:
        driver = undetec.Chrome(options=chrome_options)
        # Hide webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver, profile_dir
    except Exception as e:
        logging.error(f"Failed to create driver: {e}")
        return None, profile_dir

# Scroll random trên trang
def random_scroll(driver, min_scroll=3, max_scroll=10):
    try:
        scroll_times = random.randint(min_scroll, max_scroll)
        for i in range(scroll_times):
            # Random scroll direction and amount
            if random.choice([True, False]):
                driver.execute_script(f"window.scrollBy(0, {random.randint(200, 800)});")
            else:
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
            
            # Random pause between scrolls
            time.sleep(random.uniform(0.5, 2.5))
            
            # Sometimes scroll back up
            if i > 0 and random.random() < 0.3:
                driver.execute_script(f"window.scrollBy(0, -{random.randint(100, 400)});")
                time.sleep(random.uniform(0.3, 1.0))
    except Exception as e:
        logging.warning(f"Error during scrolling: {e}")

# Thao tác chuột random
def random_mouse_move(driver):
    try:
        body = driver.find_element(By.TAG_NAME, 'body')
        actions = ActionChains(driver)
        
        # Get window size for realistic mouse movements
        window_size = driver.get_window_size()
        max_x = min(window_size['width'] - 100, 800)
        max_y = min(window_size['height'] - 100, 600)
        
        for _ in range(random.randint(3, 8)):
            x = random.randint(50, max_x)
            y = random.randint(50, max_y)
            actions.move_to_element_with_offset(body, x, y).perform()
            time.sleep(random.uniform(0.1, 0.8))
            
            # Sometimes perform a small random movement
            if random.random() < 0.4:
                small_x = random.randint(-20, 20)
                small_y = random.randint(-20, 20)
                actions.move_by_offset(small_x, small_y).perform()
                time.sleep(random.uniform(0.1, 0.3))
                
    except Exception as e:
        logging.warning(f"Error during mouse movement: {e}")

# Check if search engine is blocked
def is_search_engine_blocked(driver):
    try:
        # Check for common blocking indicators
        page_source = driver.page_source.lower()
        blocked_indicators = [
            "captcha", "robot", "automation", "blocked", "403 forbidden",
            "access denied", "too many requests", "rate limit"
        ]
        
        for indicator in blocked_indicators:
            if indicator in page_source:
                return True
                
        # Check for CAPTCHA elements
        captcha_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'captcha') or contains(@id, 'captcha')]")
        if captcha_elements:
            return True
            
        return False
    except Exception:
        return True

# Enhanced natural browsing behavior
def natural_browsing_behavior(driver, min_time=30, max_time=300):
    """Simulate natural user behavior on a website"""
    try:
        start_time = time.time()
        dwell_time = random.randint(min_time, max_time)
        
        # Determine if this is a bounce (30% chance)
        is_bounce = random.random() < 0.3
        
        if is_bounce:
            # Quick bounce - just scroll a bit and leave
            logging.info("Simulating bounce behavior")
            random_scroll(driver, 1, 3)
            time.sleep(random.uniform(5, 15))
            return
        
        # Normal browsing behavior
        logging.info(f"Simulating normal browsing for {dwell_time} seconds")
        
        actions_performed = 0
        max_actions = random.randint(3, 8)
        
        while time.time() - start_time < dwell_time and actions_performed < max_actions:
            action = random.choice(['scroll', 'mouse_move', 'click_link', 'wait'])
            
            if action == 'scroll':
                random_scroll(driver, 2, 5)
                actions_performed += 1
                
            elif action == 'mouse_move':
                random_mouse_move(driver)
                actions_performed += 1
                
            elif action == 'click_link':
                # Try to click internal links
                try:
                    links = driver.find_elements(By.TAG_NAME, 'a')
                    internal_links = []
                    
                    for link in links:
                        href = link.get_attribute('href')
                        if href and ('vpsx.me' in href or href.startswith('/')):
                            if link.is_displayed() and link.is_enabled():
                                internal_links.append(link)
                    
                    if internal_links and random.random() < 0.7:  # 70% chance to click
                        link = random.choice(internal_links)
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                        time.sleep(random.uniform(0.5, 1.5))
                        
                        try:
                            link.click()
                            logging.info(f"Clicked internal link: {link.get_attribute('href')}")
                            time.sleep(random.uniform(2, 5))
                            random_scroll(driver, 1, 3)
                            actions_performed += 1
                        except Exception:
                            try:
                                driver.execute_script("arguments[0].click();", link)
                                logging.info(f"JS clicked internal link: {link.get_attribute('href')}")
                                time.sleep(random.uniform(2, 5))
                                actions_performed += 1
                            except Exception as e:
                                logging.warning(f"Failed to click link: {e}")
                                
                except Exception as e:
                    logging.warning(f"Error finding/clicking links: {e}")
                    
            elif action == 'wait':
                time.sleep(random.uniform(3, 8))
            
            # Random pause between actions
            time.sleep(random.uniform(1, 4))
            
    except Exception as e:
        logging.error(f"Error in natural browsing behavior: {e}")

# Search on search engines with fallback
def search_with_fallback(proxy=None, max_retry=3):
    """Search for vpsx.me with fallback to different search engines"""
    search_engines = ['google', 'bing', 'coccoc']
    random.shuffle(search_engines)  # Randomize order
    
    for engine in search_engines:
        for attempt in range(max_retry):
            driver = None
            profile_dir = None
            
            try:
                logging.info(f"Attempting search on {engine} (attempt {attempt + 1})")
                driver, profile_dir = get_driver(proxy)
                
                if not driver:
                    continue
                
                # Navigate to search engine
                engine_config = SEARCH_ENGINES[engine]
                driver.get(engine_config["url"])
                time.sleep(random.uniform(2, 5))
                
                # Check if blocked
                if is_search_engine_blocked(driver):
                    logging.warning(f"{engine} appears to be blocked")
                    driver.quit()
                    force_delete_profile(profile_dir)
                    break  # Try next search engine
                
                # Perform search
                random_mouse_move(driver)
                keyword = random.choice(SEARCH_KEYWORDS)
                
                try:
                    search_box = driver.find_element(By.CSS_SELECTOR, engine_config["search_box"])
                except:
                    search_box = driver.find_element(By.NAME, 'q')
                
                # Type search query naturally
                for char in keyword:
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.05, 0.2))
                
                search_box.send_keys(Keys.RETURN)
                time.sleep(random.uniform(3, 6))
                
                # Look for vpsx.me links
                vpsx_links = []
                
                # Try different methods to find vpsx.me links
                try:
                    links = driver.find_elements(By.PARTIAL_LINK_TEXT, 'vpsx.me')
                    vpsx_links.extend(links)
                except:
                    pass
                
                if not vpsx_links:
                    all_links = driver.find_elements(By.TAG_NAME, 'a')
                    for link in all_links:
                        href = link.get_attribute('href')
                        if href and 'vpsx.me' in href:
                            vpsx_links.append(link)
                            break
                
                if vpsx_links:
                    # Click on vpsx.me link
                    target_link = vpsx_links[0]
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_link)
                    time.sleep(random.uniform(1, 2))
                    
                    try:
                        target_link.click()
                    except:
                        driver.execute_script("arguments[0].click();", target_link)
                    
                    logging.info(f"Successfully clicked vpsx.me link from {engine}")
                    time.sleep(random.uniform(2, 4))
                    
                    # Perform natural browsing on vpsx.me
                    natural_browsing_behavior(driver)
                    
                    traffic_stats["search_engines_used"][engine] += 1
                    traffic_stats["search_visits"] += 1
                    traffic_stats["successful_visits"] += 1
                    
                    driver.quit()
                    force_delete_profile(profile_dir)
                    return True
                else:
                    logging.warning(f"No vpsx.me links found on {engine}")
                    
                driver.quit()
                force_delete_profile(profile_dir)
                break  # Try next search engine
                
            except Exception as e:
                logging.error(f"Error with {engine}: {e}")
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                if profile_dir:
                    force_delete_profile(profile_dir)
                
                if attempt == max_retry - 1:
                    break  # Try next search engine
                else:
                    time.sleep(random.uniform(2, 5))
    
    logging.warning("All search engines failed, falling back to direct access")
    return False

# Direct visit to vpsx.me
def visit_vpsx_direct(proxy=None, max_retry=3):
    """Direct visit to vpsx.me"""
    for attempt in range(max_retry):
        driver = None
        profile_dir = None
        
        try:
            logging.info(f"Direct visit to vpsx.me (attempt {attempt + 1})")
            driver, profile_dir = get_driver(proxy)
            
            if not driver:
                continue
            
            driver.get('https://vpsx.me')
            time.sleep(random.uniform(2, 5))
            
            # Perform natural browsing behavior
            natural_browsing_behavior(driver)
            
            traffic_stats["direct_visits"] += 1
            traffic_stats["successful_visits"] += 1
            
            driver.quit()
            force_delete_profile(profile_dir)
            return True
            
        except Exception as e:
            logging.error(f"Error in direct visit: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            if profile_dir:
                force_delete_profile(profile_dir)
            
            if attempt < max_retry - 1:
                time.sleep(random.uniform(2, 5))
    
    traffic_stats["failed_visits"] += 1
    return False

# Force delete profile directory
def force_delete_profile(profile_dir, max_retry=3):
    """Force delete profile directory with retry mechanism"""
    for attempt in range(max_retry):
        try:
            # Kill all chrome processes to release file locks
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], 
                          shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        
        try:
            if os.path.exists(profile_dir):
                shutil.rmtree(profile_dir)
            break
        except Exception as e:
            if attempt < max_retry - 1:
                time.sleep(1)
                continue
            else:
                logging.warning(f"Failed to delete profile {profile_dir}: {e}")

def cleanup_profiles():
    """Clean up all profile directories"""
    profiles_dir = os.path.abspath("profiles")
    if os.path.exists(profiles_dir):
        for name in os.listdir(profiles_dir):
            path = os.path.join(profiles_dir, name)
            if os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    logging.warning(f"Failed to cleanup profile {path}: {e}")

# Legacy functions (keeping for compatibility)
def visit_vpsx_me(proxy=None):
    """Legacy function - redirects to new direct visit function"""
    return visit_vpsx_direct(proxy)

def search_and_click_google(proxy=None):
    """Legacy function - redirects to new search function"""
    return search_with_fallback(proxy)

def search_google_only(proxy=None):
    """Legacy function - redirects to new search function"""
    return search_with_fallback(proxy)

def visit_alibaba_then_vpsx(proxy=None, max_retry=20):
    """Legacy function - redirects to new direct visit function"""
    return visit_vpsx_direct(proxy, max_retry)

# Print traffic statistics
def print_traffic_stats():
    """Print current traffic statistics"""
    elapsed_time = datetime.now() - traffic_stats["start_time"]
    
    print("\n" + "="*50)
    print("TRAFFIC STATISTICS")
    print("="*50)
    print(f"Runtime: {elapsed_time}")
    print(f"Total visits: {traffic_stats['total_visits']}")
    print(f"Successful visits: {traffic_stats['successful_visits']}")
    print(f"Failed visits: {traffic_stats['failed_visits']}")
    print(f"Success rate: {(traffic_stats['successful_visits']/max(traffic_stats['total_visits'], 1)*100):.1f}%")
    print("\nVisit types:")
    print(f"  Direct visits: {traffic_stats['direct_visits']}")
    print(f"  Search visits: {traffic_stats['search_visits']}")
    print("\nSearch engines used:")
    for engine, count in traffic_stats['search_engines_used'].items():
        print(f"  {engine.capitalize()}: {count}")
    print("="*50)

# Save statistics to file
def save_stats_to_file():
    """Save traffic statistics to JSON file"""
    try:
        stats_copy = traffic_stats.copy()
        stats_copy["start_time"] = stats_copy["start_time"].isoformat()
        stats_copy["last_updated"] = datetime.now().isoformat()
        
        with open('traffic_stats.json', 'w', encoding='utf-8') as f:
            json.dump(stats_copy, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to save stats: {e}")

# Enhanced run_traffic function
def run_traffic():
    """
    Main function to simulate natural traffic to vpsx.me
    Implements 50/50 split between direct access and search-based access
    """
    cleanup_profiles()  # Clean up old profiles
    proxy = FIXED_PROXY
    
    logging.info("Starting traffic simulation to vpsx.me")
    logging.info(f"Using proxy: {proxy}")
    
    visit_count = 0
    
    try:
        while True:
            visit_count += 1
            traffic_stats["total_visits"] += 1
            
            # Random delay between visits (1-10 minutes)
            delay_between_visits = random.uniform(60, 600)
            
            logging.info(f"\n--- Visit #{visit_count} ---")
            
            # 50/50 split: direct vs search
            visit_type = random.choice(['direct', 'search'])
            
            success = False
            
            if visit_type == 'direct':
                logging.info("Performing direct visit")
                success = visit_vpsx_direct(proxy)
            else:
                logging.info("Performing search-based visit")
                success = search_with_fallback(proxy)
                
                # If search fails, fallback to direct
                if not success:
                    logging.info("Search failed, falling back to direct visit")
                    success = visit_vpsx_direct(proxy)
            
            if success:
                logging.info(f"Visit #{visit_count} completed successfully")
            else:
                logging.error(f"Visit #{visit_count} failed")
            
            # Print stats every 10 visits
            if visit_count % 10 == 0:
                print_traffic_stats()
                save_stats_to_file()
            
            # Wait before next visit
            logging.info(f"Waiting {delay_between_visits:.1f} seconds before next visit...")
            time.sleep(delay_between_visits)
            
    except KeyboardInterrupt:
        logging.info("\nTraffic simulation stopped by user")
        print_traffic_stats()
        save_stats_to_file()
    except Exception as e:
        logging.error(f"Unexpected error in run_traffic: {e}")
        print_traffic_stats()
        save_stats_to_file()
    finally:
        cleanup_profiles()

# Demo function for testing
def run_demo_traffic(num_visits=5):
    """
    Demo function to run a few visits for testing
    """
    cleanup_profiles()
    proxy = FIXED_PROXY
    
    logging.info(f"Starting demo traffic simulation - {num_visits} visits")
    
    for i in range(num_visits):
        traffic_stats["total_visits"] += 1
        
        logging.info(f"\n--- Demo Visit #{i+1}/{num_visits} ---")
        
        # Alternate between direct and search for demo
        if i % 2 == 0:
            logging.info("Demo: Performing direct visit")
            success = visit_vpsx_direct(proxy)
        else:
            logging.info("Demo: Performing search-based visit")
            success = search_with_fallback(proxy)
        
        if success:
            logging.info(f"Demo visit #{i+1} completed successfully")
        else:
            logging.error(f"Demo visit #{i+1} failed")
        
        # Short delay between demo visits
        if i < num_visits - 1:
            delay = random.uniform(30, 60)
            logging.info(f"Waiting {delay:.1f} seconds before next demo visit...")
            time.sleep(delay)
    
    print_traffic_stats()
    save_stats_to_file()
    cleanup_profiles()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        # Run demo mode
        num_visits = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        run_demo_traffic(num_visits)
    else:
        # Run full traffic simulation
        run_traffic()
