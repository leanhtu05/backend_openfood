"""
Test script for AI Price Analysis endpoints
Run this to test all AI endpoints before using in Flutter app
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "POST":
            response = requests.post(url, json=data, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        
        print(f"\n{'='*60}")
        print(f"Testing: {method} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS")
            print(f"Response keys: {list(result.keys())}")
            
            # Print some sample data
            if isinstance(result, dict):
                for key, value in list(result.items())[:3]:  # First 3 items
                    if isinstance(value, (str, int, float)):
                        print(f"  {key}: {value}")
                    elif isinstance(value, list):
                        print(f"  {key}: [{len(value)} items]")
                    elif isinstance(value, dict):
                        print(f"  {key}: {{{len(value)} keys}}")
        else:
            print("❌ FAILED")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"\n{'='*60}")
        print(f"Testing: {method} {endpoint}")
        print(f"❌ CONNECTION ERROR: {e}")

def main():
    """Test all AI Price Analysis endpoints"""
    
    print("🤖 Testing AI Price Analysis Endpoints")
    print(f"Backend URL: {BASE_URL}")
    print(f"Test time: {datetime.now()}")
    
    # Test health check first
    test_endpoint("/ai-price/health")
    
    # Test trend analysis
    trend_data = {
        "category": "🥬 Rau củ quả",
        "days_back": 30
    }
    test_endpoint("/ai-price/analyze-trends", "POST", trend_data)
    
    # Test price prediction
    prediction_data = {
        "food_name": "thịt bò",
        "days_ahead": 7
    }
    test_endpoint("/ai-price/predict-price", "POST", prediction_data)
    
    # Test seasonal analysis
    seasonal_data = {
        "category": "🍎 Trái cây",
        "current_month": datetime.now().month
    }
    test_endpoint("/ai-price/analyze-seasonal", "POST", seasonal_data)
    
    # Test grocery optimization
    grocery_data = {
        "grocery_items": [
            {
                "name": "thịt bò",
                "amount": "1",
                "unit": "kg",
                "category": "🥩 Thịt tươi sống",
                "estimated_cost": 350000,
                "price_per_unit": 350000
            },
            {
                "name": "cà chua",
                "amount": "2",
                "unit": "kg", 
                "category": "🥬 Rau củ quả",
                "estimated_cost": 50000,
                "price_per_unit": 25000
            }
        ],
        "budget_limit": 500000
    }
    test_endpoint("/ai-price/optimize-grocery", "POST", grocery_data)
    
    # Test market insights
    market_data = {
        "region": "TP.HCM",
        "include_trends": True
    }
    test_endpoint("/ai-price/market-insights", "POST", market_data)
    
    # Test GET endpoints
    print(f"\n{'='*60}")
    print("Testing GET endpoints...")
    
    test_endpoint("/ai-price/analyze-trends?category=🥬 Rau củ quả&days_back=30")
    test_endpoint("/ai-price/predict-price?food_name=thịt bò&days_ahead=7")
    test_endpoint("/ai-price/analyze-seasonal?category=🍎 Trái cây")
    test_endpoint("/ai-price/market-insights?region=TP.HCM&include_trends=true")
    
    print(f"\n{'='*60}")
    print("🎉 Testing completed!")
    print("\nIf all endpoints return 200 status, your backend is ready for Flutter integration.")
    print("If you see connection errors, make sure:")
    print("1. Backend server is running (python main.py)")
    print("2. Server is accessible at http://localhost:8000")
    print("3. All dependencies are installed")

if __name__ == "__main__":
    main()
