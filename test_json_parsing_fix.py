#!/usr/bin/env python3
"""
Test JSON Parsing Fix
Kiểm tra và sửa lỗi JSON parsing từ Groq API
"""

import json
import re
from groq_integration import GroqService

def test_malformed_json_samples():
    """Test với các mẫu JSON bị lỗi thực tế từ Groq"""
    
    groq_service = GroqService()
    
    # Các mẫu JSON bị lỗi thực tế từ log
    malformed_samples = [
        # Sample 1: Missing "name" key
        '''[
  {
    "Bánh Mì Chay",
    "description": "Món bánh mì chay thơm ngon, chứa nhiều chất xơ và protein, phù hợp cho mục tiêu giảm cân.",
    "ingredients": [
      {"name": "Bánh mì", "amount": "100g"},
      {"name": "Đậu phụ", "amount": "50g"}
    ],
    "preparation": [
      "Xếp bánh mì ra đĩa.",
      "Đậu phụ cắt nhỏ và xếp lên bánh mì."
    ],
    "nutrition": {
      "calories": 377,
      "protein": 28,
      "fat": 10,
      "carbs": 42
    },
    "preparation_time": "20 phút",
    "health_benefits": "Cung cấp protein chất lượng cao từ đậu phụ."
  }
]''',
        
        # Sample 2: Missing field names
        '''[
  {
    "Bánh Mì Chay",
    "Món bánh mì chay thơm ngon với đậu hũ, rau củ và nước sốt trứng",
    [
      {"name": "Bánh mì", "amount": "100g"},
      {"name": "Đậu hũ", "amount": "50g"}
    ],
    [
      "Chiên đậu hũ với rau và gia vị.",
      "Xếp bánh mì ra đĩa, thêm đậu hũ."
    ],
    {
      "calories": 377,
      "protein": 28,
      "fat": 10,
      "carbs": 42
    },
    "30 phút",
    "Cung cấp protein chất lượng cao từ đậu hũ và trứng."
  }
]''',
        
        # Sample 3: Mixed issues
        '''[
  {
    "Cháo Gà Đậu Xanh",
    "Món cháo gà đậu xanh thơm ngon, với gà xay, đậu xanh và gia vị.",
    [
      {"name": "Gà xay", "amount": "100g"},
      {"name": "Đậu xanh", "amount": "50g"}
    ],
    [
      "Ướp gà xay với gia vị trong 30 phút.",
      "Nấu cháo với gà xay và đậu xanh đến khi chín."
    ],
    {
      "calories": 377,
      "protein": 28,
      "fat": 10,
      "carbs": 42
    },
    "45 phút",
    "Cung cấp protein chất lượng cao từ gà."
  }
]'''
    ]
    
    print("🧪 TESTING MALFORMED JSON PARSING")
    print("=" * 50)
    
    success_count = 0
    for i, sample in enumerate(malformed_samples, 1):
        print(f"\n📋 Test Sample {i}:")
        print(f"Original length: {len(sample)} chars")
        print(f"First 100 chars: {sample[:100]}...")
        
        try:
            # Test original parsing (should fail)
            try:
                original_parsed = json.loads(sample)
                print("⚠️ Original sample is actually valid JSON!")
            except json.JSONDecodeError:
                print("✅ Original sample is malformed as expected")
            
            # Test our fixing
            fixed_json = groq_service._fix_malformed_json(sample)
            print(f"Fixed length: {len(fixed_json)} chars")
            
            # Try to parse fixed JSON
            parsed_data = json.loads(fixed_json)
            
            if isinstance(parsed_data, list) and len(parsed_data) > 0:
                meal = parsed_data[0]
                required_fields = ["name", "description", "ingredients", "preparation", "nutrition"]
                missing_fields = [field for field in required_fields if field not in meal]
                
                if not missing_fields:
                    print(f"✅ Successfully fixed and parsed! Meal: {meal.get('name', 'Unknown')}")
                    success_count += 1
                else:
                    print(f"⚠️ Parsed but missing fields: {missing_fields}")
                    print(f"Available fields: {list(meal.keys())}")
            else:
                print("❌ Fixed JSON is not a valid meal list")
                
        except json.JSONDecodeError as e:
            print(f"❌ Still invalid after fixing: {e}")
            print(f"Fixed JSON preview: {fixed_json[:200]}...")
        except Exception as e:
            print(f"❌ Error during fixing: {e}")
    
    print(f"\n📊 RESULTS: {success_count}/{len(malformed_samples)} samples fixed successfully")
    return success_count == len(malformed_samples)

def test_enhanced_json_fixing():
    """Test enhanced JSON fixing với regex patterns mới"""
    
    print("\n🔧 TESTING ENHANCED JSON FIXING")
    print("=" * 45)
    
    # Test patterns cụ thể
    test_patterns = [
        {
            "name": "Missing name key pattern 1",
            "input": '{ "Bánh Mì Chay", "description": "test" }',
            "expected_fix": '{"name": "Bánh Mì Chay", "description": "test"}'
        },
        {
            "name": "Missing name key pattern 2", 
            "input": '[{ "Cháo Gà", "description": "test" }]',
            "expected_fix": '[{"name": "Cháo Gà", "description": "test"}]'
        },
        {
            "name": "Missing field names",
            "input": '"name": "Test", "Some text", [{"name": "ingredient"}]',
            "expected_contains": '"description":'
        }
    ]
    
    groq_service = GroqService()
    success_count = 0
    
    for test in test_patterns:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"Input: {test['input']}")
        
        try:
            fixed = groq_service._fix_malformed_json(test['input'])
            print(f"Fixed: {fixed}")
            
            if "expected_fix" in test:
                if fixed.strip() == test["expected_fix"].strip():
                    print("✅ Perfect match!")
                    success_count += 1
                else:
                    print("⚠️ Different but may still be valid")
            elif "expected_contains" in test:
                if test["expected_contains"] in fixed:
                    print("✅ Contains expected pattern!")
                    success_count += 1
                else:
                    print("❌ Missing expected pattern")
            
            # Try to parse if it looks like complete JSON
            if fixed.startswith('[') or fixed.startswith('{'):
                try:
                    json.loads(fixed)
                    print("✅ Fixed JSON is parseable")
                except:
                    print("⚠️ Fixed JSON still not parseable")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 Pattern Tests: {success_count}/{len(test_patterns)} passed")

def test_real_groq_generation():
    """Test với Groq API thực tế"""
    
    print("\n🤖 TESTING REAL GROQ GENERATION")
    print("=" * 45)
    
    try:
        groq_service = GroqService()
        
        if not groq_service.available:
            print("❌ Groq service not available")
            return False
        
        print("🔄 Generating meal with Groq...")
        
        # Test với parameters đơn giản
        meals = groq_service.generate_meal_suggestions(
            calories_target=400,
            protein_target=25,
            fat_target=15,
            carbs_target=50,
            meal_type="bữa sáng",
            use_ai=True
        )
        
        if meals and len(meals) > 0:
            print(f"✅ Successfully generated {len(meals)} meals")
            
            for i, meal in enumerate(meals, 1):
                print(f"\n📋 Meal {i}: {meal.get('name', 'Unknown')}")
                
                # Validate structure
                required_fields = ["name", "description", "ingredients", "preparation", "nutrition"]
                missing_fields = [field for field in required_fields if field not in meal]
                
                if not missing_fields:
                    print("✅ All required fields present")
                else:
                    print(f"⚠️ Missing fields: {missing_fields}")
                
                # Check nutrition values
                nutrition = meal.get('nutrition', {})
                if isinstance(nutrition, dict) and 'calories' in nutrition:
                    print(f"📊 Nutrition: {nutrition.get('calories')}kcal, {nutrition.get('protein')}g protein")
                else:
                    print("⚠️ Invalid nutrition data")
            
            return True
        else:
            print("❌ No meals generated")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Groq: {e}")
        return False

def main():
    """Main test runner"""
    
    print("🚀 COMPREHENSIVE JSON PARSING FIX TEST")
    print("=" * 60)
    
    tests = [
        ("Malformed JSON Samples", test_malformed_json_samples),
        ("Enhanced JSON Fixing", test_enhanced_json_fixing),
        ("Real Groq Generation", test_real_groq_generation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 FINAL RESULTS")
    print("="*60)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - JSON parsing is working!")
    else:
        print(f"\n⚠️ {total - passed} tests failed - needs more work")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
