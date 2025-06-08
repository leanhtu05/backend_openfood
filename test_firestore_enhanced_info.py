"""
Script kiểm tra việc lưu trữ thông tin nâng cao (preparation_time và health_benefits) vào Firestore
"""
import json
import time
from services.firestore_service import firestore_service
from models import Dish, NutritionInfo, Ingredient

def create_test_meal_plan():
    """Tạo dữ liệu kế hoạch bữa ăn mẫu"""
    # Tạo dữ liệu món ăn trực tiếp
    dish_dict = {
        "name": "Món Ăn Test",
        "ingredients": [
            {"name": "Nguyên liệu 1", "amount": "100g"},
            {"name": "Nguyên liệu 2", "amount": "50g"}
        ],
        "preparation": [
            "Bước 1: Làm cái này", 
            "Bước 2: Làm cái kia", 
            "Bước 3: Hoàn thành"
        ],
        "nutrition": {
            "calories": 300, 
            "protein": 20, 
            "fat": 10, 
            "carbs": 30
        },
        "dish_type": "main",
        "region": "north",
        "preparation_time": "30 phút",
        "health_benefits": "Giàu protein. Hỗ trợ giảm cân. Tốt cho sức khỏe tim mạch"
    }
    
    print(f"Dish dictionary: {json.dumps(dish_dict, indent=2, ensure_ascii=False)}")
    
    # Kiểm tra xem các trường quan trọng có tồn tại không
    assert "preparation_time" in dish_dict, "Thiếu trường preparation_time"
    assert "health_benefits" in dish_dict, "Thiếu trường health_benefits"
    
    # Tạo dữ liệu kế hoạch bữa ăn đơn giản
    meal_plan_data = {
        "user_id": "test_user",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "days": [
            {
                "day_of_week": "Thứ 2",
                "breakfast": {
                    "dishes": [dish_dict],
                    "nutrition": {"calories": 300, "protein": 20, "fat": 10, "carbs": 30}
                },
                "lunch": {
                    "dishes": [],
                    "nutrition": {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
                },
                "dinner": {
                    "dishes": [],
                    "nutrition": {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
                },
                "nutrition": {"calories": 300, "protein": 20, "fat": 10, "carbs": 30}
            }
        ]
    }
    
    return meal_plan_data

def transform_meal_plan_data():
    """Kiểm tra quá trình chuyển đổi dữ liệu kế hoạch bữa ăn"""
    meal_plan_data = create_test_meal_plan()
    
    # Lấy dữ liệu món ăn gốc trước khi chuyển đổi
    original_dish = meal_plan_data["days"][0]["breakfast"]["dishes"][0]
    print(f"Original dish preparation_time: {original_dish.get('preparation_time')}")
    print(f"Original dish health_benefits: {original_dish.get('health_benefits')}")
    
    # Chuyển đổi dữ liệu bằng hàm _transform_meal_plan_data
    transformed_data = firestore_service._transform_meal_plan_data(meal_plan_data)
    
    # Kiểm tra dữ liệu sau khi chuyển đổi
    transformed_dish = transformed_data["days"][0]["breakfast"]["dishes"][0]
    print(f"Transformed dish preparation_time: {transformed_dish.get('preparation_time')}")
    print(f"Transformed dish health_benefits: {transformed_dish.get('health_benefits')}")
    
    # Kiểm tra xem các trường quan trọng có được giữ nguyên không
    assert transformed_dish.get("preparation_time") == original_dish.get("preparation_time"), "preparation_time bị thay đổi"
    assert transformed_dish.get("health_benefits") is not None, "health_benefits bị mất"
    
    return True

def test_save_to_firestore():
    """Kiểm tra việc lưu dữ liệu vào Firestore"""
    # Tạo dữ liệu kế hoạch bữa ăn
    meal_plan_data = create_test_meal_plan()
    
    # Lưu vào Firestore
    try:
        # Trước tiên, chỉ sử dụng _transform_meal_plan_data để kiểm tra
        transformed_data = firestore_service._transform_meal_plan_data(meal_plan_data)
        
        # Kiểm tra dữ liệu sau khi chuyển đổi
        transformed_dish = transformed_data["days"][0]["breakfast"]["dishes"][0]
        print(f"Dữ liệu món ăn sau khi chuyển đổi:")
        print(f"- preparation_time: {transformed_dish.get('preparation_time')}")
        print(f"- health_benefits: {transformed_dish.get('health_benefits')}")
        
        # Nếu dữ liệu đã được chuyển đổi đúng, tiến hành lưu vào Firestore
        user_id = "test_user_" + str(int(time.time()))
        success = firestore_service.save_meal_plan(user_id, meal_plan_data)
        
        if success:
            print(f"Đã lưu kế hoạch bữa ăn vào Firestore thành công với user_id: {user_id}")
            return True
        else:
            print("Lưu vào Firestore thất bại")
            return False
    except Exception as e:
        print(f"Lỗi khi lưu vào Firestore: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("==== Kiểm tra chuyển đổi dữ liệu ====")
    transform_meal_plan_data()
    
    print("\n==== Kiểm tra lưu vào Firestore ====")
    test_save_to_firestore() 