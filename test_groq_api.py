# -*- coding: utf-8 -*-
"""
Test script để kiểm tra Groq API connection
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_groq_api_connection():
    """Test kết nối Groq API"""
    try:
        from groq import Groq
        from dotenv import load_dotenv
        
        # Load environment variables
        load_dotenv()
        
        print("🔧 Testing Groq API Connection...")
        print("=" * 60)
        
        # Get API key
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("❌ GROQ_API_KEY not found in environment")
            return False
        
        print(f"🔑 API Key: {api_key[:20]}...{api_key[-10:]}")
        
        # Initialize client
        client = Groq(api_key=api_key)
        
        # Test simple request
        print("\n🚀 Testing simple API request...")
        
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Hello, respond with just 'API Working'"
                }
            ],
            model="llama3-8b-8192",
            temperature=0.1,
            max_tokens=10
        )
        
        if response and response.choices:
            content = response.choices[0].message.content
            print(f"✅ API Response: {content}")
            
            if "API Working" in content or "working" in content.lower():
                print("✅ Groq API is working correctly!")
                return True
            else:
                print("⚠️ API responded but content unexpected")
                return False
        else:
            print("❌ No response from API")
            return False
            
    except Exception as e:
        print(f"❌ Groq API test failed: {e}")
        
        # Check specific error types
        error_str = str(e).lower()
        if "403" in error_str or "forbidden" in error_str:
            print("🔍 Error Analysis: 403 Forbidden - API key may be invalid or expired")
        elif "401" in error_str or "unauthorized" in error_str:
            print("🔍 Error Analysis: 401 Unauthorized - API key authentication failed")
        elif "429" in error_str or "rate limit" in error_str:
            print("🔍 Error Analysis: 429 Rate Limited - Too many requests")
        elif "timeout" in error_str:
            print("🔍 Error Analysis: Timeout - Network or server issue")
        else:
            print(f"🔍 Error Analysis: {e}")
        
        return False

def test_groq_meal_generation():
    """Test Groq meal generation specifically"""
    try:
        from groq_integration import groq_service
        
        print("\n🔧 Testing Groq Meal Generation...")
        print("=" * 60)
        
        # Test meal generation
        print("🍽️ Generating test meal...")
        
        meals = groq_service.generate_meal_suggestions(
            calories_target=400,
            protein_target=25,
            fat_target=15,
            carbs_target=50,
            meal_type="bữa sáng",
            preferences=None,
            allergies=None,
            cuisine_style=None
        )
        
        if meals and len(meals) > 0:
            print(f"✅ Successfully generated {len(meals)} meals:")
            for i, meal in enumerate(meals, 1):
                name = meal.get('name', 'Unknown')
                calories = meal.get('nutrition', {}).get('calories', 0)
                source = "AI Generated" if not meal.get('is_fallback', False) else "Fallback"
                print(f"   {i}. {name} ({calories} kcal) - {source}")
            
            # Check if AI generated or fallback
            ai_generated = any(not meal.get('is_fallback', False) for meal in meals)
            
            if ai_generated:
                print("✅ AI generation is working!")
                return True
            else:
                print("⚠️ Only fallback meals generated - AI not working")
                return False
        else:
            print("❌ No meals generated")
            return False
            
    except Exception as e:
        print(f"❌ Meal generation test failed: {e}")
        return False

def test_groq_api_models():
    """Test available Groq models"""
    try:
        from groq import Groq
        from dotenv import load_dotenv
        
        load_dotenv()
        
        print("\n🔧 Testing Available Groq Models...")
        print("=" * 60)
        
        api_key = os.getenv('GROQ_API_KEY')
        client = Groq(api_key=api_key)
        
        # Test different models
        models_to_test = [
            "llama3-8b-8192",
            "llama3-70b-8192", 
            "mixtral-8x7b-32768",
            "gemma-7b-it"
        ]
        
        working_models = []
        
        for model in models_to_test:
            try:
                print(f"\n🧪 Testing model: {model}")
                
                response = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": "Say 'OK'"
                        }
                    ],
                    model=model,
                    temperature=0.1,
                    max_tokens=5
                )
                
                if response and response.choices:
                    content = response.choices[0].message.content
                    print(f"   ✅ {model}: {content}")
                    working_models.append(model)
                else:
                    print(f"   ❌ {model}: No response")
                    
            except Exception as e:
                print(f"   ❌ {model}: {str(e)[:100]}...")
        
        print(f"\n📊 WORKING MODELS: {len(working_models)}/{len(models_to_test)}")
        for model in working_models:
            print(f"   ✅ {model}")
        
        return len(working_models) > 0
        
    except Exception as e:
        print(f"❌ Model testing failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 TESTING GROQ API FUNCTIONALITY")
    print("=" * 80)
    
    # Run tests
    test1 = test_groq_api_connection()
    test2 = test_groq_meal_generation()
    test3 = test_groq_api_models()
    
    print("\n" + "=" * 80)
    print("📊 GROQ API TEST RESULTS:")
    print(f"✅ API Connection: {'PASS' if test1 else 'FAIL'}")
    print(f"✅ Meal Generation: {'PASS' if test2 else 'FAIL'}")
    print(f"✅ Model Availability: {'PASS' if test3 else 'FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 GROQ API IS WORKING!")
        print("🔧 AI meal generation should work properly!")
        print("📊 No need to rely on fallback meals!")
    else:
        print("\n❌ GROQ API ISSUES DETECTED")
        
        if not test1:
            print("🔧 SOLUTION: Check API key and network connection")
        if not test2:
            print("🔧 SOLUTION: Debug meal generation logic")
        if not test3:
            print("🔧 SOLUTION: Try different models or check quotas")
        
    print("\n🔍 NEXT STEPS:")
    if test1:
        print("  ✅ API connection works - focus on meal generation logic")
    else:
        print("  ❌ Fix API connection first")
        print("  🔑 Check if API key is valid and has credits")
        print("  🌐 Check network connectivity")
        print("  📊 Check Groq service status")
