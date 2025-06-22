# -*- coding: utf-8 -*-
"""
Test script để kiểm tra tính đa dạng của meal generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_meal_diversity():
    """Test tính đa dạng của meal generation"""
    try:
        from groq_integration import groq_service
        
        print("🔧 Testing Meal Diversity...")
        print("=" * 60)
        
        # Clear cache để test từ đầu
        groq_service.clear_cache()
        
        generated_meals = []
        meal_types = ["bữa sáng", "bữa trưa", "bữa tối"]
        
        # Generate 9 meals (3 for each meal type)
        for i in range(9):
            meal_type = meal_types[i % 3]
            
            print(f"\n🍽️ Generating meal {i+1}/9 ({meal_type})...")
            
            meals = groq_service.generate_meal_suggestions(
                calories_target=400,
                protein_target=25,
                fat_target=15,
                carbs_target=50,
                meal_type=meal_type,
                preferences=None,
                allergies=None,
                cuisine_style=None
            )
            
            if meals and len(meals) > 0:
                meal_name = meals[0].get('name', 'Unknown')
                generated_meals.append({
                    'name': meal_name,
                    'type': meal_type,
                    'base_dish': extract_base_dish(meal_name)
                })
                print(f"   ✅ Generated: {meal_name}")
            else:
                print(f"   ❌ Failed to generate meal")
        
        # Analyze diversity
        print(f"\n📊 DIVERSITY ANALYSIS:")
        print("=" * 60)
        
        # Check for exact duplicates
        meal_names = [meal['name'] for meal in generated_meals]
        unique_names = set(meal_names)
        
        print(f"📝 Total meals generated: {len(generated_meals)}")
        print(f"🎯 Unique meal names: {len(unique_names)}")
        print(f"📊 Uniqueness rate: {len(unique_names)/len(generated_meals)*100:.1f}%")
        
        # Check for base dish diversity
        base_dishes = [meal['base_dish'] for meal in generated_meals]
        unique_base_dishes = set(base_dishes)
        
        print(f"\n🍽️ Base dish analysis:")
        print(f"   Unique base dishes: {len(unique_base_dishes)}")
        print(f"   Base dish diversity: {len(unique_base_dishes)/len(generated_meals)*100:.1f}%")
        
        # Show all generated meals
        print(f"\n📋 ALL GENERATED MEALS:")
        for i, meal in enumerate(generated_meals, 1):
            print(f"   {i}. {meal['name']} ({meal['type']}) - Base: {meal['base_dish']}")
        
        # Check for problematic patterns
        print(f"\n⚠️ DUPLICATION CHECK:")
        
        # Count base dish occurrences
        from collections import Counter
        base_dish_counts = Counter(base_dishes)
        
        duplicated_bases = {base: count for base, count in base_dish_counts.items() if count > 1}
        
        if duplicated_bases:
            print(f"   ❌ Found duplicated base dishes:")
            for base, count in duplicated_bases.items():
                print(f"      - {base}: {count} times")
            return False
        else:
            print(f"   ✅ No duplicated base dishes found")
        
        # Check for exact name duplicates
        name_counts = Counter(meal_names)
        duplicated_names = {name: count for name, count in name_counts.items() if count > 1}
        
        if duplicated_names:
            print(f"   ❌ Found exact name duplicates:")
            for name, count in duplicated_names.items():
                print(f"      - {name}: {count} times")
            return False
        else:
            print(f"   ✅ No exact name duplicates found")
        
        # Success criteria
        uniqueness_threshold = 80  # 80% uniqueness required
        diversity_threshold = 70   # 70% base dish diversity required
        
        uniqueness_rate = len(unique_names)/len(generated_meals)*100
        diversity_rate = len(unique_base_dishes)/len(generated_meals)*100
        
        success = (uniqueness_rate >= uniqueness_threshold and 
                  diversity_rate >= diversity_threshold and
                  not duplicated_bases and 
                  not duplicated_names)
        
        print(f"\n🎯 DIVERSITY SCORE:")
        print(f"   Uniqueness: {uniqueness_rate:.1f}% (target: {uniqueness_threshold}%)")
        print(f"   Diversity: {diversity_rate:.1f}% (target: {diversity_threshold}%)")
        
        return success
        
    except Exception as e:
        print(f"❌ Diversity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def extract_base_dish(dish_name: str) -> str:
    """Extract base dish name for analysis"""
    dish_lower = dish_name.lower()
    
    # Common base dishes
    base_dishes = [
        "cơm tấm", "bánh mì", "phở", "cháo", "bún", "hủ tiếu", 
        "mì quảng", "bánh xèo", "bánh khọt", "nem", "chả cá",
        "lẩu", "xôi", "bánh cuốn", "bánh căn", "cơm chiên",
        "cơm gà", "cơm âm phủ", "bún bò", "bún riêu"
    ]
    
    for base in base_dishes:
        if base in dish_lower:
            return base
    
    # If no base found, return first 2 words
    words = dish_lower.split()
    return " ".join(words[:2]) if len(words) >= 2 else dish_lower

def test_recent_dishes_tracking():
    """Test recent dishes tracking functionality"""
    try:
        from groq_integration import groq_service
        
        print("\n🔧 Testing Recent Dishes Tracking...")
        print("=" * 60)
        
        # Clear cache
        groq_service.clear_cache()
        
        print(f"📝 Initial recent dishes: {groq_service.recent_dishes}")
        
        # Generate a few meals
        for i in range(3):
            meals = groq_service.generate_meal_suggestions(
                calories_target=400,
                protein_target=25,
                fat_target=15,
                carbs_target=50,
                meal_type="bữa sáng"
            )
            
            if meals:
                meal_name = meals[0].get('name', 'Unknown')
                print(f"   Generated: {meal_name}")
        
        print(f"📝 Final recent dishes: {groq_service.recent_dishes}")
        print(f"📊 Tracking {len(groq_service.recent_dishes)} recent dishes")
        
        return len(groq_service.recent_dishes) > 0
        
    except Exception as e:
        print(f"❌ Recent dishes tracking test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING MEAL DIVERSITY SYSTEM")
    print("=" * 80)
    
    # Run tests
    test1 = test_meal_diversity()
    test2 = test_recent_dishes_tracking()
    
    print("\n" + "=" * 80)
    print("📊 DIVERSITY TEST RESULTS:")
    print(f"✅ Meal Diversity: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Recent Dishes Tracking: {'PASS' if test2 else 'FAIL'}")
    
    if all([test1, test2]):
        print("\n🎉 ALL DIVERSITY TESTS PASSED!")
        print("🔧 Meal generation now provides diverse dishes!")
        print("📊 No more repetitive meals!")
    else:
        print("\n⚠️ Some diversity issues detected")
        
    print("\n🔧 DIVERSITY IMPROVEMENTS IMPLEMENTED:")
    improvements = [
        "✅ Enhanced anti-duplication with fuzzy matching",
        "✅ Stronger prompt instructions to avoid repetition",
        "✅ Base dish similarity detection",
        "✅ Recent dishes tracking (20 dishes)",
        "✅ Gradual restriction relaxation when needed",
        "✅ Category-based diversity enforcement"
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")
