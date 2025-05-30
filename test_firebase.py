import os
import json
from datetime import datetime
from models import WeeklyMealPlan, DayMealPlan, Meal, Dish, NutritionInfo, Ingredient
from firebase_integration import firebase

def test_firebase_direct():
    """Test trực tiếp việc lưu dữ liệu lên Firebase không qua storage_manager"""
    print("=== TESTING FIREBASE DIRECT SAVE ===")
    
    # Tạo dữ liệu mẫu giống với dữ liệu trong Firestore hiện tại
    test_dish = Dish(
        name="Test Dish Direct",
        ingredients=[
            Ingredient(name="Gạo", amount="150g"),
            Ingredient(name="Thịt gà", amount="100g"),
            Ingredient(name="Rau cải", amount="50g")
        ],
        preparation="Chế biến tất cả nguyên liệu theo công thức",
        nutrition=NutritionInfo(calories=250, protein=20, fat=10, carbs=30)
    )
    
    # Tạo bữa ăn
    breakfast = Meal(
        dishes=[test_dish],
        nutrition=NutritionInfo(calories=250, protein=20, fat=10, carbs=30)
    )
    
    # Tạo kế hoạch ngày
    day_plan = DayMealPlan(
        day_of_week="Thứ 2",
        breakfast=breakfast,
        lunch=breakfast,  # Tái sử dụng cho đơn giản
        dinner=breakfast,  # Tái sử dụng cho đơn giản
        nutrition=NutritionInfo(calories=750, protein=60, fat=30, carbs=90)
    )
    
    # Tạo kế hoạch tuần
    meal_plan = WeeklyMealPlan(days=[day_plan])
    
    # Tạo user_id test
    user_id = f"test_firebase_direct_{int(datetime.now().timestamp())}"
    
    print(f"\nTạo kế hoạch bữa ăn cho user: {user_id}")
    print(f"- Món ăn: {test_dish.name}")
    print(f"- Nguyên liệu: {[ing.name for ing in test_dish.ingredients]}")
    print(f"- Dinh dưỡng: {test_dish.nutrition.calories} calo")
    
    # Lưu trực tiếp vào Firebase
    print("\nLưu kế hoạch vào Firebase...")
    try:
        if firebase.initialized:
            doc_id = firebase.save_meal_plan(meal_plan, user_id)
            if doc_id:
                print(f"Lưu thành công! Document ID: {doc_id}")
                
                # Thử đọc lại dữ liệu
                print("\nĐọc lại kế hoạch từ Firebase...")
                loaded_plan = firebase.load_meal_plan(user_id)
                
                if loaded_plan:
                    print("Đọc kế hoạch thành công!")
                    print(f"- Số ngày: {len(loaded_plan.days)}")
                    print(f"- Ngày: {loaded_plan.days[0].day_of_week}")
                    print(f"- Món ăn sáng: {len(loaded_plan.days[0].breakfast.dishes)} món")
                    
                    if loaded_plan.days[0].breakfast.dishes:
                        first_dish = loaded_plan.days[0].breakfast.dishes[0]
                        print(f"- Tên món đầu tiên: {first_dish.name}")
                        print(f"- Số nguyên liệu: {len(first_dish.ingredients)}")
                else:
                    print("Không thể đọc lại kế hoạch từ Firebase!")
                
                # Thử lấy lịch sử kế hoạch
                print("\nLấy lịch sử kế hoạch...")
                history = firebase.get_meal_plan_history(user_id)
                if history:
                    print(f"Tìm thấy {len(history)} kế hoạch trong lịch sử")
                    for i, plan in enumerate(history):
                        print(f"- Kế hoạch {i+1}: ID {plan.get('id')}, ngày {plan.get('timestamp')}")
                else:
                    print("Không tìm thấy lịch sử kế hoạch!")
            else:
                print("Lưu thất bại! Không nhận được Document ID")
        else:
            print("Firebase chưa được khởi tạo!")
    except Exception as e:
        print(f"Lỗi khi tương tác với Firebase: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_firebase_direct() 