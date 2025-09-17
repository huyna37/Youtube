import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import os
import shutil
import logging
from datetime import datetime

FIXED_PROXY = "103.171.1.4:8174:YZzexadult:YlyHvtdx"

VISIT_PAGES = [
    "https://fptshop.com.vn/",
    "https://www.traveloka.com/vi-vn",
    "https://www.agoda.com/vi-vn/city/hanoi-vn.html",
]
TARGET_PAGE = "https://noithatspa.io.vn"

NAV_LINKS = [
    "https://noithatspa.io.vn/index.php?rp=/announcements",
    "https://noithatspa.io.vn/index.php?rp=/knowledgebase",
    "https://noithatspa.io.vn"
]

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traffic_log.txt', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_driver(proxy=None):
    firefox_options = FirefoxOptions()
    profile_id = random.randint(100000, 999999)
    profile_dir = os.path.abspath(f"profiles/profile_{profile_id}")
    os.makedirs(profile_dir, exist_ok=True)
    firefox_options.set_preference("profile", profile_dir)
    user_agent = random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ])
    firefox_options.set_preference("general.useragent.override", user_agent)
    if proxy:
        firefox_options.set_preference("network.proxy.type", 1)
        proxy_host, proxy_port = proxy.replace("http://","").split(":")
        firefox_options.set_preference("network.proxy.http", proxy_host)
        firefox_options.set_preference("network.proxy.http_port", int(proxy_port))
        firefox_options.set_preference("network.proxy.ssl", proxy_host)
        firefox_options.set_preference("network.proxy.ssl_port", int(proxy_port))
    try:
        driver = webdriver.Firefox(options=firefox_options)
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

def safe_get(driver, url, timeout=30, try_new_tab_on_fail=True):
    try:
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        return True
    except Exception as e:
        logging.error(f"Timeout or error loading {url}: {e}")
        if try_new_tab_on_fail:
            try:
                logging.info(f"Trying to open {url} in a new tab due to timeout...")
                driver.execute_script(f"window.open('{url}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(5)  # Wait for new tab to load
                return True
            except Exception as e2:
                logging.error(f"Failed to open {url} in new tab: {e2}")
        return False

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
            if random.random() < 0.7:
                # Direct to TARGET_PAGE
                logging.info(f"Directly visiting: {TARGET_PAGE}")
                driver, profile_dir = get_driver(proxy)
                if not driver:
                    force_delete_profile(profile_dir)
                    continue
                try:
                    if safe_get(driver, TARGET_PAGE):
                        # Click all nav links, wait 10s after each
                        time.sleep(10)
                        for nav_url in NAV_LINKS:
                            logging.info(f"Clicking nav link: {nav_url}")
                            driver.get(nav_url)
                            logging.info("Waiting 10 seconds on nav page")
                            time.sleep(10)
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
                    driver.get(page)
                    logging.info(f"Arrived at: {page}, waiting 3 seconds before direct to target.")
                    time.sleep(3)
                    if safe_get(driver, TARGET_PAGE):
                        time.sleep(10)
                        for nav_url in NAV_LINKS:
                            logging.info(f"Clicking nav link: {nav_url}")
                            driver.get(nav_url)
                            logging.info("Waiting 10 seconds on nav page")
                            time.sleep(10)
                        time.sleep(20)
                except Exception as e:
                    logging.error(f"Error during visit: {e}")
                finally:
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    force_delete_profile(profile_dir)
    except KeyboardInterrupt:
        logging.info("Traffic simulation stopped by user")
    finally:
        cleanup_profiles()

if __name__ == "__main__":
    run_custom_traffic()
