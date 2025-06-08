"""
Kiểm tra sửa lỗi cho trường preparation trong Dish model.
"""

import json
import requests
from services.firestore_service import firestore_service
from models import Dish, Ingredient, NutritionInfo, DishType

# Địa chỉ API
SERVER_URL = "http://localhost:8000"  # Thay đổi nếu cần

def test_transform_meal_plan_data():
    """
    Kiểm tra hàm _transform_meal_plan_data có chuyển đổi preparation thành list đúng cách.
    """
    print("\n=== KIỂM TRA HÀM _transform_meal_plan_data ===\n")
    
    # Tạo dữ liệu mẫu với các định dạng preparation khác nhau
    test_data = {
        "days": [
            {
                "day_of_week": "Thứ 2",
                "breakfast": {
                    "dishes": [
                        {
                            "name": "Món 1 - preparation dạng chuỗi",
                            "preparation": "Bước 1: Làm việc A. Bước 2: Làm việc B.",
                            "ingredients": []
                        },
                        {
                            "name": "Món 2 - preparation dạng chuỗi có xuống dòng",
                            "preparation": "Bước 1: Làm việc A.\nBước 2: Làm việc B.",
                            "ingredients": []
                        },
                        {
                            "name": "Món 3 - preparation dạng danh sách",
                            "preparation": ["Bước 1: Làm việc A", "Bước 2: Làm việc B"],
                            "ingredients": []
                        },
                        {
                            "name": "Món 4 - không có preparation",
                            "ingredients": []
                        }
                    ],
                    "nutrition": {"calories": 500, "protein": 30, "fat": 20, "carbs": 50}
                },
                "lunch": {
                    "dishes": [],
                    "nutrition": {"calories": 600, "protein": 35, "fat": 25, "carbs": 60}
                },
                "dinner": {
                    "dishes": [],
                    "nutrition": {"calories": 500, "protein": 30, "fat": 20, "carbs": 50}
                }
            }
        ]
    }
    
    # Gọi hàm chuyển đổi
    transformed_data = firestore_service._transform_meal_plan_data(test_data)
    
    # Kiểm tra kết quả
    print("\n=== KẾT QUẢ CHUYỂN ĐỔI ===\n")
    
    # Lấy các món ăn trong bữa sáng
    breakfast_dishes = transformed_data["days"][0]["breakfast"]["dishes"]
    
    # Kiểm tra từng món ăn
    for i, dish in enumerate(breakfast_dishes):
        print(f"Món {i+1}: {dish['name']}")
        if "preparation" in dish:
            print(f"  - Kiểu dữ liệu preparation: {type(dish['preparation'])}")
            print(f"  - Giá trị preparation: {dish['preparation']}")
        else:
            print("  - Không có trường preparation")
        print()
    
    # Kiểm tra xem tất cả preparation có phải là list không
    all_list = all(isinstance(dish.get("preparation", []), list) for dish in breakfast_dishes)
    print(f"Tất cả preparation có dạng list: {all_list}")
    
    return all_list

def test_api_replace_day():
    """
    Kiểm tra API /api/replace-day với dữ liệu preparation khác nhau.
    """
    print("\n=== KIỂM TRA API /api/replace-day ===\n")
    
    # Dữ liệu gửi đi
    request_data = {
        "user_id": "test_user",
        "day_of_week": "Thứ 2",
        "calories_target": 2000,
        "protein_target": 120,
        "fat_target": 67,
        "carbs_target": 250,
        "use_ai": False
    }
    
    # Lưu một meal plan mẫu vào Firestore
    sample_dish = Dish(
        name="Món ăn mẫu",
        ingredients=[Ingredient(name="Nguyên liệu 1", amount="100g")],
        preparation=["Bước 1: Làm việc A", "Bước 2: Làm việc B"],
        nutrition=NutritionInfo(calories=500, protein=30, fat=20, carbs=50),
        dish_type=DishType.MAIN
    )
    
    # Gửi yêu cầu API
    try:
        response = requests.post(
            f"{SERVER_URL}/api/replace-day",
            json=request_data
        )
        
        print(f"Mã trạng thái: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Phản hồi API: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
            
            # Kiểm tra cấu trúc dữ liệu phản hồi
            if "day_meal_plan" in result:
                # Lấy một món ăn từ kết quả để kiểm tra
                day_plan = result["day_meal_plan"]
                if "breakfast" in day_plan and "dishes" in day_plan["breakfast"]:
                    dishes = day_plan["breakfast"]["dishes"]
                    if dishes:
                        sample_dish = dishes[0]
                        print(f"\nKiểm tra món ăn mẫu: {sample_dish.get('name')}")
                        if "preparation" in sample_dish:
                            prep = sample_dish["preparation"]
                            print(f"  - Kiểu dữ liệu preparation: {type(prep)}")
                            print(f"  - Giá trị preparation: {prep}")
                            
                            # Kiểm tra xem preparation có phải là list không
                            is_list = isinstance(prep, list)
                            print(f"  - Preparation có dạng list: {is_list}")
                            return is_list
            
            return False
        else:
            print(f"Lỗi: {response.text}")
            return False
    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")
        return False

if __name__ == "__main__":
    print("Bắt đầu kiểm tra sửa lỗi cho trường preparation trong Dish model...")
    
    # Kiểm tra hàm chuyển đổi
    transform_result = test_transform_meal_plan_data()
    
    # Kiểm tra API
    api_result = test_api_replace_day()
    
    # Kết luận
    print("\n=== KẾT LUẬN ===\n")
    if transform_result and api_result:
        print("✅ Sửa lỗi thành công! Trường preparation được xử lý đúng dạng list trong cả hàm chuyển đổi và API.")
    elif transform_result:
        print("⚠️ Hàm chuyển đổi hoạt động tốt, nhưng API vẫn chưa trả về preparation dạng list.")
    elif api_result:
        print("⚠️ API trả về preparation dạng list, nhưng hàm chuyển đổi chưa hoạt động đúng.")
    else:
        print("❌ Sửa lỗi chưa thành công. Cần kiểm tra lại cả hàm chuyển đổi và API.") 