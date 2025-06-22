# -*- coding: utf-8 -*-
"""
Test nutrition fix cho Vietnamese dish generator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_nutrition_fix():
    """Test nutrition calculation sau khi sửa"""
    try:
        from services.vietnamese_dish_generator import vietnamese_dish_generator
        
        print("🔧 Testing nutrition calculation fix...")
        print("=" * 50)
        
        for meal_type in ["breakfast", "lunch", "dinner"]:
            print(f"\n🍽️ Testing {meal_type}:")
            
            for i in range(3):
                dish = vietnamese_dish_generator.generate_single_dish(meal_type)
                nutrition = dish["nutrition"]
                
                print(f"  {i+1}. {dish['name']}")
                print(f"     📊 {nutrition['calories']} kcal, {nutrition['protein']}g protein")
                print(f"     🥘 {len(dish['ingredients'])} ingredients")
                
                # Check if nutrition is reasonable
                if nutrition['calories'] < 100:
                    print(f"     ⚠️ Low calories detected")
                elif nutrition['calories'] > 800:
                    print(f"     ⚠️ High calories detected")
                else:
                    print(f"     ✅ Reasonable calories")
        
        print("\n✅ Nutrition fix test completed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_nutrition_fix()
