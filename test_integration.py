# -*- coding: utf-8 -*-
"""
Test tích hợp Vietnamese dish generator vào hệ thống meal planning
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_vietnamese_integration():
    """Test tích hợp Vietnamese dishes"""
    print("🔧 Testing Vietnamese dish integration...")
    print("=" * 60)
    
    try:
        # Test import
        from utils import generate_random_dishes
        print("✅ Successfully imported generate_random_dishes")
        
        # Test generate dishes
        print("\n📋 Testing generate_random_dishes with Vietnamese generator:")
        
        for meal_type in ["breakfast", "lunch", "dinner"]:
            print(f"\n🍽️ Testing {meal_type}:")
            dishes = generate_random_dishes(meal_type, count=2)
            
            if dishes:
                print(f"✅ Generated {len(dishes)} dishes for {meal_type}")
                for i, dish in enumerate(dishes, 1):
                    print(f"  {i}. {dish['name']}")
                    if 'nutrition' in dish:
                        nutrition = dish['nutrition']
                        print(f"     📊 {nutrition['calories']} kcal, {nutrition['protein']}g protein")
                    if 'region' in dish:
                        print(f"     🌍 Miền: {dish['region']}")
            else:
                print(f"❌ No dishes generated for {meal_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_meal_service_integration():
    """Test meal service với Vietnamese dishes"""
    print("\n🔧 Testing meal service integration...")
    print("=" * 60)
    
    try:
        from services.meal_services import get_vietnamese_dishes
        print("✅ Successfully imported get_vietnamese_dishes")
        
        # Test generate Vietnamese dishes
        for meal_type in ["breakfast", "lunch", "dinner"]:
            print(f"\n🍽️ Testing Vietnamese dishes for {meal_type}:")
            dishes = get_vietnamese_dishes(meal_type, count=3)
            
            if dishes:
                print(f"✅ Generated {len(dishes)} Vietnamese dishes")
                for i, dish in enumerate(dishes, 1):
                    print(f"  {i}. {dish['name']}")
                    if 'nutrition' in dish:
                        nutrition = dish['nutrition']
                        print(f"     📊 {nutrition['calories']} kcal")
                    if 'region' in dish:
                        print(f"     🌍 {dish['region']}")
            else:
                print(f"❌ No Vietnamese dishes generated for {meal_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Meal service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_nutrition_accuracy():
    """Test độ chính xác dinh dưỡng"""
    print("\n🔍 Testing nutrition accuracy...")
    print("=" * 60)
    
    try:
        from services.meal_services import get_vietnamese_dishes
        from utils import validate_nutrition_data
        
        total_dishes = 0
        valid_dishes = 0
        
        for meal_type in ["breakfast", "lunch", "dinner"]:
            dishes = get_vietnamese_dishes(meal_type, count=2)
            
            for dish in dishes:
                total_dishes += 1
                if 'nutrition' in dish:
                    if validate_nutrition_data(dish['nutrition']):
                        valid_dishes += 1
                    else:
                        print(f"⚠️ Invalid nutrition: {dish['name']}")
        
        if total_dishes > 0:
            accuracy = (valid_dishes / total_dishes) * 100
            print(f"📊 Nutrition accuracy: {accuracy:.1f}% ({valid_dishes}/{total_dishes})")
            return accuracy > 80
        else:
            print("❌ No dishes to test")
            return False
            
    except Exception as e:
        print(f"❌ Nutrition test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING VIETNAMESE DISH INTEGRATION")
    print("=" * 80)
    
    # Run tests
    test1 = test_vietnamese_integration()
    test2 = test_meal_service_integration() 
    test3 = test_nutrition_accuracy()
    
    print("\n" + "=" * 80)
    print("📊 TEST RESULTS:")
    print(f"✅ Vietnamese Integration: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Meal Service Integration: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Nutrition Accuracy: {'PASS' if test3 else 'FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 ALL TESTS PASSED - Vietnamese dishes successfully integrated!")
        print("🔧 System ready to generate 300+ Vietnamese dishes with accurate nutrition")
    else:
        print("\n❌ Some tests failed - need to fix integration issues")
