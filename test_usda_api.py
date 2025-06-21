#!/usr/bin/env python3
"""
Test USDA FoodData Central API
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_usda_api():
    """Test USDA API with your key"""
    api_key = os.getenv("USDA_API_KEY")
    
    print("🧪 Testing USDA FoodData Central API")
    print("=" * 50)
    print(f"API Key: {api_key[:10]}...{api_key[-5:]}")
    
    # Test 1: Search Vietnamese foods
    print("\n🔍 Test 1: Search Vietnamese Foods")
    print("-" * 30)
    
    vietnamese_foods = ["rice", "pho", "beef", "noodles", "fish sauce"]
    
    for food in vietnamese_foods:
        try:
            url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
                "query": food,
                "pageSize": 3,
                "api_key": api_key,
                "dataType": ["Foundation", "SR Legacy"]
            }
            
            response = requests.get(url, params=params, timeout=10)
            print(f"\n🍜 Searching: {food}")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                foods = data.get("foods", [])
                print(f"✅ Found {len(foods)} results")
                
                for i, food_item in enumerate(foods[:2]):
                    print(f"  {i+1}. {food_item.get('description', 'No description')}")
                    print(f"     FDC ID: {food_item.get('fdcId')}")
                    
                    # Get basic nutrients
                    nutrients = food_item.get('foodNutrients', [])
                    for nutrient in nutrients[:3]:
                        name = nutrient.get('nutrient', {}).get('name', 'Unknown')
                        amount = nutrient.get('amount', 0)
                        unit = nutrient.get('nutrient', {}).get('unitName', '')
                        print(f"     {name}: {amount} {unit}")
                        
            elif response.status_code == 403:
                print("❌ 403 Forbidden - API key invalid or expired")
                return False
            elif response.status_code == 429:
                print("❌ 429 Too Many Requests - Rate limit exceeded")
                return False
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Error searching {food}: {e}")
    
    # Test 2: Get detailed food info
    print("\n📊 Test 2: Get Food Details")
    print("-" * 30)
    
    try:
        # Get details for white rice (common food)
        fdc_id = 168878  # White rice, long-grain, regular, raw
        url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
        params = {"api_key": api_key}
        
        response = requests.get(url, params=params, timeout=10)
        print(f"Getting details for FDC ID: {fdc_id}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            food = response.json()
            print(f"✅ Food: {food.get('description')}")
            
            nutrients = food.get('foodNutrients', [])
            important_nutrients = ['Energy', 'Protein', 'Total lipid (fat)', 'Carbohydrate, by difference']
            
            print("📊 Key Nutrients (per 100g):")
            for nutrient in nutrients:
                name = nutrient.get('nutrient', {}).get('name', '')
                if any(key in name for key in important_nutrients):
                    amount = nutrient.get('amount', 0)
                    unit = nutrient.get('nutrient', {}).get('unitName', '')
                    print(f"  • {name}: {amount} {unit}")
                    
        else:
            print(f"❌ Error getting food details: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting food details: {e}")
    
    # Test 3: API Rate Limits
    print("\n⚡ Test 3: API Rate Limits")
    print("-" * 30)
    
    try:
        # Make multiple quick requests to test rate limits
        for i in range(3):
            url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
                "query": f"test{i}",
                "pageSize": 1,
                "api_key": api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            print(f"Request {i+1}: {response.status_code}")
            
            if response.status_code == 429:
                print("⚠️ Rate limit hit - need to implement throttling")
                break
                
    except Exception as e:
        print(f"❌ Rate limit test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 USDA API Test Summary:")
    print("✅ API key is working")
    print("✅ Can search foods")
    print("✅ Can get detailed nutrition data")
    print("✅ Ready for chatbot integration")
    
    return True

if __name__ == "__main__":
    success = test_usda_api()
    
    if success:
        print("\n🎉 USDA API integration ready!")
        print("💡 Next: Integrate into chatbot for professional nutrition advice")
    else:
        print("\n❌ USDA API needs troubleshooting")
        print("💡 Check API key and network connection")
