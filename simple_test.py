#!/usr/bin/env python3
"""
Simple test for meal planning functionality
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test basic health check"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {data.get('status')}")
            print(f"   AI Available: {data.get('ai_available')}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_meal_generation_without_auth():
    """Test meal generation without authentication (if allowed)"""
    print("\n🍽️ Testing meal generation...")
    
    test_data = {
        "calories_target": 1500,
        "protein_target": 90,
        "fat_target": 50,
        "carbs_target": 180,
        "fiber_target": 25,
        "sodium_target": 2000,
        "preferences": ["vietnamese"],
        "allergies": [],
        "cuisine_style": "vietnamese",
        "use_ai": False  # Use fallback data first
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/meal-plan/generate",
            json=test_data,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Meal generation successful!")
            
            # Check if we have weekly_plan
            if "weekly_plan" in data:
                weekly_plan = data["weekly_plan"]
                print(f"📊 Generated plan for {len(weekly_plan)} days")
                
                # Check first day
                first_day = list(weekly_plan.keys())[0]
                first_day_meals = weekly_plan[first_day]
                
                print(f"\n📅 Sample day ({first_day}):")
                for meal_type in ["breakfast", "lunch", "dinner"]:
                    if meal_type in first_day_meals:
                        meals = first_day_meals[meal_type]
                        print(f"  🍽️ {meal_type}: {len(meals)} meals")
                        
                        if meals:
                            first_meal = meals[0]
                            print(f"    📝 Sample meal: {first_meal.get('name', 'Unknown')}")
                            
                            # Check required fields
                            required_fields = ['name', 'description', 'ingredients', 'preparation', 'nutrition', 'preparation_time', 'health_benefits']
                            missing_fields = [field for field in required_fields if field not in first_meal]
                            
                            if not missing_fields:
                                print(f"    ✅ All required fields present")
                                print(f"    ⏰ Time: {first_meal.get('preparation_time')}")
                                print(f"    💊 Benefits: {first_meal.get('health_benefits', '')[:50]}...")
                                print(f"    🍳 Steps: {len(first_meal.get('preparation', []))} steps")
                            else:
                                print(f"    ❌ Missing fields: {missing_fields}")
                
                return True
            else:
                print("❌ No weekly_plan in response")
                print(f"Response keys: {list(data.keys())}")
                return False
                
        elif response.status_code == 401:
            print("❌ Authentication required")
            return False
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_groq_service_directly():
    """Test Groq service directly"""
    print("\n🤖 Testing Groq service directly...")
    
    try:
        # Import and test groq service
        import sys
        sys.path.append('.')
        
        from groq_integration import groq_service
        
        print(f"Groq available: {groq_service.available}")
        print(f"Quota exceeded: {groq_service.quota_exceeded}")
        
        if groq_service.available:
            print("✅ Groq service is available")
            
            # Test with fallback data
            print("🔧 Testing with fallback data...")
            fallback_meals = groq_service.generate_meal_suggestions(
                calories_target=400,
                protein_target=25,
                fat_target=15,
                carbs_target=45,
                meal_type="bữa sáng",
                use_ai=False  # Force fallback
            )
            
            if fallback_meals:
                print(f"✅ Got {len(fallback_meals)} fallback meals")
                first_meal = fallback_meals[0]
                
                # Check required fields
                required_fields = ['name', 'description', 'ingredients', 'preparation', 'nutrition', 'preparation_time', 'health_benefits']
                missing_fields = [field for field in required_fields if field not in first_meal]
                
                if not missing_fields:
                    print(f"✅ All required fields present in fallback meal")
                    print(f"   Name: {first_meal['name']}")
                    print(f"   Time: {first_meal['preparation_time']}")
                    print(f"   Benefits: {first_meal['health_benefits'][:50]}...")
                else:
                    print(f"❌ Missing fields in fallback meal: {missing_fields}")
                
                return True
            else:
                print("❌ No fallback meals generated")
                return False
        else:
            print("❌ Groq service not available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Groq service: {e}")
        return False

def main():
    """Run simple tests"""
    print("🚀 Starting Simple Meal Planning Tests")
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Health check
    results.append(test_health_check())
    
    # Test 2: Groq service directly
    results.append(test_groq_service_directly())
    
    # Test 3: Meal generation
    results.append(test_meal_generation_without_auth())
    
    # Summary
    print("\n" + "="*50)
    print("📊 Test Summary")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
