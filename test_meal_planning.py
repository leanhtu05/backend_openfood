#!/usr/bin/env python3
"""
Test script for meal planning functionality
Tests all endpoints and validates required fields
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_123"

# Test authentication token (you'll need to replace this with a real token)
TEST_TOKEN = "your_test_token_here"

HEADERS = {
    "Authorization": f"Bearer {TEST_TOKEN}",
    "Content-Type": "application/json"
}

def print_separator(title):
    """Print a nice separator for test sections"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_result(success, message):
    """Print test result with emoji"""
    emoji = "✅" if success else "❌"
    print(f"{emoji} {message}")

def validate_meal_fields(meal_data):
    """Validate that meal has all required fields"""
    required_fields = [
        'name', 'description', 'ingredients', 'preparation', 
        'nutrition', 'preparation_time', 'health_benefits'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in meal_data:
            missing_fields.append(field)
    
    return len(missing_fields) == 0, missing_fields

def test_meal_plan_generation():
    """Test meal plan generation endpoint"""
    print_separator("Testing Meal Plan Generation")
    
    # Test data
    test_data = {
        "calories_target": 2000,
        "protein_target": 120,
        "fat_target": 65,
        "carbs_target": 250,
        "fiber_target": 25,
        "sodium_target": 2000,
        "preferences": ["healthy", "vietnamese"],
        "allergies": [],
        "cuisine_style": "vietnamese",
        "use_ai": True
    }
    
    try:
        print("📤 Sending request to /api/meal-plan/generate...")
        response = requests.post(
            f"{BASE_URL}/api/meal-plan/generate",
            json=test_data,
            headers=HEADERS,
            timeout=60
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Meal plan generation successful")
            
            # Validate response structure
            if "weekly_plan" in data:
                weekly_plan = data["weekly_plan"]
                print(f"📊 Generated plan for {len(weekly_plan)} days")
                
                # Check each day
                total_meals = 0
                valid_meals = 0
                
                for day, meals in weekly_plan.items():
                    print(f"\n📅 Day: {day}")
                    
                    for meal_type in ["breakfast", "lunch", "dinner"]:
                        if meal_type in meals:
                            meal_list = meals[meal_type]
                            print(f"  🍽️ {meal_type}: {len(meal_list)} meals")
                            
                            for i, meal in enumerate(meal_list):
                                total_meals += 1
                                is_valid, missing = validate_meal_fields(meal)
                                
                                if is_valid:
                                    valid_meals += 1
                                    print(f"    ✅ Meal {i+1}: {meal['name']}")
                                    print(f"       ⏰ Time: {meal['preparation_time']}")
                                    print(f"       💊 Benefits: {meal['health_benefits'][:50]}...")
                                    print(f"       🍳 Steps: {len(meal['preparation'])} steps")
                                else:
                                    print(f"    ❌ Meal {i+1}: Missing fields {missing}")
                
                print(f"\n📈 Summary: {valid_meals}/{total_meals} meals are valid")
                print_result(valid_meals == total_meals, f"All meals have required fields")
                
            else:
                print_result(False, "Response missing 'weekly_plan' field")
                
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")

def test_get_meal_plan():
    """Test getting existing meal plan"""
    print_separator("Testing Get Meal Plan")
    
    try:
        print("📤 Sending request to /api/meal-plan/default...")
        response = requests.get(
            f"{BASE_URL}/api/meal-plan/default",
            headers=HEADERS,
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Get meal plan successful")
            
            if "meal_plan" in data:
                meal_plan = data["meal_plan"]
                if "weekly_plan" in meal_plan:
                    print(f"📊 Retrieved plan with {len(meal_plan['weekly_plan'])} days")
                else:
                    print("📊 Retrieved meal plan (different format)")
            else:
                print_result(False, "Response missing 'meal_plan' field")
                
        elif response.status_code == 404:
            print_result(True, "No existing meal plan found (expected for new user)")
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")

def test_replace_day():
    """Test replacing a day in meal plan"""
    print_separator("Testing Replace Day")
    
    test_data = {
        "day_of_week": "monday",
        "calories_target": 2000,
        "protein_target": 120,
        "fat_target": 65,
        "carbs_target": 250
    }
    
    try:
        print("📤 Sending request to /api/replace-day...")
        response = requests.post(
            f"{BASE_URL}/api/replace-day",
            json=test_data,
            headers=HEADERS,
            timeout=60
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Replace day successful")
            
            if "day_meal_plan" in data:
                day_plan = data["day_meal_plan"]
                print(f"📊 Replaced day plan for {day_plan.get('day_of_week', 'unknown')}")
                
                # Validate meals in the day
                total_meals = 0
                valid_meals = 0
                
                for meal_type in ["breakfast", "lunch", "dinner"]:
                    if meal_type in day_plan:
                        meals = day_plan[meal_type].get("dishes", [])
                        for meal in meals:
                            total_meals += 1
                            is_valid, missing = validate_meal_fields(meal)
                            if is_valid:
                                valid_meals += 1
                
                print_result(valid_meals == total_meals, f"Day meals valid: {valid_meals}/{total_meals}")
            else:
                print_result(False, "Response missing 'day_meal_plan' field")
                
        elif response.status_code == 404:
            print_result(False, "No existing meal plan to replace (need to generate first)")
        else:
            print_result(False, f"Request failed with status {response.status_code}")
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")

def test_health_check():
    """Test API health check"""
    print_separator("Testing API Health Check")
    
    try:
        print("📤 Sending request to /health...")
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_result(True, "Health check successful")
            print(f"📊 Status: {data.get('status', 'unknown')}")
            print(f"🤖 AI Available: {data.get('ai_available', False)}")
        else:
            print_result(False, f"Health check failed with status {response.status_code}")
            
    except Exception as e:
        print_result(False, f"Exception occurred: {str(e)}")

def main():
    """Run all tests"""
    print("🚀 Starting Meal Planning Tests")
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests in order
    test_health_check()
    test_meal_plan_generation()
    test_get_meal_plan()
    test_replace_day()
    
    print_separator("Test Summary")
    print("🏁 All tests completed!")
    print("\n📝 Notes:")
    print("- If authentication fails, update TEST_TOKEN with a valid JWT token")
    print("- Make sure the backend server is running on localhost:8000")
    print("- Some tests may fail if no meal plan exists yet")

if __name__ == "__main__":
    main()
