#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_chat_endpoint():
    """Test chat endpoint với tin nhắn về hôm qua"""
    
    url = "http://localhost:5000/chat"
    
    # Test case 1: Hỏi về hôm nay (để test nước uống)
    payload1 = {
        "message": "hôm nay tôi uống bao nhiêu nước rồi",
        "user_id": "49DhdmJHFAY40eEgaPNEJqGdDQK2"
    }
    
    print("🧪 Test 1: Hỏi về nước uống hôm nay")
    print(f"Request: {json.dumps(payload1, ensure_ascii=False)}")
    
    try:
        response1 = requests.post(url, json=payload1, timeout=30)
        print(f"Status: {response1.status_code}")
        print(f"Response: {json.dumps(response1.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")

    # Test case 2: Hỏi về hôm nay
    payload2 = {
        "message": "hôm nay tôi tập gì rồi",
        "user_id": "49DhdmJHFAY40eEgaPNEJqGdDQK2"
    }

    print("🧪 Test 2: Hỏi về hôm nay")
    print(f"Request: {json.dumps(payload2, ensure_ascii=False)}")

    try:
        response2 = requests.post(url, json=payload2, timeout=30)
        print(f"Status: {response2.status_code}")
        print(f"Response: {json.dumps(response2.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "="*50 + "\n")

    # Test case 3: Hỏi về ngày cụ thể
    payload3 = {
        "message": "ngày 10/06/2025 tôi ăn gì",
        "user_id": "49DhdmJHFAY40eEgaPNEJqGdDQK2"
    }

    print("🧪 Test 3: Hỏi về ngày cụ thể")
    print(f"Request: {json.dumps(payload3, ensure_ascii=False)}")

    try:
        response3 = requests.post(url, json=payload3, timeout=30)
        print(f"Status: {response3.status_code}")
        print(f"Response: {json.dumps(response3.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "="*50 + "\n")

    # Test case 4: Hỏi về 2 ngày trước
    payload4 = {
        "message": "2 ngày trước tôi có tập không",
        "user_id": "49DhdmJHFAY40eEgaPNEJqGdDQK2"
    }

    print("🧪 Test 4: Hỏi về 2 ngày trước")
    print(f"Request: {json.dumps(payload4, ensure_ascii=False)}")

    try:
        response4 = requests.post(url, json=payload4, timeout=30)
        print(f"Status: {response4.status_code}")
        print(f"Response: {json.dumps(response4.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat_endpoint()
