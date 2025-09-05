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

FIXED_PROXY = "http://103.214.8.89:10000"

USER_AGENTS = [
    # Một số user-agent phổ biến
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
]

SEARCH_KEYWORDS = [
    "vpsx.me", "vpsx.me review", "vpsx.me proxy", "vpsx.me là gì", "vpsx.me tốc độ", "vpsx.me giá rẻ",
]

# Khởi tạo trình duyệt với proxy

def get_driver(proxy=None):
    # Xóa toàn bộ profile cũ trước khi tạo profile mới
    profiles_dir = os.path.abspath("profiles")
    if os.path.exists(profiles_dir):
        for name in os.listdir(profiles_dir):
            path = os.path.join(profiles_dir, name)
            if os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                except Exception:
                    pass
    chrome_options = Options()
    ext_path = None
    # Tạo profile mới cho mỗi lần chạy
    profile_id = random.randint(100000, 999999)
    profile_dir = os.path.abspath(f"profiles/profile_{profile_id}")
    os.makedirs(profile_dir, exist_ok=True)
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    # Random user-agent
    chrome_options.add_argument(f'--user-agent={random.choice(USER_AGENTS)}')
    # Random window size
    w = random.randint(900, 1920)
    h = random.randint(600, 1080)
    chrome_options.add_argument(f'--window-size={w},{h}')
    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')
    driver = undetec.Chrome(options=chrome_options)
    return driver, profile_dir

# Scroll random trên trang

def random_scroll(driver, min_scroll=3, max_scroll=10):
    scroll_times = random.randint(min_scroll, max_scroll)
    for _ in range(scroll_times):
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(random.uniform(0.5, 2))

# Thao tác chuột random

def random_mouse_move(driver):
    try:
        body = driver.find_element(By.TAG_NAME, 'body')
        actions = ActionChains(driver)
        for _ in range(random.randint(3, 8)):
            x = random.randint(0, 500)
            y = random.randint(0, 500)
            actions.move_to_element_with_offset(body, x, y).perform()
            time.sleep(random.uniform(0.1, 0.5))
    except Exception:
        pass

# Truy cập vpsx.me trực tiếp

def force_delete_profile(profile_dir, max_retry=3):
    for _ in range(max_retry):
        # Kill all chrome processes to release file locks
        try:
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        try:
            shutil.rmtree(profile_dir)
            break
        except Exception:
            time.sleep(1)
            continue

def visit_vpsx_me(proxy=None):
    driver, profile_dir = get_driver(proxy)
    driver.get('https://vpsx.me')
    time.sleep(random.uniform(2, 5))
    random_scroll(driver)
    time.sleep(random.uniform(2, 5))
    # Lượn web: click random các link trên trang vpsx.me
    for _ in range(random.randint(2, 4)):
        page_links = driver.find_elements(By.TAG_NAME, 'a')
        page_links = [l for l in page_links if l.is_displayed() and l.get_attribute('href')]
        if page_links:
            link = random.choice(page_links)
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                time.sleep(random.uniform(0.2, 0.5))
                link.click()
            except Exception:
                # Nếu vẫn lỗi, thử click bằng JavaScript
                try:
                    driver.execute_script("arguments[0].click();", link)
                except Exception:
                    pass
            time.sleep(random.uniform(2, 4))
            random_scroll(driver)
    time.sleep(10)
    try:
        driver.quit()
    except Exception:
        pass
    # Xóa profile_dir vĩnh viễn
    force_delete_profile(profile_dir)

# Tìm kiếm vpsx.me trên Google và click vào

def search_and_click_google(proxy=None):
    driver, profile_dir = get_driver(proxy)
    driver.get('https://www.google.com')
    time.sleep(random.uniform(2, 4))
    random_mouse_move(driver)
    keyword = random.choice(SEARCH_KEYWORDS)
    box = driver.find_element(By.NAME, 'q')
    for c in keyword:
        box.send_keys(c)
        time.sleep(random.uniform(0.05, 0.2))
    box.send_keys(Keys.RETURN)
    time.sleep(random.uniform(2, 4))
    random_mouse_move(driver)
    # Tìm link vpsx.me
    links = driver.find_elements(By.PARTIAL_LINK_TEXT, 'vpsx.me')
    if not links:
        # Nếu không tìm thấy, thử tìm link chứa vpsx.me trong href
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        for l in all_links:
            href = l.get_attribute('href')
            if href and 'vpsx.me' in href:
                links = [l]
                break
    if not links:
        # Nếu vẫn không có, click vào link đầu tiên trên trang
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        if all_links:
            links = [all_links[0]]
    if links:
        links[0].click()
        time.sleep(random.uniform(2, 5))
        random_scroll(driver)
    time.sleep(random.uniform(2, 5))
    time.sleep(10)
    try:
        driver.quit()
    except Exception:
        pass
    try:
        shutil.rmtree(profile_dir)
    except Exception:
        pass

# Tìm kiếm vpsx.me trên Google (không click vào link, chỉ search)

def search_google_only(proxy=None):
    driver, profile_dir = get_driver(proxy)
    driver.get('https://www.google.com')
    time.sleep(random.uniform(2, 4))
    random_mouse_move(driver)
    keyword = random.choice(SEARCH_KEYWORDS)
    box = driver.find_element(By.NAME, 'q')
    for c in keyword:
        box.send_keys(c)
        time.sleep(random.uniform(0.05, 0.2))
    box.send_keys(Keys.RETURN)
    time.sleep(random.uniform(2, 5))
    random_mouse_move(driver)
    # Tìm link vpsx.me và click
    links = driver.find_elements(By.PARTIAL_LINK_TEXT, 'vpsx.me')
    if not links:
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        for l in all_links:
            href = l.get_attribute('href')
            if href and 'vpsx.me' in href:
                links = [l]
                break
    if not links:
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        if all_links:
            links = [all_links[0]]
    if links:
        links[0].click()
        time.sleep(random.uniform(2, 5))
        random_scroll(driver)
        # Lượn web: click random các link trên trang vpsx.me
        for _ in range(random.randint(2, 4)):
            page_links = driver.find_elements(By.TAG_NAME, 'a')
            page_links = [l for l in page_links if l.is_displayed() and l.get_attribute('href')]
            if page_links:
                link = random.choice(page_links)
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                    time.sleep(random.uniform(0.2, 0.5))
                    link.click()
                except Exception:
                    # Nếu vẫn lỗi, thử click bằng JavaScript
                    try:
                        driver.execute_script("arguments[0].click();", link)
                    except Exception:
                        pass
                time.sleep(random.uniform(2, 4))
                random_scroll(driver)
    time.sleep(10)
    try:
        driver.quit()
    except Exception:
        pass
    try:
        shutil.rmtree(profile_dir)
    except Exception:
        pass

# Vào alibaba.com trước, lượn web, sau đó mới vào vpsx.me và lượn web như cũ

def visit_alibaba_then_vpsx(proxy=None, max_retry=20):
    for attempt in range(max_retry):
        driver = None
        profile_dir = None
        try:
            driver, profile_dir = get_driver(proxy)
            # Vào vpsx.me
            driver.get('https://vpsx.me')
            time.sleep(random.uniform(2, 5))
            random_scroll(driver)
            # Lượn web trên vpsx.me
            for _ in range(random.randint(2, 4)):
                page_links = driver.find_elements(By.TAG_NAME, 'a')
                page_links = [l for l in page_links if l.is_displayed() and l.get_attribute('href')]
                if page_links:
                    link = random.choice(page_links)
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", link)
                        time.sleep(random.uniform(0.2, 0.5))
                        link.click()
                    except Exception:
                        try:
                            driver.execute_script("arguments[0].click();", link)
                        except Exception:
                            pass
                    time.sleep(random.uniform(2, 4))
                    random_scroll(driver)
            time.sleep(10)
            try:
                driver.quit()
            except Exception:
                pass
            force_delete_profile(profile_dir)
            break  # thành công thì thoát vòng lặp
        except Exception:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            if profile_dir:
                force_delete_profile(profile_dir)
            if attempt == max_retry - 1:
                print("Lỗi liên tục, bỏ qua lần này!")
            else:
                print(f"Lỗi, thử lại lần {attempt+2}")
                time.sleep(2)

# Hàm chính để chạy traffic liên tục

def cleanup_profiles():
    profiles_dir = os.path.abspath("profiles")
    if os.path.exists(profiles_dir):
        for name in os.listdir(profiles_dir):
            path = os.path.join(profiles_dir, name)
            if os.path.isdir(path):
                try:
                    shutil.rmtree(path)
                except Exception:
                    pass

def run_traffic():
    cleanup_profiles()  # Dọn dẹp profile cũ trước khi chạy
    proxy = FIXED_PROXY
    while True:
        visit_alibaba_then_vpsx(proxy)
