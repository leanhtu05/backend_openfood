#!/usr/bin/env python3
"""
Debug video URL serialization
"""

from services.meal_services import generate_meal
from services.firestore_service import firestore_service
import json

def debug_video_serialization():
    """Debug xem video URLs có được serialize và lưu đúng không"""
    
    print("🔍 Debug Video URL Serialization...")
    
    # Tạo một bữa ăn đơn giản
    print("\n📋 Tạo bữa ăn với video enhancement...")
    meal = generate_meal(
        meal_type='bữa sáng',
        target_calories=400,
        target_protein=20,
        target_fat=15,
        target_carbs=45,
        use_ai=False  # Dùng random để test nhanh
    )
    
    print(f"✅ Đã tạo bữa ăn với {len(meal.dishes)} món")
    
    # Kiểm tra video URLs trong memory
    print("\n🔍 Kiểm tra video URLs trong memory:")
    for i, dish in enumerate(meal.dishes, 1):
        print(f"{i}. {dish.name}")
        print(f"   Video URL: {dish.video_url}")
        print(f"   Has video_url attr: {hasattr(dish, 'video_url')}")
    
    # Test serialization của meal
    print("\n🔄 Test serialization của meal...")
    try:
        meal_dict = meal.dict()
        print("✅ Meal serialization thành công")
        
        # Kiểm tra video URLs trong serialized data
        print("\n📊 Video URLs trong serialized meal:")
        for i, dish_dict in enumerate(meal_dict['dishes'], 1):
            dish_name = dish_dict.get('name', 'Unknown')
            video_url = dish_dict.get('video_url', 'NOT_FOUND')
            print(f"{i}. {dish_name}")
            print(f"   Serialized video_url: {video_url}")
        
        # Lưu sample để debug
        with open("meal_serialized_debug.json", "w", encoding="utf-8") as f:
            json.dump(meal_dict, f, indent=2, ensure_ascii=False)
        print("\n💾 Đã lưu serialized meal vào meal_serialized_debug.json")
        
    except Exception as e:
        print(f"❌ Meal serialization error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test lưu vào Firebase
    print("\n💾 Test lưu vào Firebase...")
    try:
        user_id = "debug_video_test"
        
        # Tạo một DayMealPlan đơn giản
        from models import DayMealPlan, NutritionInfo
        
        day_plan = DayMealPlan(
            day_of_week="Test Day",
            breakfast=meal,
            lunch=meal,  # Dùng cùng meal cho đơn giản
            dinner=meal,
            nutrition=NutritionInfo(calories=1200, protein=60, fat=45, carbs=135)
        )
        
        print("📤 Lưu DayMealPlan vào Firebase...")
        
        # Serialize day plan
        day_dict = day_plan.dict()
        
        # Kiểm tra video URLs trong day plan
        print("\n📊 Video URLs trong DayMealPlan:")
        for meal_name in ['breakfast', 'lunch', 'dinner']:
            meal_data = day_dict[meal_name]
            print(f"\n{meal_name.title()}:")
            for i, dish_dict in enumerate(meal_data['dishes'], 1):
                dish_name = dish_dict.get('name', 'Unknown')
                video_url = dish_dict.get('video_url', 'NOT_FOUND')
                print(f"  {i}. {dish_name}: {video_url}")
        
        # Lưu vào Firestore
        doc_ref = firestore_service.db.collection('debug_meal_plans').document(user_id)
        doc_ref.set(day_dict)
        print("✅ Đã lưu vào Firebase")
        
        # Đọc lại từ Firebase
        print("\n📖 Đọc lại từ Firebase...")
        doc = doc_ref.get()
        if doc.exists:
            firebase_data = doc.to_dict()
            
            print("📊 Video URLs từ Firebase:")
            for meal_name in ['breakfast', 'lunch', 'dinner']:
                meal_data = firebase_data[meal_name]
                print(f"\n{meal_name.title()}:")
                for i, dish_dict in enumerate(meal_data['dishes'], 1):
                    dish_name = dish_dict.get('name', 'Unknown')
                    video_url = dish_dict.get('video_url', 'NOT_FOUND')
                    print(f"  {i}. {dish_name}: {video_url}")
            
            # Lưu Firebase data để debug
            with open("firebase_data_debug.json", "w", encoding="utf-8") as f:
                json.dump(firebase_data, f, indent=2, ensure_ascii=False)
            print("\n💾 Đã lưu Firebase data vào firebase_data_debug.json")
        else:
            print("❌ Không tìm thấy data trong Firebase")
            
    except Exception as e:
        print(f"❌ Firebase error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_video_serialization()
