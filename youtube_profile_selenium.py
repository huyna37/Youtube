#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Giả lập trình duyệt Chrome bằng Python cho nhiều profile, truy cập YouTube,
cuộn lên/xuống, đặt header giống người dùng thật, và tự động bật/tắt theo chu kỳ.

⚠️ Lưu ý trách nhiệm:
- Hãy đảm bảo bạn tuân thủ Điều khoản Dịch vụ của trang web bạn truy cập (ví dụ: YouTube).
- Script này chỉ mang tính kỹ thuật. Sử dụng vào mục đích không phù hợp có thể vi phạm chính sách của dịch vụ.
"""

import os                                   # thao tác với hệ thống tệp
import time                                 # sleep và timestamp
import random                               # ngẫu nhiên hóa hành vi
import string                               # hỗ trợ tạo chuỗi ngẫu nhiên
import threading                            # chạy song song đơn giản
from datetime import datetime               # log thời gian
from typing import List, Tuple              # kiểu dữ liệu gợi ý

# Selenium + undetected-chromedriver để trông giống người thật hơn
import undetected_chromedriver as uc        # ChromeDriver chống bị phát hiện
from selenium.webdriver.common.by import By # tìm phần tử (không dùng nhiều ở đây)
from selenium.webdriver.common.keys import Keys  # phím tắt nếu cần
from selenium.webdriver.chrome.options import Options  # cấu hình Chrome
from selenium.common.exceptions import WebDriverException # xử lý lỗi webdriver


# ------------------------- CẤU HÌNH CƠ BẢN -------------------------

YOUTUBE_URL = "https://www.youtube.com/test"  # URL đích cần truy cập

# Danh sách profile (mỗi profile nằm trong thư mục riêng); tạo trước khi chạy
PROFILE_DIRS = [
    os.path.abspath("./profiles/profile_1"),  # đường dẫn profile 1
]

# Thời lượng chạy cho MỖI PHIÊN (tự động bật)
SESSION_DURATION_SEC = (45, 90)  # khoảng thời gian ngẫu nhiên: tối thiểu, tối đa

# Thời gian nghỉ giữa các phiên (tự động tắt)
COOLDOWN_SEC = (20, 40)          # khoảng nghỉ ngẫu nhiên trước khi bật lại

# Số vòng lặp mỗi profile (một vòng = 1 phiên chạy + 1 cooldown)
LOOPS_PER_PROFILE = 2

# Số trình duyệt chạy song song tối đa
MAX_CONCURRENCY = 1

# Bật/tắt headless (để giống người thật, nên để False)
HEADLESS = False

# Danh sách user-agent phổ biến (có thể bổ sung thêm)
USER_AGENTS = [
    # Chrome Windows 10/11
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    # Chrome macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    # Chrome Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

# Một số độ phân giải màn hình phổ biến
WINDOW_SIZES = [
    (1366, 768),
    (1440, 900),
    (1536, 864),
    (1600, 900),
    (1920, 1080),
]


# ------------------------- HÀM TIỆN ÍCH -------------------------

def ensure_dirs():
    """Tạo thư mục profile nếu chưa tồn tại."""
    for p in PROFILE_DIRS:
        os.makedirs(p, exist_ok=True)  # tạo thư mục profile nếu chưa có


def random_user_agent() -> str:
    """Chọn user-agent ngẫu nhiên từ danh sách."""
    return random.choice(USER_AGENTS)  # trả về 1 UA ngẫu nhiên


def random_window_size() -> Tuple[int, int]:
    """Chọn kích thước cửa sổ ngẫu nhiên."""
    return random.choice(WINDOW_SIZES)  # trả về 1 cặp (width, height)


def random_headers() -> dict:
    """Sinh bộ header bổ sung 'giống người thật'. Lưu ý: một số header đặc thù (sec-ch-ua) do Chrome tự thêm, không nên fake."""
    accept_languages = ["vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
                        "en-US,en;q=0.9,vi-VN;q=0.8,vi;q=0.7"]
    dnt = random.choice(["1", "0"])  # Do-Not-Track ngẫu nhiên
    return {
        "Accept-Language": random.choice(accept_languages),  # ngôn ngữ
        "DNT": dnt,                                         # do-not-track
        "Upgrade-Insecure-Requests": "1",                   # nâng http->https
        "Pragma": "no-cache",                               # hành vi cache
        "Cache-Control": "no-cache",                        # hành vi cache
    }


def human_pause(a: float, b: float) -> None:
    """Tạm dừng ngẫu nhiên (giả lập hành vi người)."""
    time.sleep(random.uniform(a, b))  # ngủ trong khoảng a..b giây


def log(msg: str) -> None:
    """In log có timestamp và thread name."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [{threading.current_thread().name}] {msg}")


# ------------------------- KHỞI TẠO TRÌNH DUYỆT -------------------------

def build_driver(profile_path: str, headless: bool = HEADLESS):
    """Tạo driver Chrome với profile riêng, UA, kích thước cửa sổ, và header bổ sung."""
    ua = random_user_agent()                       # chọn UA
    width, height = random_window_size()           # chọn kích thước cửa sổ

    chrome_opts = uc.ChromeOptions()               # tạo options Chrome
    chrome_opts.add_argument(f"--user-data-dir={profile_path}")  # trỏ tới thư mục profile
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")  # hạn chế bị phát hiện
    chrome_opts.add_argument("--disable-infobars")              # ẩn 'Chrome is being controlled...'
    chrome_opts.add_argument("--no-first-run")                  # bỏ màn hình chào mừng
    chrome_opts.add_argument("--no-default-browser-check")      # bỏ hỏi đặt mặc định
    chrome_opts.add_argument(f"--window-size={width},{height}") # đặt kích thước cửa sổ
    chrome_opts.add_argument(f"--user-agent={ua}")              # đặt UA
    if headless:                                               # nếu chạy headless
        chrome_opts.add_argument("--headless=new")              # dùng headless mới

    # Khởi tạo driver
    driver = uc.Chrome(options=chrome_opts)                     # tạo Chrome chống phát hiện
    driver.set_page_load_timeout(60)                            # timeout tải trang
    driver.implicitly_wait(5)                                   # chờ mặc định khi find_element

    # Thiết lập header bổ sung qua CDP
    try:
        driver.execute_cdp_cmd("Network.enable", {})            # bật Network domain
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", { # đặt header bổ sung
            "headers": random_headers()
        })
    except Exception as e:
        log(f"Không thể set header bổ sung: {e}")               # log nếu lỗi

    return driver                                               # trả về driver đã cấu hình


# ------------------------- HÀNH VI LƯU LƯỢNG -------------------------

def visit_and_scroll(driver, url: str, session_time: int):
    """Mở URL, cuộn xuống rồi cuộn lên nhiều lần trong thời gian session_time."""
    start = time.time()                                         # mốc thời gian bắt đầu
    log(f"Đi tới: {url}")                                       # log URL
    driver.get(url)                                             # mở trang
    human_pause(2.0, 4.0)                                       # dừng ngẫu nhiên

    # Thực hiện một số hành vi đơn giản cho "giống người"
    # - cuộn thành nhiều nhịp
    # - dừng ngẫu nhiên
    # - có thể thay đổi tốc độ cuộn
    scroll_height = driver.execute_script("return document.body.scrollHeight")  # lấy chiều cao trang

    while time.time() - start < session_time:                   # chạy tới khi hết thời gian phiên
        # Cuộn xuống theo bước ngẫu nhiên
        step = random.randint(250, 800)                         # bước cuộn
        current_pos = driver.execute_script("return window.pageYOffset || document.documentElement.scrollTop;")  # vị trí hiện tại
        next_pos = min(current_pos + step, scroll_height)       # vị trí kế tiếp
        driver.execute_script(f"window.scrollTo(0, {next_pos});")  # cuộn
        human_pause(0.5, 2.0)                                   # dừng ngẫu nhiên

        # Thỉnh thoảng cuộn lên một chút
        if random.random() < 0.3:                               # 30% xác suất
            step_up = random.randint(100, 500)                  # bước cuộn lên
            current_pos = driver.execute_script("return window.pageYOffset || document.documentElement.scrollTop;")  # vị trí hiện tại
            prev_pos = max(current_pos - step_up, 0)            # vị trí trước
            driver.execute_script(f"window.scrollTo(0, {prev_pos});")  # cuộn lên
            human_pause(0.3, 1.2)                               # dừng ngẫu nhiên

        # Thỉnh thoảng refresh
        if random.random() < 0.1:                               # 10% xác suất
            driver.refresh()                                    # refresh trang
            human_pause(1.5, 3.0)                               # dừng ngẫu nhiên

        # Cập nhật chiều cao (phòng trường hợp lazy load)
        scroll_height = driver.execute_script("return document.body.scrollHeight")  # cập nhật chiều cao

    log("Kết thúc phiên.")                                      # log kết thúc


# ------------------------- VÒNG ĐIỀU KHIỂN (BẬT/TẮT) -------------------------

def run_profile_loop(profile_path: str, loops: int):
    """Chạy nhiều phiên cho 1 profile, mỗi phiên có thời lượng cố định, sau đó nghỉ 15s."""
    ensure_dirs()
    name = os.path.basename(profile_path)
    for i in range(1, loops + 1):
        try:
            session_time = random.randint(*SESSION_DURATION_SEC)  # thời lượng phiên (vẫn ngẫu nhiên)
            log(f"[{name}] Bắt đầu phiên {i}/{loops} trong {session_time}s")
            driver = build_driver(profile_path, headless=HEADLESS)
            visit_and_scroll(driver, YOUTUBE_URL, session_time)
        except WebDriverException as e:
            log(f"[{name}] Lỗi WebDriver: {e}")
        except Exception as e:
            log(f"[{name}] Lỗi: {e}")
        finally:
            try:
                driver.quit()   # luôn đóng trình duyệt sau mỗi phiên
            except Exception:
                pass

        if i < loops:  # còn vòng tiếp theo
            log(f"[{name}] Nghỉ 15s rồi bật lại...")
            time.sleep(15)  # nghỉ cố định 15 giây
    log(f"[{name}] Hoàn tất tất cả phiên.")


# ------------------------- ĐIỀU PHỐI SONG SONG -------------------------

def chunked(lst: List[str], n: int) -> List[List[str]]:
    """Chia danh sách thành các nhóm nhỏ kích thước n."""
    for i in range(0, len(lst), n):                             # bước n phần tử
        yield lst[i:i + n]                                      # yield nhóm


UC_CACHE_DIR = os.path.expanduser(
    r"~\AppData\Roaming\undetected_chromedriver"
)

def clear_uc_cache():
    """Xoá cache undetected_chromedriver để tránh WinError 183"""
    if os.path.exists(UC_CACHE_DIR):
        try:
            shutil.rmtree(UC_CACHE_DIR)
            print(f"[INFO] Đã xoá cache: {UC_CACHE_DIR}")
        except Exception as e:
            print(f"[WARNING] Không xoá được cache: {e}")

def main():
     # Xoá cache cũ trước khi chạy
    clear_uc_cache()

    ensure_dirs()                                               # tạo sẵn thư mục
    profiles = PROFILE_DIRS[:]                                  # sao chép danh sách profile
    random.shuffle(profiles)                                    # xáo trộn thứ tự chạy

    # Chạy theo lô để không vượt quá MAX_CONCURRENCY
    for batch in chunked(profiles, MAX_CONCURRENCY):            # chia thành các lô
        threads = []                                            # danh sách thread
        for p in batch:
            t = threading.Thread(target=run_profile_loop, args=(p, LOOPS_PER_PROFILE), daemon=True)  # tạo thread
            threads.append(t)                                   # thêm vào danh sách
            t.start()                                           # khởi động

        # Chờ lô hiện tại hoàn tất
        for t in threads:
            t.join()                                            # chờ thread kết thúc

    log("Tất cả profile đã chạy xong.")                         # log tổng kết


if __name__ == "__main__":
    main()                                                      # chạy chương trình
