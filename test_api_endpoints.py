import requests
import json
from pprint import pprint

# Base URL for local testing
BASE_URL = "http://localhost:8000"

def test_meal_plan_generate():
    """Test the meal plan generation endpoint"""
    print("Testing /api/meal-plan/generate...")
    
    # Parameters for the request
    params = {
        "calories": 2000,
        "protein": 100,
        "fat": 70,
        "carbs": 250,
        "user_id": "test_user",
        "use_ai": False
    }
    
    # Make the request
    try:
        response = requests.get(f"{BASE_URL}/api/meal-plan/generate", params=params)
        
        # Check status code
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: Meal plan generation endpoint is working!")
            # Print a sample of the response
            data = response.json()
            print(f"Message: {data.get('message', 'No message')}")
            days = data.get('meal_plan', {}).get('days', [])
            print(f"Generated meal plan with {len(days)} days")
        else:
            print(f"ERROR: Failed to generate meal plan. Response: {response.text}")
    except Exception as e:
        print(f"ERROR: Exception when testing meal plan generation: {str(e)}")

def test_user_profile():
    """Test the user profile endpoint"""
    print("\nTesting /api/user-profile...")
    
    # Sample user profile data
    user_data = {
        "name": "Test User",
        "email": "test@example.com",
        "age": 30,
        "weight": 70.5,
        "height": 175.0,
        "targetCalories": 2000,
        "gender": "male",
        "activity_level": "medium",
        "goal": "maintain",
        "dietType": "omnivore",
        "preferred_cuisines": ["Vietnamese", "Italian"],
        "allergies": ["peanuts"]
    }
    
    # Make the request
    try:
        response = requests.post(
            f"{BASE_URL}/api/user-profile", 
            json=user_data,
            params={"user_id": "test_user"}
        )
        
        # Check status code
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: User profile endpoint is working!")
            data = response.json()
            print(f"Response: {data}")
        else:
            print(f"ERROR: Failed to create/update user profile. Response: {response.text}")
    except Exception as e:
        print(f"ERROR: Exception when testing user profile: {str(e)}")

def test_get_user_meal_plan():
    """Test the get user meal plan endpoint"""
    print("\nTesting /api/meal-plan/{user_id}...")
    
    # User ID to test with
    user_id = "test_user"  # Use a user that should have a meal plan
    
    # Make the request
    try:
        response = requests.get(f"{BASE_URL}/api/meal-plan/{user_id}")
        
        # Check status code
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("SUCCESS: Get user meal plan endpoint is working!")
            data = response.json()
            if "meal_plan" in data:
                print("Meal plan found in response")
            else:
                print("No meal plan found in response")
        elif response.status_code == 404:
            print(f"No meal plan found for user {user_id}")
        else:
            print(f"ERROR: Failed to get meal plan. Response: {response.text}")
    except Exception as e:
        print(f"ERROR: Exception when testing get user meal plan: {str(e)}")

if __name__ == "__main__":
    # Run the tests
    test_meal_plan_generate()
    test_user_profile()
    test_get_user_meal_plan()
    
    print("\nAll tests completed!") 