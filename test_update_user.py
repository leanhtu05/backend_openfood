import requests
import json
import os
from firebase_admin import auth
import firebase_admin
from firebase_admin import credentials, firestore
import time

# Kiểm tra xem Firebase đã được khởi tạo chưa
try:
    app = firebase_admin.get_app()
except ValueError:
    # Nếu chưa khởi tạo, tìm file credentials
    cred_paths = [
        "firebase-credentials.json",
        os.path.join(os.path.dirname(__file__), "firebase-credentials.json")
    ]
    
    cred = None
    for path in cred_paths:
        if os.path.exists(path):
            print(f"Sử dụng credentials từ: {path}")
            cred = credentials.Certificate(path)
            break
    
    if cred is None:
        raise Exception("Không tìm thấy file credentials Firebase!")
        
    firebase_admin.initialize_app(cred)

# URL API
API_URL = "http://localhost:8000"  # Thay đổi nếu API chạy trên URL khác

# Khởi tạo Firestore client
db = firestore.client()

def verify_user_data(user_id):
    """
    Kiểm tra dữ liệu người dùng trong Firestore
    
    Args:
        user_id: ID của người dùng cần kiểm tra
    """
    try:
        # Lấy dữ liệu người dùng từ Firestore
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            print(f"❌ Không tìm thấy người dùng với ID: {user_id}")
            return False
        
        # Lấy dữ liệu người dùng
        user_data = user_doc.to_dict()
        
        # Hiển thị thông tin
        print("\n✅ Dữ liệu người dùng trong Firestore:")
        print(f"  - Tên: {user_data.get('name', 'Không có')}")
        print(f"  - Email: {user_data.get('email', 'Không có')}")
        print(f"  - Tuổi: {user_data.get('age', 'Không có')}")
        print(f"  - Giới tính: {user_data.get('gender', 'Không có')}")
        print(f"  - Chiều cao: {user_data.get('height', 'Không có')} cm")
        print(f"  - Cân nặng: {user_data.get('weight', 'Không có')} kg")
        print(f"  - Mục tiêu: {user_data.get('goal', 'Không có')}")
        print(f"  - Mức độ hoạt động: {user_data.get('activityLevel', 'Không có')}")
        
        # Kiểm tra thời gian cập nhật
        updated_at = user_data.get('updated_at')
        if updated_at:
            print(f"  - Thời gian cập nhật: {updated_at}")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra dữ liệu người dùng: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_update_user():
    """Kiểm tra API cập nhật thông tin người dùng"""
    
    # Tạo user test nếu chưa có
    try:
        user = auth.get_user_by_email("test_user@example.com")
        user_id = user.uid
        print(f"Sử dụng user đã tồn tại: {user_id}")
    except:
        # Tạo user mới
        user = auth.create_user(
            email="test_user@example.com",
            password="Test@123456",
            display_name="Test User"
        )
        user_id = user.uid
        print(f"Đã tạo user mới: {user_id}")
    
    # Tạo custom token để đăng nhập
    custom_token = auth.create_custom_token(user_id)
    print(f"Đã tạo custom token")
    
    # Lấy ID token từ custom token (cần sử dụng Firebase Auth REST API)
    # Trong môi trường thực tế, bạn sẽ sử dụng Firebase SDK trên Flutter để lấy ID token
    # Ở đây chúng ta giả lập bằng cách in ra custom token và yêu cầu nhập ID token
    print(f"Custom token: {custom_token.decode('utf-8')}")
    id_token = input("Nhập ID token (sử dụng Firebase Auth REST API để đổi custom token thành ID token): ")
    
    # Dữ liệu cập nhật
    update_data = {
        "name": "Nguyễn Văn Test",
        "age": 30,
        "gender": "male",
        "height": 175,
        "weight": 70,
        "goal": "giảm cân",
        "activityLevel": "moderate"
    }
    
    # Gọi API cập nhật
    headers = {
        "Authorization": f"Bearer {id_token}",
        "Content-Type": "application/json"
    }
    
    response = requests.patch(
        f"{API_URL}/firestore/users/{user_id}",
        headers=headers,
        json=update_data
    )
    
    # In kết quả
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Kiểm tra kết quả
    if response.status_code == 200:
        print("✅ Cập nhật thông tin người dùng thành công!")
        
        # Kiểm tra dữ liệu đã được cập nhật
        print("\nĐang kiểm tra dữ liệu trong Firestore...")
        time.sleep(2)  # Đợi 2 giây để đảm bảo dữ liệu đã được cập nhật
        
        # Kiểm tra dữ liệu trong Firestore
        verify_user_data(user_id)
        
        # Lấy thông tin người dùng từ Firebase Auth
        user_data = auth.get_user(user_id)
        print(f"\nThông tin người dùng từ Firebase Auth:")
        print(f"  - UID: {user_data.uid}")
        print(f"  - Email: {user_data.email}")
        print(f"  - Display name: {user_data.display_name}")
    else:
        print("❌ Cập nhật thông tin người dùng thất bại!")
        print(f"Chi tiết lỗi: {response.text}")

if __name__ == "__main__":
    test_update_user() 