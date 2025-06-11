#!/usr/bin/env python3
"""
Test video URL fix sau khi cập nhật serialization
"""

from services.meal_services import generate_weekly_meal_plan
from services.firestore_service import firestore_service
import json

def test_video_url_fix():
    """Test xem video URLs có được lưu đúng cách không"""
    
    print("🧪 Testing video URL fix...")
    
    # Tạo meal plan mới với video enhancement
    print("\n📋 Tạo weekly meal plan mới...")
    weekly_plan = generate_weekly_meal_plan(
        calories_target=2000,
        protein_target=100,
        fat_target=70,
        carbs_target=250,
        preferences=['món Việt Nam'],
        use_ai=True
    )
    
    print(f"✅ Đã tạo meal plan với {len(weekly_plan.days)} ngày")
    
    # Kiểm tra video URLs trong memory trước khi lưu
    print("\n🔍 Kiểm tra video URLs trong memory:")
    first_day = weekly_plan.days[0]
    video_count = 0
    total_dishes = 0
    
    for meal_name in ['breakfast', 'lunch', 'dinner']:
        meal = getattr(first_day, meal_name)
        print(f"\n🍽️ {meal_name.title()}:")
        
        for i, dish in enumerate(meal.dishes, 1):
            total_dishes += 1
            print(f"  {i}. {dish.name}")
            if hasattr(dish, 'video_url') and dish.video_url:
                video_count += 1
                print(f"     ✅ Video: {dish.video_url}")
            else:
                print(f"     ❌ Không có video")
    
    print(f"\n📊 Memory: {video_count}/{total_dishes} món có video ({video_count/total_dishes*100:.1f}%)")
    
    # Test serialization
    print("\n🔄 Test serialization...")
    try:
        serialized = weekly_plan.dict()
        
        # Kiểm tra video URLs trong serialized data
        serialized_video_count = 0
        serialized_total_dishes = 0
        
        if 'days' in serialized and serialized['days']:
            first_day_serialized = serialized['days'][0]
            
            for meal_name in ['breakfast', 'lunch', 'dinner']:
                if meal_name in first_day_serialized and 'dishes' in first_day_serialized[meal_name]:
                    for dish in first_day_serialized[meal_name]['dishes']:
                        serialized_total_dishes += 1
                        if dish.get('video_url'):
                            serialized_video_count += 1
        
        print(f"📊 Serialized: {serialized_video_count}/{serialized_total_dishes} món có video ({serialized_video_count/serialized_total_dishes*100:.1f}%)")
        
        # Lưu sample serialized data
        with open("serialized_sample.json", "w", encoding="utf-8") as f:
            json.dump(first_day_serialized, f, indent=2, ensure_ascii=False)
        print("💾 Đã lưu serialized sample vào serialized_sample.json")
        
    except Exception as e:
        print(f"❌ Serialization error: {e}")
        import traceback
        traceback.print_exc()
    
    # Lưu vào Firebase
    print("\n💾 Lưu vào Firebase...")
    try:
        user_id = "test_video_fix_user"
        firestore_service.save_meal_plan(user_id, weekly_plan)
        print("✅ Đã lưu vào Firebase")
        
        # Đọc lại từ Firebase để kiểm tra
        print("\n📖 Đọc lại từ Firebase...")
        db = firestore_service.db
        
        # Kiểm tra latest_meal_plans
        doc = db.collection('latest_meal_plans').document(user_id).get()
        if doc.exists:
            data = doc.to_dict()
            
            firebase_video_count = 0
            firebase_total_dishes = 0
            
            if 'days' in data and data['days']:
                first_day_firebase = data['days'][0]
                
                for meal_name in ['breakfast', 'lunch', 'dinner']:
                    if meal_name in first_day_firebase and 'dishes' in first_day_firebase[meal_name]:
                        for dish in first_day_firebase[meal_name]['dishes']:
                            firebase_total_dishes += 1
                            if dish.get('video_url'):
                                firebase_video_count += 1
                                print(f"     ✅ Firebase video: {dish['name']} - {dish['video_url']}")
            
            print(f"📊 Firebase: {firebase_video_count}/{firebase_total_dishes} món có video ({firebase_video_count/firebase_total_dishes*100:.1f}%)")
            
            # Lưu Firebase sample
            with open("firebase_sample_new.json", "w", encoding="utf-8") as f:
                json.dump(first_day_firebase, f, indent=2, ensure_ascii=False)
            print("💾 Đã lưu Firebase sample vào firebase_sample_new.json")
            
        else:
            print("❌ Không tìm thấy data trong Firebase")
            
    except Exception as e:
        print(f"❌ Firebase error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_video_url_fix()
