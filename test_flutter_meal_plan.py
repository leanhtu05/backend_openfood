import requests
import json
import firebase_admin
from firebase_admin import auth, credentials, firestore

# Constants
BASE_URL = "http://localhost:8000"
USER_ID = "49DhdmJHFAY40eEgaPNEJqGdDQK2"

# Get Firebase token for authentication
def get_firebase_token():
    try:
        # Initialize Firebase Admin SDK if not already initialized
        try:
            app = firebase_admin.get_app()
        except ValueError:
            cred = credentials.Certificate("firebase-credentials.json")
            firebase_admin.initialize_app(cred)
        
        # Create a custom token
        custom_token = auth.create_custom_token(USER_ID)
        
        print(f"✅ Created custom token for user: {USER_ID}")
        return custom_token.decode('utf-8')
    except Exception as e:
        print(f"❌ Error getting Firebase token: {str(e)}")
        return None

# Generate a meal plan
def generate_meal_plan():
    try:
        # Get Firebase token
        token = get_firebase_token()
        if not token:
            print("❌ Could not get Firebase token")
            return False
        
        # Set up headers with Firebase token
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        # Set up request data
        data = {
            "calories_target": 2172,
            "protein_target": 163,
            "fat_target": 72,
            "carbs_target": 217,
            "user_id": USER_ID,
            "use_ai": True
        }
        
        # Make API request to generate meal plan
        url = f"{BASE_URL}/api/meal-plan/generate"
        print(f"🔄 Generating meal plan from API: {url}")
        print(f"📦 Request data: {json.dumps(data)}")
        
        response = requests.post(url, json=data, headers=headers)
        
        # Print response details
        print(f"🔍 Response status: {response.status_code}")
        print(f"🔍 Response headers: {response.headers}")
        
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
        # Get Firebase token
        token = get_firebase_token()
        if not token:
            print("❌ Could not get Firebase token")
            return False
        
        # Set up headers with Firebase token
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        # Set up request data
        data = {
            "user_id": USER_ID,
            "day_of_week": "Thứ 7",
            "meal_type": "breakfast",  # Use English meal type as expected by API
            "calories_target": 2172.3,
            "protein_target": 162.9,
            "fat_target": 72.4,
            "carbs_target": 217.2,
            "use_ai": True
        }
        
        # Make API request to replace meal
        url = f"{BASE_URL}/api/meal-plan/replace-meal"
        print(f"🔄 Replacing meal from API: {url}")
        print(f"📦 Request data: {json.dumps(data)}")
        
        response = requests.post(url, json=data, headers=headers)
        
        # Print response details
        print(f"🔍 Response status: {response.status_code}")
        print(f"🔍 Response headers: {response.headers}")
        
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
    print("=== Testing Flutter Meal Plan Integration ===")
    
    # First generate a meal plan
    print("\n=== Step 1: Generate Meal Plan ===")
    if generate_meal_plan():
        # Then try to replace a meal
        print("\n=== Step 2: Replace Meal ===")
        replace_meal()
    else:
        print("❌ Skipping meal replacement as meal plan generation failed") 