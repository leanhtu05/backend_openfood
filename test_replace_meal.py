import requests
import json
from typing import Dict, Any, List, Optional

# Thông tin người dùng cần kiểm tra
USER_ID = "49DhdmJHFAY40eEgaPNEJqGdDQK2"
SERVER_URL = "http://localhost:8000"  # URL của backend server

def test_replace_meal():
    """
    Kiểm tra endpoint /api/meal-plan/replace-meal
    """
    print(f"\n=== KIỂM TRA REPLACE MEAL CHO USER {USER_ID} ===\n")
    
    # Tạo request body
    request_data = {
        "user_id": USER_ID,
        "day_of_week": "Chủ Nhật",
        "meal_type": "dinner",  # dinner, lunch, breakfast
        "calories_target": 2468,
        "protein_target": 185,
        "fat_target": 82,
        "carbs_target": 247,
        "use_ai": True,
        "diet_restrictions": [],
        "health_conditions": [],
        "diet_preference": ""
    }
    
    # Thêm headers với token xác thực - sử dụng token test mode để bypass xác thực
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_mode_token"  # Token đặc biệt để bypass authentication
    }
    
    # Gửi request tới API
    url = f"{SERVER_URL}/api/meal-plan/replace-meal"
    print(f"📦 Dữ liệu gửi đi: {json.dumps(request_data)}")
    
    try:
        response = requests.post(url, json=request_data, headers=headers)
        
        # In thông tin response
        print(f"📦 Response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            # Phân tích dữ liệu trả về
            data = response.json()
            
            # Kiểm tra xem có đúng ngày và loại bữa ăn không
            if data.get("day_of_week") == request_data["day_of_week"] and data.get("meal_type") == request_data["meal_type"]:
                print(f"✅ Đã thay thế thành công {request_data['meal_type']} cho {request_data['day_of_week']}")
                
                # Kiểm tra xem meal có đúng format không
                meal = data.get("meal", {})
                dishes = meal.get("dishes", [])
                
                if dishes:
                    print(f"✅ Bữa ăn mới có {len(dishes)} món")
                    
                    # Kiểm tra trường preparation của từng món
                    for i, dish in enumerate(dishes):
                        print(f"Món {i+1}: {dish.get('name')}")
                        
                        # In ra kiểu dữ liệu của preparation
                        preparation = dish.get("preparation", "")
                        print(f"- Preparation (type: {type(preparation).__name__}): {preparation[:50]}...")
                        
                        # Kiểm tra xem preparation có phải là chuỗi không
                        if isinstance(preparation, str):
                            print(f"✅ Preparation là chuỗi")
                        elif isinstance(preparation, list):
                            print(f"❌ Preparation là danh sách: {preparation}")
                        else:
                            print(f"❓ Preparation có kiểu dữ liệu không xác định: {type(preparation).__name__}")
                else:
                    print(f"❌ Không có món ăn nào trong bữa ăn mới")
            else:
                print(f"❌ Dữ liệu trả về không khớp với yêu cầu:")
                print(f"- Yêu cầu: {request_data['day_of_week']} / {request_data['meal_type']}")
                print(f"- Nhận được: {data.get('day_of_week')} / {data.get('meal_type')}")
        else:
            print(f"❌ Lỗi khi gọi API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")

# Chạy kiểm tra
if __name__ == "__main__":
    test_replace_meal() 