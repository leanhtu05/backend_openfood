import requests
import json
import time
import uuid
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_flutter_to_firebase_flow():
    """Kiểm tra luồng dữ liệu từ Flutter đến Firebase"""
    
    # Tạo ID người dùng test ngẫu nhiên
    user_id = f"flutter_test_{int(time.time())}"
    print(f"\n=== BẮT ĐẦU KIỂM TRA VỚI USER_ID: {user_id} ===")
    
    # BƯỚC 1: Gửi dữ liệu người dùng từ Flutter đến API
    print("\n--- BƯỚC 1: Gửi dữ liệu người dùng từ Flutter ---")
    user_data = {
        "name": "Người dùng Test Flutter",
        "email": f"test_{user_id}@example.com",
        "height": 170,
        "weight": 65,
        "age": 30,
        "gender": "male",
        "activityLevel": "moderate",
        "goal": "maintain_weight",
        "targetCalories": 2000,
        "allergies": ["tôm", "cua"],
        "preferred_cuisines": ["Việt Nam", "Nhật Bản"]
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
    
    # BƯỚC 3: Gửi bản ghi nhật ký hàng ngày (như từ ứng dụng Flutter)
    print("\n--- BƯỚC 3: Gửi bản ghi nhật ký dinh dưỡng hàng ngày ---")
    today = datetime.now().strftime("%Y-%m-%d")
    daily_log = {
        "date": today,
        "caloriesIntake": 1850,
        "meals": ["Cơm gà", "Phở bò", "Salad rau"]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/firestore/users/{user_id}/daily-logs",
            json=daily_log
        )
        
        print(f"Mã trạng thái: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Phản hồi: {json.dumps(response.json(), indent=2)}")
            print("✅ Đã gửi bản ghi nhật ký hàng ngày thành công!")
            log_created = True
        else:
            print(f"❌ Không thể gửi bản ghi nhật ký: {response.text}")
            log_created = False
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")
        log_created = False
    
    # BƯỚC 4: Kiểm tra bản ghi nhật ký hàng ngày từ Firebase
    print("\n--- BƯỚC 4: Kiểm tra bản ghi nhật ký hàng ngày từ Firebase ---")
    try:
        response = requests.get(f"{BASE_URL}/firestore/users/{user_id}/daily-logs/{today}")
        
        print(f"Mã trạng thái: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Bản ghi nhật ký từ Firebase: {json.dumps(response.json(), indent=2)}")
            print("✅ Đã xác minh bản ghi nhật ký hàng ngày trong Firebase!")
            log_verified = True
        else:
            print(f"❌ Không thể đọc bản ghi nhật ký từ Firebase: {response.text}")
            log_verified = False
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")
        log_verified = False
    
    # BƯỚC 5: Gửi thông tin tiêu thụ thực phẩm (như từ ứng dụng Flutter)
    print("\n--- BƯỚC 5: Gửi thông tin tiêu thụ thực phẩm ---")
    food_intake = {
        "userId": user_id,
        "foodId": str(uuid.uuid4())[:8],
        "food_name": "Phở bò tái chín",
        "date": today,
        "meal_type": "lunch",
        "amount_g": 350,
        "calories": 480,
        "protein": 25,
        "fat": 12,
        "carbs": 65,
        "notes": "Ăn tại nhà hàng"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/firestore/users/{user_id}/food-intake",
            json=food_intake
        )
        
        print(f"Mã trạng thái: {response.status_code}")
        
        if response.status_code in (200, 201):
            print(f"Phản hồi: {json.dumps(response.json(), indent=2)}")
            print("✅ Đã gửi thông tin tiêu thụ thực phẩm thành công!")
            food_intake_created = True
        else:
            print(f"❌ Không thể gửi thông tin tiêu thụ thực phẩm: {response.text}")
            food_intake_created = False
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")
        food_intake_created = False
    
    # BƯỚC 6: Kiểm tra lịch sử tiêu thụ thực phẩm từ Firebase
    print("\n--- BƯỚC 6: Kiểm tra lịch sử tiêu thụ thực phẩm từ Firebase ---")
    try:
        response = requests.get(f"{BASE_URL}/firestore/users/{user_id}/food-intake/history?limit=10")
        
        print(f"Mã trạng thái: {response.status_code}")
        
        if response.status_code == 200:
            print(f"Lịch sử tiêu thụ thực phẩm từ Firebase: {json.dumps(response.json(), indent=2)}")
            print("✅ Đã xác minh thông tin tiêu thụ thực phẩm trong Firebase!")
            food_intake_verified = True
        else:
            print(f"❌ Không thể đọc lịch sử tiêu thụ thực phẩm từ Firebase: {response.text}")
            food_intake_verified = False
    except Exception as e:
        print(f"❌ Lỗi kết nối: {str(e)}")
        food_intake_verified = False
    
    # Tổng kết
    print("\n=== KẾT QUẢ KIỂM TRA ===")
    print(f"ID người dùng: {user_id}")
    print(f"Tạo người dùng: {'✅ THÀNH CÔNG' if user_created else '❌ THẤT BẠI'}")
    print(f"Xác minh người dùng từ Firebase: {'✅ THÀNH CÔNG' if user_verified else '❌ THẤT BẠI'}")
    print(f"Gửi bản ghi nhật ký hàng ngày: {'✅ THÀNH CÔNG' if log_created else '❌ THẤT BẠI'}")
    print(f"Xác minh bản ghi nhật ký từ Firebase: {'✅ THÀNH CÔNG' if log_verified else '❌ THẤT BẠI'}")
    print(f"Gửi thông tin tiêu thụ thực phẩm: {'✅ THÀNH CÔNG' if food_intake_created else '❌ THẤT BẠI'}")
    print(f"Xác minh thông tin tiêu thụ thực phẩm từ Firebase: {'✅ THÀNH CÔNG' if food_intake_verified else '❌ THẤT BẠI'}")

if __name__ == "__main__":
    test_flutter_to_firebase_flow() 