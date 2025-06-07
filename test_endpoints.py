import requests
import json
from typing import Dict, Any, List, Optional

# Thông tin người dùng cần kiểm tra
USER_ID = "49DhdmJHFAY40eEgaPNEJqGdDQK2"
SERVER_URL = "http://localhost:8000"  # URL của backend server

def test_replace_day_endpoint():
    """
    Kiểm tra endpoint /api/replace-day
    """
    print("\n=== KIỂM TRA ENDPOINT /api/replace-day ===\n")
    
    # Dữ liệu gửi đi
    data = {
        "user_id": USER_ID,
        "day_of_week": "Chủ Nhật",
        "calories_target": 2468,
        "protein_target": 185,
        "fat_target": 82,
        "carbs_target": 247,
        "use_ai": True,
        "diet_restrictions": [],
        "health_conditions": [],
        "diet_preference": ""
    }
    
    # Đường dẫn tới server FastAPI
    url = f"{SERVER_URL}/api/replace-day"
    
    # Gửi yêu cầu
    print(f"Gửi yêu cầu đến: {url}")
    print(f"Dữ liệu gửi đi: {json.dumps(data)}")
    
    try:
        response = requests.post(url, json=data)
        print(f"Mã trạng thái: {response.status_code}")
        print(f"Nội dung phản hồi: {response.text}")
    except Exception as e:
        print(f"❌ Lỗi khi gọi API: {str(e)}")

def test_with_get_current_meal_plan():
    """
    Kiểm tra hàm get_current_meal_plan trực tiếp
    """
    print("\n=== KIỂM TRA HÀM get_current_meal_plan ===\n")
    
    from main import get_current_meal_plan
    import asyncio
    
    async def test_meal_plan():
        try:
            # Gọi hàm get_current_meal_plan với user_id
            meal_plan = await get_current_meal_plan(USER_ID)
            
            if meal_plan:
                print(f"✅ Tìm thấy kế hoạch ăn cho user {USER_ID}")
                print(f"Số ngày trong kế hoạch: {len(meal_plan.days)}")
                
                # Kiểm tra ngày Chủ Nhật
                sunday_exists = any(day.day_of_week == 'Chủ Nhật' for day in meal_plan.days)
                if sunday_exists:
                    print(f"✅ Tìm thấy ngày 'Chủ Nhật' trong kế hoạch")
                else:
                    print(f"❌ Không tìm thấy ngày 'Chủ Nhật' trong kế hoạch")
            else:
                print(f"❌ Không tìm thấy kế hoạch ăn cho user {USER_ID}")
        except Exception as e:
            print(f"❌ Lỗi khi gọi hàm get_current_meal_plan: {str(e)}")
    
    # Chạy hàm bất đồng bộ
    asyncio.run(test_meal_plan())

def check_meal_plan_directly():
    """
    Kiểm tra kế hoạch ăn trực tiếp từ Firestore
    """
    print("\n=== KIỂM TRA KẾ HOẠCH ĂN TRỰC TIẾP TỪ FIRESTORE ===\n")
    
    from services.firestore_service import firestore_service
    
    # Lấy kế hoạch ăn từ phương thức get_latest_meal_plan
    meal_plan = firestore_service.get_latest_meal_plan(USER_ID)
    
    if meal_plan:
        print(f"✅ Tìm thấy kế hoạch ăn cho user {USER_ID} qua firestore_service.get_latest_meal_plan")
        print(f"Số ngày trong kế hoạch: {len(meal_plan.days)}")
        
        # Kiểm tra ngày Chủ Nhật
        sunday_exists = any(day.day_of_week == 'Chủ Nhật' for day in meal_plan.days)
        if sunday_exists:
            print(f"✅ Tìm thấy ngày 'Chủ Nhật' trong kế hoạch")
        else:
            print(f"❌ Không tìm thấy ngày 'Chủ Nhật' trong kế hoạch")
    else:
        print(f"❌ Không tìm thấy kế hoạch ăn cho user {USER_ID} qua firestore_service.get_latest_meal_plan")
    
    # Lấy trực tiếp từ collection
    doc_ref = firestore_service.db.collection('latest_meal_plans').document(USER_ID)
    doc = doc_ref.get()
    
    if doc.exists:
        print(f"\n✅ Document tồn tại trong collection 'latest_meal_plans'")
        data = doc.to_dict()
        
        if 'days' in data:
            print(f"✅ Document có trường 'days' với {len(data['days'])} ngày")
            
            # Kiểm tra ngày Chủ Nhật
            sunday_exists = any(day.get('day_of_week') == 'Chủ Nhật' for day in data['days'])
            if sunday_exists:
                print(f"✅ Tìm thấy ngày 'Chủ Nhật' trong dữ liệu trực tiếp")
            else:
                print(f"❌ Không tìm thấy ngày 'Chủ Nhật' trong dữ liệu trực tiếp")
        else:
            print(f"❌ Document không có trường 'days'")
    else:
        print(f"\n❌ Document không tồn tại trong collection 'latest_meal_plans'")

def debug_endpoint():
    """
    Debug endpoint và thêm thông tin chi tiết
    """
    print("\n=== DEBUG ENDPOINT /api/replace-day ===\n")
    
    # Thêm code để theo dõi hành vi của endpoint
    
    print("Kiểm tra luồng hoạt động:")
    print("1. Flutter gửi request đến /api/replace-day")
    print("2. main.py:1223 xử lý endpoint, gọi get_current_meal_plan(user_id)")
    print("3. get_current_meal_plan sử dụng storage_manager.load_meal_plan(user_id)")
    print("4. storage_manager.load_meal_plan gọi firebase.load_meal_plan(user_id)")
    print("5. firebase.load_meal_plan truy cập Firestore 'latest_meal_plans/{user_id}'")
    
    print("\nTrong trường hợp này, có thể xảy ra vấn đề ở bước 3-5 khi load_meal_plan")
    print("Khả năng cao nhất là hàm không tìm thấy document hoặc đường dẫn không đúng")

# Chạy các hàm kiểm tra
if __name__ == "__main__":
    test_replace_day_endpoint()
    check_meal_plan_directly()
    test_with_get_current_meal_plan()
    debug_endpoint() 