# -*- coding: utf-8 -*-
"""
Kiểm tra vị trí mạng và khả năng kết nối với Groq API
"""

import requests
import json
import os
from dotenv import load_dotenv

def check_ip_location():
    """Kiểm tra IP và vị trí hiện tại"""
    try:
        print("🌍 Checking IP Location...")
        print("=" * 50)
        
        # Get public IP
        ip_response = requests.get('https://api.ipify.org?format=json', timeout=10)
        ip_data = ip_response.json()
        public_ip = ip_data.get('ip', 'Unknown')
        
        print(f"🔍 Public IP: {public_ip}")
        
        # Get location info
        location_response = requests.get(f'http://ip-api.com/json/{public_ip}', timeout=10)
        location_data = location_response.json()
        
        if location_data.get('status') == 'success':
            country = location_data.get('country', 'Unknown')
            region = location_data.get('regionName', 'Unknown')
            city = location_data.get('city', 'Unknown')
            isp = location_data.get('isp', 'Unknown')
            
            print(f"🏳️ Country: {country}")
            print(f"🏙️ Region: {region}")
            print(f"🌆 City: {city}")
            print(f"🌐 ISP: {isp}")
            
            # Check if Vietnam
            if 'vietnam' in country.lower() or 'viet nam' in country.lower():
                print("✅ Location: Vietnam detected")
                return True, country
            else:
                print(f"⚠️ Location: Not Vietnam ({country})")
                return False, country
        else:
            print("❌ Could not determine location")
            return False, "Unknown"
            
    except Exception as e:
        print(f"❌ IP location check failed: {e}")
        return False, "Error"

def test_groq_connectivity():
    """Test kết nối trực tiếp với Groq API"""
    try:
        print("\n🔧 Testing Groq API Connectivity...")
        print("=" * 50)
        
        # Test basic connectivity to Groq
        groq_endpoints = [
            'https://api.groq.com',
            'https://api.groq.com/openai/v1/models'
        ]
        
        for endpoint in groq_endpoints:
            try:
                print(f"🌐 Testing: {endpoint}")
                response = requests.get(endpoint, timeout=10)
                print(f"   Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("   ✅ Connection successful")
                elif response.status_code == 401:
                    print("   ✅ Connection OK (401 expected without auth)")
                elif response.status_code == 403:
                    print("   ⚠️ 403 Forbidden - May be region blocked")
                else:
                    print(f"   ⚠️ Unexpected status: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print("   ❌ Timeout - Network issue or blocking")
            except requests.exceptions.ConnectionError:
                print("   ❌ Connection Error - May be blocked")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")
        return False

def test_groq_with_api_key():
    """Test Groq API với API key"""
    try:
        load_dotenv()
        
        print("\n🔑 Testing Groq API with API Key...")
        print("=" * 50)
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            print("❌ No GROQ_API_KEY found")
            return False
        
        print(f"🔑 Using API Key: {api_key[:15]}...{api_key[-10:]}")
        
        # Test with requests first
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Simple test request
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": "Say hello"
                }
            ],
            "model": "llama3-8b-8192",
            "temperature": 0.1,
            "max_tokens": 10
        }
        
        try:
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                print(f"✅ API Response: {content}")
                return True
            elif response.status_code == 401:
                print("❌ 401 Unauthorized - Invalid API key")
                return False
            elif response.status_code == 403:
                print("❌ 403 Forbidden - Region may be blocked or API key issue")
                print("🔍 This could be a Vietnam region restriction")
                return False
            elif response.status_code == 429:
                print("⚠️ 429 Rate Limited - Too many requests")
                return False
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return False
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout - Network or region blocking issue")
            return False
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - May be region blocked")
            return False
            
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

def suggest_solutions():
    """Đề xuất giải pháp dựa trên kết quả test"""
    print("\n🔧 SUGGESTED SOLUTIONS:")
    print("=" * 50)
    
    solutions = [
        "1. 🌐 VPN Solution:",
        "   - Use VPN to connect through US/Europe servers",
        "   - Recommended: ExpressVPN, NordVPN, or Surfshark",
        "   - Connect to US East Coast for best Groq performance",
        "",
        "2. 🔄 Alternative AI APIs:",
        "   - OpenAI GPT-4 (works well from Vietnam)",
        "   - Anthropic Claude (via AWS Bedrock)",
        "   - Google Gemini (good Vietnam support)",
        "   - Cohere API (region-friendly)",
        "",
        "3. 🏠 Local AI Solutions:",
        "   - Ollama with Vietnamese models",
        "   - Local LLaMA deployment",
        "   - Edge AI solutions",
        "",
        "4. 🔧 Network Troubleshooting:",
        "   - Try different DNS (8.8.8.8, 1.1.1.1)",
        "   - Check firewall settings",
        "   - Try mobile hotspot",
        "   - Contact ISP about API restrictions"
    ]
    
    for solution in solutions:
        print(solution)

def main():
    print("🚀 GROQ API REGION CONNECTIVITY TEST")
    print("=" * 80)
    
    # Check location
    is_vietnam, country = check_ip_location()
    
    # Test connectivity
    connectivity_ok = test_groq_connectivity()
    
    # Test with API key
    api_works = test_groq_with_api_key()
    
    print("\n" + "=" * 80)
    print("📊 DIAGNOSIS RESULTS:")
    print(f"🌍 Location: {country}")
    print(f"🌐 Basic Connectivity: {'OK' if connectivity_ok else 'ISSUES'}")
    print(f"🔑 API Authentication: {'WORKING' if api_works else 'FAILED'}")
    
    if not api_works:
        print("\n❌ GROQ API NOT WORKING")
        
        if is_vietnam:
            print("🔍 LIKELY CAUSE: Vietnam region restrictions")
            print("💡 Groq may block requests from Vietnam/Southeast Asia")
        else:
            print("🔍 LIKELY CAUSE: API key or network issue")
        
        suggest_solutions()
        
        print("\n🔄 IMMEDIATE WORKAROUND:")
        print("  1. Enable VPN (US/Europe server)")
        print("  2. Or switch to OpenAI/Gemini API")
        print("  3. Or use enhanced fallback system")
        
    else:
        print("\n✅ GROQ API IS WORKING!")
        print("🔧 The issue may be in the meal generation logic")

if __name__ == "__main__":
    main()
