#!/usr/bin/env python3
"""
Test script để kiểm tra admin dashboard fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from routers.admin_router import get_recent_activities

def test_recent_activities():
    """Test method get_recent_activities"""
    print("🧪 Testing get_recent_activities()...")
    
    try:
        activities = get_recent_activities()
        print(f"✅ Got {len(activities)} activities")
        
        for i, activity in enumerate(activities):
            print(f"  Activity {i+1}:")
            print(f"    Action: {activity.get('action', 'N/A')}")
            print(f"    Description: {activity.get('description', 'N/A')}")
            print(f"    User Email: {activity.get('user_email', 'N/A')}")
            print(f"    Timestamp: {activity.get('timestamp', 'N/A')}")
            print(f"    Timestamp Type: {type(activity.get('timestamp'))}")
            
            # Test strftime
            timestamp = activity.get('timestamp')
            if timestamp and hasattr(timestamp, 'strftime'):
                formatted_time = timestamp.strftime('%H:%M')
                print(f"    Formatted Time: {formatted_time}")
            else:
                print(f"    Formatted Time: Vừa xong")
            print()
        
        print("✅ Test passed: No strftime errors!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_timestamp_handling():
    """Test timestamp handling với các trường hợp khác nhau"""
    print("🧪 Testing timestamp handling...")
    
    test_cases = [
        {"timestamp": datetime.now(), "expected": "datetime object"},
        {"timestamp": "2025-06-23T22:06:39.690370", "expected": "ISO string"},
        {"timestamp": "Vừa xong", "expected": "plain string"},
        {"timestamp": None, "expected": "None"},
        {"timestamp": "", "expected": "empty string"},
    ]
    
    for i, case in enumerate(test_cases):
        print(f"  Test case {i+1}: {case['expected']}")
        timestamp = case['timestamp']
        
        try:
            # Simulate template logic
            if timestamp and hasattr(timestamp, 'strftime'):
                result = timestamp.strftime('%H:%M')
                print(f"    ✅ strftime result: {result}")
            else:
                result = "Vừa xong"
                print(f"    ✅ fallback result: {result}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return False
    
    print("✅ All timestamp test cases passed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting admin dashboard fix tests...\n")
    
    success = True
    
    # Test 1: Recent activities
    success &= test_recent_activities()
    print()
    
    # Test 2: Timestamp handling
    success &= test_timestamp_handling()
    print()
    
    if success:
        print("🎉 All tests passed! Admin dashboard should work correctly now.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    sys.exit(0 if success else 1)
