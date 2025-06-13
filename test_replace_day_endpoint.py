#!/usr/bin/env python3
"""
Test script cho endpoint /api/replace-day để kiểm tra hệ thống Groq cải tiến
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Thay đổi nếu server chạy ở port khác
ENDPOINT = "/api/replace-day"

def print_separator(title):
    """In separator với title"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_subsection(title):
    """In subsection header"""
    print(f"\n--- {title} ---")

def test_replace_day_endpoint():
    """Test endpoint /api/replace-day với các scenario khác nhau"""
    print_separator("🧪 TESTING /api/replace-day ENDPOINT")
    
    # Test cases
    test_cases = [
        {
            "name": "Thay thế Thứ 2 - Giảm cân",
            "payload": {
                "user_id": "test_user_001",
                "day_of_week": "Thứ 2",
                "calories_target": 1200,
                "protein_target": 80,
                "fat_target": 40,
                "carbs_target": 120,
                "preferences": ["healthy", "low-calorie", "vietnamese"],
                "allergies": [],
                "cuisine_style": "Vietnamese",
                "use_ai": True
            }
        },
        {
            "name": "Thay thế Thứ 4 - Tăng cân",
            "payload": {
                "user_id": "test_user_002", 
                "day_of_week": "Thứ 4",
                "calories_target": 2200,
                "protein_target": 120,
                "fat_target": 80,
                "carbs_target": 250,
                "preferences": ["high-protein", "nutritious", "vietnamese"],
                "allergies": ["seafood"],
                "cuisine_style": "Vietnamese",
                "use_ai": True
            }
        },
        {
            "name": "Thay thế Chủ nhật - Cân bằng",
            "payload": {
                "user_id": "test_user_003",
                "day_of_week": "Chủ nhật", 
                "calories_target": 1800,
                "protein_target": 100,
                "fat_target": 60,
                "carbs_target": 180,
                "preferences": ["balanced", "vietnamese"],
                "allergies": ["nuts", "dairy"],
                "cuisine_style": "Vietnamese",
                "use_ai": True
            }
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print_subsection(f"Test Case {i}: {test_case['name']}")
        
        try:
            payload = test_case['payload']
            print(f"📋 Request Payload:")
            print(f"   User ID: {payload['user_id']}")
            print(f"   Day: {payload['day_of_week']}")
            print(f"   Calories: {payload['calories_target']}kcal")
            print(f"   Protein: {payload['protein_target']}g")
            print(f"   Fat: {payload['fat_target']}g")
            print(f"   Carbs: {payload['carbs_target']}g")
            print(f"   Preferences: {payload['preferences']}")
            print(f"   Allergies: {payload['allergies']}")
            print(f"   Use AI: {payload['use_ai']}")
            
            print(f"\n🚀 Sending request to {BASE_URL}{ENDPOINT}...")
            
            # Gửi request
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}{ENDPOINT}",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120  # 2 phút timeout
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"⏱️ Response time: {response_time:.2f} seconds")
            
            if response.status_code == 200:
                print(f"✅ SUCCESS: Status {response.status_code}")
                
                try:
                    response_data = response.json()
                    
                    # Validate response structure
                    validation_result = validate_response_structure(response_data)
                    
                    results.append({
                        "test_case": test_case['name'],
                        "status": "SUCCESS",
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "validation": validation_result,
                        "response_data": response_data
                    })
                    
                    # In chi tiết response
                    print(f"\n📊 Response Summary:")
                    print(f"   Message: {response_data.get('message', 'N/A')}")
                    print(f"   User ID: {response_data.get('user_id', 'N/A')}")
                    print(f"   Day: {response_data.get('day_of_week', 'N/A')}")
                    print(f"   Success: {response_data.get('success', False)}")
                    
                    # Kiểm tra meal plan data
                    if 'day_plan' in response_data:
                        day_plan = response_data['day_plan']
                        print(f"\n🍽️ Day Plan Details:")
                        print(f"   Day Index: {day_plan.get('day_index', 'N/A')}")
                        print(f"   Day Name: {day_plan.get('day_name', 'N/A')}")
                        
                        # Kiểm tra từng bữa ăn
                        meals = ['breakfast', 'lunch', 'dinner', 'snack']
                        for meal in meals:
                            if meal in day_plan:
                                meal_data = day_plan[meal]
                                dishes = meal_data.get('dishes', [])
                                print(f"   {meal.capitalize()}: {len(dishes)} dishes")
                                
                                for j, dish in enumerate(dishes, 1):
                                    print(f"     {j}. {dish.get('name', 'Unknown')}")
                                    nutrition = dish.get('nutrition', {})
                                    print(f"        Nutrition: {nutrition.get('calories', 0)}kcal, "
                                          f"{nutrition.get('protein', 0)}g protein")
                    
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response")
                    results.append({
                        "test_case": test_case['name'],
                        "status": "INVALID_JSON",
                        "status_code": response.status_code,
                        "response_time": response_time,
                        "raw_response": response.text[:500]
                    })
                    
            else:
                print(f"❌ FAILED: Status {response.status_code}")
                print(f"Response: {response.text[:500]}")
                results.append({
                    "test_case": test_case['name'],
                    "status": "HTTP_ERROR",
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "error_message": response.text[:500]
                })
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: Request took longer than 120 seconds")
            results.append({
                "test_case": test_case['name'],
                "status": "TIMEOUT",
                "error": "Request timeout after 120 seconds"
            })
            
        except requests.exceptions.ConnectionError:
            print(f"🔌 CONNECTION ERROR: Cannot connect to server")
            results.append({
                "test_case": test_case['name'],
                "status": "CONNECTION_ERROR",
                "error": "Cannot connect to server"
            })
            
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            results.append({
                "test_case": test_case['name'],
                "status": "ERROR",
                "error": str(e)
            })
    
    return results

def validate_response_structure(response_data):
    """Validate cấu trúc response"""
    validation = {
        "has_message": "message" in response_data,
        "has_success": "success" in response_data,
        "has_day_plan": "day_plan" in response_data,
        "is_valid": True,
        "missing_fields": []
    }
    
    required_fields = ["message", "success", "user_id", "day_of_week"]
    for field in required_fields:
        if field not in response_data:
            validation["missing_fields"].append(field)
            validation["is_valid"] = False
    
    # Validate day_plan structure if exists
    if "day_plan" in response_data:
        day_plan = response_data["day_plan"]
        if not isinstance(day_plan, dict):
            validation["is_valid"] = False
            validation["missing_fields"].append("day_plan (should be dict)")
        else:
            # Check meals
            meals = ['breakfast', 'lunch', 'dinner']
            for meal in meals:
                if meal not in day_plan:
                    validation["missing_fields"].append(f"day_plan.{meal}")
                    validation["is_valid"] = False
                elif "dishes" not in day_plan[meal]:
                    validation["missing_fields"].append(f"day_plan.{meal}.dishes")
                    validation["is_valid"] = False
    
    return validation

def print_test_summary(results):
    """In tóm tắt kết quả test"""
    print_separator("📊 TEST SUMMARY")
    
    total_tests = len(results)
    successful_tests = len([r for r in results if r["status"] == "SUCCESS"])
    failed_tests = total_tests - successful_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Successful: {successful_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests > 0:
        successful_results = [r for r in results if r["status"] == "SUCCESS"]
        avg_response_time = sum(r["response_time"] for r in successful_results) / len(successful_results)
        print(f"⏱️ Average Response Time: {avg_response_time:.2f} seconds")
    
    print_subsection("Detailed Results")
    
    for result in results:
        status_emoji = {
            "SUCCESS": "✅", 
            "HTTP_ERROR": "❌", 
            "TIMEOUT": "⏰",
            "CONNECTION_ERROR": "🔌",
            "INVALID_JSON": "📄",
            "ERROR": "💥"
        }.get(result["status"], "❓")
        
        print(f"{status_emoji} {result['test_case']}: {result['status']}")
        
        if result["status"] == "SUCCESS":
            print(f"   ⏱️ Response time: {result['response_time']:.2f}s")
            validation = result["validation"]
            if validation["is_valid"]:
                print(f"   ✅ Response structure valid")
            else:
                print(f"   ⚠️ Missing fields: {validation['missing_fields']}")
        else:
            error_msg = result.get('error', result.get('error_message', 'Unknown error'))
            print(f"   💥 Error: {error_msg}")

def save_test_results(results):
    """Lưu kết quả test vào file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"replace_day_test_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Test results saved to: {filename}")

def main():
    """Main function"""
    print("🚀 Starting /api/replace-day Endpoint Test")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Target URL: {BASE_URL}{ENDPOINT}")
    
    try:
        # Run tests
        results = test_replace_day_endpoint()
        
        # Print summary
        print_test_summary(results)
        
        # Save results
        save_test_results(results)
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Test finished!")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
