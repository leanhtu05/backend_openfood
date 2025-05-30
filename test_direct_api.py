import requests
import json

# Constants
BASE_URL = "http://localhost:8000"
USER_ID = "49DhdmJHFAY40eEgaPNEJqGdDQK2"

# Generate a meal plan
def generate_meal_plan():
    try:
        # Set up request data
        data = {
            "calories_target": 2172,
            "protein_target": 163,
            "fat_target": 72,
            "carbs_target": 217,
            "user_id": USER_ID,
            "use_ai": False  # Set to False for faster testing
        }
        
        # Make API request to generate meal plan
        url = f"{BASE_URL}/api/meal-plan/generate"
        print(f"🔄 Generating meal plan from API: {url}")
        print(f"📦 Request data: {json.dumps(data)}")
        
        response = requests.post(url, json=data)
        
        # Print response details
        print(f"🔍 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully generated meal plan")
            response_data = response.json()
            print(f"✅ Response message: {response_data.get('message', '')}")
            return True
        else:
            print(f"❌ Error generating meal plan: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception when generating meal plan: {str(e)}")
        return False

# Replace a meal
def replace_meal():
    try:
        # Set up request data
        data = {
            "user_id": USER_ID,
            "day_of_week": "Thứ 7",
            "meal_type": "Bữa sáng",  # Using Vietnamese meal type to test translation
            "calories_target": 2172.3,
            "protein_target": 162.9,
            "fat_target": 72.4,
            "carbs_target": 217.2,
            "use_ai": False  # Set to False for faster testing
        }
        
        # Make API request to replace meal
        url = f"{BASE_URL}/api/meal-plan/replace-meal"
        print(f"🔄 Replacing meal from API: {url}")
        print(f"📦 Request data: {json.dumps(data)}")
        
        response = requests.post(url, json=data)
        
        # Print response details
        print(f"🔍 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully replaced meal")
            response_data = response.json()
            print(f"✅ Response message: {response_data.get('message', '')}")
            return True
        else:
            print(f"❌ Error replacing meal: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Exception when replacing meal: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== Testing Direct API Integration ===")
    
    # First generate a meal plan
    print("\n=== Step 1: Generate Meal Plan ===")
    if generate_meal_plan():
        # Then try to replace a meal
        print("\n=== Step 2: Replace Meal ===")
        replace_meal()
    else:
        print("❌ Skipping meal replacement as meal plan generation failed") 