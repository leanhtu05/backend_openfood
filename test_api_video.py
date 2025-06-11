#!/usr/bin/env python3
"""
Test API endpoint để kiểm tra video URL
"""

import requests
import json

def test_meal_plan_api():
    """Test API endpoint để tạo meal plan và kiểm tra video URL"""
    
    # URL của API
    base_url = "http://localhost:8000"
    
    # Test data
    test_data = {
        "calories_target": 2000,
        "protein_target": 100,
        "fat_target": 70,
        "carbs_target": 250,
        "preferences": ["món Việt Nam"],
        "use_ai": True
    }
    
    print("🧪 Testing meal plan API...")
    
    try:
        # Gọi API tạo meal plan
        response = requests.post(
            f"{base_url}/api/generate-weekly-meal",
            json=test_data,
            timeout=120
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Kiểm tra structure
            if "meal_plan" in data and "days" in data["meal_plan"]:
                days = data["meal_plan"]["days"]
                print(f"📅 Meal plan có {len(days)} ngày")
                
                # Kiểm tra ngày đầu tiên
                if days:
                    first_day = days[0]
                    print(f"\n🔍 Kiểm tra ngày: {first_day.get('day_of_week', 'Unknown')}")
                    
                    # Kiểm tra các bữa ăn
                    meals = ["breakfast", "lunch", "dinner"]
                    for meal_name in meals:
                        if meal_name in first_day:
                            meal = first_day[meal_name]
                            if "dishes" in meal:
                                dishes = meal["dishes"]
                                print(f"\n🍽️ {meal_name.title()} có {len(dishes)} món:")
                                
                                for i, dish in enumerate(dishes, 1):
                                    name = dish.get("name", "Unknown")
                                    video_url = dish.get("video_url")
                                    
                                    print(f"  {i}. {name}")
                                    if video_url:
                                        print(f"     🎥 Video: {video_url}")
                                    else:
                                        print(f"     ❌ Không có video")
                
                # Lưu response để debug
                with open("api_response_debug.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"\n💾 Đã lưu response vào api_response_debug.json")
                
            else:
                print("❌ Response không có cấu trúc meal_plan mong đợi")
                
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_meal_plan_api()
