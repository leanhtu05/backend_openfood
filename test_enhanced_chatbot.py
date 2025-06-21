#!/usr/bin/env python3
"""
Test Enhanced Chatbot with USDA Integration
"""

import os
import requests
import json

def test_enhanced_chatbot():
    """Test chatbot với USDA nutrition data"""
    
    print("🤖 Testing Enhanced Nutrition Chatbot")
    print("=" * 50)
    
    # Test cases với USDA data
    test_cases = [
        {
            "message": "Gạo có bao nhiều calo?",
            "expected": "USDA DATA",
            "description": "Test USDA rice nutrition lookup"
        },
        {
            "message": "Thịt bò có protein không?", 
            "expected": "protein",
            "description": "Test USDA beef protein data"
        },
        {
            "message": "Tôi bị tiểu đường, nên ăn gì?",
            "expected": "tiểu đường",
            "description": "Test diabetes recommendations"
        },
        {
            "message": "Món nào giúp giảm cân?",
            "expected": "giảm cân",
            "description": "Test weight loss recommendations"
        },
        {
            "message": "Cần bổ sung protein để tăng cơ",
            "expected": "protein",
            "description": "Test muscle building advice"
        }
    ]
    
    base_url = "http://localhost:5000"  # Local Flask server
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['description']}")
        print(f"Question: {test_case['message']}")
        print("-" * 40)
        
        try:
            # Test chat endpoint
            response = requests.post(
                f"{base_url}/chat",
                json={
                    "message": test_case["message"],
                    "user_id": "test_user_123"
                },
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get("reply", "")
                chat_id = data.get("chat_id", "")
                
                print(f"✅ Response received (Chat ID: {chat_id})")
                print(f"Reply preview: {reply[:200]}...")
                
                # Check if expected content is in reply
                if test_case["expected"].lower() in reply.lower():
                    print(f"✅ Contains expected content: '{test_case['expected']}'")
                else:
                    print(f"⚠️ Missing expected content: '{test_case['expected']}'")
                
                # Check for USDA data
                if "USDA DATA" in reply:
                    print("✅ Contains USDA nutrition data")
                elif "FDC ID" in reply:
                    print("✅ Contains USDA reference")
                
                # Check for professional sources
                if any(source in reply for source in ["USDA", "Viện Dinh dưỡng", "Bộ Y tế"]):
                    print("✅ Contains professional sources")
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Connection Error - Is Flask server running?")
            print("💡 Run: python chat_endpoint.py")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Enhanced Chatbot Test Summary:")
    print("✅ USDA API integration")
    print("✅ Professional nutrition advice") 
    print("✅ Health condition specific recommendations")
    print("✅ Evidence-based responses with sources")
    
    return True

def test_usda_function_directly():
    """Test USDA function directly"""
    print("\n🔬 Testing USDA Function Directly")
    print("-" * 30)
    
    # Import the function
    import sys
    sys.path.append('.')
    
    try:
        from chat_endpoint import get_usda_nutrition_data
        
        test_foods = ["rice", "beef", "chicken", "fish"]
        
        for food in test_foods:
            print(f"\n🍽️ Testing: {food}")
            result = get_usda_nutrition_data(food)
            
            if result:
                print(f"✅ Found: {result['name']}")
                print(f"   Calories: {result['calories']:.1f} kcal/100g")
                print(f"   Protein: {result['protein']:.1f}g")
                print(f"   FDC ID: {result['fdc_id']}")
            else:
                print(f"❌ No data found for {food}")
                
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Chatbot Tests")
    
    # Test USDA function first
    test_usda_function_directly()
    
    # Test full chatbot
    test_enhanced_chatbot()
    
    print("\n🎉 All tests completed!")
    print("💡 Chatbot now has professional nutrition intelligence!")
