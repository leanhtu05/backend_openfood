#!/usr/bin/env python3
"""
Test đơn giản để kiểm tra video enhancement
"""

from services.meal_services import generate_meal

def test_simple_video():
    """Test video enhancement với một bữa ăn đơn giản"""
    
    print("🧪 Test video enhancement đơn giản...")
    
    # Tạo một bữa ăn với random (không dùng AI để tránh rate limit)
    print("\n📋 Tạo bữa ăn ngẫu nhiên...")
    meal = generate_meal(
        meal_type='bữa sáng',
        target_calories=400,
        target_protein=20,
        target_fat=15,
        target_carbs=45,
        use_ai=False  # Dùng random để tránh rate limit
    )
    
    print(f"\n✅ Đã tạo bữa ăn với {len(meal.dishes)} món:")
    
    for i, dish in enumerate(meal.dishes, 1):
        print(f"\n{i}. 🍜 {dish.name}")
        print(f"   📊 Calories: {dish.nutrition.calories}")
        
        # Kiểm tra video URL
        if hasattr(dish, 'video_url') and dish.video_url:
            print(f"   🎥 Video: {dish.video_url}")
        else:
            print(f"   ❌ Không có video (video_url: {getattr(dish, 'video_url', 'MISSING_ATTR')})")
        
        # Kiểm tra các thuộc tính khác
        print(f"   🥬 Nguyên liệu: {len(dish.ingredients)} loại")
        if hasattr(dish, 'preparation_time') and dish.preparation_time:
            print(f"   ⏱️ Thời gian: {dish.preparation_time}")

if __name__ == "__main__":
    test_simple_video()
