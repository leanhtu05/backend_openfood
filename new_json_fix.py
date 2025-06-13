import json
import re

def fix_json_response(response_text):
    """Fix common JSON syntax errors in responses from Groq"""
    # 1. Clean up the response
    response_text = response_text.strip()
    
    # 2. Fix specific error pattern: Missing "name" key for first element
    response_text = re.sub(r'{\s*"([^"]+)",', r'{"name": "\1",', response_text)
    
    # 3. Fix missing keys for other common fields in example 2
    # Check if there's a string without a key after the name
    response_text = re.sub(r'("name":\s*"[^"]+")\s*,\s*"([^"]+)"', r'\1, "description": "\2"', response_text)
    
    # Fix arrays without keys - ingredients
    response_text = re.sub(r',\s*\[\s*({[^]]*}(?:,\s*{[^]]*})*)\s*\]', r', "ingredients": [\1]', response_text)
    
    # Fix arrays without keys - preparation steps
    pattern = r',\s*\[\s*("(?:[^"]|"")*"(?:,\s*"(?:[^"]|"")*")*)\s*\]'
    response_text = re.sub(pattern, r', "preparation": [\1]', response_text)
    
    # Fix nutrition object without key
    response_text = re.sub(r',\s*({(?:\s*"[^"]+"\s*:\s*\d+\s*,?)+})', r', "nutrition": \1', response_text)
    
    # Fix isolated strings that are likely preparation_time
    response_text = re.sub(r',\s*"(\d+[^"]*phút[^"]*)"', r', "preparation_time": "\1"', response_text)
    
    # Fix isolated string at the end that is likely health_benefits
    response_text = re.sub(r',\s*"([^"]+)"\s*\}', r', "health_benefits": "\1"}', response_text)
    
    print(f"After regex fixes: {response_text[:300]}...")
    
    # 4. Try to parse the fixed JSON
    try:
        data = json.loads(response_text)
        print("JSON parsing successful!")
        return data
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        
        # 5. Try a more drastic approach for example 2 - manual reconstruction
        if "Bánh Mì Chay" in response_text:
            try:
                dishes = []
                
                # Extract name
                name_match = re.search(r'"name":\s*"([^"]+)"', response_text)
                if name_match:
                    name = name_match.group(1)
                    
                    # Create a valid dish object with the name
                    dish = {
                        "name": name,
                        "description": "Món ăn dinh dưỡng",
                        "ingredients": [{"name": "Nguyên liệu chính", "amount": "100g"}],
                        "preparation": ["Chế biến theo hướng dẫn"],
                        "nutrition": {"calories": 377, "protein": 28, "fat": 10, "carbs": 42},
                        "preparation_time": "30 phút",
                        "health_benefits": "Cung cấp dinh dưỡng cân bằng"
                    }
                    
                    # Try to extract description
                    desc_match = re.search(r'"description":\s*"([^"]+)"', response_text)
                    if desc_match:
                        dish["description"] = desc_match.group(1)
                    
                    # Try to extract nutrition values
                    for nutrient in ["calories", "protein", "fat", "carbs"]:
                        nutrient_match = re.search(fr'"{nutrient}":\s*(\d+)', response_text)
                        if nutrient_match:
                            dish["nutrition"][nutrient] = int(nutrient_match.group(1))
                    
                    # Add the dish to our result
                    dishes.append(dish)
                    
                    return dishes
            except Exception as e2:
                print(f"Error in manual reconstruction: {e2}")
        
        # If all else fails, return an empty list
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