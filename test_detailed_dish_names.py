#!/usr/bin/env python3
"""
Test script cho tính năng tạo tên món ăn chi tiết
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groq_integration import GroqService
import json

def test_detailed_dish_names():
    """Test tính năng tạo tên món ăn chi tiết"""
    print("🧪 Testing Detailed Dish Names Generation")
    print("=" * 60)
    
    # Initialize Groq service
    groq_service = GroqService()
    
    # Test combinations
    test_combinations = [
        ("cơm", "thịt", "lunch"),
        ("cơm", "cá", "dinner"),
        ("bún", "gà", "lunch"),
        ("phở", "bò", "breakfast"),
        ("mì", "tôm", "lunch"),
        ("bánh mì", "chả cá", "breakfast"),
        ("xôi", "thịt", "breakfast"),
        ("cháo", "gà", "breakfast")
    ]
    
    print("🍽️ Generating detailed dish names:")
    print("-" * 40)
    
    for i, (base_food, protein_type, meal_type) in enumerate(test_combinations, 1):
        try:
            # Generate detailed dish name
            detailed_name = groq_service._create_detailed_dish_name(base_food, protein_type, meal_type)
            print(f"{i:2d}. {base_food} + {protein_type} ({meal_type})")
            print(f"    → {detailed_name}")
            print()
        except Exception as e:
            print(f"{i:2d}. {base_food} + {protein_type} ({meal_type})")
            print(f"    → Error: {str(e)}")
            print()

def test_detailed_combination_generation():
    """Test tạo danh sách món ăn kết hợp với tên chi tiết"""
    print("🧪 Testing Detailed Combination Dishes Generation")
    print("=" * 60)
    
    groq_service = GroqService()
    
    meal_types = ["breakfast", "lunch", "dinner"]
    
    for meal_type in meal_types:
        print(f"\n🍽️ {meal_type.upper()} - Detailed Combination Dishes")
        print("-" * 40)
        
        try:
            combination_dishes = groq_service._generate_realistic_combination_dishes(
                meal_type=meal_type,
                preferences=[],
                allergies=[]
            )
            
            print(f"✅ Generated {len(combination_dishes)} detailed dishes:")
            for i, dish in enumerate(combination_dishes[:8], 1):  # Show first 8
                print(f"   {i}. {dish}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_multiple_generations():
    """Test tạo nhiều lần để xem sự đa dạng"""
    print("\n🧪 Testing Multiple Generations for Variety")
    print("=" * 60)
    
    groq_service = GroqService()
    
    base_food = "cơm"
    protein_type = "gà"
    meal_type = "lunch"
    
    print(f"🍽️ Generating 10 variations of: {base_food} + {protein_type} ({meal_type})")
    print("-" * 50)
    
    generated_names = set()
    
    for i in range(10):
        try:
            detailed_name = groq_service._create_detailed_dish_name(base_food, protein_type, meal_type)
            generated_names.add(detailed_name)
            print(f"{i+1:2d}. {detailed_name}")
        except Exception as e:
            print(f"{i+1:2d}. Error: {str(e)}")
    
    print(f"\n📊 Generated {len(generated_names)} unique variations out of 10 attempts")
    print(f"📈 Variety rate: {(len(generated_names)/10)*100:.1f}%")

def test_fallback_with_detailed_names():
    """Test fallback meals với tên chi tiết"""
    print("\n🧪 Testing Fallback Meals with Detailed Names")
    print("=" * 60)
    
    groq_service = GroqService()
    
    meal_type = "lunch"
    print(f"🍽️ Testing {meal_type} fallback meals with detailed names")
    print("-" * 40)
    
    try:
        fallback_meals = groq_service._fallback_meal_suggestions(meal_type)
        
        if fallback_meals:
            print(f"✅ Generated {len(fallback_meals)} fallback meals:")
            for i, meal in enumerate(fallback_meals, 1):
                print(f"\n   {i}. {meal['name']}")
                print(f"      📝 {meal['description']}")
                print(f"      🥘 Ingredients: {len(meal['ingredients'])} items")
                print(f"      📊 {meal['nutrition']['calories']} kcal")
                print(f"      ⏱️ {meal['preparation_time']}")
        else:
            print("❌ No fallback meals generated")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_meal_generation_with_detailed_names():
    """Test meal generation với detailed names"""
    print("\n🧪 Testing Full Meal Generation with Detailed Names")
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
    
    print(f"🍽️ Generating meals for {test_params['meal_type']} with detailed names")
    print(f"📊 Targets: {test_params['calories_target']} kcal, {test_params['protein_target']}g protein")
    print("-" * 50)
    
    try:
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
            print(f"✅ Generated {len(meals)} meals with detailed names:")
            for i, meal in enumerate(meals, 1):
                print(f"\n   {i}. {meal['name']}")
                print(f"      📝 {meal['description'][:100]}...")
                print(f"      📊 Nutrition: {meal['nutrition']['calories']} kcal, "
                      f"{meal['nutrition']['protein']}g protein")
                print(f"      🥘 {len(meal['ingredients'])} ingredients")
                print(f"      ⏱️ {meal['preparation_time']}")
        else:
            print("❌ No meals generated")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Detailed Dish Names Tests")
    print("=" * 70)
    
    try:
        # Run all tests
        test_detailed_dish_names()
        test_detailed_combination_generation()
        test_multiple_generations()
        test_fallback_with_detailed_names()
        test_meal_generation_with_detailed_names()
        
        print("\n🎉 All detailed dish name tests completed!")
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
