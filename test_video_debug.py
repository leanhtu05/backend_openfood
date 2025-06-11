#!/usr/bin/env python3
"""
Test script để debug video URL trong meal generation
"""

from services.meal_services import generate_meal
from models import Dish, Ingredient, NutritionInfo

def test_video_integration():
    print('🔍 Debug video URL trong meal generation...')

    # Tạo một bữa ăn đơn giản
    meal = generate_meal(
        meal_type='bữa sáng',
        target_calories=400,
        target_protein=20,
        target_fat=15,
        target_carbs=45,
        use_ai=False  # Dùng random để test nhanh
    )

    print(f'\n📊 Meal có {len(meal.dishes)} món:')
    for i, dish in enumerate(meal.dishes, 1):
        print(f'\n{i}. {dish.name}')
        print(f'   Video URL: {dish.video_url}')
        
        has_attr = hasattr(dish, 'video_url')
        print(f'   Has video_url attr: {has_attr}')
        
        # Test serialize
        try:
            dish_dict = dish.dict()
            video_in_dict = dish_dict.get('video_url', 'NOT_FOUND')
            print(f'   Dict video_url: {video_in_dict}')
        except Exception as e:
            print(f'   Dict error: {e}')
            
        try:
            dish_model_dump = dish.model_dump()
            video_in_model_dump = dish_model_dump.get('video_url', 'NOT_FOUND')
            print(f'   Model_dump video_url: {video_in_model_dump}')
        except Exception as e:
            print(f'   Model_dump error: {e}')

if __name__ == "__main__":
    test_video_integration()
