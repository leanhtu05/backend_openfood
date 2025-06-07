import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import sys
from datetime import datetime
import requests
from typing import Dict, Any, List, Optional

# Kiểm tra xem Firebase đã được khởi tạo chưa
try:
    app = firebase_admin.get_app()
    print("Firebase đã được khởi tạo trước đó")
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
        print("Không tìm thấy file credentials Firebase!")
        sys.exit(1)
        
    firebase_admin.initialize_app(cred)
    print("Firebase đã được khởi tạo thành công")

# Khởi tạo Firestore client
db = firestore.client()

# Thông tin người dùng cần kiểm tra
USER_ID = "49DhdmJHFAY40eEgaPNEJqGdDQK2"
SERVER_URL = "http://localhost:8000"  # URL của backend server

def verify_user_data(user_id=None):
    """
    Kiểm tra dữ liệu người dùng trong Firestore
    
    Args:
        user_id: ID của người dùng cần kiểm tra (nếu không cung cấp, sẽ yêu cầu nhập)
    """
    if not user_id:
        user_id = input("Nhập Firebase UID của người dùng cần kiểm tra: ")
    
    print(f"\n=== ĐANG KIỂM TRA DỮ LIỆU NGƯỜI DÙNG: {user_id} ===\n")
    
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
        print("✅ Tìm thấy dữ liệu người dùng trong Firestore:")
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
            try:
                # Chuyển đổi chuỗi ISO thành đối tượng datetime
                updated_datetime = datetime.fromisoformat(updated_at)
                # Tính thời gian trôi qua
                time_diff = datetime.now() - updated_datetime
                
                if time_diff.total_seconds() < 3600:  # Trong vòng 1 giờ
                    print(f"✅ Dữ liệu đã được cập nhật gần đây: {updated_at}")
                else:
                    print(f"⚠️ Dữ liệu đã được cập nhật cách đây {time_diff.days} ngày {time_diff.seconds // 3600} giờ: {updated_at}")
            except:
                print(f"⚠️ Không thể phân tích thời gian cập nhật: {updated_at}")
        else:
            print("⚠️ Không tìm thấy thời gian cập nhật")
        
        # Hiển thị thông tin TDEE nếu có
        tdee_values = user_data.get('tdeeValues')
        if tdee_values:
            print("\nThông tin TDEE:")
            print(f"  - Calories: {tdee_values.get('calories', 'Không có')}")
            print(f"  - Protein: {tdee_values.get('protein', 'Không có')} g")
            print(f"  - Carbs: {tdee_values.get('carbs', 'Không có')} g")
            print(f"  - Fat: {tdee_values.get('fat', 'Không có')} g")
        
        # Hiển thị thông tin sở thích và dị ứng nếu có
        preferred_cuisines = user_data.get('preferred_cuisines', [])
        if preferred_cuisines:
            print("\nẨm thực ưa thích:")
            for cuisine in preferred_cuisines:
                print(f"  - {cuisine}")
        
        allergies = user_data.get('allergies', [])
        if allergies:
            print("\nDị ứng thực phẩm:")
            for allergy in allergies:
                print(f"  - {allergy}")
        
        # Hiển thị toàn bộ dữ liệu dưới dạng JSON
        print("\nDữ liệu đầy đủ:")
        print(json.dumps(user_data, indent=2, ensure_ascii=False))
        
        return True
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra dữ liệu người dùng: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_endpoint_urls():
    """
    Kiểm tra danh sách các endpoints có sẵn
    """
    print("\n=== KIỂM TRA DANH SÁCH ENDPOINT ===\n")
    
    try:
        # Gửi yêu cầu GET đến endpoint gốc để lấy thông tin OpenAPI
        response = requests.get(f"{SERVER_URL}/openapi.json")
        
        if response.status_code == 200:
            api_docs = response.json()
            
            # Lấy danh sách các đường dẫn
            paths = api_docs.get("paths", {})
            
            # Tìm các endpoint liên quan đến meal-plan và replace-day
            related_endpoints = []
            for path, methods in paths.items():
                if "meal-plan" in path or "replace-day" in path or "meal_plan" in path:
                    for method, details in methods.items():
                        related_endpoints.append({
                            "path": path,
                            "method": method.upper(),
                            "summary": details.get("summary", "No summary"),
                            "description": details.get("description", "No description")
                        })
            
            print(f"Tìm thấy {len(related_endpoints)} endpoints liên quan đến meal-plan/replace-day:")
            for i, endpoint in enumerate(related_endpoints, 1):
                print(f"{i}. {endpoint['method']} {endpoint['path']}")
                print(f"   Summary: {endpoint['summary']}")
        else:
            print(f"❌ Không thể lấy thông tin OpenAPI: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra endpoints: {str(e)}")

def verify_endpoint_access():
    """
    Kiểm tra khả năng truy cập các endpoints liên quan đến meal-plan và replace-day
    """
    print("\n=== KIỂM TRA KHẢ NĂNG TRUY CẬP ENDPOINT ===\n")
    
    endpoints = [
        # Endpoint trong main.py
        {
            "url": f"{SERVER_URL}/api/replace-day",
            "method": "POST",
            "data": {
                "user_id": USER_ID,
                "day_of_week": "Chủ Nhật",
                "calories_target": 2468,
                "protein_target": 185,
                "fat_target": 82,
                "carbs_target": 247,
                "use_ai": True
            },
            "description": "Endpoint replace-day trong main.py"
        },
        # Endpoint trong api_router.py
        {
            "url": f"{SERVER_URL}/replace-day",
            "method": "POST",
            "data": {
                "user_id": USER_ID,
                "day_of_week": "Chủ Nhật",
                "calories_target": 2468,
                "protein_target": 185,
                "fat_target": 82,
                "carbs_target": 247,
                "use_ai": True
            },
            "description": "Endpoint replace-day trong api_router.py"
        },
        # Endpoint meal-plan/replace-meal
        {
            "url": f"{SERVER_URL}/api/meal-plan/replace-meal",
            "method": "POST",
            "data": {
                "user_id": USER_ID,
                "day_of_week": "Chủ Nhật",
                "meal_type": "dinner",
                "calories_target": 2468,
                "protein_target": 185,
                "fat_target": 82,
                "carbs_target": 247,
                "use_ai": True
            },
            "description": "Endpoint meal-plan/replace-meal trong main.py"
        },
        # Endpoint meal-plan/replace-meal với query parameter
        {
            "url": f"{SERVER_URL}/meal-plan/replace-meal?user_id={USER_ID}",
            "method": "POST",
            "data": {
                "day_of_week": "Chủ Nhật",
                "meal_type": "dinner",
                "calories_target": 2468,
                "protein_target": 185,
                "fat_target": 82,
                "carbs_target": 247,
                "use_ai": True
            },
            "description": "Endpoint meal-plan/replace-meal trong api_router.py"
        }
    ]
    
    for i, endpoint in enumerate(endpoints, 1):
        print(f"\n{i}. Kiểm tra {endpoint['description']}")
        print(f"URL: {endpoint['url']}")
        print(f"Dữ liệu: {json.dumps(endpoint['data'])}")
        
        try:
            response = requests.request(
                method=endpoint['method'],
                url=endpoint['url'],
                json=endpoint['data']
            )
            
            print(f"Mã trạng thái: {response.status_code}")
            print(f"Phản hồi: {response.text[:200]}...")
            
            if response.status_code == 200:
                print(f"✅ Truy cập thành công endpoint {endpoint['url']}")
            else:
                print(f"❌ Không thể truy cập endpoint {endpoint['url']}")
        except Exception as e:
            print(f"❌ Lỗi khi truy cập endpoint {endpoint['url']}: {str(e)}")

def fix_endpoint_issues():
    """
    Gợi ý cách sửa vấn đề với endpoints dựa trên kết quả kiểm tra
    """
    print("\n=== GỢI Ý SỬA VẤN ĐỀ VỚI ENDPOINTS ===\n")
    
    print("Dựa trên kết quả kiểm tra, có thể thực hiện các biện pháp sau:")
    print("1. Nếu endpoint /api/replace-day trả về lỗi 404 \"Không tìm thấy kế hoạch ăn\":")
    print("   - Kiểm tra lại phương thức storage_manager.load_meal_plan có đang sử dụng đúng user_id")
    print("   - Đảm bảo get_current_meal_plan trong main.py truy cập đúng vào Firestore")
    
    print("\n2. Nếu Flutter gọi sai endpoint:")
    print("   - Kiểm tra URL trong mã Flutter, đảm bảo gọi đúng /api/replace-day")
    print("   - Đảm bảo dữ liệu được gửi đi đúng định dạng")
    
    print("\n3. Nếu xác thực là vấn đề:")
    print("   - Sửa hàm get_optional_current_user để không yêu cầu xác thực")
    print("   - Thêm bypass cho chế độ phát triển")

def check_specific_user_data():
    """
    Kiểm tra dữ liệu cụ thể của user_id từ request Flutter
    """
    print(f"\n=== KIỂM TRA DỮ LIỆU CỤ THỂ CỦA USER {USER_ID} ===\n")
    
    from services.firestore_service import firestore_service
    
    # Đọc dữ liệu trực tiếp từ Firestore
    doc_ref = firestore_service.db.collection('latest_meal_plans').document(USER_ID)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"❌ Không tìm thấy kế hoạch ăn cho user {USER_ID} trong collection 'latest_meal_plans'")
        return
    
    print(f"✅ Tìm thấy kế hoạch ăn trong collection 'latest_meal_plans'")
    data = doc.to_dict()
    
    # Kiểm tra trường days
    if 'days' in data:
        days = data['days']
        print(f"✅ Document có {len(days)} ngày")
        
        # Kiểm tra các ngày trong kế hoạch
        days_of_week = [day.get('day_of_week', f'Ngày {i+1}') for i, day in enumerate(days)]
        print(f"Các ngày trong kế hoạch: {days_of_week}")
        
        # Kiểm tra ngày Chủ Nhật
        sunday_exists = any(day.get('day_of_week') == 'Chủ Nhật' for day in days)
        if sunday_exists:
            print(f"✅ Tìm thấy ngày 'Chủ Nhật' trong kế hoạch")
            
            # Tìm chi tiết về ngày Chủ Nhật
            for day in days:
                if day.get('day_of_week') == 'Chủ Nhật':
                    print(f"Chi tiết ngày Chủ Nhật:")
                    print(f"- Breakfast: {len(day.get('breakfast', {}).get('dishes', []))} món")
                    print(f"- Lunch: {len(day.get('lunch', {}).get('dishes', []))} món")
                    print(f"- Dinner: {len(day.get('dinner', {}).get('dishes', []))} món")
                    break
        else:
            print(f"❌ Không tìm thấy ngày 'Chủ Nhật' trong kế hoạch")
    else:
        print(f"❌ Document không có trường 'days'")

if __name__ == "__main__":
    # Kiểm tra xem có tham số dòng lệnh không
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        user_id = None
    
    verify_user_data(user_id)
    verify_endpoint_urls()
    verify_endpoint_access()
    check_specific_user_data()
    fix_endpoint_issues() 