"""
JSON Prompt Templates for Groq Integration
Các template prompt chuẩn để đảm bảo Groq trả về JSON hợp lệ
"""

def get_strict_json_prompt(meal_type: str, calories_target: int, protein_target: int, 
                          fat_target: int, carbs_target: int, preferences: str = "", 
                          allergies: str = "", diverse_dishes: str = "", 
                          recent_dishes: str = "") -> str:
    """
    Tạo prompt cực kỳ nghiêm ngặt để đảm bảo JSON hợp lệ
    
    Args:
        meal_type: Loại bữa ăn
        calories_target, protein_target, fat_target, carbs_target: Mục tiêu dinh dưỡng
        preferences: Sở thích ăn uống
        allergies: Dị ứng thực phẩm
        diverse_dishes: Danh sách món ăn đa dạng
        recent_dishes: Món ăn gần đây để tránh lặp lại
    
    Returns:
        str: Prompt chuẩn JSON
    """
    
    # Template JSON chuẩn
    template_example = {
        "name": "Tên món ăn",
        "description": "Mô tả món ăn",
        "ingredients": [
            {"name": "Tên nguyên liệu", "amount": "Số lượng"}
        ],
        "preparation": ["Bước 1", "Bước 2", "Bước 3"],
        "nutrition": {
            "calories": calories_target // 2,
            "protein": protein_target // 2,
            "fat": fat_target // 2,
            "carbs": carbs_target // 2
        },
        "preparation_time": "Thời gian chuẩn bị",
        "health_benefits": "Lợi ích sức khỏe"
    }
    
    prompt = f"""ABSOLUTE REQUIREMENT: Return ONLY valid JSON array. NO other text allowed.

MANDATORY JSON STRUCTURE - Each object MUST have ALL these keys in EXACT order:
{{"name": "string", "description": "string", "ingredients": [object], "preparation": [string], "nutrition": object, "preparation_time": "string", "health_benefits": "string"}}

PERFECT EXAMPLE OUTPUT (copy this structure exactly):
[{template_example}]

TASK: Create 1-2 Vietnamese {meal_type} dishes with these nutrition targets:
- Calories: {calories_target}kcal
- Protein: {protein_target}g
- Fat: {fat_target}g
- Carbs: {carbs_target}g

AVAILABLE DISHES TO CHOOSE FROM:
{diverse_dishes}

AVOID THESE RECENT DISHES:
{recent_dishes}

PREFERENCES: {preferences}
ALLERGIES: {allergies}

CRITICAL RULES (FAILURE TO FOLLOW = INVALID RESPONSE):
1. Output MUST start with [ and end with ]
2. Each object MUST start with "name" as the FIRST key
3. NEVER write {{"Dish Name", "description": ...}} - ALWAYS write {{"name": "Dish Name", "description": ...}}
4. All nutrition values MUST be numbers (not strings)
5. Ingredients MUST be array of objects with "name" and "amount"
6. Preparation MUST be array of strings
7. NO markdown formatting (```json)
8. NO explanatory text before or after JSON
9. If you cannot create valid JSON, return: []

RESPOND WITH ONLY THE JSON ARRAY (starting with [ and ending with ]):"""

    return prompt

def get_one_shot_example_prompt(meal_type: str, calories_target: int, protein_target: int,
                               fat_target: int, carbs_target: int) -> str:
    """
    Prompt với one-shot example để hướng dẫn AI
    """
    
    example_output = [
        {
            "name": "Bánh Mì Chay",
            "description": "Bánh mì chay với đậu hũ và rau thơm, thơm ngon bổ dưỡng",
            "ingredients": [
                {"name": "Bánh mì", "amount": "1 ổ"},
                {"name": "Đậu hũ", "amount": "100g"},
                {"name": "Rau thơm", "amount": "50g"},
                {"name": "Dưa leo", "amount": "30g"}
            ],
            "preparation": [
                "Cắt bánh mì dọc, nướng giòn",
                "Chiên đậu hũ vàng đều",
                "Rửa sạch rau thơm và dưa leo",
                "Kẹp đậu hũ và rau vào bánh mì"
            ],
            "nutrition": {
                "calories": 320,
                "protein": 18,
                "fat": 12,
                "carbs": 42
            },
            "preparation_time": "15 phút",
            "health_benefits": "Giàu protein thực vật, ít cholesterol, cung cấp chất xơ tốt cho tiêu hóa"
        }
    ]
    
    prompt = f"""You are a JSON-only response system. Study this example and create similar output.

EXAMPLE INPUT: Create Vietnamese breakfast dish, 350 calories, 20g protein, 15g fat, 45g carbs

EXAMPLE OUTPUT:
{example_output}

NOW CREATE: Vietnamese {meal_type} dish, {calories_target} calories, {protein_target}g protein, {fat_target}g fat, {carbs_target}g carbs

RULES:
- Return ONLY JSON array like the example
- Use Vietnamese dish names and descriptions  
- Include realistic ingredients with amounts
- Add 3-4 preparation steps
- Set nutrition close to targets
- NO other text, NO markdown

JSON OUTPUT:"""

    return prompt

def get_validation_retry_prompt(failed_json: str, error_message: str) -> str:
    """
    Prompt để sửa JSON bị lỗi
    """
    
    prompt = f"""The previous JSON response had an error: {error_message}

FAILED JSON:
{failed_json}

Please fix this JSON and return a valid JSON array. Common issues to fix:
1. Missing "name" key - add {{"name": "dish_name"}} 
2. Missing quotes around keys
3. Trailing commas
4. Unbalanced brackets/braces
5. Missing required fields

REQUIRED FIELDS: name, description, ingredients, preparation, nutrition, preparation_time, health_benefits

Return ONLY the corrected JSON array:"""

    return prompt

def get_fallback_prompt(meal_type: str) -> str:
    """
    Prompt đơn giản khi các prompt phức tạp thất bại
    """
    
    prompt = f"""Create 1 simple Vietnamese {meal_type} dish in JSON format.

Template:
[{{"name": "Vietnamese dish name", "description": "Brief description", "ingredients": [{{"name": "ingredient", "amount": "100g"}}], "preparation": ["step 1", "step 2"], "nutrition": {{"calories": 300, "protein": 20, "fat": 10, "carbs": 40}}, "preparation_time": "30 phút", "health_benefits": "Nutritious and healthy"}}]

Return only JSON:"""

    return prompt

# Utility functions for prompt management
def get_temperature_settings():
    """Cài đặt temperature tối ưu cho JSON generation"""
    return {
        "temperature": 0.0,  # Maximum determinism
        "top_p": 0.1,       # Very focused sampling
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }

def get_system_message():
    """System message chuẩn cho JSON generation"""
    return "You are a JSON-only response system. You MUST respond with valid JSON arrays only. Never include explanatory text, markdown formatting, or any other content outside the JSON structure."

def validate_json_response(response: str) -> tuple[bool, str]:
    """
    Validate JSON response và trả về lỗi nếu có
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        import json
        data = json.loads(response.strip())
        
        if not isinstance(data, list):
            return False, "Response is not a JSON array"
        
        if len(data) == 0:
            return False, "Empty array returned"
        
        required_keys = ["name", "description", "ingredients", "preparation", "nutrition", "preparation_time", "health_benefits"]
        
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                return False, f"Item {i} is not an object"
            
            for key in required_keys:
                if key not in item:
                    return False, f"Item {i} missing required key: {key}"
        
        return True, "Valid JSON"
        
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"
    except Exception as e:
        return False, f"Validation error: {str(e)}"
