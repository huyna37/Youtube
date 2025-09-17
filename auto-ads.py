import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as undetec
import os
import shutil
import logging
from datetime import datetime

FIXED_PROXY = "http://103.214.8.89:10000"

VISIT_PAGES = [
    "https://thegioididong.com",
    "https://hoanghamobile.com",
    "https://mobilecity.vn",
    "https://nhathuoclongchau.com.vn",
    "https://www.traveloka.com/vi-vn",
    "https://www.agoda.com/vi-vn/city/hanoi-vn.html"
]
TARGET_PAGE = "https://noithatspa.io.vn"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traffic_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_driver(proxy=None):
    chrome_options = Options()
    profile_id = random.randint(100000, 999999)
    profile_dir = os.path.abspath(f"profiles/profile_{profile_id}")
    os.makedirs(profile_dir, exist_ok=True)
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    user_agent = random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 13; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36"
    ])
    chrome_options.add_argument(f'--user-agent={user_agent}')
    if "Mobile" in user_agent or "iPhone" in user_agent or "Android" in user_agent:
        w = random.randint(360, 414)
        h = random.randint(640, 896)
    else:
        w = random.randint(1024, 1920)
        h = random.randint(768, 1080)
    chrome_options.add_argument(f'--window-size={w},{h}')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    try:
        driver = undetec.Chrome(options=chrome_options)
        try:
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception:
            pass
        return driver, profile_dir
    except Exception:
        try:
            driver = webdriver.Chrome(options=chrome_options)
            return driver, profile_dir
        except Exception:
            return None, profile_dir

def force_delete_profile(profile_dir, max_retry=3):
    for attempt in range(max_retry):
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
    profiles_dir = os.path.abspath("profiles")
    if os.path.exists(profiles_dir):
        for name in os.listdir(profiles_dir):
            path = os.path.join(profiles_dir, name)
            if os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                except Exception as e:
                    logging.warning(f"Failed to cleanup profile {path}: {e}")

def scroll_top_to_bottom(driver):
    try:
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        height = driver.execute_script("return document.body.scrollHeight")
        for y in range(0, height, 400):
            driver.execute_script(f"window.scrollTo(0, {y});")
            time.sleep(0.5)
        driver.execute_script(f"window.scrollTo(0, {height});")
    except Exception as e:
        logging.warning(f"Scroll error: {e}")

def run_custom_traffic():
    cleanup_profiles()
    proxy = FIXED_PROXY
    visit_count = 0
    logging.info("Starting custom traffic simulation")
    logging.info(f"Using proxy: {proxy}")
    try:
        while True:
            visit_count += 1
            logging.info(f"\n--- Visit #{visit_count} ---")
            # Decide randomly: direct or via VISIT_PAGES
            if random.random() < 0.5:
                # Direct to TARGET_PAGE
                logging.info(f"Directly visiting: {TARGET_PAGE}")
                driver, profile_dir = get_driver(proxy)
                if not driver:
                    force_delete_profile(profile_dir)
                    continue
                try:
                    driver.get(TARGET_PAGE)
                    time.sleep(random.uniform(2, 4))
                    # scroll_top_to_bottom(driver)
                    logging.info("Waiting 20 seconds on target page")
                    time.sleep(20)
                except Exception as e:
                    logging.error(f"Error during direct visit: {e}")
                finally:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    force_delete_profile(profile_dir)
            else:
                # Via VISIT_PAGES
                page = random.choice(VISIT_PAGES)
                driver, profile_dir = get_driver(proxy)
                if not driver:
                    force_delete_profile(profile_dir)
                    continue
                try:
                    logging.info(f"Visiting: {page}")
                    driver.get(page)
                    time.sleep(random.uniform(3, 6))
                    logging.info(f"Redirecting to: {TARGET_PAGE}")
                    driver.get(TARGET_PAGE)
                    time.sleep(random.uniform(2, 4))
                    # scroll_top_to_bottom(driver)
                    logging.info("Waiting 20 seconds on target page")
                    time.sleep(20)
                except Exception as e:
                    logging.error(f"Error during visit: {e}")
                finally:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    force_delete_profile(profile_dir)
            delay_between_visits = random.uniform(8, 15)
            logging.info(f"Waiting {delay_between_visits:.1f} seconds before next visit...")
    except KeyboardInterrupt:
        logging.info("Traffic simulation stopped by user")
    finally:
        cleanup_profiles()

if __name__ == "__main__":
    run_custom_traffic()
