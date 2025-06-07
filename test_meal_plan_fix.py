import json
import requests
import sys
from pathlib import Path

# Change to the parent directory (main backend directory)
sys.path.append(str(Path(__file__).parent.parent))

# Import the firestore service and models
from services.firestore_service import firestore_service
from models import WeeklyMealPlan

def test_get_meal_plan():
    """Test retrieving a meal plan from Firestore and validating it"""
    print("Testing meal plan retrieval and validation...")
    
    # Test user ID
    user_id = "49DhdmJHFAY40eEgaPNEJqGdDQK2"
    
    # Try to get the meal plan
    meal_plan = firestore_service.get_latest_meal_plan(user_id)
    
    if meal_plan:
        print(f"✅ Successfully retrieved and validated meal plan with {len(meal_plan.days)} days")
        return True
    else:
        print("❌ Failed to retrieve or validate meal plan")
        return False

def test_api_request():
    """Test making an API request to replace a meal"""
    print("\nTesting API request to replace a meal...")
    
    try:
        # Make a request to the local API
        response = requests.post(
            "http://localhost:8000/api/meal-plan/replace-meal",
            json={
                "user_id": "49DhdmJHFAY40eEgaPNEJqGdDQK2",
                "day_of_week": "Thứ 7",
                "meal_type": "Bữa sáng",
                "calories_target": 2468,
                "protein_target": 185,
                "fat_target": 82,
                "carbs_target": 247,
                "use_ai": True
            },
            timeout=5
        )
        
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Error making API request: {str(e)}")
        return False

if __name__ == "__main__":
    # Test getting meal plan from Firestore
    get_plan_result = test_get_meal_plan()
    
    # Test API request
    api_result = test_api_request()
    
    # Print overall results
    print("\nTest Results:")
    print(f"- Get Meal Plan: {'✅ PASS' if get_plan_result else '❌ FAIL'}")
    print(f"- API Request: {'✅ PASS' if api_result else '❌ FAIL'}") 