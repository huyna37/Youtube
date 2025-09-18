import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
import os
import shutil
import logging
from datetime import datetime
import tempfile
import uuid

FIXED_PROXY = "http://103.214.8.89:10000"

VISIT_PAGES = [
    "https://www.agoda.com/vi-vn/city/hanoi-vn.html",
]
TARGET_PAGE = "https://noithatspa.io.vn"

NAV_LINKS = [
    "https://noithatspa.io.vn/index.php?rp=/announcements",
    "https://noithatspa.io.vn/index.php?rp=/knowledgebase",
    "https://noithatspa.io.vn/serverstatus.php",
    "https://noithatspa.io.vn/contact.php"
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
    # Tạo profile mới hoàn toàn bằng UUID, đảm bảo không trùng lặp
    profile_id = str(uuid.uuid4())
    profile_dir = os.path.abspath(f"profiles/profile_{profile_id}")
    if os.path.exists(profile_dir):
        shutil.rmtree(profile_dir)
    os.makedirs(profile_dir, exist_ok=True)
    firefox_options.profile = profile_dir
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference("useAutomationExtension", False)
    firefox_options.set_preference("privacy.clearOnShutdown.cookies", True)
    firefox_options.set_preference("privacy.clearOnShutdown.cache", True)
    firefox_options.set_preference("network.cookie.cookieBehavior", 0)
    user_agent = random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:117.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:117.0) Gecko/20100101 Firefox/117.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0"
    ])
    firefox_options.set_preference("general.useragent.override", user_agent)
    if proxy:
        firefox_options.set_preference("network.proxy.type", 1)
        # Loại bỏ scheme nếu có
        proxy_clean = proxy.replace("http://", "").replace("https://", "")
        host, port = proxy_clean.split(":")
        firefox_options.set_preference("network.proxy.http", host)
        firefox_options.set_preference("network.proxy.http_port", int(port))
        firefox_options.set_preference("network.proxy.ssl", host)
        firefox_options.set_preference("network.proxy.ssl_port", int(port))
    try:
        driver = webdriver.Firefox(options=firefox_options)
        # Xóa navigator.webdriver
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        # Tăng độ giống người thật
        driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['vi-VN', 'en-US', 'en']})")
        driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})")
        driver.delete_all_cookies()
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

def random_mouse_move(driver, moves=5):
    try:
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(moves):
            x = random.randint(50, 500)
            y = random.randint(50, 400)
            driver.execute_script(f"window.scrollBy({random.randint(-50,50)}, {random.randint(-100,100)});")
            driver.execute_script(f"window.scrollTo({x}, {y});")
            time.sleep(random.uniform(0.2, 0.8))
    except Exception as e:
        logging.warning(f"Mouse move error: {e}")

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
                        # Simulate human actions
                        time.sleep(10)
                        for nav_url in NAV_LINKS:
                            logging.info(f"Clicking nav link: {nav_url}")
                            try:
                                # Tìm link trên trang và click thay vì driver.get
                                link_text = nav_url.split('/')[-1] or nav_url.split('/')[-2]
                                found = False
                                # Thử tìm theo href tuyệt đối
                                links = driver.find_elements(By.XPATH, f"//a[@href='{nav_url}']")
                                if not links:
                                    # Thử tìm theo partial href
                                    partial = nav_url.replace('https://', '').replace('http://', '').split('/')[-1]
                                    links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{partial}')]")
                                if not links:
                                    # Thử tìm theo text
                                    text_guess = link_text.replace('.php', '').replace('.html', '').replace('-', ' ').title()
                                    links = driver.find_elements(By.PARTIAL_LINK_TEXT, text_guess)
                                if links:
                                    links[0].click()
                                    found = True
                                    logging.info(f"Clicked nav link element for {nav_url}")
                                    time.sleep(2)
                                else:
                                    logging.warning(f"Nav link not found for {nav_url}, fallback to driver.get")
                                logging.info("Waiting 10 seconds on nav page")
                                time.sleep(5)
                            except Exception as e:
                                logging.error(f"Error clicking nav link {nav_url}: {e}")
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
                            try:
                                # Tìm link trên trang và click thay vì driver.get
                                link_text = nav_url.split('/')[-1] or nav_url.split('/')[-2]
                                found = False
                                # Thử tìm theo href tuyệt đối
                                links = driver.find_elements(By.XPATH, f"//a[@href='{nav_url}']")
                                if not links:
                                    # Thử tìm theo partial href
                                    partial = nav_url.replace('https://', '').replace('http://', '').split('/')[-1]
                                    links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{partial}')]")
                                if not links:
                                    # Thử tìm theo text
                                    text_guess = link_text.replace('.php', '').replace('.html', '').replace('-', ' ').title()
                                    links = driver.find_elements(By.PARTIAL_LINK_TEXT, text_guess)
                                if links:
                                    links[0].click()
                                    found = True
                                    logging.info(f"Clicked nav link element for {nav_url}")
                                    time.sleep(2)
                                else:
                                    logging.warning(f"Nav link not found for {nav_url}, fallback to driver.get")
                                logging.info("Waiting 10 seconds on nav page")
                                time.sleep(5)
                            except Exception as e:
                                logging.error(f"Error clicking nav link {nav_url}: {e}")
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
