#!/usr/bin/env python3
"""
🔍 Firebase Indexes Checker
Kiểm tra và tạo các indexes cần thiết cho Firestore
"""

import sys
import os
import json
import traceback
from typing import List, Dict, Any

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.firestore_service import FirestoreService

def check_required_indexes():
    """
    Kiểm tra các indexes cần thiết và in ra links để tạo
    """
    print("🔍 CHECKING FIREBASE INDEXES...")
    
    firestore_service = FirestoreService()
    
    # Test queries that require indexes
    test_queries = [
        {
            "name": "meal_plans by timestamp DESC",
            "test": lambda: firestore_service.get_recent_meal_plans(5)
        },
        {
            "name": "meal_plans by user_id",
            "test": lambda: firestore_service.get_user_meal_plans("test_user", 5)
        },
        {
            "name": "ai_suggestions by userId + timestamp DESC",
            "test": lambda: firestore_service.get_ai_suggestions("test_user", 5)
        },
        {
            "name": "exercises by user_id",
            "test": lambda: firestore_service.get_exercise_history("test_user", limit=5)
        },
        {
            "name": "water_entries by user_id + date",
            "test": lambda: firestore_service.get_water_intake_by_date("test_user", "2024-01-01")
        }
    ]
    
    missing_indexes = []
    
    for query_info in test_queries:
        try:
            print(f"\n📋 Testing: {query_info['name']}")
            result = query_info['test']()
            print(f"✅ Query successful: {len(result) if result else 0} results")
        except Exception as e:
            error_str = str(e)
            if "requires an index" in error_str:
                print(f"❌ Index required: {query_info['name']}")
                
                # Extract index URL if available
                if "create it here: " in error_str:
                    index_url = error_str.split("create it here: ")[1].split(" ")[0]
                    missing_indexes.append({
                        "query": query_info['name'],
                        "url": index_url,
                        "error": error_str
                    })
                    print(f"🔗 Create index: {index_url}")
                else:
                    missing_indexes.append({
                        "query": query_info['name'],
                        "url": None,
                        "error": error_str
                    })
            else:
                print(f"⚠️ Other error: {error_str}")
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"✅ Successful queries: {len(test_queries) - len(missing_indexes)}")
    print(f"❌ Missing indexes: {len(missing_indexes)}")
    
    if missing_indexes:
        print(f"\n🔧 REQUIRED ACTIONS:")
        for i, index_info in enumerate(missing_indexes, 1):
            print(f"\n{i}. {index_info['query']}")
            if index_info['url']:
                print(f"   🔗 Create index: {index_info['url']}")
            else:
                print(f"   ⚠️ Manual index creation needed")
                print(f"   Error: {index_info['error'][:200]}...")
    else:
        print(f"\n🎉 All indexes are properly configured!")
    
    return missing_indexes

def generate_index_commands():
    """
    Tạo commands để deploy indexes
    """
    print(f"\n🚀 FIREBASE CLI COMMANDS:")
    print(f"1. Deploy indexes:")
    print(f"   firebase deploy --only firestore:indexes")
    print(f"")
    print(f"2. Check index status:")
    print(f"   firebase firestore:indexes")
    print(f"")
    print(f"3. Manual index creation:")
    print(f"   - Go to Firebase Console")
    print(f"   - Navigate to Firestore Database")
    print(f"   - Click on 'Indexes' tab")
    print(f"   - Click 'Create Index'")

def main():
    """
    Main function
    """
    try:
        print("🔥 FIREBASE INDEXES CHECKER")
        print("=" * 50)
        
        # Check indexes
        missing_indexes = check_required_indexes()
        
        # Generate commands
        generate_index_commands()
        
        # Load and display firestore.indexes.json
        try:
            with open('firestore.indexes.json', 'r') as f:
                indexes_config = json.load(f)
                print(f"\n📄 FIRESTORE.INDEXES.JSON:")
                print(f"   Total indexes configured: {len(indexes_config.get('indexes', []))}")
                print(f"   File: firestore.indexes.json")
        except FileNotFoundError:
            print(f"\n⚠️ firestore.indexes.json not found")
        
        print(f"\n" + "=" * 50)
        if missing_indexes:
            print(f"❌ {len(missing_indexes)} indexes need to be created")
            sys.exit(1)
        else:
            print(f"✅ All indexes are properly configured")
            sys.exit(0)
            
    except Exception as e:
        print(f"💥 Error checking indexes: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
