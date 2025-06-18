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
            "calories": {calories_target},
            "protein": {protein_target},
            "fat": {fat_target},
            "carbs": {carbs_target}
        },
        "preparation_time": "Thời gian chuẩn bị",
        "health_benefits": "Lợi ích sức khỏe"
    }
    
    prompt = f"""ABSOLUTE REQUIREMENT: Return ONLY valid JSON array. NO other text allowed.

MANDATORY JSON STRUCTURE - Each object MUST have ALL these keys in EXACT order:
{{"name": "string", "description": "string", "ingredients": [object], "preparation": [string], "nutrition": object, "preparation_time": "string", "health_benefits": "string"}}

PERFECT EXAMPLE OUTPUT (copy this structure exactly):
[{template_example}]

TASK: CREATE AUTHENTIC Vietnamese {meal_type} dishes with creative variations, meeting these EXACT nutrition targets:
- Calories: {calories_target}kcal (MUST be within ±20 calories)
- Protein: {protein_target}g (MUST be within ±3g)
- Fat: {fat_target}g (MUST be within ±3g)
- Carbs: {carbs_target}g (MUST be within ±5g)

VIETNAMESE AUTHENTICITY RULES:
1. USE traditional Vietnamese ingredients (gạo, thịt, cá, rau Việt Nam)
2. APPLY authentic cooking methods (nấu, luộc, xào, nướng, hấp)
3. MAINTAIN Vietnamese flavor profiles (nước mắm, mắm tôm, lá chanh, sả)
4. KEEP regional characteristics (miền Bắc, Trung, Nam)

CREATIVE VARIATION GUIDELINES:
1. ADD regional twists to traditional dishes (Phở Gà Miền Tây, Cơm Tấm Huế)
2. COMBINE ingredients from different regions (Bún Bò Huế với Tôm Miền Tây)
3. ENHANCE traditional recipes (Cháo Gà với Nấm Hương, Bánh Mì với Chả Cá)
4. VARY cooking techniques (Phở Áp Chảo, Cơm Niêu Đất)

REFERENCE DISHES FOR INSPIRATION:
{diverse_dishes}

AVOID THESE RECENT DISHES:
{recent_dishes}

USER PREFERENCES: {preferences}
ALLERGIES TO AVOID: {allergies}

AUTHENTIC INNOVATION EXAMPLES:
- "Phở Gà Nấu Dừa Miền Tây" (Western-style Coconut Chicken Pho)
- "Cháo Tôm Cua Đồng Cà Mau" (Ca Mau Field Crab and Shrimp Porridge)
- "Bánh Mì Chả Cá Nha Trang" (Nha Trang Fish Cake Banh Mi)

CRITICAL NUTRITION ACCURACY RULES (FAILURE TO FOLLOW = INVALID RESPONSE):
1. NUTRITION VALUES must be EXACTLY calculated based on ingredients
2. TOTAL CALORIES must equal sum of: (protein×4) + (carbs×4) + (fat×9)
3. INGREDIENTS must have realistic amounts that add up to nutrition targets
4. COOKING METHODS must be authentic Vietnamese techniques

VIETNAMESE AUTHENTICITY RULES (FAILURE TO FOLLOW = INVALID RESPONSE):
1. DISH NAMES must include Vietnamese regional/style indicators
2. INGREDIENTS must be authentic Vietnamese (no Western fusion ingredients)
3. COOKING METHODS must be traditional (nấu, luộc, xào, nướng, hấp, chiên)
4. FLAVOR PROFILES must use Vietnamese seasonings (nước mắm, mắm tôm, sả, lá chanh)

CREATIVE VARIATION EXAMPLES (FOLLOW THIS PATTERN):
- "Phở Bò Đặc Biệt Sài Gòn" instead of "Phở Bò"
- "Cơm Tấm Sườn Nướng Mật Ong" instead of "Cơm Tấm"
- "Bánh Mì Chả Cá Nha Trang" instead of "Bánh Mì"
- "Cháo Gà Hạt Sen Miền Bắc" instead of "Cháo Gà"

TECHNICAL RULES (FAILURE TO FOLLOW = INVALID RESPONSE):
1. Output MUST start with [ and end with ]
2. Each object MUST start with "name" as the FIRST key
3. NEVER write {{"Dish Name", "description": ...}} - ALWAYS write {{"name": "Dish Name", "description": ...}}
4. All nutrition values MUST be numbers (not strings) and ACCURATE
5. Ingredients MUST be array of objects with "name" and "amount"
6. Preparation MUST be array of strings with detailed Vietnamese cooking steps
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
            "name": "Bánh Mì Chả Cá Nha Trang Đặc Biệt",
            "description": "Bánh mì truyền thống Nha Trang với chả cá tươi, rau thơm miền Trung và nước mắm Phú Quốc",
            "ingredients": [
                {"name": "Bánh mì Việt Nam", "amount": "1 ổ (80g)"},
                {"name": "Chả cá Nha Trang", "amount": "120g"},
                {"name": "Rau thơm miền Trung", "amount": "40g"},
                {"name": "Dưa leo", "amount": "30g"},
                {"name": "Cà rốt ngâm chua", "amount": "25g"},
                {"name": "Nước mắm Phú Quốc", "amount": "10ml"},
                {"name": "Ớt tươi", "amount": "5g"}
            ],
            "preparation": [
                "Bước 1: Nướng bánh mì trên than hoa đến giòn vàng",
                "Bước 2: Chả cá nướng lại trên chảo gang đến thơm",
                "Bước 3: Rau thơm rửa sạch, để ráo nước",
                "Bước 4: Cắt bánh mì dọc, kẹp chả cá và rau thơm",
                "Bước 5: Chấm nước mắm pha ớt theo kiểu Nha Trang"
            ],
            "nutrition": {
                "calories": 320,
                "protein": 18,
                "fat": 12,
                "carbs": 42
            },
            "preparation_time": "20 phút",
            "health_benefits": "Giàu protein từ cá biển, omega-3 tốt cho tim mạch, vitamin từ rau thơm tươi"
        }
    ]
    
    prompt = f"""You are an authentic Vietnamese chef AI. Study this example and create REGIONAL VARIATIONS of traditional dishes.

EXAMPLE INPUT: Create authentic Vietnamese breakfast dish with regional twist, 350 calories, 20g protein, 15g fat, 45g carbs

AUTHENTIC VIETNAMESE EXAMPLE OUTPUT:
{example_output}

NOW CREATE: AUTHENTIC Vietnamese {meal_type} dish with regional variation, {calories_target} calories, {protein_target}g protein, {fat_target}g fat, {carbs_target}g carbs

VIETNAMESE AUTHENTICITY RULES:
- CREATE regional variations of traditional dishes (Miền Bắc, Trung, Nam style)
- USE only authentic Vietnamese ingredients and cooking methods
- MAINTAIN traditional flavor profiles with Vietnamese seasonings
- ADD regional specialties and local ingredients
- ENSURE accurate nutrition calculation based on ingredients
- Return ONLY JSON array like the example
- Include 4-5 detailed Vietnamese cooking steps
- Set nutrition EXACTLY to targets
- NO other text, NO markdown

AUTHENTIC VIETNAMESE JSON OUTPUT:"""

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
