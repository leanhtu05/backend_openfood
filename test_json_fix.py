#!/usr/bin/env python3
"""
Script kiểm tra hàm fix_json_response với các JSON không hợp lệ từ Groq API
"""
import json
from groq_client_fixed import fix_json_response

# Các ví dụ JSON không hợp lệ từ log
invalid_json_examples = [
    # Example 1: Missing "name" key
    '''[
  {
    "Bánh Mì Chay",
    "description": "Món bánh mì chay thơm ngon, chứa nhiều chất xơ và protein, phù hợp cho mục tiêu giảm cân.",
    "ingredients": [
      {"name": "Bánh mì", "amount": "100g"},
      {"name": "Đậu phụ", "amount": "50g"},
      {"name": "Rau thơm", "amount": "20g"},
      {"name": "Nước mắm chay", "amount": "1 thìa canh"}
    ],
    "preparation": [
      "Xếp bánh mì ra đĩa.",
      "Đậu phụ cắt nhỏ và xếp lên bánh mì.",
      "Rau thơm cắt nhỏ và xếp lên trên.",
      "Dùng nước mắm chay để chấm."
    ],
    "nutrition": {
      "calories": 377,
      "protein": 28,
      "fat": 10,
      "carbs": 42
    },
    "preparation_time": "20 phút",
    "health_benefits": "Cung cấp protein chất lượng cao từ đậu phụ, carbs từ bánh mì giúp bổ sung năng lượng, phù hợp cho mục tiêu dinh dưỡng của người dùng."
  }
]''',

    # Example 2: Arrays with no field names
    '''[
  {
    "Bánh Mì Chay",
    "Món bánh mì chay thơm ngon, với nhân đậu phụ, rau củ và nước mắm chua ngọt.",
    [
      {"name": "Bánh mì", "amount": "100g"},
      {"name": "Đậu phụ", "amount": "50g"},
      {"name": "Rau củ", "amount": "50g"},
      {"name": "Nước mắm", "amount": "2 thìa canh"}
    ],
    [
      "Ướp đậu phụ với gia vị trong 30 phút.",
      "Nướng bánh mì trên than hoa đến khi chín vàng.",
      "Chiên rau củ thành chả mỏng.",
      "Bày bánh mì ra đĩa, xếp đậu phụ và rau củ lên trên."
    ],
    {
      "calories": 377,
      "protein": 28,
      "fat": 10,
      "carbs": 42
    },
    "45 phút",
    "Cung cấp protein chất lượng cao từ đậu phụ, carbs từ bánh mì giúp bổ sung năng lượng, phù hợp cho mục tiêu dinh dưỡng của người dùng."
  }
]''',

    # Example 3: Markdown formatting in the response
    '''```json
[
  {
    "name": "Bánh Mì Chay",
    "description": "Món bánh mì chay thơm ngon, chứa nhiều chất xơ và protein.",
    "ingredients": [
      {"name": "Bánh mì", "amount": "100g"},
      {"name": "Đậu phụ", "amount": "50g"}
    ],
    "nutrition": {
      calories: 377,
      protein: 28,
      fat: 10,
      carbs: 42
    }
  }
]
```'''
]

def test_json_fixes():
    """Test the JSON fixing function on sample invalid JSONs"""
    for i, invalid_json in enumerate(invalid_json_examples):
        print(f"\n=== Testing Example {i+1} ===")
        print(f"Original (invalid) JSON:")
        print(f"{invalid_json[:200]}...")
        
        try:
            # Try parsing directly (should fail)
            json.loads(invalid_json)
            print("Surprisingly, this JSON is already valid!")
        except json.JSONDecodeError as e:
            print(f"JSON validation error: {e}")
            
            # Try fixing the JSON
            fixed_json = fix_json_response(invalid_json)
            print(f"\nFixed JSON:")
            print(f"{fixed_json[:200]}...")
            
            # Check if the fixed JSON is valid
            try:
                parsed_data = json.loads(fixed_json)
                print("\nSuccessfully parsed fixed JSON!")
                print(f"Data structure: {type(parsed_data)}")
                if isinstance(parsed_data, list):
                    print(f"Number of items: {len(parsed_data)}")
                    if len(parsed_data) > 0:
                        print(f"First item keys: {list(parsed_data[0].keys())}")
                elif isinstance(parsed_data, dict):
                    print(f"Keys: {list(parsed_data.keys())}")
                    if "meals" in parsed_data and len(parsed_data["meals"]) > 0:
                        print(f"First meal keys: {list(parsed_data['meals'][0].keys())}")
            except json.JSONDecodeError as e:
                print(f"Still invalid JSON after fixing: {e}")

if __name__ == "__main__":
    test_json_fixes() 