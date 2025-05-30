"""
Test file để kiểm tra tính năng TDEE và điều chỉnh giá trị dinh dưỡng.
"""
import json
import os
import sys

# Thêm thư mục gốc vào đường dẫn để import các module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.tdee_nutrition_service import tdee_nutrition_service

def test_calculate_tdee():
    """Kiểm tra tính toán TDEE"""
    print("\n===== KIỂM TRA TÍNH TOÁN TDEE =====")
    
    # Test case 1: Nam, 70kg, 175cm, 30 tuổi, hoạt động vừa phải
    tdee1 = tdee_nutrition_service.calculate_tdee(70, 175, 30, "male", "moderate")
    print(f"Nam, 70kg, 175cm, 30 tuổi, hoạt động vừa phải: {tdee1} kcal")
    
    # Test case 2: Nữ, 55kg, 165cm, 25 tuổi, hoạt động nhẹ
    tdee2 = tdee_nutrition_service.calculate_tdee(55, 165, 25, "female", "light")
    print(f"Nữ, 55kg, 165cm, 25 tuổi, hoạt động nhẹ: {tdee2} kcal")
    
    # Test case 3: Nam, 85kg, 180cm, 40 tuổi, hoạt động nhiều
    tdee3 = tdee_nutrition_service.calculate_tdee(85, 180, 40, "male", "active")
    print(f"Nam, 85kg, 180cm, 40 tuổi, hoạt động nhiều: {tdee3} kcal")

def test_adjust_nutrition_targets():
    """Kiểm tra điều chỉnh mục tiêu dinh dưỡng"""
    print("\n===== KIỂM TRA ĐIỀU CHỈNH MỤC TIÊU DINH DƯỠNG =====")
    
    # Test case 1: TDEE = 2000, mục tiêu duy trì cân nặng
    calories, protein, fat, carbs = tdee_nutrition_service.adjust_nutrition_targets(2000, "maintain")
    print(f"TDEE = 2000, mục tiêu duy trì: calories={calories}, protein={protein}g, fat={fat}g, carbs={carbs}g")
    
    # Test case 2: TDEE = 2500, mục tiêu giảm cân
    calories, protein, fat, carbs = tdee_nutrition_service.adjust_nutrition_targets(2500, "lose_weight")
    print(f"TDEE = 2500, mục tiêu giảm cân: calories={calories}, protein={protein}g, fat={fat}g, carbs={carbs}g")
    
    # Test case 3: TDEE = 1800, mục tiêu tăng cân
    calories, protein, fat, carbs = tdee_nutrition_service.adjust_nutrition_targets(1800, "gain_weight")
    print(f"TDEE = 1800, mục tiêu tăng cân: calories={calories}, protein={protein}g, fat={fat}g, carbs={carbs}g")
    
    # Test case 4: Không có TDEE, sử dụng giá trị mặc định
    calories, protein, fat, carbs = tdee_nutrition_service.adjust_nutrition_targets()
    print(f"Không có TDEE, giá trị mặc định: calories={calories}, protein={protein}g, fat={fat}g, carbs={carbs}g")

def test_get_nutrition_targets_from_user_profile():
    """Kiểm tra lấy mục tiêu dinh dưỡng từ profile người dùng"""
    print("\n===== KIỂM TRA LẤY MỤC TIÊU DINH DƯỠNG TỪ PROFILE =====")
    
    # Test case 1: Có tdeeValues đầy đủ
    user_profile1 = {
        "tdeeValues": {
            "calories": 1800,
            "protein": 120,
            "fat": 60,
            "carbs": 200
        },
        "goal": "maintain",
        "weightKg": 70,
        "heightCm": 175,
        "age": 30,
        "gender": "male",
        "activityLevel": "moderate"
    }
    
    calories, protein, fat, carbs = tdee_nutrition_service.get_nutrition_targets_from_user_profile(user_profile1)
    print(f"Profile với tdeeValues: calories={calories}, protein={protein}g, fat={fat}g, carbs={carbs}g")
    
    # Test case 2: Có TDEE nhưng không có tdeeValues
    user_profile2 = {
        "tdee": 2200,
        "goal": "lose_weight",
        "weightKg": 80,
        "heightCm": 180,
        "age": 35,
        "gender": "male",
        "activityLevel": "active"
    }
    
    calories, protein, fat, carbs = tdee_nutrition_service.get_nutrition_targets_from_user_profile(user_profile2)
    print(f"Profile với TDEE: calories={calories}, protein={protein}g, fat={fat}g, carbs={carbs}g")
    
    # Test case 3: Không có TDEE nhưng có thông tin cơ bản
    user_profile3 = {
        "weightKg": 55,
        "heightCm": 165,
        "age": 25,
        "gender": "female",
        "activityLevel": "light",
        "goal": "gain_weight"
    }
    
    calories, protein, fat, carbs = tdee_nutrition_service.get_nutrition_targets_from_user_profile(user_profile3)
    print(f"Profile với thông tin cơ bản: calories={calories}, protein={protein}g, fat={fat}g, carbs={carbs}g")
    
    # Test case 4: Không có thông tin
    user_profile4 = {
        "displayName": "Test User",
        "email": "test@example.com"
    }
    
    calories, protein, fat, carbs = tdee_nutrition_service.get_nutrition_targets_from_user_profile(user_profile4)
    print(f"Profile không có thông tin: calories={calories}, protein={protein}g, fat={fat}g, carbs={carbs}g")

if __name__ == "__main__":
    print("===== KIỂM TRA TÍNH NĂNG TDEE =====\n")
    
    test_calculate_tdee()
    test_adjust_nutrition_targets()
    test_get_nutrition_targets_from_user_profile()
    
    print("\n===== KIỂM TRA HOÀN TẤT =====") 