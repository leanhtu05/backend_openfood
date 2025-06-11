#!/usr/bin/env python3
"""
Kiểm tra video URL đã được lưu trên Firebase chưa
"""

from services.firestore_service import firestore_service
import json

def check_firebase_video_urls():
    """Kiểm tra video URLs trong Firebase"""
    
    print("🔍 Kiểm tra video URLs trong Firebase...")
    
    try:
        # Lấy meal plan mới nhất từ Firebase
        print("\n📋 Lấy meal plans từ Firebase...")
        
        # Kiểm tra collection latest_meal_plans
        db = firestore_service.db
        latest_plans = db.collection('latest_meal_plans').limit(5).get()
        
        print(f"📊 Tìm thấy {len(latest_plans)} meal plans trong latest_meal_plans")
        
        for doc in latest_plans:
            user_id = doc.id
            data = doc.to_dict()
            
            print(f"\n👤 User ID: {user_id}")
            
            if 'days' in data:
                days = data['days']
                print(f"📅 Có {len(days)} ngày trong meal plan")
                
                # Kiểm tra ngày đầu tiên
                if days:
                    first_day = days[0]
                    day_name = first_day.get('day_of_week', 'Unknown')
                    print(f"🗓️ Ngày đầu tiên: {day_name}")
                    
                    # Kiểm tra các bữa ăn
                    meals = ['breakfast', 'lunch', 'dinner']
                    video_count = 0
                    total_dishes = 0
                    
                    for meal_name in meals:
                        if meal_name in first_day:
                            meal = first_day[meal_name]
                            if 'dishes' in meal:
                                dishes = meal['dishes']
                                print(f"\n🍽️ {meal_name.title()}:")
                                
                                for i, dish in enumerate(dishes, 1):
                                    total_dishes += 1
                                    name = dish.get('name', 'Unknown')
                                    video_url = dish.get('video_url')
                                    
                                    print(f"  {i}. {name}")
                                    if video_url:
                                        video_count += 1
                                        print(f"     ✅ Video: {video_url}")
                                    else:
                                        print(f"     ❌ Không có video")
                    
                    print(f"\n📊 Tổng kết: {video_count}/{total_dishes} món có video ({video_count/total_dishes*100:.1f}%)")
                    
                    # Lưu sample data để debug
                    with open(f"firebase_sample_{user_id}.json", "w", encoding="utf-8") as f:
                        json.dump(first_day, f, indent=2, ensure_ascii=False)
                    print(f"💾 Đã lưu sample data vào firebase_sample_{user_id}.json")
                    
                    break  # Chỉ kiểm tra user đầu tiên
            else:
                print("❌ Meal plan không có cấu trúc 'days'")
        
        # Kiểm tra collection meal_plans (history)
        print(f"\n📚 Kiểm tra meal_plans history...")
        history_plans = db.collection('meal_plans').order_by('created_at', direction='DESCENDING').limit(3).get()
        
        print(f"📊 Tìm thấy {len(history_plans)} meal plans trong history")
        
        for doc in history_plans:
            doc_id = doc.id
            data = doc.to_dict()
            created_at = data.get('created_at', 'Unknown')
            user_id = data.get('user_id', 'Unknown')
            
            print(f"\n📄 Doc ID: {doc_id}")
            print(f"👤 User ID: {user_id}")
            print(f"⏰ Created: {created_at}")
            
            # Kiểm tra có video URLs không
            if 'days' in data and data['days']:
                first_day = data['days'][0]
                video_found = False
                
                for meal_name in ['breakfast', 'lunch', 'dinner']:
                    if meal_name in first_day and 'dishes' in first_day[meal_name]:
                        for dish in first_day[meal_name]['dishes']:
                            if dish.get('video_url'):
                                video_found = True
                                print(f"     ✅ Tìm thấy video trong {meal_name}: {dish['name']}")
                                break
                        if video_found:
                            break
                
                if not video_found:
                    print(f"     ❌ Không tìm thấy video URLs")
            
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra Firebase: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_firebase_video_urls()
