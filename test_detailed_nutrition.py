#!/usr/bin/env python3
"""
Test script cho tính năng lấy nutrition từ tên món chi tiết
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groq_integration import GroqService
import json

def test_detailed_nutrition_extraction():
    """Test tính năng lấy nutrition từ tên món chi tiết"""
    print("🧪 Testing Detailed Nutrition Extraction")
    print("=" * 60)
    
    # Initialize Groq service
    groq_service = GroqService()
    
    # Test cases với tên món chi tiết
    test_dishes = [
        "Cơm gạo lứt với cá hấp và rau luộc",
        "Bún tươi với gà nướng mật ong và rau thơm", 
        "Phở tươi với thịt bò tái và rau sống",
        "Mì trứng với tôm nướng và mướp xào",
        "Cháo gạo tẻ với gà xào sả ớt và rau sống",
        "Bánh mì tươi với chả cá và dưa chua",
        "Xôi dẻo với thịt nướng than và dưa chua"
    ]
    
    for i, dish_name in enumerate(test_dishes, 1):
        print(f"\n🍽️ Test Case {i}: {dish_name}")
        print("-" * 50)
        
        try:
            # Test extract simple dish name
            simple_name = groq_service._extract_simple_dish_name(dish_name)
            print(f"📝 Simple name: {simple_name}")
            
            # Test parse detailed components
            components = groq_service._parse_detailed_dish_components(dish_name)
            print(f"🥘 Components ({len(components)} items):")
            for comp in components:
                print(f"   - {comp['name']}: {comp['amount']}")
            
            # Test get official nutrition
            nutrition = groq_service._get_official_nutrition(dish_name, components)
            print(f"📊 Nutrition:")
            print(f"   - Calories: {nutrition['calories']}")
            print(f"   - Protein: {nutrition['protein']}g")
            print(f"   - Fat: {nutrition['fat']}g")
            print(f"   - Carbs: {nutrition['carbs']}g")
            print(f"   - Source: {nutrition['source']}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

def test_simple_vs_detailed_nutrition():
    """So sánh nutrition giữa tên món đơn giản và chi tiết"""
    print("\n🧪 Testing Simple vs Detailed Nutrition Comparison")
    print("=" * 60)
    
    groq_service = GroqService()
    
    test_pairs = [
        ("Cơm Gà", "Cơm gạo lứt với gà nướng mật ong và rau luộc"),
        ("Bún Bò", "Bún tươi với thịt bò nướng lá lốt và rau thơm"),
        ("Phở Gà", "Phở tươi với gà luộc và rau sống"),
        ("Cháo Cá", "Cháo gạo tẻ với cá hấp và rau muống luộc")
    ]
    
    for simple_name, detailed_name in test_pairs:
        print(f"\n🔍 Comparing: '{simple_name}' vs '{detailed_name}'")
        print("-" * 60)
        
        try:
            # Get nutrition for simple name
            simple_nutrition = groq_service._get_official_nutrition(simple_name, [])
            print(f"📊 Simple ({simple_name}):")
            print(f"   Calories: {simple_nutrition['calories']}, Protein: {simple_nutrition['protein']}g")
            print(f"   Source: {simple_nutrition['source']}")
            
            # Get nutrition for detailed name
            detailed_nutrition = groq_service._get_official_nutrition(detailed_name, [])
            print(f"📊 Detailed ({detailed_name}):")
            print(f"   Calories: {detailed_nutrition['calories']}, Protein: {detailed_nutrition['protein']}g")
            print(f"   Source: {detailed_nutrition['source']}")
            
            # Compare
            calorie_diff = detailed_nutrition['calories'] - simple_nutrition['calories']
            protein_diff = detailed_nutrition['protein'] - simple_nutrition['protein']
            
            print(f"📈 Difference:")
            print(f"   Calories: {calorie_diff:+.1f} ({calorie_diff/simple_nutrition['calories']*100:+.1f}%)")
            print(f"   Protein: {protein_diff:+.1f}g ({protein_diff/simple_nutrition['protein']*100:+.1f}%)")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_ingredient_parsing_accuracy():
    """Test độ chính xác của việc parse ingredients"""
    print("\n🧪 Testing Ingredient Parsing Accuracy")
    print("=" * 60)
    
    groq_service = GroqService()
    
    test_cases = [
        {
            "dish": "Cơm gạo lứt với thịt bò nướng và rau muống xào",
            "expected_ingredients": ["gạo tẻ", "thịt bò", "rau muống", "nước mắm", "dầu ăn"]
        },
        {
            "dish": "Bún tươi với tôm hấp và cải thảo luộc",
            "expected_ingredients": ["bún tươi", "tôm sú", "cải bắp", "nước mắm", "dầu ăn"]
        },
        {
            "dish": "Phở với gà luộc và rau thơm",
            "expected_ingredients": ["bánh phở", "thịt gà", "rau muống", "nước mắm", "dầu ăn"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        dish_name = test_case["dish"]
        expected = test_case["expected_ingredients"]
        
        print(f"\n🍽️ Test Case {i}: {dish_name}")
        print(f"🎯 Expected ingredients: {expected}")
        
        try:
            parsed_ingredients = groq_service._parse_detailed_dish_components(dish_name)
            parsed_names = [ing["name"] for ing in parsed_ingredients]
            
            print(f"🔍 Parsed ingredients: {parsed_names}")
            
            # Check accuracy
            matches = 0
            for exp_ing in expected:
                if any(exp_ing in parsed_name for parsed_name in parsed_names):
                    matches += 1
                    print(f"   ✅ Found: {exp_ing}")
                else:
                    print(f"   ❌ Missing: {exp_ing}")
            
            accuracy = (matches / len(expected)) * 100
            print(f"📊 Accuracy: {matches}/{len(expected)} ({accuracy:.1f}%)")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_nutrition_database_coverage():
    """Test coverage của nutrition database"""
    print("\n🧪 Testing Nutrition Database Coverage")
    print("=" * 60)
    
    from vietnamese_nutrition_database import VIETNAMESE_NUTRITION_DATABASE, VIETNAMESE_DISHES_NUTRITION
    
    print(f"📊 Database Statistics:")
    print(f"   Ingredients: {len(VIETNAMESE_NUTRITION_DATABASE)} items")
    print(f"   Complete dishes: {len(VIETNAMESE_DISHES_NUTRITION)} items")
    
    print(f"\n🥘 Sample ingredients:")
    for i, (name, data) in enumerate(list(VIETNAMESE_NUTRITION_DATABASE.items())[:10], 1):
        print(f"   {i:2d}. {name}: {data['calories']} kcal, {data['protein']}g protein")
    
    print(f"\n🍽️ Sample complete dishes:")
    for i, (name, data) in enumerate(list(VIETNAMESE_DISHES_NUTRITION.items())[:5], 1):
        print(f"   {i}. {name}: {data['calories']} kcal, {data['protein']}g protein")

def test_meal_generation_with_detailed_nutrition():
    """Test meal generation với detailed nutrition"""
    print("\n🧪 Testing Meal Generation with Detailed Nutrition")
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
    
    print(f"🍽️ Generating meals with detailed nutrition")
    print(f"📊 Targets: {test_params['calories_target']} kcal, {test_params['protein_target']}g protein")
    
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
            print(f"✅ Generated {len(meals)} meals with detailed nutrition:")
            total_calories = 0
            total_protein = 0
            
            for i, meal in enumerate(meals, 1):
                nutrition = meal.get('nutrition', {})
                calories = nutrition.get('calories', 0)
                protein = nutrition.get('protein', 0)
                source = nutrition.get('source', 'Unknown')
                
                total_calories += calories
                total_protein += protein
                
                print(f"\n   {i}. {meal['name']}")
                print(f"      📊 {calories} kcal, {protein}g protein")
                print(f"      📝 Source: {source}")
                print(f"      🥘 Ingredients: {len(meal.get('ingredients', []))} items")
            
            print(f"\n📊 Total nutrition:")
            print(f"   Calories: {total_calories} / {test_params['calories_target']} (target)")
            print(f"   Protein: {total_protein:.1f}g / {test_params['protein_target']}g (target)")
            
            accuracy_calories = (total_calories / test_params['calories_target']) * 100
            accuracy_protein = (total_protein / test_params['protein_target']) * 100
            
            print(f"📈 Accuracy:")
            print(f"   Calories: {accuracy_calories:.1f}%")
            print(f"   Protein: {accuracy_protein:.1f}%")
        else:
            print("❌ No meals generated")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting Detailed Nutrition Tests")
    print("=" * 70)
    
    try:
        # Run all tests
        test_detailed_nutrition_extraction()
        test_simple_vs_detailed_nutrition()
        test_ingredient_parsing_accuracy()
        test_nutrition_database_coverage()
        test_meal_generation_with_detailed_nutrition()
        
        print("\n🎉 All detailed nutrition tests completed!")
        
    except Exception as e:
        print(f"\n💥 Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()
