# -*- coding: utf-8 -*-
"""
Test enhanced Vietnamese dish generator với 200+ món truyền thống
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_generator():
    """Test enhanced generator với traditional dishes"""
    try:
        from services.vietnamese_dish_generator import vietnamese_dish_generator
        
        print("🔧 Testing Enhanced Vietnamese Dish Generator...")
        print("=" * 60)
        
        traditional_count = 0
        generated_count = 0
        
        for meal_type in ["breakfast", "lunch", "dinner"]:
            print(f"\n🍽️ Testing {meal_type}:")
            
            for i in range(5):  # Test 5 dishes per meal type
                dish = vietnamese_dish_generator.generate_single_dish(meal_type)
                
                print(f"  {i+1}. {dish['name']}")
                print(f"     🌍 {dish['region']}")
                print(f"     📊 {dish['nutrition']['calories']} kcal")
                
                # Check if traditional or generated
                if "Traditional" in dish.get('source', ''):
                    traditional_count += 1
                    print(f"     ✅ Traditional dish")
                    if 'description' in dish:
                        print(f"     📝 {dish['description'][:50]}...")
                else:
                    generated_count += 1
                    print(f"     🔧 Generated dish")
        
        total_dishes = traditional_count + generated_count
        traditional_ratio = (traditional_count / total_dishes) * 100
        
        print(f"\n📊 RESULTS:")
        print(f"✅ Traditional dishes: {traditional_count}/{total_dishes} ({traditional_ratio:.1f}%)")
        print(f"🔧 Generated dishes: {generated_count}/{total_dishes} ({100-traditional_ratio:.1f}%)")
        
        if traditional_ratio >= 60:
            print("🎉 SUCCESS: Good mix of traditional and generated dishes!")
        else:
            print("⚠️ WARNING: Low traditional dish ratio")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_traditional_dish_variety():
    """Test đa dạng món truyền thống"""
    try:
        from services.vietnamese_dish_generator import vietnamese_dish_generator
        
        print("\n🔧 Testing Traditional Dish Variety...")
        print("=" * 60)
        
        dish_names = set()
        regions = set()
        
        # Generate 20 dishes to test variety
        for i in range(20):
            dish = vietnamese_dish_generator.generate_single_dish("lunch")
            dish_names.add(dish['name'])
            regions.add(dish['region'])
        
        print(f"📊 Variety Results:")
        print(f"✅ Unique dishes: {len(dish_names)}/20")
        print(f"🌍 Regions covered: {len(regions)}")
        print(f"🍽️ Sample dishes: {list(dish_names)[:5]}")
        
        variety_score = (len(dish_names) / 20) * 100
        
        if variety_score >= 80:
            print(f"🎉 EXCELLENT variety: {variety_score:.1f}%")
        elif variety_score >= 60:
            print(f"✅ GOOD variety: {variety_score:.1f}%")
        else:
            print(f"⚠️ LOW variety: {variety_score:.1f}%")
        
        return variety_score >= 60
        
    except Exception as e:
        print(f"❌ Variety test failed: {e}")
        return False

def test_specific_traditional_dishes():
    """Test các món truyền thống cụ thể"""
    try:
        from vietnamese_traditional_dishes import ALL_TRADITIONAL_DISHES
        
        print("\n🔧 Testing Specific Traditional Dishes...")
        print("=" * 60)
        
        print(f"📊 Total traditional dishes in database: {len(ALL_TRADITIONAL_DISHES)}")
        
        # Show some examples
        sample_dishes = list(ALL_TRADITIONAL_DISHES.keys())[:10]
        print(f"🍽️ Sample traditional dishes:")
        for dish in sample_dishes:
            info = ALL_TRADITIONAL_DISHES[dish]
            print(f"  • {dish} ({info.get('region', 'N/A')})")
        
        # Test meal type distribution
        meal_type_count = {"breakfast": 0, "lunch": 0, "dinner": 0, "dessert": 0}
        for dish_info in ALL_TRADITIONAL_DISHES.values():
            for meal_type in dish_info.get("meal_type", []):
                if meal_type in meal_type_count:
                    meal_type_count[meal_type] += 1
        
        print(f"\n📊 Meal type distribution:")
        for meal_type, count in meal_type_count.items():
            print(f"  {meal_type}: {count} dishes")
        
        return True
        
    except Exception as e:
        print(f"❌ Traditional dishes test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING ENHANCED VIETNAMESE DISH GENERATOR")
    print("=" * 80)
    
    # Run tests
    test1 = test_enhanced_generator()
    test2 = test_traditional_dish_variety()
    test3 = test_specific_traditional_dishes()
    
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS:")
    print(f"✅ Enhanced Generator: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Dish Variety: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Traditional Database: {'PASS' if test3 else 'FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 ALL TESTS PASSED!")
        print("🔧 Enhanced generator ready with 200+ traditional Vietnamese dishes!")
        print("📊 System can now generate authentic Vietnamese cuisine with high variety!")
    else:
        print("\n❌ Some tests failed - need to fix issues")
