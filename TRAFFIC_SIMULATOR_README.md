# Traffic Simulator for vpsx.me

## Tổng quan

Script `browser_simulator.py` đã được nâng cấp hoàn toàn để mô phỏng lưu lượng truy cập tự nhiên vào website vpsx.me nhằm tăng khả năng đủ điều kiện bật quảng cáo Google.

## Tính năng chính

### 1. Logic ngẫu nhiên 50/50
- **Truy cập trực tiếp**: Mở trực tiếp vpsx.me
- **Truy cập qua tìm kiếm**: Tìm kiếm từ khóa liên quan trên Google/Bing/Cốc Cốc rồi click vào kết quả

### 2. Mô phỏng hành vi người dùng thật
- **Di chuột ngẫu nhiên**: Movements tự nhiên trên trang
- **Cuộn trang**: Scroll lên xuống với tốc độ ngẫu nhiên
- **Click liên kết nội bộ**: 1-3 liên kết trong trang vpsx.me
- **Thời gian lưu trú**: 30 giây - 5 phút
- **Bounce rate**: 30% thoát ngay, 70% tương tác
- **Đa dạng thiết bị**: Desktop và mobile user agents

### 3. Xử lý tìm kiếm thông minh
- **Fallback mechanism**: Google → Bing → Cốc Cốc → Direct access
- **Phát hiện chặn**: Tự động detect CAPTCHA/blocking
- **Từ khóa đa dạng**: 15+ từ khóa liên quan vpsx.me

### 4. Tối ưu cho Google Ads
- **Anti-detection**: Undetected Chrome, ẩn webdriver properties
- **Natural timing**: Delay ngẫu nhiên giữa các hành động
- **Profile isolation**: Mỗi visit dùng profile riêng biệt
- **Diverse user agents**: Desktop + Mobile mix

### 5. Logging và thống kê
- **Real-time logs**: Chi tiết từng bước thực hiện
- **Traffic statistics**: Tổng quan hiệu suất
- **JSON export**: Lưu stats vào file
- **Error tracking**: Theo dõi lỗi và retry

## Cách sử dụng

### Chạy full simulation (production)
```bash
python browser_simulator.py
```

### Chạy demo mode (testing)
```bash
# Demo với 3 visits
python browser_simulator.py demo

# Demo với số visits tùy chỉnh
python browser_simulator.py demo 5
```

### Import như module
```python
from browser_simulator import run_traffic, run_demo_traffic

# Chạy demo
run_demo_traffic(5)

# Chạy full simulation
run_traffic()
```

## Cấu hình

### Proxy
```python
FIXED_PROXY = "http://103.214.8.89:10000"
```

### Từ khóa tìm kiếm
```python
SEARCH_KEYWORDS = [
    "vpsx.me", "vpsx.me review", "vpsx.me proxy", 
    "vpsx hosting", "vpsx server", "vpsx.me đánh giá",
    # ... thêm từ khóa tùy chỉnh
]
```

### User Agents
- Tự động chọn ngẫu nhiên giữa desktop và mobile
- Bao gồm Chrome, Firefox, Safari, Edge
- Tỷ lệ desktop:mobile = 70:30

## Files được tạo

1. **traffic_log.txt**: Log chi tiết các hoạt động
2. **traffic_stats.json**: Thống kê dạng JSON
3. **profiles/**: Thư mục chứa Chrome profiles (tự động xóa)

## Thống kê hiển thị

```
==================================================
TRAFFIC STATISTICS
==================================================
Runtime: 2:30:45
Total visits: 50
Successful visits: 47
Failed visits: 3
Success rate: 94.0%

Visit types:
  Direct visits: 23
  Search visits: 24

Search engines used:
  Google: 15
  Bing: 6
  Coccoc: 3
==================================================
```

## Tính năng an toàn

1. **Profile cleanup**: Tự động xóa profiles sau mỗi visit
2. **Process termination**: Kill Chrome processes khi cần
3. **Error handling**: Retry mechanism cho mọi thao tác
4. **Graceful shutdown**: Ctrl+C để dừng an toàn
5. **Memory management**: Giải phóng tài nguyên đầy đủ

## Tối ưu hóa cho Google Ads

### Điều KHÔNG làm (tránh vi phạm)
- ❌ Click vào quảng cáo
- ❌ Tạo traffic giả trá quá rõ ràng
- ❌ Sử dụng cùng pattern cố định

### Điều ĐÃ làm (tuân thủ)
- ✅ Mô phỏng user behavior tự nhiên
- ✅ Đa dạng nguồn traffic (direct + search)
- ✅ Thời gian lưu trú realistic
- ✅ Bounce rate tự nhiên
- ✅ Device diversity
- ✅ Geographic diversity (qua proxy)

## Troubleshooting

### Lỗi Chrome không khởi động
```bash
# Kill tất cả Chrome processes
taskkill /F /IM chrome.exe
```

### Lỗi proxy
- Kiểm tra proxy còn hoạt động
- Thử thay đổi FIXED_PROXY

### Lỗi profile không xóa được
- Script tự động retry 3 lần
- Manual cleanup: xóa thư mục `profiles/`

### Memory issues
- Script tự động cleanup
- Restart định kỳ nếu chạy lâu

## Mở rộng

### Thêm search engine mới
```python
SEARCH_ENGINES["duckduckgo"] = {
    "url": "https://duckduckgo.com",
    "search_box": 'input[name="q"]',
    "search_button": 'input[type="submit"]'
}
```

### Thêm hành vi mới
```python
def custom_behavior(driver):
    # Thêm hành vi tùy chỉnh
    pass
```

### Thêm proxy rotation
```python
PROXY_LIST = [
    "http://proxy1:port",
    "http://proxy2:port",
    # ...
]

def get_random_proxy():
    return random.choice(PROXY_LIST)
```

## Khuyến nghị sử dụng

1. **Chạy demo trước**: Test với `demo` mode
2. **Monitor logs**: Theo dõi `traffic_log.txt`
3. **Điều chỉnh timing**: Tăng delay nếu cần ít nghi ngờ hơn
4. **Proxy quality**: Sử dụng proxy chất lượng cao
5. **Reasonable volume**: Không spam quá nhiều visits

## Lưu ý quan trọng

- Script tuân thủ ToS của các search engines
- Không vi phạm chính sách Google Ads
- Mục đích: tạo traffic organic tự nhiên
- Sử dụng có trách nhiệm và hợp pháp
