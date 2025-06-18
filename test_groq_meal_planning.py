#!/usr/bin/env python3
"""
Comprehensive test for Groq-based meal planning
Tests AI generation, validation, and all required fields
"""

import sys
import json
import time
from datetime import datetime

# Add current directory to path
sys.path.append('.')

def test_groq_service_initialization():
    """Test Groq service initialization"""
    print("🔧 Testing Groq Service Initialization...")
    
    try:
        from groq_integration import groq_service
        
        print(f"✅ Groq service imported successfully")
        print(f"   Available: {groq_service.available}")
        print(f"   Model: {groq_service.model}")
        print(f"   Quota exceeded: {groq_service.quota_exceeded}")
        print(f"   API Key present: {'***' + groq_service.api_key[-4:] if groq_service.api_key else 'No'}")
        
        return groq_service.available
        
    except Exception as e:
        print(f"❌ Error importing Groq service: {e}")
        return False

def test_groq_meal_generation_with_ai():
    """Test meal generation with AI enabled"""
    print("\n🤖 Testing Groq AI Meal Generation...")
    
    try:
        from groq_integration import groq_service
        
        if not groq_service.available:
            print("❌ Groq service not available, skipping AI test")
            return False
        
        print("📤 Generating meals with AI...")
        start_time = time.time()
        
        # Test breakfast generation
        breakfast_meals = groq_service.generate_meal_suggestions(
            calories_target=400,
            protein_target=25,
            fat_target=15,
            carbs_target=45,
            meal_type="bữa sáng",
            preferences=["healthy", "vietnamese"],
            allergies=[],
            cuisine_style="vietnamese",
            use_ai=True,  # Enable AI
            day_of_week="monday",
            random_seed=12345
        )
        
        generation_time = time.time() - start_time
        print(f"⏱️ Generation time: {generation_time:.2f} seconds")
        
        if not breakfast_meals:
            print("❌ No meals generated")
            return False
        
        print(f"✅ Generated {len(breakfast_meals)} breakfast meals")
        
        # Validate each meal
        required_fields = ['name', 'description', 'ingredients', 'preparation', 'nutrition', 'preparation_time', 'health_benefits']
        
        for i, meal in enumerate(breakfast_meals):
            print(f"\n📋 Meal {i+1}: {meal.get('name', 'Unknown')}")
            
            missing_fields = []
            for field in required_fields:
                if field not in meal:
                    missing_fields.append(field)
                else:
                    # Check field content
                    value = meal[field]
                    if field == 'ingredients':
                        if not isinstance(value, list) or len(value) == 0:
                            missing_fields.append(f"{field} (empty)")
                        else:
                            print(f"   🥬 Ingredients: {len(value)} items")
                    elif field == 'preparation':
                        if not isinstance(value, list) or len(value) == 0:
                            missing_fields.append(f"{field} (empty)")
                        else:
                            print(f"   🍳 Preparation: {len(value)} steps")
                    elif field == 'nutrition':
                        if not isinstance(value, dict):
                            missing_fields.append(f"{field} (invalid)")
                        else:
                            calories = value.get('calories', 0)
                            protein = value.get('protein', 0)
                            print(f"   📊 Nutrition: {calories} cal, {protein}g protein")
                    elif field == 'preparation_time':
                        print(f"   ⏰ Time: {value}")
                    elif field == 'health_benefits':
                        print(f"   💊 Benefits: {value[:50]}...")
                    elif field == 'description':
                        print(f"   📝 Description: {value[:50]}...")
            
            if missing_fields:
                print(f"   ❌ Missing/Invalid fields: {missing_fields}")
                return False
            else:
                print(f"   ✅ All required fields present and valid")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in AI meal generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_groq_meal_generation_fallback():
    """Test meal generation with fallback data"""
    print("\n🔄 Testing Groq Fallback Meal Generation...")
    
    try:
        from groq_integration import groq_service
        
        print("📤 Generating meals with fallback...")
        
        # Test with AI disabled to force fallback
        fallback_meals = groq_service.generate_meal_suggestions(
            calories_target=400,
            protein_target=25,
            fat_target=15,
            carbs_target=45,
            meal_type="bữa sáng",
            preferences=["vietnamese"],
            allergies=[],
            cuisine_style="vietnamese",
            use_ai=False  # Force fallback
        )
        
        if not fallback_meals:
            print("❌ No fallback meals generated")
            return False
        
        print(f"✅ Generated {len(fallback_meals)} fallback meals")
        
        # Check first meal
        meal = fallback_meals[0]
        print(f"📋 Sample meal: {meal.get('name', 'Unknown')}")
        
        required_fields = ['name', 'description', 'ingredients', 'preparation', 'nutrition', 'preparation_time', 'health_benefits']
        missing_fields = [field for field in required_fields if field not in meal]
        
        if missing_fields:
            print(f"❌ Missing fields in fallback: {missing_fields}")
            print(f"Available fields: {list(meal.keys())}")
            return False
        else:
            print(f"✅ All required fields present in fallback")
            return True
        
    except Exception as e:
        print(f"❌ Error in fallback generation: {e}")
        return False

def test_weekly_meal_plan_generation():
    """Test full weekly meal plan generation"""
    print("\n📅 Testing Weekly Meal Plan Generation...")
    
    try:
        from services import generate_weekly_meal_plan
        
        print("📤 Generating weekly meal plan...")
        start_time = time.time()
        
        weekly_plan = generate_weekly_meal_plan(
            calories_target=2000,
            protein_target=120,
            fat_target=65,
            carbs_target=250,
            preferences=["vietnamese", "healthy"],
            allergies=[],
            cuisine_style="vietnamese",
            use_ai=True,
            use_tdee=False
        )
        
        generation_time = time.time() - start_time
        print(f"⏱️ Weekly plan generation time: {generation_time:.2f} seconds")
        
        if not weekly_plan:
            print("❌ No weekly plan generated")
            return False
        
        print(f"✅ Weekly plan generated successfully")
        
        # Check plan structure
        if hasattr(weekly_plan, 'days'):
            days = weekly_plan.days
            print(f"📊 Plan has {len(days)} days")
            
            # Check first day
            if days:
                first_day = days[0]
                print(f"📅 Sample day: {first_day.day_of_week}")
                
                # Check meals in first day
                for meal_type in ['breakfast', 'lunch', 'dinner']:
                    if hasattr(first_day, meal_type):
                        meal_data = getattr(first_day, meal_type)
                        if hasattr(meal_data, 'dishes'):
                            dishes = meal_data.dishes
                            print(f"   🍽️ {meal_type}: {len(dishes)} dishes")
                            
                            if dishes:
                                first_dish = dishes[0]
                                print(f"      📝 Sample dish: {getattr(first_dish, 'name', 'Unknown')}")
                        else:
                            print(f"   ❌ {meal_type} has no dishes attribute")
            
            return True
        else:
            print(f"❌ Weekly plan has no days attribute")
            print(f"Plan type: {type(weekly_plan)}")
            print(f"Plan attributes: {dir(weekly_plan)}")
            return False
        
    except Exception as e:
        print(f"❌ Error in weekly plan generation: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_parsing():
    """Test JSON parsing capabilities"""
    print("\n🔍 Testing JSON Parsing...")
    
    try:
        from groq_integration import groq_service
        
        # Test sample JSON response
        sample_json = '''[
        {
            "name": "Phở Gà",
            "description": "Món phở truyền thống với thịt gà",
            "ingredients": [
                {"name": "Bánh phở", "amount": "100g"},
                {"name": "Thịt gà", "amount": "150g"}
            ],
            "preparation": [
                "Luộc gà chín",
                "Nấu nước dùng",
                "Trình bày phở"
            ],
            "nutrition": {
                "calories": 400,
                "protein": 25,
                "fat": 15,
                "carbs": 45
            },
            "preparation_time": "30 phút",
            "health_benefits": "Giàu protein từ thịt gà"
        }]'''
        
        print("📤 Testing JSON extraction...")
        extracted_data = groq_service._extract_json_from_response(sample_json)
        
        if extracted_data and len(extracted_data) > 0:
            print(f"✅ Successfully extracted {len(extracted_data)} meals from JSON")
            
            meal = extracted_data[0]
            required_fields = ['name', 'description', 'ingredients', 'preparation', 'nutrition', 'preparation_time', 'health_benefits']
            missing_fields = [field for field in required_fields if field not in meal]
            
            if not missing_fields:
                print(f"✅ All required fields present in parsed JSON")
                return True
            else:
                print(f"❌ Missing fields in parsed JSON: {missing_fields}")
                return False
        else:
            print(f"❌ Failed to extract data from JSON")
            return False
        
    except Exception as e:
        print(f"❌ Error in JSON parsing test: {e}")
        return False

def test_meal_validation():
    """Test meal validation process"""
    print("\n✅ Testing Meal Validation...")
    
    try:
        from groq_integration import groq_service
        
        # Test with incomplete meal data
        incomplete_meals = [
            {
                "name": "Test Meal",
                "ingredients": [{"name": "Test", "amount": "100g"}]
                # Missing other fields
            }
        ]
        
        print("📤 Testing validation with incomplete data...")
        validated_meals = groq_service._validate_meals(incomplete_meals)
        
        if validated_meals and len(validated_meals) > 0:
            meal = validated_meals[0]
            required_fields = ['name', 'description', 'ingredients', 'preparation', 'nutrition', 'preparation_time', 'health_benefits']
            missing_fields = [field for field in required_fields if field not in meal]
            
            if not missing_fields:
                print(f"✅ Validation successfully added missing fields")
                print(f"   Added description: {meal.get('description', '')[:50]}...")
                print(f"   Added preparation_time: {meal.get('preparation_time')}")
                print(f"   Added health_benefits: {meal.get('health_benefits', '')[:50]}...")
                return True
            else:
                print(f"❌ Validation failed to add fields: {missing_fields}")
                return False
        else:
            print(f"❌ Validation returned no meals")
            return False
        
    except Exception as e:
        print(f"❌ Error in validation test: {e}")
        return False

def main():
    """Run comprehensive Groq meal planning tests"""
    print("🚀 Comprehensive Groq Meal Planning Test")
    print("="*60)
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Groq Service Initialization", test_groq_service_initialization),
        ("JSON Parsing", test_json_parsing),
        ("Meal Validation", test_meal_validation),
        ("Fallback Meal Generation", test_groq_meal_generation_fallback),
        ("AI Meal Generation", test_groq_meal_generation_with_ai),
        ("Weekly Meal Plan Generation", test_weekly_meal_plan_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Running: {test_name}")
        print(f"{'='*60}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            print(f"💥 {test_name}: CRASHED - {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Groq meal planning is working perfectly!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
