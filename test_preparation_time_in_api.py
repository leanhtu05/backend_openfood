"""
Script kiểm tra việc xử lý preparation_time và health_benefits trong API
"""
import os
import json
import time
from typing import Dict, List

# Import services
from services.meal_services import generate_dish, generate_meal
from models import Dish, NutritionInfo, Ingredient

def create_test_dish_data():
    """Tạo dữ liệu món ăn mẫu để kiểm tra"""
    dish_data = {
        "name": "Món Ăn Test API",
        "ingredients": [
            {"name": "Nguyên liệu 1", "amount": "100g"},
            {"name": "Nguyên liệu 2", "amount": "50g"}
        ],
        "preparation": "Bước 1: Làm cái này. Bước 2: Làm cái kia. Bước 3: Hoàn thành.",
        "nutrition": {"calories": 300, "protein": 20, "fat": 10, "carbs": 30},
        "dish_type": "main",
        "region": "north",
        "preparation_time": "30 phút",
        "health_benefits": "Giàu protein. Hỗ trợ giảm cân. Tốt cho sức khỏe tim mạch."
    }
    return dish_data

def test_generate_dish():
    """Kiểm tra hàm generate_dish với dữ liệu có preparation_time và health_benefits"""
    dish_data = create_test_dish_data()
    
    # In dữ liệu đầu vào
    print("=== Dữ liệu đầu vào ===")
    print(f"preparation_time: {dish_data.get('preparation_time')}")
    print(f"health_benefits: {dish_data.get('health_benefits')}")
    
    # Tạo Dish từ dữ liệu
    dish = generate_dish(dish_data)
    
    # Kiểm tra kết quả
    print("\n=== Dữ liệu đối tượng Dish ===")
    print(f"preparation_time: {dish.preparation_time}")
    print(f"health_benefits: {dish.health_benefits}")
    
    # Chuyển đổi thành dictionary và kiểm tra
    dish_dict = {
        "name": dish.name,
        "ingredients": [ing.dict() for ing in dish.ingredients],
        "preparation": dish.preparation,
        "nutrition": dish.nutrition.dict(),
        "dish_type": dish.dish_type,
        "region": dish.region,
        "preparation_time": dish.preparation_time,
        "health_benefits": dish.health_benefits
    }
    
    print("\n=== Dữ liệu Dictionary từ Dish ===")
    print(f"preparation_time: {dish_dict.get('preparation_time')}")
    print(f"health_benefits: {dish_dict.get('health_benefits')}")
    
    # Chuyển đổi sang JSON để kiểm tra serialization
    json_data = json.dumps(dish_dict, ensure_ascii=False, indent=2)
    print("\n=== Dữ liệu JSON ===")
    print(json_data)
    
    # Chuyển đổi từ JSON trở lại để kiểm tra deserialization
    parsed_data = json.loads(json_data)
    print("\n=== Dữ liệu sau khi parse từ JSON ===")
    print(f"preparation_time: {parsed_data.get('preparation_time')}")
    print(f"health_benefits: {parsed_data.get('health_benefits')}")
    
    # Thực hiện assertion để kiểm tra
    assert dish.preparation_time is not None, "preparation_time bị mất trong đối tượng Dish"
    assert dish.health_benefits is not None, "health_benefits bị mất trong đối tượng Dish"
    assert dish_dict.get('preparation_time') is not None, "preparation_time bị mất trong dictionary"
    assert dish_dict.get('health_benefits') is not None, "health_benefits bị mất trong dictionary"
    assert parsed_data.get('preparation_time') is not None, "preparation_time bị mất sau khi serialize/deserialize JSON"
    assert parsed_data.get('health_benefits') is not None, "health_benefits bị mất sau khi serialize/deserialize JSON"
    
    return True

def test_generate_meal():
    """Kiểm tra hàm generate_meal xem có xử lý preparation_time và health_benefits đúng không"""
    # Gọi hàm generate_meal với tham số phù hợp
    meal = generate_meal(
        meal_type="bữa sáng",
        target_calories=500,
        target_protein=30,
        target_fat=15,
        target_carbs=60,
        use_ai=False  # Không sử dụng AI để tránh gọi API thật
    )
    
    # Kiểm tra kết quả
    print("\n=== Kết quả từ generate_meal ===")
    print(f"Số món ăn: {len(meal.dishes)}")
    
    for i, dish in enumerate(meal.dishes):
        print(f"\nMón {i+1}: {dish.name}")
        print(f"preparation_time: {dish.preparation_time}")
        print(f"health_benefits: {dish.health_benefits}")
        
        # Kiểm tra xem các trường có tồn tại không
        assert dish.preparation_time is not None, f"preparation_time bị mất trong món {dish.name}"
        assert dish.health_benefits is not None, f"health_benefits bị mất trong món {dish.name}"
    
    return True

if __name__ == "__main__":
    print("==== Kiểm tra hàm generate_dish ====")
    test_generate_dish()
    
    print("\n==== Kiểm tra hàm generate_meal ====")
    test_generate_meal()
    
    print("\n==== Tất cả kiểm tra hoàn thành thành công! ====") 