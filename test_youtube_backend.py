#!/usr/bin/env python3
"""
Test YouTube Backend Service
"""

import requests
import json
import time

def test_backend_health():
    """Test backend health"""
    print("🏥 Testing backend health...")
    
    url = 'http://localhost:8000/'
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Backend is healthy: {result.get('message', 'OK')}")
            return True
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        return False

def main():
    """Run basic test"""
    print("🧪 YouTube Backend Service Test")
    print("=" * 40)
    
    # Test backend health first
    if test_backend_health():
        print("✅ Backend is running and accessible")
        print("\n💡 To test YouTube endpoints:")
        print("   1. Make sure YouTube API key is configured")
        print("   2. Test search: POST /youtube/search")
        print("   3. Test trending: GET /youtube/trending")
    else:
        print("❌ Backend is not running")
        print("\n💡 Start backend with: python main.py")

if __name__ == "__main__":
    main()
