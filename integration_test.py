"""
Script kiểm tra tích hợp các API endpoints và xác nhận chúng hoạt động đúng
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None, expected_status=200):
    """Kiểm tra một endpoint API cụ thể"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n=== Kiểm tra {method} {endpoint} ===")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"Không hỗ trợ phương thức {method}")
            return False
            
        status = response.status_code
        print(f"Status Code: {status}")
        
        if status != expected_status:
            print(f"❌ Thất bại - Expected status {expected_status}, nhận được {status}")
            return False
            
        # Hiển thị response dạng JSON
        try:
            print("Response:")
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))
        except:
            print("Response không phải JSON hợp lệ")
            print(response.text)
            
        print(f"✅ Thành công - Status code {status}")
        return True
            
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return False

def test_chat_endpoint():
    """Kiểm tra endpoint /chat của FastAPI"""
    chat_url = f"{BASE_URL}/chat"
    print(f"\n=== Kiểm tra POST {chat_url} ===")
    
    try:
        data = {"message": "Gợi ý món ăn lành mạnh cho người tập gym"}
        response = requests.post(chat_url, json=data)
        
        status = response.status_code
        print(f"Status Code: {status}")
        
        if status != 200:
            print(f"❌ Thất bại - Chat API trả về status {status}")
            if status == 503:
                print("Lưu ý: Bạn cần thiết lập GROQ_API_KEY trong biến môi trường")
            return False
            
        # Hiển thị response
        try:
            result = response.json()
            print("Response:")
            print(f"AI reply: {result.get('reply', 'Không có phản hồi')}")
            print(f"✅ Thành công - Chat API hoạt động")
            return True
        except:
            print("❌ Thất bại - Response không phải JSON hợp lệ")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Lỗi kết nối đến Chat API: {str(e)}")
        return False

def main():
    """Chức năng chính chạy tất cả các kiểm tra"""
    print("=== BẮT ĐẦU KIỂM TRA TÍCH HỢP ===")
    start_time = time.time()
    
    # Kiểm tra các endpoint FastAPI
    endpoints = [
        ("/", "GET"),
        ("/check-ai-availability", "GET"),
        ("/api-status", "GET"),
        ("/cache-info", "GET")
    ]
    
    fastapi_results = []
    for endpoint, method in endpoints:
        success = test_endpoint(endpoint, method)
        fastapi_results.append(success)
    
    # Kiểm tra endpoint chat
    chat_success = test_chat_endpoint()
    
    # Hiển thị kết quả tóm tắt
    print("\n=== KẾT QUẢ KIỂM TRA ===")
    print(f"FastAPI endpoints: {sum(fastapi_results)}/{len(fastapi_results)} thành công")
    print(f"Chat API: {'✅ Hoạt động' if chat_success else '❌ Không hoạt động'}")
    
    # Thời gian chạy
    duration = time.time() - start_time
    print(f"\nThời gian chạy: {duration:.2f} giây")
    print("=== KẾT THÚC KIỂM TRA TÍCH HỢP ===")

if __name__ == "__main__":
    main() 