#!/usr/bin/env python3
"""
Quick Diversity Test
"""

import sys
import os
from collections import Counter

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groq_integration import GroqService

def quick_test():
    """Quick diversity test"""
    print("🚀 QUICK DIVERSITY TEST")
    print("="*40)
    
    groq_service = GroqService()
    
    # Clear cache and recent dishes
    groq_service.cache = {}
    groq_service.recent_dishes = []
    
    all_dishes = []
    
    # Test 5 rounds with different parameters
    test_cases = [
        {"meal_type": "bữa sáng", "calories": 350, "protein": 20},
        {"meal_type": "bữa trưa", "calories": 450, "protein": 30},
        {"meal_type": "bữa tối", "calories": 400, "protein": 25},
        {"meal_type": "bữa sáng", "calories": 380, "protein": 22},
        {"meal_type": "bữa trưa", "calories": 500, "protein": 35},
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['meal_type']} ---")
        
        try:
            meals = groq_service.generate_meal_suggestions(
                meal_type=test_case['meal_type'],
                calories_target=test_case['calories'],
                protein_target=test_case['protein'],
                fat_target=15,
                carbs_target=45,
                preferences=["healthy"],
                allergies=[],
                cuisine_style="Vietnamese"
            )
            
            if meals:
                for meal in meals:
                    dish_name = meal.get('name', 'Unknown')
                    all_dishes.append(dish_name)
                    print(f"   🍽️ {dish_name}")
            else:
                print(f"   ❌ No meals generated")
                
        except Exception as e:
            print(f"   💥 Error: {str(e)}")
    
    # Analyze results
    print(f"\n📊 RESULTS:")
    dish_counter = Counter(all_dishes)
    unique_dishes = len(dish_counter)
    total_dishes = len(all_dishes)
    diversity_rate = (unique_dishes / total_dishes * 100) if total_dishes > 0 else 0
    
    print(f"Total dishes: {total_dishes}")
    print(f"Unique dishes: {unique_dishes}")
    print(f"Diversity rate: {diversity_rate:.1f}%")
    
    print(f"\n🍽️ Dishes generated:")
    for dish, count in dish_counter.items():
        print(f"   {dish}: {count} times")
    
    print(f"\n📝 Recent dishes tracked: {groq_service.recent_dishes}")
    
    if diversity_rate >= 70:
        print(f"\n✅ GOOD DIVERSITY!")
    else:
        print(f"\n⚠️ NEEDS IMPROVEMENT")
    
    return diversity_rate >= 70

if __name__ == "__main__":
    quick_test()
