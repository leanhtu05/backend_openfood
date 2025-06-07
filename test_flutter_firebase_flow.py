import requests
import json
import time
import uuid
from datetime import datetime
from services.firestore_service import firestore_service
from storage_manager import storage_manager

# ID người dùng cần kiểm tra
USER_ID = "49DhdmJHFAY40eEgaPNEJqGdDQK2"

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

def test_firebase_vs_storage_manager():
    """Kiểm tra sự khác biệt giữa việc đọc dữ liệu từ Firestore trực tiếp và qua storage_manager"""
    
    print("\n=== KIỂM TRA KẾ HOẠCH ĂN CHO NGƯỜI DÙNG ===")
    print(f"ID Người dùng: {USER_ID}")
    
    # Kiểm tra trực tiếp từ Firestore
    print("\n1. Đọc từ firestore_service.get_latest_meal_plan:")
    meal_plan_firestore = firestore_service.get_latest_meal_plan(USER_ID)
    if meal_plan_firestore:
        print(f"  ✅ Tìm thấy kế hoạch ăn trong Firestore với {len(meal_plan_firestore.days)} ngày")
        # In một phần nhỏ để xác nhận
        print(f"  Ngày đầu tiên: {meal_plan_firestore.days[0].day_of_week}")
    else:
        print("  ❌ Không tìm thấy kế hoạch ăn trong Firestore")
    
    # Kiểm tra từ storage_manager
    print("\n2. Đọc từ storage_manager.load_meal_plan:")
    meal_plan_storage = storage_manager.load_meal_plan(USER_ID)
    if meal_plan_storage:
        print(f"  ✅ Tìm thấy kế hoạch ăn qua storage_manager với {len(meal_plan_storage.days)} ngày")
        # In một phần nhỏ để xác nhận
        print(f"  Ngày đầu tiên: {meal_plan_storage.days[0].day_of_week}")
    else:
        print("  ❌ Không tìm thấy kế hoạch ăn qua storage_manager")
    
    # Kiểm tra trực tiếp document trong Firestore
    print("\n3. Kiểm tra trực tiếp document trong collection 'latest_meal_plans':")
    doc_ref = firestore_service.db.collection('latest_meal_plans').document(USER_ID)
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        print(f"  ✅ Document tồn tại trong collection 'latest_meal_plans'")
        if 'days' in data and data['days']:
            print(f"  Số ngày trong document: {len(data['days'])}")
            if data['days'][0].get('day_of_week'):
                print(f"  Ngày đầu tiên: {data['days'][0]['day_of_week']}")
        else:
            print("  ⚠️ Document không có trường 'days' hoặc trường này rỗng")
    else:
        print("  ❌ Document không tồn tại trong collection 'latest_meal_plans'")
    
    # Kiểm tra trong collection 'meal_plans'
    print("\n4. Kiểm tra trong collection 'meal_plans':")
    query = firestore_service.db.collection('meal_plans').where('user_id', '==', USER_ID).limit(1)
    results = list(query.stream())
    if results:
        data = results[0].to_dict()
        print(f"  ✅ Tìm thấy kế hoạch ăn trong collection 'meal_plans'")
        if 'days' in data and data['days']:
            print(f"  Số ngày trong document: {len(data['days'])}")
            if data['days'][0].get('day_of_week'):
                print(f"  Ngày đầu tiên: {data['days'][0]['day_of_week']}")
        else:
            print("  ⚠️ Document không có trường 'days' hoặc trường này rỗng")
    else:
        print("  ❌ Không tìm thấy kế hoạch ăn trong collection 'meal_plans'")
    
    # Kiểm tra xem storage_manager có sử dụng Firebase không
    print("\n5. Kiểm tra cấu hình storage_manager:")
    print(f"  Sử dụng Firebase: {storage_manager.use_firebase}")
    print(f"  Firebase đã khởi tạo: {storage_manager.firebase_initialized}")

# Kiểm tra xem có collection 'latest_meal_plans' không
def check_collections():
    print("\n=== KIỂM TRA CÁC COLLECTION TRONG FIRESTORE ===\n")
    
    try:
        # Lấy danh sách các collection
        collections = firestore_service.db.collections()
        collection_names = [col.id for col in collections]
        
        print(f"Các collection trong Firestore: {collection_names}")
        
        # Kiểm tra collection 'latest_meal_plans'
        if 'latest_meal_plans' in collection_names:
            print(f"✅ Tìm thấy collection 'latest_meal_plans'")
            
            # Liệt kê các document trong collection
            docs = firestore_service.db.collection('latest_meal_plans').stream()
            doc_ids = [doc.id for doc in docs]
            
            print(f"Các document trong 'latest_meal_plans': {doc_ids}")
            
            # Kiểm tra document của user cụ thể
            if USER_ID in doc_ids:
                print(f"✅ Tìm thấy document cho user {USER_ID}")
            else:
                print(f"❌ Không tìm thấy document cho user {USER_ID}")
        else:
            print(f"❌ Không tìm thấy collection 'latest_meal_plans'")
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra collections: {str(e)}")

def check_meal_plan_document():
    print("\n=== KIỂM TRA CHI TIẾT DOCUMENT CỦA USER ===\n")
    
    try:
        # Lấy document của user
        doc_ref = firestore_service.db.collection('latest_meal_plans').document(USER_ID)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            
            # Kiểm tra các trường cơ bản
            print(f"Document có các trường: {list(data.keys())}")
            
            # Kiểm tra trường days
            if 'days' in data:
                days = data['days']
                print(f"Document có {len(days)} ngày")
                
                # Liệt kê các ngày
                days_of_week = [day.get('day_of_week', f'Ngày {i+1}') for i, day in enumerate(days)]
                print(f"Các ngày trong kế hoạch: {days_of_week}")
                
                # Kiểm tra ngày Chủ Nhật
                sunday_exists = any(day.get('day_of_week') == 'Chủ Nhật' for day in days)
                if sunday_exists:
                    print(f"✅ Tìm thấy ngày 'Chủ Nhật' trong kế hoạch")
                else:
                    print(f"❌ Không tìm thấy ngày 'Chủ Nhật' trong kế hoạch")
            else:
                print(f"❌ Document không có trường 'days'")
        else:
            print(f"❌ Document không tồn tại")
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra document: {str(e)}")

if __name__ == "__main__":
    test_flutter_to_firebase_flow()
    test_firebase_vs_storage_manager()
    check_collections()
    check_meal_plan_document() 