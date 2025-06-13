import json
import re

def fix_json_response(response_text):
    """Fix common JSON syntax errors in responses from Groq"""
    # 1. Clean up the response
    response_text = response_text.strip()
    
    # 2. Fix specific error pattern: Missing "name" key
    response_text = re.sub(r'{\s*"([^"]+)",', r'{"name": "\1",', response_text)
    
    print(f"After regex fix: {response_text[:200]}...")
    
    # 3. Try to parse the fixed JSON
    try:
        data = json.loads(response_text)
        print("JSON parsing successful!")
        return data
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        # If parsing fails, return an empty list
        return []

# Example 1 from log
example1 = """[
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
]"""

# Example 2 from log
example2 = """[
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
]"""

# Test with example 1
print("TESTING EXAMPLE 1:")
print("-----------------")
print("Original:")
print(example1)
fixed1 = fix_json_response(example1)
print("\nFixed JSON result:")
if fixed1:
    print(json.dumps(fixed1, indent=2, ensure_ascii=False))
else:
    print("Failed to fix JSON")

# Test with example 2
print("\n\nTESTING EXAMPLE 2:")
print("-----------------")
print("Original:")
print(example2)
fixed2 = fix_json_response(example2)
print("\nFixed JSON result:")
if fixed2:
    print(json.dumps(fixed2, indent=2, ensure_ascii=False))
else:
    print("Failed to fix JSON") 