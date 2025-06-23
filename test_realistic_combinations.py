#!/usr/bin/env python3
"""
Test script cho tính năng tạo món ăn kết hợp thực tế trong meal planning
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groq_integration import GroqService
import json

def test_realistic_combination_generation():
    """Test tính năng tạo món ăn kết hợp thực tế"""
    print("🧪 Testing Realistic Combination Dishes Generation")
    print("=" * 60)
    
    # Initialize Groq service
    groq_service = GroqService()
    
    # Test cases for different meal types
    test_cases = [
        {
            "meal_type": "breakfast",
            "preferences": [],
            "allergies": []
        },
        {
            "meal_type": "lunch", 
            "preferences": ["gà", "cơm"],
            "allergies": []
        },
        {
            "meal_type": "dinner",
            "preferences": [],
            "allergies": ["tôm", "cua"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🍽️ Test Case {i}: {test_case['meal_type'].upper()}")
        print("-" * 40)
        
        try:
            # Generate realistic combination dishes
            combination_dishes = groq_service._generate_realistic_combination_dishes(
                meal_type=test_case["meal_type"],
                preferences=test_case["preferences"],
                allergies=test_case["allergies"]
            )
            
            print(f"✅ Generated {len(combination_dishes)} combination dishes:")
            for j, dish in enumerate(combination_dishes[:10], 1):  # Show first 10
                print(f"   {j:2d}. {dish}")
                
            if test_case["preferences"]:
                print(f"📝 Preferences applied: {test_case['preferences']}")
            if test_case["allergies"]:
                print(f"🚫 Allergies filtered: {test_case['allergies']}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_fallback_meal_suggestions():
    """Test fallback meal suggestions với realistic combinations"""
    print("\n🧪 Testing Fallback Meal Suggestions")
    print("=" * 60)
    
    groq_service = GroqService()
    
    meal_types = ["breakfast", "lunch", "dinner"]
    
    for meal_type in meal_types:
        print(f"\n🍽️ Testing {meal_type.upper()} fallback meals")
        print("-" * 30)
        
        try:
            fallback_meals = groq_service._fallback_meal_suggestions(meal_type)
            
            print(f"✅ Generated {len(fallback_meals)} fallback meals:")
            for i, meal in enumerate(fallback_meals, 1):
                print(f"   {i}. {meal['name']}")
                print(f"      📝 {meal['description'][:80]}...")
                print(f"      🥘 {len(meal['ingredients'])} ingredients")
                print(f"      📊 {meal['nutrition']['calories']} kcal")
                print()
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_dish_name_parsing():
    """Test parsing dish names"""
    print("\n🧪 Testing Dish Name Parsing")
    print("=" * 60)
    
    groq_service = GroqService()
    
    test_dishes = [
        "Cơm Thịt Nướng",
        "Bún Gà",
        "Phở Bò",
        "Mì Tôm",
        "Rau Muống Xào",
        "Cháo Gà",
        "Bánh Mì Chả Cá"
    ]
    
    print("Testing dish name parsing:")
    for dish_name in test_dishes:
        try:
            base_food, protein_type = groq_service._parse_combination_dish_name(dish_name)
            print(f"  {dish_name:20} → Base: {base_food:10} | Protein: {protein_type}")
        except Exception as e:
            print(f"  {dish_name:20} → Error: {str(e)}")

def test_meal_generation_with_combinations():
    """Test meal generation với realistic combinations"""
    print("\n🧪 Testing Full Meal Generation with Combinations")
    print("=" * 60)
    
    groq_service = GroqService()
    
    # Test meal generation
    test_params = {
        "meal_type": "lunch",
        "calories_target": 500,
        "protein_target": 30,
        "fat_target": 20,
        "carbs_target": 60,
        "preferences": [],
        "allergies": []
    }
    
    print(f"🍽️ Generating meals for {test_params['meal_type']}")
    print(f"📊 Targets: {test_params['calories_target']} kcal, {test_params['protein_target']}g protein")
    
    try:
        # This will use the enhanced prompt with realistic combinations
        meals = groq_service.generate_meal_suggestions(
            meal_type=test_params["meal_type"],
            calories_target=test_params["calories_target"],
            protein_target=test_params["protein_target"],
            fat_target=test_params["fat_target"],
            carbs_target=test_params["carbs_target"],
            preferences=test_params["preferences"],
            allergies=test_params["allergies"]
        )
        
        if meals:
            print(f"✅ Generated {len(meals)} meals:")
            for i, meal in enumerate(meals, 1):
                print(f"\n   {i}. {meal['name']}")
                print(f"      📝 {meal['description']}")
                print(f"      📊 Nutrition:")
                print(f"         - Calories: {meal['nutrition']['calories']}")
                print(f"         - Protein: {meal['nutrition']['protein']}g")
                print(f"         - Fat: {meal['nutrition']['fat']}g")
                print(f"         - Carbs: {meal['nutrition']['carbs']}g")
                print(f"      🥘 Ingredients: {len(meal['ingredients'])} items")
                print(f"      ⏱️ Prep time: {meal['preparation_time']}")
        else:
            print("❌ No meals generated")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Realistic Combination Dishes Tests")
    print("=" * 70)
    
    try:
        # Run all tests
        test_realistic_combination_generation()
        test_fallback_meal_suggestions()
        test_dish_name_parsing()
        test_meal_generation_with_combinations()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
