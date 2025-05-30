import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Server URL
SERVER_URL = "http://localhost:8000"

def test_replace_meal():
    """Test replacing a meal with AI"""
    
    # Endpoint URL
    url = f"{SERVER_URL}/api/meal-plan/replace-meal"
    
    # Request data
    data = {
        "user_id": "test_user",
        "day_of_week": "Thứ 2",
        "meal_type": "Bữa sáng",
        "calories_target": 500,
        "protein_target": 30,
        "fat_target": 20,
        "carbs_target": 50,
        "use_ai": True  # Đảm bảo use_ai=True
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    # Send request
    print(f"Sending request to {url}")
    print(f"Request data: {json.dumps(data, indent=2)}")
    
    response = requests.post(url, json=data, headers=headers)
    
    # Print response
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        response_data = response.json()
        print(f"Response data: {json.dumps(response_data, indent=2)}")
        
        # Check if the response contains AI-generated meals
        meal = response_data.get("meal", {})
        dishes = meal.get("dishes", [])
        
        print(f"Number of dishes: {len(dishes)}")
        
        if dishes:
            for i, dish in enumerate(dishes):
                print(f"\nDish {i+1}: {dish.get('name', 'N/A')}")
                print(f"Ingredients: {len(dish.get('ingredients', []))} items")
                print(f"Preparation: {dish.get('preparation', 'N/A')[:50]}...")
                print(f"Nutrition: {dish.get('nutrition', {})}")
    else:
        print(f"Error response: {response.text}")

if __name__ == "__main__":
    test_replace_meal() 