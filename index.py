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

def get_current_ip(proxy=None):
    """Get current IP address using multiple services (with optional proxy)"""
    ip_services = [
        "https://api.ipify.org",
        "https://ipinfo.io/ip",
        "https://checkip.amazonaws.com",
        "https://api.ip.sb/ip"
    ]
    
    # Setup proxy if provided
    proxies = None
    if proxy:
        proxies = {
            'http': proxy,
            'https': proxy
        }
    
    for service in ip_services:
        try:
            response = requests.get(service, timeout=10, proxies=proxies)
            if response.status_code == 200:
                return response.text.strip()
        except Exception:
            continue
    
    return "Unknown"

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
    "vpsx.me", "vpsx.me blogs", "vpsx.me proxy", "vpsx.me là gì", "vpsx.me tốc độ", "vpsx.me giá rẻ",
    "vpsx.me hosting", "vpsx server", "vpsx proxy vietnam", "vpsx vps", "vpsx.me đánh giá",
    "vpsx.me chất lượng", "vpsx.me dịch vụ", "vpsx.me hỗ trợ", "vpsx.me proxy service"
]

SEARCH_ENGINES = {
    "google": {
        "url": "https://www.google.com",
        "search_box": 'input[name="q"]',
        "search_button": 'input[type="submit"]'
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
    "search_engines_used": {"google": 0},
    "start_time": datetime.now()
}

# Khởi tạo trình duyệt với proxy

def get_driver(proxy=None):
    """Create Chrome driver with optimized options for compatibility"""
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
    
    # Basic options for stability
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    
    # Anti-detection options (simplified)
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    
    try:
        # Try with undetected chrome first
        driver = undetec.Chrome(options=chrome_options)
        
        # Hide webdriver property if possible
        try:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception:
            pass
            
        logging.info(f"Chrome driver created successfully with profile: {profile_dir}")
        return driver, profile_dir
        
    except Exception as e:
        logging.error(f"Failed to create undetected Chrome driver: {e}")
        
        # Fallback to regular Chrome
        try:
            logging.info("Trying fallback to regular Chrome driver...")
            # Remove undetected-specific options for regular Chrome
            chrome_options_fallback = Options()
            chrome_options_fallback.add_argument(f'--user-data-dir={profile_dir}')
            chrome_options_fallback.add_argument(f'--user-agent={user_agent}')
            chrome_options_fallback.add_argument(f'--window-size={w},{h}')
            chrome_options_fallback.add_argument('--no-sandbox')
            chrome_options_fallback.add_argument('--disable-dev-shm-usage')
            chrome_options_fallback.add_argument('--disable-gpu')
            
            if proxy:
                chrome_options_fallback.add_argument(f'--proxy-server={proxy}')
            
            driver = webdriver.Chrome(options=chrome_options_fallback)
            logging.info("Regular Chrome driver created successfully")
            return driver, profile_dir
            
        except Exception as e2:
            logging.error(f"Failed to create regular Chrome driver: {e2}")
            return None, profile_dir

# Scroll random trên trang
def random_scroll(driver, min_scroll=3, max_scroll=10):
    try:
        scroll_times = random.randint(min_scroll, max_scroll)
        
        for i in range(scroll_times):
            try:
                # Random scroll method
                scroll_method = random.choice(['pagedown', 'javascript', 'wheel'])
                
                if scroll_method == 'pagedown':
                    # Traditional page down
                    body = driver.find_element(By.TAG_NAME, 'body')
                    body.send_keys(Keys.PAGE_DOWN)
                    
                elif scroll_method == 'javascript':
                    # JavaScript scroll with random amount
                    scroll_amount = random.randint(200, 600)
                    if random.choice([True, False]):
                        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                    else:
                        driver.execute_script(f"window.scrollBy(0, -{scroll_amount//2});")
                        
                else:  # wheel
                    # Simulate mouse wheel
                    body = driver.find_element(By.TAG_NAME, 'body')
                    actions = ActionChains(driver)
                    actions.move_to_element(body).perform()
                    time.sleep(0.1)
                    
                    # Multiple small scrolls
                    for _ in range(random.randint(2, 4)):
                        if random.choice([True, False]):
                            body.send_keys(Keys.ARROW_DOWN)
                        else:
                            body.send_keys(Keys.PAGE_DOWN)
                        time.sleep(random.uniform(0.1, 0.3))
                
                # Random pause between scrolls
                time.sleep(random.uniform(0.5, 2.5))
                
                # Sometimes scroll back up (but less than we scrolled down)
                if i > 0 and random.random() < 0.2:  # Reduced probability
                    back_scroll = random.randint(100, 300)
                    try:
                        driver.execute_script(f"window.scrollBy(0, -{back_scroll});")
                        time.sleep(random.uniform(0.3, 1.0))
                    except Exception:
                        pass
                        
            except Exception as e:
                logging.warning(f"Error in individual scroll action: {e}")
                # Try simple fallback scroll
                try:
                    driver.execute_script("window.scrollBy(0, 300);")
                    time.sleep(1)
                except Exception:
                    pass
                continue
                
    except Exception as e:
        logging.warning(f"Error during scrolling: {e}")
        # Final fallback - simple JavaScript scroll
        try:
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)
        except Exception:
            logging.warning("All scroll methods failed")

# Thao tác chuột random
def random_mouse_move(driver):
    try:
        # Get actual window size and viewport size
        window_size = driver.get_window_size()
        
        # Get viewport size (visible area)
        viewport_width = driver.execute_script("return window.innerWidth;")
        viewport_height = driver.execute_script("return window.innerHeight;")
        
        # Use smaller safe area to avoid out of bounds
        safe_width = min(viewport_width - 100, 600)
        safe_height = min(viewport_height - 100, 400)
        
        # Ensure minimum safe area
        if safe_width < 100:
            safe_width = 100
        if safe_height < 100:
            safe_height = 100
        
        body = driver.find_element(By.TAG_NAME, 'body')
        actions = ActionChains(driver)
        
        # Perform safer mouse movements
        num_moves = random.randint(2, 5)  # Reduced number of moves
        
        for i in range(num_moves):
            try:
                # Generate safe coordinates
                x = random.randint(50, safe_width - 50)
                y = random.randint(50, safe_height - 50)
                
                # Move to element with offset using safe coordinates
                actions.move_to_element_with_offset(body, x, y).perform()
                time.sleep(random.uniform(0.2, 0.8))
                
                # Sometimes perform a small random movement
                if random.random() < 0.3 and i < num_moves - 1:
                    small_x = random.randint(-10, 10)
                    small_y = random.randint(-10, 10)
                    
                    # Check bounds before small movement
                    if (x + small_x > 10 and x + small_x < safe_width - 10 and 
                        y + small_y > 10 and y + small_y < safe_height - 10):
                        actions.move_by_offset(small_x, small_y).perform()
                        time.sleep(random.uniform(0.1, 0.3))
                        
            except Exception as e:
                logging.warning(f"Error in individual mouse movement: {e}")
                # Continue with next movement
                continue
                
    except Exception as e:
        logging.warning(f"Error during mouse movement: {e}")
        # Try alternative simple mouse movement
        try:
            # Fallback: just move to center of page
            body = driver.find_element(By.TAG_NAME, 'body')
            actions = ActionChains(driver)
            actions.move_to_element(body).perform()
            time.sleep(0.5)
        except Exception:
            # If even this fails, just skip mouse movement
            logging.warning("All mouse movement methods failed, skipping")
            pass

# Check if search engine is blocked
def is_search_engine_blocked(driver):
    try:
        # Check for common blocking indicators
        page_source = driver.page_source.lower()
        blocked_indicators = [
            "captcha", "robot", "automation", "blocked", "403 forbidden",
            "access denied", "too many requests", "rate limit", "unusual traffic"
        ]
        
        # Check page title for blocking signs
        try:
            page_title = driver.title.lower()
            if any(indicator in page_title for indicator in ["blocked", "captcha", "error"]):
                return True
        except:
            pass
        
        # Only consider it blocked if we find strong indicators
        strong_indicators = ["captcha", "blocked", "403 forbidden", "rate limit"]
        for indicator in strong_indicators:
            if indicator in page_source:
                return True
                
        # Check for CAPTCHA elements (more specific)
        try:
            captcha_elements = driver.find_elements(By.XPATH, 
                "//*[contains(@class, 'captcha') or contains(@id, 'captcha') or contains(@class, 'recaptcha')]")
            if captcha_elements:
                return True
        except:
            pass
            
        # Check if we can't find the search box (might indicate blocking)
        try:
            search_boxes = driver.find_elements(By.NAME, 'q')
            if not search_boxes:
                # Try alternative search box selectors
                search_boxes = driver.find_elements(By.CSS_SELECTOR, 'input[type="search"]')
                if not search_boxes:
                    return True
        except:
            return True
            
        return False
    except Exception:
        return True

# Enhanced natural browsing behavior
def natural_browsing_behavior(driver, min_time=15, max_time=50):
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
            time.sleep(random.uniform(3, 8))
            return
        
        # Normal browsing behavior
        logging.info(f"Simulating normal browsing for {dwell_time} seconds")
        
        actions_performed = 0
        max_actions = random.randint(3, 8)
        
        while time.time() - start_time < dwell_time and actions_performed < max_actions:
            # Add some randomness to action selection
            action_weights = {
                'scroll': 0.4,
                'mouse_move': 0.2, 
                'click_link': 0.3,
                'wait': 0.1
            }
            
            action = random.choices(
                list(action_weights.keys()), 
                weights=list(action_weights.values())
            )[0]
            
            try:
                if action == 'scroll':
                    random_scroll(driver, 2, 5)
                    actions_performed += 1
                    
                elif action == 'mouse_move':
                    random_mouse_move(driver)
                    actions_performed += 1
                    
                elif action == 'click_link':
                    # Try to click internal links with better error handling
                    try:
                        # Wait a bit for page to load
                        time.sleep(random.uniform(1, 2))
                        
                        links = driver.find_elements(By.TAG_NAME, 'a')
                        internal_links = []
                        
                        for link in links[:20]:  # Limit to first 20 links for performance
                            try:
                                href = link.get_attribute('href')
                                if href and ('vpsx.me' in href or href.startswith('/')):
                                    if link.is_displayed() and link.is_enabled():
                                        # Check if link has reasonable text
                                        link_text = link.text.strip()
                                        if len(link_text) > 0 and len(link_text) < 50:
                                            internal_links.append(link)
                            except Exception:
                                continue
                        
                        if internal_links and random.random() < 0.6:  # 60% chance to click
                            link = random.choice(internal_links[:5])  # Choose from top 5
                            
                            try:
                                # Scroll to link first
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                                time.sleep(random.uniform(0.5, 1.5))
                                
                                # Get link info before clicking
                                link_href = link.get_attribute('href')
                                link_text = link.text[:30] + "..." if len(link.text) > 30 else link.text
                                
                                # Try normal click first
                                link.click()
                                logging.info(f"Clicked internal link: {link_text} -> {link_href}")
                                
                            except Exception:
                                try:
                                    # Fallback to JavaScript click
                                    driver.execute_script("arguments[0].click();", link)
                                    logging.info(f"JS clicked internal link: {link_text}")
                                except Exception as e:
                                    logging.warning(f"Failed to click link: {e}")
                                    continue
                            
                            # Wait after clicking
                            time.sleep(random.uniform(2, 5))
                            random_scroll(driver, 1, 3)
                            actions_performed += 1
                            
                    except Exception as e:
                        logging.warning(f"Error finding/clicking links: {e}")
                        
                elif action == 'wait':
                    time.sleep(random.uniform(3, 8))
                
                # Random pause between actions
                time.sleep(random.uniform(1, 4))
                
            except Exception as e:
                logging.warning(f"Error in action '{action}': {e}")
                time.sleep(random.uniform(1, 3))
                continue
            
    except Exception as e:
        logging.error(f"Error in natural browsing behavior: {e}")
        # Minimal fallback behavior
        try:
            time.sleep(random.uniform(5, 15))
            random_scroll(driver, 1, 2)
        except Exception:
            time.sleep(8)

# Search on search engines with fallback
def search_with_fallback(proxy=None, max_retry=3):
    """Search for vpsx.me using Google search"""
    
    # Get and log current IP
    current_ip = get_current_ip(proxy)
    logging.info(f"Starting Google search visit with IP: {current_ip}")
    
    for attempt in range(max_retry):
        driver = None
        profile_dir = None
        
        try:
            logging.info(f"Attempting Google search (attempt {attempt + 1})")
            driver, profile_dir = get_driver(proxy)
            
            if not driver:
                continue
            
            # Navigate to Google
            logging.info("Navigating to Google")
            driver.get("https://www.google.com")
            time.sleep(random.uniform(3, 6))  # Give time to load
            
            # Log page title for debugging
            try:
                page_title = driver.title
                logging.info(f"Page loaded: {page_title}")
            except:
                logging.warning("Could not get page title")
            
            # Check if blocked
            if is_search_engine_blocked(driver):
                logging.warning("Google appears to be blocked")
                driver.quit()
                force_delete_profile(profile_dir)
                continue  # Try again
            
            logging.info("Google appears to be accessible")
            
            # Perform search
            random_mouse_move(driver)
            keyword = random.choice(SEARCH_KEYWORDS)
            logging.info(f"Searching for: {keyword}")
            
            # Wait a bit more for page to fully load
            time.sleep(random.uniform(2, 3))
            
            try:
                # Find search box with multiple selectors
                search_box = None
                search_selectors = [
                    'input[name="q"]',
                    'textarea[name="q"]',
                    'input[title="Search"]',
                    'textarea[title="Search"]',
                    'input[role="combobox"]',
                    'textarea[role="combobox"]'
                ]
                
                for selector in search_selectors:
                    try:
                        search_box = driver.find_element(By.CSS_SELECTOR, selector)
                        if search_box and search_box.is_displayed():
                            logging.info(f"Found search box using selector: {selector}")
                            break
                    except:
                        continue
                
                if not search_box:
                    logging.warning("Could not find Google search box with any selector")
                    # Try to click on the search area to activate it
                    try:
                        search_area = driver.find_element(By.CSS_SELECTOR, 'div[role="search"]')
                        search_area.click()
                        time.sleep(1)
                        # Try selectors again
                        for selector in search_selectors:
                            try:
                                search_box = driver.find_element(By.CSS_SELECTOR, selector)
                                if search_box and search_box.is_displayed():
                                    logging.info(f"Found search box after click using: {selector}")
                                    break
                            except:
                                continue
                    except:
                        pass
                
                if not search_box:
                    raise Exception("Could not find Google search box")
                
                # Perform search
                search_box.clear()
                search_box.send_keys(keyword)
                search_box.send_keys(Keys.RETURN)
                
                # Wait for search results
                time.sleep(random.uniform(3, 5))
                
                # Find vpsx.me links in search results
                vpsx_links = []
                all_links = driver.find_elements(By.XPATH, '//a')
                for link in all_links:
                    href = link.get_attribute('href')
                    if href and 'vpsx.me' in href and not href.startswith('https://www.google.'):
                        vpsx_links.append(link)
                
                # Prioritize links that look like main site
                main_links = [l for l in vpsx_links if l.get_attribute('href').startswith('https://vpsx.me')]
                if main_links:
                    vpsx_links = main_links
                
                # Click the first valid vpsx.me link
                if vpsx_links:
                    target_link = vpsx_links[0]
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target_link)
                    time.sleep(random.uniform(1, 2))
                    
                    try:
                        target_link.click()
                    except Exception:
                        driver.execute_script("arguments[0].click();", target_link)
                    
                    logging.info("Successfully clicked vpsx.me link from Google")
                    time.sleep(random.uniform(2, 4))
                    
                    # Wait for page to load and verify domain
                    time.sleep(random.uniform(2, 4))
                    if 'vpsx.me' in driver.current_url:
                        natural_browsing_behavior(driver)
                        traffic_stats["search_engines_used"]["google"] += 1
                        traffic_stats["search_visits"] += 1
                        traffic_stats["successful_visits"] += 1
                        driver.quit()
                        force_delete_profile(profile_dir)
                        return True
                    else:
                        logging.warning(f"Clicked link did not lead to vpsx.me: {driver.current_url}")
                else:
                    logging.warning("No vpsx.me links found on Google")
                
            except Exception as e:
                logging.error(f"Error during Google search: {e}")
            
            driver.quit()
            force_delete_profile(profile_dir)
            
        except Exception as e:
            logging.error(f"Error with Google search: {e}")
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            if profile_dir:
                force_delete_profile(profile_dir)
            
            if attempt < max_retry - 1:
                time.sleep(random.uniform(2, 5))
    
    logging.warning("Google search failed, falling back to direct access")
    return False

# Direct visit to vpsx.me
def visit_vpsx_direct(proxy=None, max_retry=3):
    """Direct visit to vpsx.me"""
    
    # Get and log current IP
    current_ip = get_current_ip(proxy)
    logging.info(f"Starting direct visit with IP: {current_ip}")
    
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
    Implements 50/50 split: 50% direct access and 50% search-based access for balanced traffic
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
            
            # Random delay between visits (8-15 seconds)
            delay_between_visits = random.uniform(8, 15)
            
            # Log current IP for this visit
            current_ip = get_current_ip(proxy)
            logging.info(f"\n--- Visit #{visit_count} (IP: {current_ip}) ---")
            
            # 50/50 split: 50% direct vs 50% search (balanced traffic)
            visit_type = random.choices(['direct', 'search'], weights=[50, 50])[0]
            
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
        
        # Log current IP for this demo visit
        current_ip = get_current_ip(proxy)
        logging.info(f"\n--- Demo Visit #{i+1}/{num_visits} (IP: {current_ip}) ---")
        
        # 50/50 split for demo too: 50% direct vs 50% search
        visit_type = random.choices(['direct', 'search'], weights=[50, 50])[0]
        
        if visit_type == 'direct':
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
            delay = random.uniform(5, 10)
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
