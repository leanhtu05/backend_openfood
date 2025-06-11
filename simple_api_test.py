#!/usr/bin/env python3
"""
Simple API test để kiểm tra video URL
"""

import requests
import json

# Test tạo một bữa ăn đơn giản
print("🧪 Testing simple meal generation...")

try:
    # Test endpoint tạo meal plan
    response = requests.post(
        "http://localhost:8000/api/meal-plan/generate",
        json={
            "calories_target": 2000,
            "protein_target": 100,
            "fat_target": 70,
            "carbs_target": 250,
            "preferences": ["món Việt Nam"],
            "use_ai": True
        },
        timeout=120
    )
    
    print(f"📡 Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ API call successful!")
        
        # Kiểm tra meal plan structure
        if "meal_plan" in data and "days" in data["meal_plan"]:
            days = data["meal_plan"]["days"]
            print(f"📅 Meal plan có {len(days)} ngày")

            # Kiểm tra ngày đầu tiên
            if days:
                first_day = days[0]
                print(f"🔍 Kiểm tra ngày: {first_day.get('day_of_week', 'Unknown')}")

                # Kiểm tra các bữa ăn
                meals = ["breakfast", "lunch", "dinner"]
                for meal_name in meals:
                    if meal_name in first_day:
                        meal = first_day[meal_name]
                        if "dishes" in meal:
                            dishes = meal["dishes"]
                            print(f"🍽️ {meal_name.title()} có {len(dishes)} món:")

                            for i, dish in enumerate(dishes, 1):
                                name = dish.get("name", "Unknown")
                                video_url = dish.get("video_url")

                                print(f"  {i}. {name}")
                                if video_url:
                                    print(f"     🎥 Video: {video_url}")
                                else:
                                    print(f"     ❌ Không có video")
        else:
            print("❌ Response không có cấu trúc meal_plan mong đợi")
        
        # Lưu response
        with open("simple_api_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("💾 Đã lưu response vào simple_api_response.json")
        
    else:
        print(f"❌ API call failed: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
