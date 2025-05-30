import os
import json
from datetime import datetime
from firebase_integration import firebase
from storage_manager import storage_manager

def test_firebase_meal_plan_structure():
    """Test đọc cấu trúc meal plan từ Firebase và in ra chi tiết để kiểm tra"""
    
    print("\n=== TESTING FIREBASE MEAL PLAN STRUCTURE ===")
    
    # Kiểm tra xem Firebase đã được khởi tạo chưa
    if not firebase.initialized:
        print("Firebase is not initialized")
        return
        
    print("Firebase initialized successfully")
    
    # Tạo một user_id để đọc dữ liệu
    user_id = input("Enter user ID to check (or press Enter for test_firebase_direct_1748078204): ").strip()
    if not user_id:
        user_id = "test_firebase_direct_1748078204"  # User ID mặc định từ test trước
    
    print(f"\nReading meal plan for user: {user_id}")
    
    # Đọc meal plan từ Firebase
    meal_plan = firebase.load_meal_plan(user_id)
    
    if not meal_plan:
        print(f"No meal plan found for user {user_id}")
        return
        
    print(f"\n=== MEAL PLAN STRUCTURE ===")
    print(f"Type: {type(meal_plan)}")
    
    # Thông tin cơ bản
    print(f"\nBasic Info:")
    print(f"Number of days: {len(meal_plan.days)}")
    
    # Chi tiết từng ngày
    for i, day in enumerate(meal_plan.days):
        print(f"\n--- DAY {i+1}: {day.day_of_week} ---")
        
        # Thông tin dinh dưỡng của ngày
        print(f"Day nutrition: calories={day.nutrition.calories}, protein={day.nutrition.protein}g, fat={day.nutrition.fat}g, carbs={day.nutrition.carbs}g")
        
        # Thông tin bữa sáng
        print(f"\nBREAKFAST ({len(day.breakfast.dishes)} dishes):")
        for j, dish in enumerate(day.breakfast.dishes):
            print(f"  Dish {j+1}: {dish.name}")
            print(f"    Ingredients: {len(dish.ingredients)}")
            for k, ingredient in enumerate(dish.ingredients):
                print(f"      - {ingredient.name}: {ingredient.amount}")
            print(f"    Nutrition: calories={dish.nutrition.calories}, protein={dish.nutrition.protein}g, fat={dish.nutrition.fat}g, carbs={dish.nutrition.carbs}g")
        
        # Thông tin bữa trưa
        print(f"\nLUNCH ({len(day.lunch.dishes)} dishes):")
        for j, dish in enumerate(day.lunch.dishes):
            print(f"  Dish {j+1}: {dish.name}")
            print(f"    Ingredients: {len(dish.ingredients)}")
            for k, ingredient in enumerate(dish.ingredients):
                print(f"      - {ingredient.name}: {ingredient.amount}")
            print(f"    Nutrition: calories={dish.nutrition.calories}, protein={dish.nutrition.protein}g, fat={dish.nutrition.fat}g, carbs={dish.nutrition.carbs}g")
        
        # Thông tin bữa tối
        print(f"\nDINNER ({len(day.dinner.dishes)} dishes):")
        for j, dish in enumerate(day.dinner.dishes):
            print(f"  Dish {j+1}: {dish.name}")
            print(f"    Ingredients: {len(dish.ingredients)}")
            for k, ingredient in enumerate(dish.ingredients):
                print(f"      - {ingredient.name}: {ingredient.amount}")
            print(f"    Nutrition: calories={dish.nutrition.calories}, protein={dish.nutrition.protein}g, fat={dish.nutrition.fat}g, carbs={dish.nutrition.carbs}g")
    
    # Kiểm tra định dạng JSON
    print("\n=== JSON FORMAT ===")
    try:
        json_data = meal_plan.model_dump_json(indent=2)
        print(f"JSON sample (first 500 chars):\n{json_data[:500]}...")
        print("\nJSON format is valid")
    except Exception as e:
        print(f"Error converting to JSON: {str(e)}")
        try:
            # Thử phương thức khác
            json_data = meal_plan.json(indent=2)
            print(f"JSON sample (first 500 chars):\n{json_data[:500]}...")
            print("\nJSON format is valid (using json() method)")
        except Exception as e2:
            print(f"Error with json() method: {str(e2)}")
    
    # Lấy lịch sử meal plan
    print("\n=== MEAL PLAN HISTORY ===")
    try:
        history = firebase.get_meal_plan_history(user_id)
        print(f"Found {len(history)} meal plans in history")
        for i, plan in enumerate(history[:3]):  # Chỉ hiện 3 kế hoạch đầu tiên
            print(f"  Plan {i+1}: {plan.get('id', 'Unknown ID')}, timestamp: {plan.get('timestamp', 'Unknown')}")
    except Exception as e:
        print(f"Error getting meal plan history: {str(e)}")
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_firebase_meal_plan_structure() 