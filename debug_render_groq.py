#!/usr/bin/env python3
"""
Debug Groq Issues trên Render
Tìm và sửa các vấn đề cụ thể khiến Groq hoạt động local nhưng fail trên Render
"""

import requests
import json
import time
import os

def test_groq_api_directly():
    """Test Groq API trực tiếp để kiểm tra connectivity"""
    print("\n🔍 TESTING GROQ API DIRECTLY")
    print("=" * 40)
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: ***{api_key[-4:]}")
    
    try:
        import groq
        
        client = groq.Groq(api_key=api_key)
        
        # Test simple completion
        print("📤 Testing simple completion...")
        
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "user", "content": "Say hello in JSON format: {\"message\": \"hello\"}"}
            ],
            temperature=0.0,
            max_tokens=100
        )
        
        response_text = completion.choices[0].message.content
        print(f"✅ Groq API response: {response_text}")
        
        # Try to parse as JSON
        try:
            json.loads(response_text.strip())
            print("✅ Response is valid JSON")
            return True
        except:
            print("⚠️ Response is not valid JSON but API works")
            return True
            
    except ImportError:
        print("❌ Groq module not available")
        return False
    except Exception as e:
        print(f"❌ Groq API test failed: {e}")
        return False

def test_production_endpoint_detailed(base_url: str):
    """Test production endpoint với detailed logging"""
    print(f"\n🏭 TESTING PRODUCTION ENDPOINT: {base_url}")
    print("=" * 60)
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(f"{base_url}/", timeout=30)
        print(f"✅ Basic connectivity: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return
    
    # Test 2: Simple meal generation without AI
    print("\n📋 Test 2: Fallback meal generation (use_ai=False)")
    test_data = {
        "user_id": "debug_test_fallback",
        "calories_target": 300,
        "protein_target": 20,
        "fat_target": 10,
        "carbs_target": 40,
        "use_ai": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/meal-plan/generate",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Fallback generation works")
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
        else:
            print(f"❌ Fallback failed: {response.text[:300]}")
            
    except Exception as e:
        print(f"❌ Fallback test error: {e}")
    
    # Test 3: AI meal generation
    print("\n📋 Test 3: AI meal generation (use_ai=True)")
    test_data["use_ai"] = True
    test_data["user_id"] = "debug_test_ai"
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}/api/meal-plan/generate",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=120  # Longer timeout for AI
        )
        
        duration = time.time() - start_time
        print(f"Status: {response.status_code}")
        print(f"Duration: {duration:.2f}s")
        
        if response.status_code == 200:
            print("✅ AI generation works")
            data = response.json()
            
            # Check if response looks like AI or fallback
            if "weekly_plan" in data:
                weekly_plan = data["weekly_plan"]
                
                # Look at first meal
                for day, day_data in weekly_plan.items():
                    if "meals" in day_data:
                        for meal_type, meals in day_data["meals"].items():
                            if meals:
                                first_meal = meals[0]
                                meal_name = first_meal.get("name", "")
                                description = first_meal.get("description", "")
                                
                                print(f"🍽️ Generated meal: {meal_name}")
                                print(f"📝 Description length: {len(description)} chars")
                                
                                # Check for AI vs fallback indicators
                                if len(description) > 50:
                                    print("✅ Rich description suggests AI generation")
                                else:
                                    print("⚠️ Short description suggests fallback")
                                
                                if "fallback" in description.lower():
                                    print("❌ Explicitly using fallback")
                                
                                break
                        break
                    break
        
        elif response.status_code == 500:
            print("❌ Server error during AI generation")
            error_text = response.text
            
            # Analyze error for common issues
            if "groq" in error_text.lower():
                print("🔍 Groq-related error detected")
            if "timeout" in error_text.lower():
                print("🔍 Timeout error detected")
            if "api" in error_text.lower() and "key" in error_text.lower():
                print("🔍 API key error detected")
            if "json" in error_text.lower():
                print("🔍 JSON parsing error detected")
                
            print(f"Error details: {error_text[:500]}")
            
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout - AI generation taking too long")
    except Exception as e:
        print(f"❌ AI test error: {e}")

def create_render_debug_script():
    """Tạo script debug để chạy trên Render"""
    debug_script = '''#!/usr/bin/env python3
"""
Debug script to run ON Render server
"""

import os
import json
import sys

def check_environment():
    print("=== RENDER ENVIRONMENT CHECK ===")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Check environment variables
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        print(f"GROQ_API_KEY: ***{groq_key[-4:]}")
    else:
        print("GROQ_API_KEY: NOT SET")
    
    # Check installed packages
    try:
        import groq
        print("✅ groq package available")
        
        # Test Groq client creation
        if groq_key:
            client = groq.Groq(api_key=groq_key)
            print("✅ Groq client created successfully")
            
            # Test simple API call
            try:
                completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10,
                    temperature=0.0
                )
                print("✅ Groq API call successful")
                print(f"Response: {completion.choices[0].message.content}")
            except Exception as e:
                print(f"❌ Groq API call failed: {e}")
        
    except ImportError as e:
        print(f"❌ groq package not available: {e}")
    
    # Check other dependencies
    packages = ["requests", "fastapi", "uvicorn", "firebase_admin"]
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} not available")
    
    # Check file system
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in current directory: {os.listdir('.')}")
    
    # Check if groq_integration.py exists and is importable
    try:
        from groq_integration import GroqService
        print("✅ GroqService importable")
        
        # Test GroqService initialization
        service = GroqService()
        print(f"✅ GroqService initialized, available: {service.available}")
        
    except Exception as e:
        print(f"❌ GroqService error: {e}")

if __name__ == "__main__":
    check_environment()
'''
    
    with open("render_debug.py", "w", encoding="utf-8") as f:
        f.write(debug_script)
    
    print("✅ Created render_debug.py")
    print("📋 To use on Render:")
    print("1. Upload this file to your Render deployment")
    print("2. Run: python render_debug.py")
    print("3. Check the output for environment issues")

def main():
    """Main debug runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Debug Groq Issues on Render")
    parser.add_argument("--url", help="Production URL to test")
    parser.add_argument("--create-debug", action="store_true", help="Create debug script for Render")
    
    args = parser.parse_args()
    
    print("🔧 GROQ RENDER DEBUG TOOL")
    print("=" * 50)
    
    if args.create_debug:
        create_render_debug_script()
        return
    
    # Test Groq API directly
    groq_works = test_groq_api_directly()
    
    if args.url:
        # Test production endpoint
        test_production_endpoint_detailed(args.url)
    else:
        print("\n💡 Usage:")
        print("python debug_render_groq.py --url https://your-app.onrender.com")
        print("python debug_render_groq.py --create-debug")
    
    print("\n📋 DEBUGGING CHECKLIST:")
    print("1. ✅ Groq API works locally" if groq_works else "1. ❌ Groq API fails locally")
    print("2. Check GROQ_API_KEY is set in Render environment variables")
    print("3. Check groq package is in requirements.txt")
    print("4. Check Render build logs for import errors")
    print("5. Check Render runtime logs for API errors")
    print("6. Verify network connectivity from Render to Groq API")
    print("7. Check for memory/timeout limits on Render")

if __name__ == "__main__":
    main()
