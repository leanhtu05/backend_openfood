#!/usr/bin/env python3
"""
Test Groq Integration Fix trên Render
Kiểm tra xem lỗi 're' variable đã được fix chưa
"""

import requests
import json
import time
from datetime import datetime

def test_groq_meal_generation(base_url: str):
    """Test meal generation với Groq trên production"""
    print("🧪 TESTING GROQ MEAL GENERATION ON RENDER")
    print("=" * 60)
    print(f"Target URL: {base_url}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test cases với các kịch bản khác nhau
    test_cases = [
        {
            "name": "Simple breakfast test",
            "data": {
                "user_id": "render_test_user_1",
                "calories_target": 300,
                "protein_target": 20,
                "fat_target": 10,
                "carbs_target": 40,
                "use_ai": True
            },
            "expected_errors": ["cannot access local variable 're'", "regex", "re module"]
        },
        {
            "name": "Lunch with preferences",
            "data": {
                "user_id": "render_test_user_2", 
                "calories_target": 500,
                "protein_target": 30,
                "fat_target": 15,
                "carbs_target": 60,
                "use_ai": True,
                "preferences": ["healthy", "vietnamese"]
            },
            "expected_errors": ["cannot access local variable 're'", "regex", "re module"]
        },
        {
            "name": "Fallback test (AI disabled)",
            "data": {
                "user_id": "render_test_user_3",
                "calories_target": 400,
                "protein_target": 25,
                "fat_target": 12,
                "carbs_target": 50,
                "use_ai": False  # Test fallback
            },
            "expected_errors": []  # Fallback shouldn't have regex issues
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{base_url}/api/meal-plan/generate",
                json=test_case["data"],
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "RenderGroqTester/1.0"
                },
                timeout=120  # Longer timeout for AI processing
            )
            
            duration = time.time() - start_time
            
            print(f"⏱️ Response time: {duration:.2f}s")
            print(f"📊 Status code: {response.status_code}")
            
            test_result = {
                "test_name": test_case["name"],
                "status_code": response.status_code,
                "duration": duration,
                "success": False,
                "error_found": False,
                "error_details": None,
                "meals_generated": 0
            }
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print("✅ JSON parsing successful")
                    
                    # Analyze response structure
                    if "weekly_plan" in data:
                        weekly_plan = data["weekly_plan"]
                        total_meals = 0
                        
                        for day, day_data in weekly_plan.items():
                            if "meals" in day_data:
                                for meal_type, meals in day_data["meals"].items():
                                    total_meals += len(meals)
                        
                        test_result["meals_generated"] = total_meals
                        test_result["success"] = total_meals > 0
                        
                        print(f"📈 Generated {total_meals} total meals")
                        
                        if total_meals > 0:
                            # Show first meal as example
                            first_day = list(weekly_plan.keys())[0]
                            first_meal_type = list(weekly_plan[first_day]["meals"].keys())[0]
                            first_meal = weekly_plan[first_day]["meals"][first_meal_type][0]
                            print(f"🍽️ Example meal: {first_meal.get('name', 'No name')}")
                            
                            # Check if meal looks like AI-generated vs fallback
                            description = first_meal.get('description', '')
                            if len(description) > 50:
                                print("🤖 Rich description suggests AI generation")
                            elif "fallback" in description.lower():
                                print("🔄 Using fallback data")
                            else:
                                print("⚠️ Short description - might be fallback")
                        
                    else:
                        print("❌ No 'weekly_plan' in response")
                        print(f"Response keys: {list(data.keys())}")
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing failed: {e}")
                    test_result["error_found"] = True
                    test_result["error_details"] = f"JSON decode error: {str(e)}"
                    
            elif response.status_code == 500:
                print("❌ 500 Internal Server Error")
                error_text = response.text.lower()
                
                # Check for specific regex-related errors
                regex_errors_found = []
                for expected_error in test_case["expected_errors"]:
                    if expected_error.lower() in error_text:
                        regex_errors_found.append(expected_error)
                
                if regex_errors_found:
                    print(f"🔍 REGEX ERRORS DETECTED: {regex_errors_found}")
                    test_result["error_found"] = True
                    test_result["error_details"] = f"Regex errors: {regex_errors_found}"
                else:
                    print("✅ No regex-related errors found in 500 response")
                
                # Show error details
                print(f"Error response (first 300 chars): {response.text[:300]}")
                
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
                test_result["error_details"] = f"Unexpected status: {response.status_code}"
                
            results.append(test_result)
            
        except requests.exceptions.Timeout:
            print("❌ Request timeout")
            test_result = {
                "test_name": test_case["name"],
                "status_code": 0,
                "duration": 120,
                "success": False,
                "error_found": True,
                "error_details": "Request timeout",
                "meals_generated": 0
            }
            results.append(test_result)
            
        except requests.exceptions.ConnectionError:
            print("❌ Connection error")
            test_result = {
                "test_name": test_case["name"],
                "status_code": 0,
                "duration": 0,
                "success": False,
                "error_found": True,
                "error_details": "Connection error",
                "meals_generated": 0
            }
            results.append(test_result)
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            test_result = {
                "test_name": test_case["name"],
                "status_code": 0,
                "duration": 0,
                "success": False,
                "error_found": True,
                "error_details": f"Unexpected error: {str(e)}",
                "meals_generated": 0
            }
            results.append(test_result)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r["success"])
    regex_errors = sum(1 for r in results if r["error_found"] and "regex" in str(r["error_details"]).lower())
    
    print(f"Total tests: {total_tests}")
    print(f"Successful tests: {successful_tests}")
    print(f"Regex-related errors: {regex_errors}")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if regex_errors == 0:
        print("✅ NO REGEX ERRORS DETECTED - Fix appears successful!")
    else:
        print("❌ REGEX ERRORS STILL PRESENT - Further investigation needed")
    
    print("\nDetailed results:")
    for result in results:
        status = "✅" if result["success"] else "❌"
        error_indicator = "🔍" if result["error_found"] else ""
        print(f"{status} {error_indicator} {result['test_name']}: {result['status_code']} ({result['duration']:.1f}s) - {result['meals_generated']} meals")
        if result["error_details"]:
            print(f"   Error: {result['error_details']}")
    
    return results

def test_debug_endpoint(base_url: str):
    """Test debug endpoint để kiểm tra Groq integration status"""
    print("\n🔍 TESTING DEBUG ENDPOINT")
    print("=" * 40)
    
    try:
        response = requests.get(f"{base_url}/debug/groq", timeout=30)
        
        if response.status_code == 200:
            debug_info = response.json()
            print("✅ Debug endpoint accessible")
            
            # Check key information
            print(f"Groq API key set: {debug_info.get('groq_api_key_set', 'Unknown')}")
            print(f"Groq import: {debug_info.get('groq_import', 'Unknown')}")
            print(f"Groq client: {debug_info.get('groq_client', 'Unknown')}")
            print(f"Groq API call: {debug_info.get('groq_api_call', 'Unknown')}")
            print(f"Environment: {debug_info.get('environment', 'Unknown')}")
            
            if debug_info.get('groq_service_available'):
                print("✅ GroqService is available")
            else:
                print("❌ GroqService is not available")
                
        else:
            print(f"❌ Debug endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Debug endpoint error: {e}")

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Groq Regex Fix on Render")
    parser.add_argument("url", help="Production URL to test (e.g., https://your-app.onrender.com)")
    
    args = parser.parse_args()
    
    print("🔧 GROQ REGEX FIX VERIFICATION")
    print("=" * 70)
    print("Testing if 'cannot access local variable re' error has been fixed")
    print("=" * 70)
    
    # Test debug endpoint first
    test_debug_endpoint(args.url)
    
    # Test meal generation
    results = test_groq_meal_generation(args.url)
    
    print("\n💡 NEXT STEPS:")
    if any(r["error_found"] and "regex" in str(r["error_details"]).lower() for r in results):
        print("1. Check Render logs for detailed error messages")
        print("2. Verify the updated groq_integration.py was deployed")
        print("3. Consider adding more safe_regex_* function calls")
        print("4. Check if there are other files using 're' module")
    else:
        print("1. ✅ Regex fix appears successful!")
        print("2. Monitor production logs for any remaining issues")
        print("3. Consider this fix ready for production use")

if __name__ == "__main__":
    main()
