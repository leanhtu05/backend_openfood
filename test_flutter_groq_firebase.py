"""
Kiểm tra luồng dữ liệu đầy đủ: Flutter → Groq → Firebase
Script này mô phỏng toàn bộ quy trình từ việc tạo người dùng (Flutter),
sử dụng dữ liệu để tạo thực đơn (Groq), và lưu thực đơn (Firebase)
"""
import os
import json
import requests
from datetime import datetime
import time

# Base URL cho API
BASE_URL = "http://localhost:8000"

def test_full_data_flow():
    """Kiểm tra luồng dữ liệu hoàn chỉnh từ Flutter → Groq → Firebase"""
    
    print("\n=== TESTING FULL DATA FLOW ===")
    print("Flutter → Groq → Firebase")
    
    # Tạo ID người dùng duy nhất
    user_id = f"flutter_test_{int(time.time())}"
    print(f"Using test user ID: {user_id}")
    
    # BƯỚC 1: Tạo người dùng (mô phỏng Flutter gửi dữ liệu)
    print("\n--- STEP 1: Create User (Flutter) ---")
    
    # Tạo dữ liệu người dùng mẫu
    user_data = {
        "name": "Test Flutter User",
        "email": f"{user_id}@example.com",
        "height": 175,
        "weight": 70,
        "age": 30,
        "gender": "male",
        "activity_level": "moderate",
        "goal": "maintain_weight",
        "preferred_cuisines": ["vietnamese", "asian"],
        "allergies": []
    }
    
    try:
        # Gửi dữ liệu người dùng đến API
        print(f"Sending user data to {BASE_URL}/firestore/users/{user_id}")
        user_response = requests.post(
            f"{BASE_URL}/firestore/users/{user_id}",
            json=user_data
        )
        
        print(f"Status: {user_response.status_code}")
        print(f"Response: {json.dumps(user_response.json(), indent=2)}")
        
        if user_response.status_code not in [200, 201]:
            print("⚠️ User creation failed, but continuing with test...")
        else:
            print("✅ User created successfully")
            
        # Thêm thời gian trì hoãn để đảm bảo dữ liệu được ghi
        time.sleep(1)
        
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")
        print("Continuing with test anyway...")
    
    # BƯỚC 2: Tạo thực đơn (sử dụng Groq)
    print("\n--- STEP 2: Generate Meal Plan (using Groq) ---")
    
    # Tạo dữ liệu yêu cầu thực đơn
    meal_request = {
        "calories_target": 2000,
        "protein_target": 100,
        "fat_target": 70,
        "carbs_target": 250,
        "preferences": ["rice", "chicken"],
        "allergies": ["seafood"],
        "cuisine_style": "asian" 
    }
    
    try:
        # Gọi API để tạo thực đơn
        print(f"Requesting meal plan from {BASE_URL}/generate-weekly-meal?user_id={user_id}&use_ai=true")
        meal_response = requests.post(
            f"{BASE_URL}/generate-weekly-meal?user_id={user_id}&use_ai=true",
            json=meal_request
        )
        
        print(f"Status: {meal_response.status_code}")
        
        if meal_response.status_code == 200:
            # Phân tích dữ liệu thực đơn
            meal_data = meal_response.json()
            
            # Hiển thị thông tin tổng quan về thực đơn
            meal_plan = meal_data.get("meal_plan", {})
            days = meal_plan.get("days", [])
            
            print(f"✅ Successfully generated meal plan with {len(days)} days")
            
            # Hiển thị chi tiết về ngày đầu tiên nếu có
            if days:
                day = days[0]
                day_of_week = day.get("day_of_week", "Unknown")
                
                breakfast_dishes = day.get("breakfast", {}).get("dishes", [])
                lunch_dishes = day.get("lunch", {}).get("dishes", [])
                dinner_dishes = day.get("dinner", {}).get("dishes", [])
                
                total_dishes = len(breakfast_dishes) + len(lunch_dishes) + len(dinner_dishes)
                
                print(f"First day ({day_of_week}): {total_dishes} total dishes")
                print(f"  Breakfast: {len(breakfast_dishes)} dishes")
                print(f"  Lunch: {len(lunch_dishes)} dishes")
                print(f"  Dinner: {len(dinner_dishes)} dishes")
                
                # Hiển thị món đầu tiên của bữa sáng
                if breakfast_dishes:
                    first_dish = breakfast_dishes[0]
                    print(f"\nSample dish: {first_dish.get('name', 'Unknown')}")
                    print(f"  Description: {first_dish.get('description', 'No description')}")
                    print(f"  Ingredients: {len(first_dish.get('ingredients', []))} items")
                    
                    # Hiển thị dinh dưỡng
                    nutrition = first_dish.get("nutrition", {})
                    print(f"  Nutrition: calories={nutrition.get('calories', 0)}, protein={nutrition.get('protein', 0)}g, fat={nutrition.get('fat', 0)}g, carbs={nutrition.get('carbs', 0)}g")
            else:
                print("⚠️ No days found in meal plan")
        else:
            print(f"❌ Failed to generate meal plan: {meal_response.text}")
    
    except Exception as e:
        print(f"❌ Error generating meal plan: {str(e)}")
    
    # BƯỚC 3: Kiểm tra xem thực đơn đã được lưu trong Firebase chưa
    print("\n--- STEP 3: Verify Storage in Firebase ---")
    
    try:
        # Lấy thực đơn mới nhất từ API
        print(f"Retrieving latest meal plan from {BASE_URL}/latest-meal-plan/{user_id}")
        get_response = requests.get(f"{BASE_URL}/latest-meal-plan/{user_id}")
        
        print(f"Status: {get_response.status_code}")
        
        if get_response.status_code == 200:
            meal_data = get_response.json()
            
            if meal_data:
                print("✅ Successfully retrieved meal plan from Firebase")
                
                # Kiểm tra xem meal plan có cùng số lượng ngày với thực đơn đã tạo
                days = meal_data.get("days", [])
                print(f"Meal plan has {len(days)} days")
                
                # Hiển thị timestamp để xác nhận đây là thực đơn mới
                timestamp = meal_data.get("timestamp", "Unknown")
                print(f"Timestamp: {timestamp}")
            else:
                print("⚠️ Empty meal plan data returned")
        else:
            print(f"❌ Failed to retrieve meal plan: {get_response.text}")
            
    except Exception as e:
        print(f"❌ Error retrieving meal plan: {str(e)}")
    
    # BƯỚC 4: Kiểm tra lịch sử thực đơn
    print("\n--- STEP 4: Check Meal Plan History ---")
    
    try:
        # Lấy lịch sử thực đơn
        print(f"Retrieving meal plan history from {BASE_URL}/meal-plan-history?user_id={user_id}")
        history_response = requests.get(f"{BASE_URL}/meal-plan-history?user_id={user_id}")
        
        print(f"Status: {history_response.status_code}")
        
        if history_response.status_code == 200:
            history_data = history_response.json()
            
            if history_data:
                print(f"✅ Successfully retrieved {len(history_data)} meal plans from history")
                
                # Hiển thị danh sách thực đơn trong lịch sử
                for i, plan in enumerate(history_data[:3]):  # Chỉ hiện 3 kế hoạch đầu tiên
                    timestamp = plan.get("timestamp", "Unknown")
                    plan_id = plan.get("id", "Unknown")
                    print(f"  Plan {i+1}: ID={plan_id}, timestamp={timestamp}")
            else:
                print("⚠️ No meal plans found in history")
        else:
            print(f"❌ Failed to retrieve meal plan history: {history_response.text}")
            
    except Exception as e:
        print(f"❌ Error retrieving meal plan history: {str(e)}")
    
    print("\n=== TEST COMPLETED ===")
    
    # Kết quả cuối cùng
    print("\n=== SUMMARY ===")
    print(f"User ID: {user_id}")
    if 'meal_response' in locals() and meal_response.status_code == 200:
        print("✅ Groq meal plan generation: SUCCESS")
    else:
        print("❌ Groq meal plan generation: FAILED")
        
    if 'get_response' in locals() and get_response.status_code == 200 and get_response.json():
        print("✅ Firebase storage: SUCCESS")
    else:
        print("❌ Firebase storage: FAILED")
    
    # Trả về user_id để có thể sử dụng trong các test khác
    return user_id

if __name__ == "__main__":
    test_user_id = test_full_data_flow()
    print(f"\nYou can use this user ID for further testing: {test_user_id}") 