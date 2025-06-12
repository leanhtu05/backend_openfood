#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_water_yesterday():
    """Test câu hỏi về nước uống hôm qua"""
    
    url = "http://localhost:5000/chat"
    
    # Test: Hỏi về nước uống hôm qua
    payload = {
        "message": "hôm qua tôi uống bao nhiêu nước",
        "user_id": "49DhdmJHFAY40eEgaPNEJqGdDQK2"
    }
    
    print("🧪 Test: Hỏi về nước uống hôm qua")
    print(f"Request: {json.dumps(payload, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_water_yesterday()
