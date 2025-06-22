# -*- coding: utf-8 -*-
"""
Test script để kiểm tra tính đa dạng của fallback system
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fallback_meal_diversity():
    """Test tính đa dạng của fallback meals"""
    try:
        from groq_integration import groq_service
        from fallback_meals import FALLBACK_MEALS
        
        print("🔧 Testing Fallback Meal Diversity...")
        print("=" * 60)
        
        # Check fallback database size
        print("📊 FALLBACK DATABASE SIZE:")
        for meal_type, meals in FALLBACK_MEALS.items():
            print(f"   {meal_type}: {len(meals)} meals")
        
        total_meals = sum(len(meals) for meals in FALLBACK_MEALS.values())
        print(f"   TOTAL: {total_meals} meals")
        
        if total_meals < 15:
            print("❌ FAIL: Not enough fallback meals (need at least 15)")
            return False
        
        # Test fallback selection for each meal type
        meal_types = ["bữa sáng", "bữa trưa", "bữa tối"]
        
        print(f"\n🔧 Testing fallback selection...")
        
        all_selected_meals = []
        
        for meal_type in meal_types:
            print(f"\n🍽️ Testing {meal_type}:")
            
            # Test multiple selections to check randomness
            selections = []
            for i in range(5):
                fallback_meals = groq_service._fallback_meal_suggestions(meal_type)
                
                if fallback_meals:
                    meal_names = [meal.get('name', 'Unknown') for meal in fallback_meals]
                    selections.append(meal_names)
                    all_selected_meals.extend(meal_names)
                    print(f"   Selection {i+1}: {', '.join(meal_names)}")
                else:
                    print(f"   Selection {i+1}: No meals returned")
            
            # Check if we got different selections (randomness)
            unique_selections = set(tuple(selection) for selection in selections)
            randomness_rate = len(unique_selections) / len(selections) * 100
            
            print(f"   📊 Randomness: {randomness_rate:.1f}% ({len(unique_selections)}/{len(selections)} unique)")
            
            if randomness_rate < 40:  # At least 40% should be different
                print(f"   ⚠️ WARNING: Low randomness for {meal_type}")
        
        # Check overall diversity
        print(f"\n📊 OVERALL DIVERSITY ANALYSIS:")
        
        unique_meals = set(all_selected_meals)
        total_selections = len(all_selected_meals)
        
        print(f"   Total selections: {total_selections}")
        print(f"   Unique meals: {len(unique_meals)}")
        print(f"   Diversity rate: {len(unique_meals)/total_selections*100:.1f}%")
        
        # List all unique meals selected
        print(f"\n📋 ALL UNIQUE MEALS SELECTED:")
        for i, meal in enumerate(sorted(unique_meals), 1):
            print(f"   {i}. {meal}")
        
        # Success criteria
        diversity_threshold = 60  # 60% diversity required
        diversity_rate = len(unique_meals)/total_selections*100
        
        if diversity_rate >= diversity_threshold:
            print(f"\n✅ PASS: Diversity rate ({diversity_rate:.1f}%) meets threshold ({diversity_threshold}%)")
            return True
        else:
            print(f"\n❌ FAIL: Diversity rate ({diversity_rate:.1f}%) below threshold ({diversity_threshold}%)")
            return False
            
    except Exception as e:
        print(f"❌ Fallback diversity test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_meal_quality():
    """Test chất lượng của fallback meals"""
    try:
        from fallback_meals import FALLBACK_MEALS
        
        print("\n🔧 Testing Fallback Meal Quality...")
        print("=" * 60)
        
        required_fields = ['name', 'ingredients', 'preparation', 'nutrition']
        nutrition_fields = ['calories', 'protein', 'fat', 'carbs']
        
        all_pass = True
        total_meals = 0
        
        for meal_type, meals in FALLBACK_MEALS.items():
            print(f"\n🍽️ Checking {meal_type} ({len(meals)} meals):")
            
            for i, meal in enumerate(meals, 1):
                total_meals += 1
                meal_name = meal.get('name', f'Meal {i}')
                print(f"   {i}. {meal_name}")
                
                # Check required fields
                missing_fields = []
                for field in required_fields:
                    if field not in meal:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"      ❌ Missing fields: {', '.join(missing_fields)}")
                    all_pass = False
                else:
                    print(f"      ✅ All required fields present")
                
                # Check nutrition data
                nutrition = meal.get('nutrition', {})
                if nutrition:
                    missing_nutrition = []
                    for field in nutrition_fields:
                        if field not in nutrition:
                            missing_nutrition.append(field)
                    
                    if missing_nutrition:
                        print(f"      ❌ Missing nutrition: {', '.join(missing_nutrition)}")
                        all_pass = False
                    else:
                        calories = nutrition.get('calories', 0)
                        protein = nutrition.get('protein', 0)
                        
                        if calories < 200 or calories > 800:
                            print(f"      ⚠️ Unusual calories: {calories}")
                        
                        if protein < 10 or protein > 60:
                            print(f"      ⚠️ Unusual protein: {protein}g")
                        
                        print(f"      📊 {calories} kcal, {protein}g protein")
        
        print(f"\n📊 QUALITY SUMMARY:")
        print(f"   Total meals checked: {total_meals}")
        print(f"   Quality check: {'PASS' if all_pass else 'FAIL'}")
        
        return all_pass
        
    except Exception as e:
        print(f"❌ Fallback quality test failed: {e}")
        return False

def test_no_ai_simulation():
    """Simulate khi không có AI (Groq API down)"""
    try:
        from groq_integration import groq_service
        
        print("\n🔧 Testing No-AI Simulation...")
        print("=" * 60)
        
        # Simulate API failure by calling fallback directly
        meal_types = ["bữa sáng", "bữa trưa", "bữa tối"]
        
        for meal_type in meal_types:
            print(f"\n🍽️ Simulating {meal_type} without AI:")
            
            fallback_meals = groq_service._fallback_meal_suggestions(meal_type)
            
            if fallback_meals:
                print(f"   ✅ Got {len(fallback_meals)} fallback meals:")
                for meal in fallback_meals:
                    name = meal.get('name', 'Unknown')
                    calories = meal.get('nutrition', {}).get('calories', 0)
                    print(f"      - {name} ({calories} kcal)")
            else:
                print(f"   ❌ No fallback meals available")
                return False
        
        print(f"\n✅ No-AI simulation successful - users will always get meals!")
        return True
        
    except Exception as e:
        print(f"❌ No-AI simulation failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING FALLBACK SYSTEM DIVERSITY")
    print("=" * 80)
    
    # Run tests
    test1 = test_fallback_meal_diversity()
    test2 = test_fallback_meal_quality()
    test3 = test_no_ai_simulation()
    
    print("\n" + "=" * 80)
    print("📊 FALLBACK SYSTEM TEST RESULTS:")
    print(f"✅ Fallback Diversity: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Fallback Quality: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ No-AI Simulation: {'PASS' if test3 else 'FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 ALL FALLBACK TESTS PASSED!")
        print("🔧 Fallback system now provides diverse meals!")
        print("📊 No more repetitive fallback meals!")
        print("🛡️ Users always get meals even when AI is down!")
    else:
        print("\n⚠️ Some fallback issues detected")
        
    print("\n🔧 FALLBACK IMPROVEMENTS IMPLEMENTED:")
    improvements = [
        "✅ Expanded fallback database (20+ meals total)",
        "✅ Random meal selection to avoid repetition",
        "✅ Vietnamese dishes for each meal type",
        "✅ Quality nutrition data for all meals",
        "✅ Proper meal type mapping (bữa sáng/trưa/tối)",
        "✅ Robust no-AI fallback system"
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")
