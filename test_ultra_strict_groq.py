#!/usr/bin/env python3
"""
Test Ultra-Strict Groq JSON Generation System
"""

import sys
import os
import json
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groq_integration import GroqService

def test_ultra_strict_system():
    """Test the ultra-strict JSON generation system"""
    print("🚀 TESTING ULTRA-STRICT GROQ JSON GENERATION")
    print("="*60)
    
    groq_service = GroqService()
    
    test_cases = [
        {
            "name": "Bữa sáng strict test",
            "meal_type": "bữa sáng",
            "calories": 300,
            "protein": 20,
            "fat": 10,
            "carbs": 30,
            "preferences": ["healthy"],
            "allergies": []
        },
        {
            "name": "Bữa trưa strict test",
            "meal_type": "bữa trưa", 
            "calories": 500,
            "protein": 30,
            "fat": 15,
            "carbs": 60,
            "preferences": ["high-protein"],
            "allergies": ["seafood"]
        },
        {
            "name": "Bữa tối strict test",
            "meal_type": "bữa tối",
            "calories": 400,
            "protein": 25,
            "fat": 12,
            "carbs": 50,
            "preferences": ["balanced"],
            "allergies": []
        }
    ]
    
    results = []
    total_success = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_case['name']} ---")
        
        try:
            start_time = time.time()
            
            meals = groq_service.generate_meal_suggestions(
                meal_type=test_case['meal_type'],
                calories_target=test_case['calories'],
                protein_target=test_case['protein'],
                fat_target=test_case['fat'],
                carbs_target=test_case['carbs'],
                preferences=test_case['preferences'],
                allergies=test_case['allergies'],
                cuisine_style="Vietnamese"
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if meals and len(meals) > 0:
                total_success += 1
                print(f"✅ SUCCESS: Generated {len(meals)} meals in {response_time:.2f}s")
                
                # Validate each meal has required keys
                required_keys = ["name", "description", "ingredients", "preparation", "nutrition", "preparation_time", "health_benefits"]
                
                for j, meal in enumerate(meals, 1):
                    print(f"   🍽️ Meal {j}: {meal.get('name', 'Unknown')}")
                    
                    # Check all required keys
                    missing_keys = [key for key in required_keys if key not in meal]
                    if missing_keys:
                        print(f"      ❌ Missing keys: {missing_keys}")
                    else:
                        print(f"      ✅ All required keys present")
                    
                    # Check nutrition
                    nutrition = meal.get('nutrition', {})
                    if isinstance(nutrition, dict):
                        print(f"      📊 Nutrition: {nutrition.get('calories', 0)}kcal, {nutrition.get('protein', 0)}g protein")
                    else:
                        print(f"      ❌ Invalid nutrition format: {nutrition}")
                
                results.append({
                    "test_case": test_case['name'],
                    "status": "SUCCESS",
                    "meals_count": len(meals),
                    "response_time": response_time,
                    "meals": meals
                })
            else:
                print(f"❌ FAILED: No meals returned")
                results.append({
                    "test_case": test_case['name'],
                    "status": "FAILED",
                    "error": "No meals returned"
                })
                
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            results.append({
                "test_case": test_case['name'],
                "status": "ERROR",
                "error": str(e)
            })
    
    # Summary
    success_rate = (total_success / len(test_cases)) * 100
    print(f"\n📊 ULTRA-STRICT TEST SUMMARY:")
    print(f"✅ Successful tests: {total_success}/{len(test_cases)}")
    print(f"📈 Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print(f"🎉 EXCELLENT: Ultra-strict system working perfectly!")
    elif success_rate >= 70:
        print(f"✅ GOOD: System working well with minor issues")
    else:
        print(f"⚠️ NEEDS IMPROVEMENT: Success rate too low")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ultra_strict_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "success_rate": success_rate,
            "total_tests": len(test_cases),
            "successful_tests": total_success,
            "results": results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")
    
    return success_rate >= 90

def test_json_key_validation():
    """Test specific JSON key validation"""
    print(f"\n🔍 TESTING JSON KEY VALIDATION")
    print("-"*40)
    
    groq_service = GroqService()
    
    # Test with malformed JSON samples
    test_samples = [
        '{"Bánh Mì Chay", "description": "test"}',  # Missing "name" key
        '[{"name": "Test", "ingredients": []}]',     # Missing other keys
        '[{"name": "Test", "description": "test", "ingredients": [], "preparation": [], "nutrition": {}, "preparation_time": "30 phút", "health_benefits": "test"}]'  # Complete
    ]
    
    for i, sample in enumerate(test_samples, 1):
        print(f"\nSample {i}: {sample[:50]}...")
        
        try:
            parsed = json.loads(sample)
            if isinstance(parsed, list):
                for item in parsed:
                    if isinstance(item, dict):
                        valid = groq_service._validate_required_keys(item)
                        print(f"   Validation result: {'✅ VALID' if valid else '❌ INVALID'}")
            elif isinstance(parsed, dict):
                valid = groq_service._validate_required_keys(parsed)
                print(f"   Validation result: {'✅ VALID' if valid else '❌ INVALID'}")
        except json.JSONDecodeError:
            print(f"   ❌ Invalid JSON format")

def main():
    """Main function"""
    print("🚀 Starting Ultra-Strict Groq System Test")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Test 1: Ultra-strict system
        system_success = test_ultra_strict_system()
        
        # Test 2: JSON key validation
        test_json_key_validation()
        
        print(f"\n🎯 FINAL ASSESSMENT:")
        if system_success:
            print(f"✅ Ultra-strict system is working perfectly!")
            print(f"🚀 Ready for production deployment!")
        else:
            print(f"⚠️ System needs further improvements")
            print(f"🔧 Consider additional prompt engineering")
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
