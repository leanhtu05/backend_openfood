#!/usr/bin/env python3
"""
Test Groq Integration trực tiếp trên Production Environment
Kiểm tra và debug các vấn đề khác biệt giữa local và Render
"""

import requests
import json
import time
import os
from datetime import datetime

class ProductionGroqTester:
    """Test Groq integration trên production"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 60  # Tăng timeout cho production
        
    def test_meal_generation_endpoint(self):
        """Test endpoint meal generation trực tiếp"""
        print("\n🍽️ TESTING MEAL GENERATION ON PRODUCTION")
        print("=" * 60)
        
        test_cases = [
            {
                "name": "Simple breakfast with AI=False",
                "data": {
                    "user_id": "production_test_user",
                    "calories_target": 400,
                    "protein_target": 25,
                    "fat_target": 15,
                    "carbs_target": 50,
                    "use_ai": False  # Test fallback first
                }
            },
            {
                "name": "Simple breakfast with AI=True",
                "data": {
                    "user_id": "production_test_user",
                    "calories_target": 400,
                    "protein_target": 25,
                    "fat_target": 15,
                    "carbs_target": 50,
                    "use_ai": True  # Test Groq integration
                }
            },
            {
                "name": "Lunch with preferences",
                "data": {
                    "user_id": "production_test_user",
                    "calories_target": 600,
                    "protein_target": 35,
                    "fat_target": 20,
                    "carbs_target": 70,
                    "use_ai": True,
                    "preferences": ["healthy", "vietnamese"],
                    "diet_preference": "balanced"
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}: {test_case['name']}")
            print("-" * 40)
            
            try:
                start_time = time.time()
                
                response = self.session.post(
                    f"{self.base_url}/api/meal-plan/generate",
                    json=test_case["data"],
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "ProductionGroqTester/1.0"
                    }
                )
                
                duration = time.time() - start_time
                
                print(f"⏱️ Response time: {duration:.2f}s")
                print(f"📊 Status code: {response.status_code}")
                print(f"📏 Response size: {len(response.text)} bytes")
                
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
                                        
                                        # Check if meals have proper structure
                                        for meal in meals:
                                            if "name" not in meal:
                                                print(f"⚠️ Missing 'name' in meal: {meal}")
                                            if "nutrition" not in meal:
                                                print(f"⚠️ Missing 'nutrition' in meal: {meal.get('name', 'Unknown')}")
                            
                            print(f"📈 Generated {total_meals} total meals")
                            print(f"📅 Days in plan: {list(weekly_plan.keys())}")
                            
                            # Show first meal as example
                            if total_meals > 0:
                                first_day = list(weekly_plan.keys())[0]
                                first_meal_type = list(weekly_plan[first_day]["meals"].keys())[0]
                                first_meal = weekly_plan[first_day]["meals"][first_meal_type][0]
                                print(f"🍽️ Example meal: {first_meal.get('name', 'No name')}")
                                
                                if "nutrition" in first_meal:
                                    nutrition = first_meal["nutrition"]
                                    print(f"   Calories: {nutrition.get('calories', 'N/A')}")
                                    print(f"   Protein: {nutrition.get('protein', 'N/A')}g")
                        else:
                            print("❌ No 'weekly_plan' in response")
                            print(f"Response keys: {list(data.keys())}")
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parsing failed: {e}")
                        print(f"Raw response (first 500 chars): {response.text[:500]}")
                        
                elif response.status_code == 403:
                    print("❌ 403 Forbidden - Authentication issue")
                    print("Headers:", dict(response.headers))
                    
                elif response.status_code == 500:
                    print("❌ 500 Internal Server Error")
                    print(f"Error response: {response.text[:500]}")
                    
                else:
                    print(f"❌ Unexpected status code: {response.status_code}")
                    print(f"Response: {response.text[:500]}")
                    
            except requests.exceptions.Timeout:
                print("❌ Request timeout")
                
            except requests.exceptions.ConnectionError:
                print("❌ Connection error")
                
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                
            print()
    
    def test_groq_specific_endpoint(self):
        """Test endpoint cụ thể cho Groq nếu có"""
        print("\n🤖 TESTING GROQ-SPECIFIC FUNCTIONALITY")
        print("=" * 50)
        
        # Test với data đơn giản để isolate Groq issues
        simple_data = {
            "user_id": "groq_test_user",
            "calories_target": 300,
            "protein_target": 20,
            "fat_target": 10,
            "carbs_target": 40,
            "use_ai": True,
            "meal_type": "bữa sáng"
        }
        
        try:
            print("📤 Sending simple Groq test request...")
            
            response = self.session.post(
                f"{self.base_url}/api/meal-plan/generate",
                json=simple_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Look for signs of Groq vs fallback
                if "weekly_plan" in data:
                    # Check if meals look AI-generated vs fallback
                    weekly_plan = data["weekly_plan"]
                    
                    for day, day_data in weekly_plan.items():
                        if "meals" in day_data:
                            for meal_type, meals in day_data["meals"].items():
                                for meal in meals:
                                    meal_name = meal.get("name", "")
                                    description = meal.get("description", "")
                                    
                                    # Check for signs of AI generation
                                    if "AI-generated" in description or "fallback" in description.lower():
                                        print(f"🔄 Detected fallback meal: {meal_name}")
                                    else:
                                        print(f"🤖 Potential AI meal: {meal_name}")
                                        
                                    # Check for Groq-specific patterns
                                    if len(description) > 50 and "Việt Nam" in description:
                                        print(f"✅ Rich description suggests AI: {description[:100]}...")
                                    elif len(description) < 30:
                                        print(f"⚠️ Short description suggests fallback: {description}")
                                        
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(f"Response: {response.text[:300]}")
                
        except Exception as e:
            print(f"❌ Error testing Groq functionality: {e}")
    
    def test_environment_differences(self):
        """Test các khác biệt environment có thể gây lỗi"""
        print("\n🔍 TESTING ENVIRONMENT DIFFERENCES")
        print("=" * 45)
        
        # Test 1: Check server info
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ Server is responding")
                
                # Check response headers for environment info
                headers = response.headers
                print(f"Server: {headers.get('server', 'Unknown')}")
                print(f"Content-Type: {headers.get('content-type', 'Unknown')}")
                
                if 'x-render-origin-server' in headers:
                    print("🏭 Confirmed running on Render")
                    
            else:
                print(f"⚠️ Server responded with {response.status_code}")
                
        except Exception as e:
            print(f"❌ Cannot reach server: {e}")
        
        # Test 2: Check if environment variables are available
        print("\n🔧 Environment Check:")
        test_data = {
            "user_id": "env_test",
            "calories_target": 200,
            "protein_target": 10,
            "fat_target": 5,
            "carbs_target": 30,
            "use_ai": True
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/meal-plan/generate",
                json=test_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 500:
                error_text = response.text.lower()
                
                if "groq" in error_text:
                    print("❌ Groq-related error detected")
                if "api key" in error_text or "authentication" in error_text:
                    print("❌ API key issue detected")
                if "module" in error_text or "import" in error_text:
                    print("❌ Module import issue detected")
                if "timeout" in error_text:
                    print("❌ Timeout issue detected")
                    
                print(f"Error details: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Environment test failed: {e}")
    
    def run_comprehensive_test(self):
        """Chạy tất cả tests"""
        print("🚀 PRODUCTION GROQ INTEGRATION TEST")
        print("=" * 70)
        print(f"Target URL: {self.base_url}")
        print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Run all tests
        self.test_environment_differences()
        self.test_meal_generation_endpoint()
        self.test_groq_specific_endpoint()
        
        print("\n" + "=" * 70)
        print("📋 PRODUCTION TEST COMPLETED")
        print("=" * 70)
        print("\n💡 DEBUGGING TIPS:")
        print("1. Check Render logs for detailed error messages")
        print("2. Verify GROQ_API_KEY environment variable is set")
        print("3. Check if all Python dependencies are installed")
        print("4. Verify network connectivity to Groq API from Render")
        print("5. Check for memory/CPU limits on Render")


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Production Groq Integration Tester")
    parser.add_argument("url", help="Production URL to test (e.g., https://your-app.onrender.com)")
    
    args = parser.parse_args()
    
    tester = ProductionGroqTester(args.url)
    tester.run_comprehensive_test()


if __name__ == "__main__":
    main()
