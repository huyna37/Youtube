from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import undetected_chromedriver as uc
import os
import string
import secrets

def get_undetect_chrome_options(profile_path, proxy=None):
    chrome_options = uc.ChromeOptions()
    # Đảm bảo profile_path là đường dẫn tuyệt đối
    abs_profile_path = os.path.abspath(profile_path)
    # Xoá dữ liệu cũ nếu profile đã tồn tại
    import shutil
    if os.path.exists(abs_profile_path):
        for item in os.listdir(abs_profile_path):
            item_path = os.path.join(abs_profile_path, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    else:
        os.makedirs(abs_profile_path)
    chrome_options.add_argument(f"--user-data-dir={abs_profile_path}")
    chrome_options.add_argument("--lang=en-US")
    chrome_options.add_argument("--start-maximized")
    if proxy:
        chrome_options.add_argument(f"--proxy-server=http://{proxy}")
    # KHÔNG thêm các option như disable-blink-features, disable-automation, disable-extensions, disable-notifications, no-sandbox, disable-dev-shm-usage, user-agent tuỳ chỉnh
    return chrome_options

def create_gmail_account(profile_path):
    # Đọc proxy từ proxies.txt (chọn ngẫu nhiên)
    proxy = None
    proxies_path = os.path.join(os.path.dirname(__file__), "proxies.txt")
    if os.path.exists(proxies_path):
        with open(proxies_path, "r") as f:
            proxy_list = [line.strip() for line in f if line.strip()]
        if proxy_list:
            proxy = random.choice(proxy_list)
            print(f"[INFO] Sử dụng proxy: {proxy}")
    chrome_options = get_undetect_chrome_options(profile_path, proxy)
    driver = uc.Chrome(options=chrome_options)
    # Random cookie như người thật
    cookie_name = 'NID'
    cookie_value = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
    driver.get('https://google.com')
    driver.delete_all_cookies()
    # Chỉ thêm cookie nếu domain là google.com
    current_url = driver.current_url
    if "google.com" in current_url:
        try:
            driver.add_cookie({'name': cookie_name, 'value': cookie_value, 'domain': '.google.com'})
        except Exception as e:
            print(f"[WARN] Không thể thêm cookie: {e}")
    else:
        print(f"[WARN] Không ở đúng domain để thêm cookie: {current_url}")
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    try:
        wait = WebDriverWait(driver, 20)
        # Bước 1: Nhập Họ và Tên
        driver.get("https://accounts.google.com/signup?hl=en")
        first_name = "Nguyen"
        last_name = "VanA"
        wait.until(EC.presence_of_element_located((By.NAME, "firstName"))).send_keys(first_name)
        wait.until(EC.presence_of_element_located((By.NAME, "lastName"))).send_keys(last_name)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Tiếp theo') or contains(text(),'Next') or contains(text(),'Kế tiếp')]]"))).click()
        time.sleep(4)
        # Bước 2: Ngày sinh và Giới tính
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Day']"))).send_keys("01")
        month_select = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Month']/ancestor::div[contains(@class, 'VfPpkd-TkwUic')]")))
        month_select.click()
        # Chọn tháng January bằng cách tìm theo text
        january_option = wait.until(EC.presence_of_element_located((By.XPATH, "//li[.//span[text()='January']]")))
        january_option.click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//input[@aria-label='Year']"))).send_keys("1990")
        gender_select = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Gender']/ancestor::div[contains(@class, 'VfPpkd-TkwUic')]")))
        gender_select.click()
        male_option = wait.until(EC.presence_of_element_located((By.XPATH, "//li[.//span[text()='Male']]")))
        male_option.click()
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Tiếp theo') or contains(text(),'Next') or contains(text(),'Kế tiếp')]]"))).click()
        time.sleep(4)
        # Bước 3: Nhập tên người dùng
        wait.until(EC.url_contains("username"))
        username = f"HlM{random.randint(10000,99999)}{random.randint(100,999)}"
        username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and @aria-label='Username']")))
        username_input.send_keys(username)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Tiếp theo') or contains(text(),'Next') or contains(text(),'Kế tiếp')]]"))).click()
        time.sleep(4)
        # Bước 4: Nhập mật khẩu
        wait.until(EC.url_contains("password"))
        password = "TestPassword123!"
        time.sleep(1)
        try:
            passwd_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Password']")))
            driver.execute_script("arguments[0].scrollIntoView(true);", passwd_input)
            passwd_input.send_keys(password)
            confirm_input = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Confirm']")))
            driver.execute_script("arguments[0].scrollIntoView(true);", confirm_input)
            confirm_input.send_keys(password)
        except Exception as e:
            print("Không điền được mật khẩu:", e)
            driver.save_screenshot("error_password.png")
            driver.quit()
            return None
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Tiếp theo') or contains(text(),'Next') or contains(text(),'Kế tiếp')]]"))).click()
        time.sleep(2)
        # Đến bước xác thực số điện thoại
        account_info = {
            "email": f"{username}@gmail.com",
            "password": password,
            "profile_path": profile_path
        }
        # driver.quit()
        return account_info
    except Exception as e:
        print(f"Lỗi tạo tài khoản: {e}")
        # driver.quit()
        return None