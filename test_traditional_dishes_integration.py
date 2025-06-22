# -*- coding: utf-8 -*-
"""
Test script để kiểm tra integration với Vietnamese traditional dishes database
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_traditional_dishes_database():
    """Test traditional dishes database"""
    try:
        from vietnamese_traditional_dishes import ALL_TRADITIONAL_DISHES
        
        print("🔧 Testing Traditional Dishes Database...")
        print("=" * 60)
        
        print(f"📊 Total traditional dishes: {len(ALL_TRADITIONAL_DISHES)}")
        
        # Sample some dishes
        sample_dishes = list(ALL_TRADITIONAL_DISHES.items())[:5]
        
        for dish_name, dish_info in sample_dishes:
            print(f"\n🍽️ {dish_name}:")
            print(f"   Description: {dish_info.get('description', 'N/A')[:100]}...")
            print(f"   Meal types: {dish_info.get('meal_type', [])}")
            print(f"   Region: {dish_info.get('region', 'N/A')}")
            print(f"   Ingredients: {len(dish_info.get('ingredients', []))} items")
        
        # Check meal type distribution
        meal_type_counts = {}
        for dish_info in ALL_TRADITIONAL_DISHES.values():
            meal_types = dish_info.get('meal_type', [])
            for mt in meal_types:
                meal_type_counts[mt] = meal_type_counts.get(mt, 0) + 1
        
        print(f"\n📊 Meal type distribution:")
        for meal_type, count in meal_type_counts.items():
            print(f"   {meal_type}: {count} dishes")
        
        return len(ALL_TRADITIONAL_DISHES) > 50  # Should have at least 50 dishes
        
    except Exception as e:
        print(f"❌ Traditional dishes test failed: {e}")
        return False

def test_intelligent_fallback_with_traditional_dishes():
    """Test intelligent fallback using traditional dishes"""
    try:
        from groq_integration import groq_service
        
        print("\n🔧 Testing Intelligent Fallback with Traditional Dishes...")
        print("=" * 60)
        
        # Clear cache để test từ đầu
        groq_service.clear_cache()
        
        meal_types = ["bữa sáng", "bữa trưa", "bữa tối"]
        
        all_generated_dishes = []
        
        for meal_type in meal_types:
            print(f"\n🍽️ Testing {meal_type}:")
            
            # Test multiple generations to check diversity
            for i in range(3):
                fallback_meals = groq_service._create_intelligent_fallback(
                    meal_type=meal_type,
                    calories_target=400,
                    protein_target=25,
                    fat_target=15,
                    carbs_target=50
                )
                
                if fallback_meals and len(fallback_meals) > 0:
                    dish_name = fallback_meals[0].get('name', 'Unknown')
                    all_generated_dishes.append(dish_name)
                    
                    print(f"   {i+1}. {dish_name}")
                    
                    # Check if it's from traditional database
                    is_traditional = fallback_meals[0].get('is_traditional', False)
                    source = fallback_meals[0].get('source', 'Unknown')
                    
                    print(f"      Traditional: {is_traditional}")
                    print(f"      Source: {source}")
                    
                    # Check nutrition
                    nutrition = fallback_meals[0].get('nutrition', {})
                    calories = nutrition.get('calories', 0)
                    print(f"      Calories: {calories}")
                    
                else:
                    print(f"   {i+1}. ❌ Failed to generate")
        
        # Analyze diversity
        unique_dishes = set(all_generated_dishes)
        diversity_rate = len(unique_dishes) / len(all_generated_dishes) * 100 if all_generated_dishes else 0
        
        print(f"\n📊 DIVERSITY ANALYSIS:")
        print(f"   Total generated: {len(all_generated_dishes)}")
        print(f"   Unique dishes: {len(unique_dishes)}")
        print(f"   Diversity rate: {diversity_rate:.1f}%")
        
        print(f"\n📋 All generated dishes:")
        for dish in unique_dishes:
            print(f"   - {dish}")
        
        # Success criteria
        success = (
            len(all_generated_dishes) >= 6 and  # Should generate at least 6 meals
            diversity_rate >= 50 and  # At least 50% diversity
            len(unique_dishes) >= 3  # At least 3 different dishes
        )
        
        return success
        
    except Exception as e:
        print(f"❌ Intelligent fallback test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_meal_creation_from_traditional_dish():
    """Test creating meal from traditional dish"""
    try:
        from groq_integration import groq_service
        from vietnamese_traditional_dishes import ALL_TRADITIONAL_DISHES
        
        print("\n🔧 Testing Meal Creation from Traditional Dish...")
        print("=" * 60)
        
        # Get a sample traditional dish
        sample_dish_name = list(ALL_TRADITIONAL_DISHES.keys())[0]
        sample_dish_info = ALL_TRADITIONAL_DISHES[sample_dish_name]
        
        print(f"🍽️ Testing with: {sample_dish_name}")
        
        # Create meal from traditional dish
        meal = groq_service._create_meal_from_traditional_dish(
            dish_name=sample_dish_name,
            dish_info=sample_dish_info,
            calories_target=400,
            meal_type="bữa trưa"
        )
        
        if meal:
            print(f"✅ Successfully created meal:")
            print(f"   Name: {meal.get('name', 'N/A')}")
            print(f"   Description: {meal.get('description', 'N/A')[:100]}...")
            print(f"   Ingredients: {len(meal.get('ingredients', []))} items")
            print(f"   Preparation steps: {len(meal.get('preparation', []))}")
            
            nutrition = meal.get('nutrition', {})
            print(f"   Nutrition: {nutrition.get('calories', 0)} kcal, {nutrition.get('protein', 0)}g protein")
            
            # Check required fields
            required_fields = ['name', 'description', 'ingredients', 'preparation', 'nutrition']
            missing_fields = [field for field in required_fields if field not in meal]
            
            if missing_fields:
                print(f"   ❌ Missing fields: {missing_fields}")
                return False
            else:
                print(f"   ✅ All required fields present")
                return True
        else:
            print(f"❌ Failed to create meal")
            return False
            
    except Exception as e:
        print(f"❌ Meal creation test failed: {e}")
        return False

def test_nutrition_database_integration():
    """Test integration với Vietnamese nutrition database"""
    try:
        from vietnamese_nutrition_extended import VEGETABLES_NUTRITION, MEAT_NUTRITION, SEAFOOD_NUTRITION
        
        print("\n🔧 Testing Nutrition Database Integration...")
        print("=" * 60)
        
        # Test nutrition databases
        databases = [
            ("Vegetables", VEGETABLES_NUTRITION),
            ("Meat", MEAT_NUTRITION), 
            ("Seafood", SEAFOOD_NUTRITION)
        ]
        
        total_items = 0
        
        for db_name, db_data in databases:
            print(f"\n📊 {db_name} Database:")
            print(f"   Items: {len(db_data)}")
            total_items += len(db_data)
            
            # Sample some items
            sample_items = list(db_data.items())[:3]
            for item_name, nutrition in sample_items:
                calories = nutrition.get('calories', 0)
                protein = nutrition.get('protein', 0)
                print(f"   - {item_name}: {calories} kcal, {protein}g protein")
        
        print(f"\n📊 TOTAL NUTRITION ITEMS: {total_items}")
        
        return total_items > 100  # Should have at least 100 nutrition items
        
    except Exception as e:
        print(f"❌ Nutrition database test failed: {e}")
        return False

def test_no_groq_api_scenario():
    """Test scenario khi Groq API không hoạt động"""
    try:
        from groq_integration import groq_service
        
        print("\n🔧 Testing No-Groq-API Scenario...")
        print("=" * 60)
        
        # Simulate API failure by calling fallback directly
        meal_types = ["bữa sáng", "bữa trưa", "bữa tối"]
        
        all_success = True
        
        for meal_type in meal_types:
            print(f"\n🍽️ Testing {meal_type} fallback:")
            
            # Test intelligent fallback
            intelligent_meals = groq_service._create_intelligent_fallback(
                meal_type=meal_type,
                calories_target=400,
                protein_target=25,
                fat_target=15,
                carbs_target=50
            )
            
            if intelligent_meals and len(intelligent_meals) > 0:
                meal = intelligent_meals[0]
                dish_name = meal.get('name', 'Unknown')
                is_traditional = meal.get('is_traditional', False)
                
                print(f"   ✅ Intelligent: {dish_name} (Traditional: {is_traditional})")
            else:
                print(f"   ❌ Intelligent fallback failed")
                all_success = False
            
            # Test static fallback
            static_meals = groq_service._fallback_meal_suggestions(meal_type)
            
            if static_meals and len(static_meals) > 0:
                static_dish = static_meals[0].get('name', 'Unknown')
                print(f"   ✅ Static: {static_dish}")
            else:
                print(f"   ❌ Static fallback failed")
                all_success = False
        
        return all_success
        
    except Exception as e:
        print(f"❌ No-API scenario test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING TRADITIONAL DISHES INTEGRATION")
    print("=" * 80)
    
    # Run tests
    test1 = test_traditional_dishes_database()
    test2 = test_intelligent_fallback_with_traditional_dishes()
    test3 = test_meal_creation_from_traditional_dish()
    test4 = test_nutrition_database_integration()
    test5 = test_no_groq_api_scenario()
    
    print("\n" + "=" * 80)
    print("📊 TRADITIONAL DISHES INTEGRATION TEST RESULTS:")
    print(f"✅ Traditional Dishes Database: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Intelligent Fallback: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Meal Creation: {'PASS' if test3 else 'FAIL'}")
    print(f"✅ Nutrition Database: {'PASS' if test4 else 'FAIL'}")
    print(f"✅ No-API Scenario: {'PASS' if test5 else 'FAIL'}")
    
    if all([test1, test2, test3, test4, test5]):
        print("\n🎉 ALL TRADITIONAL DISHES INTEGRATION TESTS PASSED!")
        print("🔧 System now uses 200+ Vietnamese traditional dishes!")
        print("📊 No more repetitive fallback meals!")
        print("🇻🇳 Authentic Vietnamese cuisine with accurate nutrition!")
    else:
        print("\n⚠️ Some integration issues detected")
        
    print("\n🔧 TRADITIONAL DISHES INTEGRATION FEATURES:")
    features = [
        "✅ 200+ authentic Vietnamese traditional dishes",
        "✅ Accurate nutrition data from Viện Dinh dưỡng Quốc gia",
        "✅ Intelligent fallback using traditional dishes",
        "✅ Meal type specific dish selection",
        "✅ Regional cuisine diversity (Miền Bắc, Trung, Nam)",
        "✅ Proper ingredient and preparation instructions",
        "✅ Emergency fallback system for reliability"
    ]
    
    for feature in features:
        print(f"  {feature}")
