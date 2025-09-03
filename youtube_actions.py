from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
# Sử dụng undetected-chromedriver để chống detect nâng cao
import undetected_chromedriver as uc

def get_undetect_chrome_options(profile_path):
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument(f"--user-data-dir={profile_path}")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-password-manager")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--lang=vi")
    chrome_options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
    return chrome_options

def create_gmail_account(profile_path):
    chrome_options = get_undetect_chrome_options(profile_path)
    chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    driver = uc.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    try:
        wait = WebDriverWait(driver, 20)
        # Bước 1: Nhập Họ và Tên
        driver.get("https://accounts.google.com/signup")
        first_name = "Nguyen"
        last_name = "VanA"
        wait.until(EC.presence_of_element_located((By.NAME, "firstName"))).send_keys(first_name)
        wait.until(EC.presence_of_element_located((By.NAME, "lastName"))).send_keys(last_name)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Tiếp theo') or contains(text(),'Next') or contains(text(),'Kế tiếp')]]"))).click()
        time.sleep(2)
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
        time.sleep(2)
        # Bước 3: Nhập tên người dùng
        wait.until(EC.url_contains("username"))
        username = f"test{random.randint(10000,99999)}{random.randint(100,999)}"
        username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' and @aria-label='Username']")))
        username_input.send_keys(username)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Tiếp theo') or contains(text(),'Next') or contains(text(),'Kế tiếp')]]"))).click()
        time.sleep(2)
        # Bước 4: Nhập mật khẩu
        wait.until(EC.url_contains("password"))
        password = "TestPassword123!"
        # Trường mật khẩu: tìm theo text tiếng Anh hoặc tiếng Việt
        passwd_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password' and (contains(@aria-label, 'Create a password') or contains(@aria-label, 'Mật khẩu'))]")))
        passwd_input.send_keys(password)
        confirm_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password' and (contains(@aria-label, 'Confirm your password') or contains(@aria-label, 'Xác nhận'))]")))
        confirm_input.send_keys(password)
        wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Tiếp theo') or contains(text(),'Next') or contains(text(),'Kế tiếp')]]"))).click()
        time.sleep(2)
        # Đến bước xác thực số điện thoại
        account_info = {
            "email": f"{username}@gmail.com",
            "password": password,
            "profile_path": profile_path
        }
        driver.quit()
        return account_info
    except Exception as e:
        print(f"Lỗi tạo tài khoản: {e}")
        driver.quit()
        return None

def browse_youtube_with_profile(profile_path):
    chrome_options = get_undetect_chrome_options(profile_path)
    driver = uc.Chrome(options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    try:
        driver.get("https://www.youtube.com")
        time.sleep(5)
        # Tìm các video đề xuất
        videos = driver.find_elements(By.ID, "video-title")
        if videos:
            video = random.choice(videos)
            video.click()
            print("Đã bấm vào một video đề xuất.")
            time.sleep(10)  # Xem video một thời gian
        else:
            print("Không tìm thấy video đề xuất.")
        driver.quit()
    except Exception as e:
        print(f"Lỗi Youtube: {e}")
        driver.quit()
