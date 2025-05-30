"""
Kiểm tra tự động tạo người dùng trong Firestore sau khi xác thực
"""
import requests
import json
import time
import uuid
from datetime import datetime

# Base URL cho API
BASE_URL = "http://localhost:8000"

def test_auto_user_creation_on_login():
    """Kiểm tra tự động tạo người dùng khi đăng nhập"""
    
    # Tạo ID người dùng test ngẫu nhiên
    user_id = f"auto_test_{int(time.time())}"
    print(f"\n=== BẮT ĐẦU KIỂM TRA TỰ ĐỘNG TẠO NGƯỜI DÙNG: {user_id} ===")
    
    # BƯỚC 1: Mô phỏng đăng nhập (trong thực tế, bạn sẽ sử dụng Firebase Authentication)
    # Trong test này, chúng ta sẽ tạo người dùng trực tiếp và kiểm tra xem
    # các endpoint khác có tự động sử dụng người dùng đó không
    print("\n--- BƯỚC 1: Tạo người dùng test trong Firestore ---")
    user_data = {
        "name": "Người dùng Test Auto",
        "email": f"auto_{user_id}@example.com",
        "height": 175,
        "weight": 70,
        "age": 35,
        "gender": "male",
        "activityLevel": "moderate",
        "goal": "lose_weight",
        "targetCalories": 1800,
        "allergies": ["hải sản", "đậu phộng"],
        "preferred_cuisines": ["Việt Nam", "Ý"]
    }
    
    print(f"Gửi dữ liệu người dùng đến: {BASE_URL}/firestore/users/{user_id}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/firestore/users/{user_id}",
            json=user_data
        )
        
        print(f"Mã trạng thái: {response.status_code}")
        print(f"Phản hồi: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 201:
            print("✅ Đã tạo người dùng thành công!")
            user_created = True
        else:
            print(f"❌ Không thể tạo người dùng: {response.json().get('detail', 'Lỗi không xác định')}")
            user_created = False
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")
        user_created = False
    
    # BƯỚC 2: Kiểm tra xem người dùng đã được lưu trữ trong Firebase chưa
    print("\n--- BƯỚC 2: Kiểm tra lưu trữ người dùng trong Firebase ---")
    try:
        response = requests.get(f"{BASE_URL}/firestore/users/{user_id}")
        
        print(f"Mã trạng thái: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Dữ liệu người dùng từ Firebase: {json.dumps(response.json(), indent=2)}")
            print("✅ Đã lưu trữ người dùng trong Firebase thành công!")
            user_verified = True
        else:
            print(f"❌ Không thể đọc người dùng từ Firebase: {response.text}")
            user_verified = False
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")
        user_verified = False
    
    # BƯỚC 3: Xóa người dùng để dọn dẹp
    print("\n--- BƯỚC 3: Xóa người dùng test ---")
    try:
        response = requests.delete(f"{BASE_URL}/firestore/users/{user_id}")
        
        print(f"Mã trạng thái: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Đã xóa người dùng test thành công!")
            cleanup_success = True
        else:
            print(f"❌ Không thể xóa người dùng test: {response.text}")
            cleanup_success = False
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")
        cleanup_success = False
    
    # Tổng kết
    print("\n=== KẾT QUẢ KIỂM TRA ===")
    print(f"ID người dùng: {user_id}")
    print(f"Tạo người dùng: {'✅ THÀNH CÔNG' if user_created else '❌ THẤT BẠI'}")
    print(f"Xác minh người dùng từ Firebase: {'✅ THÀNH CÔNG' if user_verified else '❌ THẤT BẠI'}")
    print(f"Dọn dẹp: {'✅ THÀNH CÔNG' if cleanup_success else '❌ THẤT BẠI'}")

if __name__ == "__main__":
    test_auto_user_creation_on_login() 