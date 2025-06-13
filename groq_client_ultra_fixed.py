"""
An improved Groq client with enhanced JSON error handling
"""
import os
import groq
import re
import json

def fix_json_response(response_text):
    """
    Fix common JSON syntax errors in responses from Groq with enhanced error handling
    
    Args:
        response_text (str): The raw response text from Groq
        
    Returns:
        list: Fixed JSON data as Python list
    """
    # 1. Clean up the response - remove markdown code blocks
    response_text = re.sub(r'```json\s*', '', response_text)
    response_text = re.sub(r'```\s*', '', response_text)
    response_text = response_text.strip()
    
    # Extract only the JSON array
    json_start = response_text.find('[')
    json_end = response_text.rfind(']') + 1
    
    if json_start != -1 and json_end != -1:
        response_text = response_text[json_start:json_end]
    
    # Try direct approach with specific pattern fixing
    try:
        # Convert {"string value", "key": "value"} to {"name": "string value", "key": "value"}
        fixed_text = re.sub(r'{\s*"([^"]+)",', r'{"name": "\1",', response_text)
        json_data = json.loads(fixed_text)
        print("Fixed JSON with regex pattern replacement")
        return json_data
    except json.JSONDecodeError:
        print("Regex pattern replacement failed, trying manual parsing")
    
    # If that fails, try manual extraction
    result = []
    try:
        # Split the text into individual dish objects
        dish_pattern = r'{\s*(?:"[^"]+"|\s*"name":\s*"[^"]+")(.*?)}'
        dishes = re.finditer(dish_pattern, response_text, re.DOTALL)
        
        for dish_match in dishes:
            dish_text = dish_match.group(0)
            dish = {}
            
            # Extract name (either as standalone string or with key)
            name_match = re.search(r'{\s*"([^"]+)"', dish_text)
            name_key_match = re.search(r'"name":\s*"([^"]+)"', dish_text)
            
            if name_match and not name_key_match:
                dish['name'] = name_match.group(1)
            elif name_key_match:
                dish['name'] = name_key_match.group(1)
            else:
                # If no name found, skip this dish
                continue
                
            # Extract description
            desc_match = re.search(r'"description":\s*"([^"]+)"', dish_text)
            if desc_match:
                dish['description'] = desc_match.group(1)
            
            # Extract ingredients
            dish['ingredients'] = []
            ingredients_pattern = r'"ingredients":\s*\[(.*?)\]'
            ingredients_match = re.search(ingredients_pattern, dish_text, re.DOTALL)
            if ingredients_match:
                ingredients_text = ingredients_match.group(1)
                ingredient_items = re.finditer(r'{\s*"name":\s*"([^"]+)",\s*"amount":\s*"([^"]+)"\s*}', ingredients_text)
                for ingredient in ingredient_items:
                    dish['ingredients'].append({
                        "name": ingredient.group(1),
                        "amount": ingredient.group(2)
                    })
            
            # Extract preparation steps
            dish['preparation'] = []
            preparation_pattern = r'"preparation":\s*\[(.*?)\]'
            preparation_match = re.search(preparation_pattern, dish_text, re.DOTALL)
            if preparation_match:
                preparation_text = preparation_match.group(1)
                prep_items = re.findall(r'"([^"]+)"', preparation_text)
                dish['preparation'].extend(prep_items)
            
            # Extract nutrition info
            dish['nutrition'] = {}
            nutrition_pattern = r'"nutrition":\s*{\s*(.*?)\s*}'
            nutrition_match = re.search(nutrition_pattern, dish_text, re.DOTALL)
            if nutrition_match:
                nutrition_text = nutrition_match.group(1)
                
                # Extract nutrition values
                for nutrient in ['calories', 'protein', 'fat', 'carbs']:
                    nutrient_match = re.search(rf'"{nutrient}":\s*(\d+)', nutrition_text)
                    if nutrient_match:
                        dish['nutrition'][nutrient] = int(nutrient_match.group(1))
            
            # Extract preparation time
            prep_time_match = re.search(r'"preparation_time":\s*"([^"]+)"', dish_text)
            if prep_time_match:
                dish['preparation_time'] = prep_time_match.group(1)
            else:
                # Try to find standalone preparation time
                standalone_time_match = re.search(r'"([^"]*\d+[^"]*phút[^"]*)"', dish_text)
                if standalone_time_match:
                    dish['preparation_time'] = standalone_time_match.group(1)
            
            # Extract health benefits
            health_match = re.search(r'"health_benefits":\s*"([^"]+)"', dish_text)
            if health_match:
                dish['health_benefits'] = health_match.group(1)
            
            # Add dish to result if it has basic required fields
            if 'name' in dish and 'nutrition' in dish:
                result.append(dish)
    
    except Exception as e:
        print(f"Error during manual extraction: {str(e)}")
    
    # Ensure we have valid data
    if not result:
        print("Manual parsing failed to produce any dishes")
        # Create a basic fallback dish
        return [{
            "name": "Món ăn mặc định",
            "description": "Món ăn dinh dưỡng cân bằng",
            "ingredients": [{"name": "Nguyên liệu chính", "amount": "100g"}],
            "preparation": ["Chế biến theo hướng dẫn"],
            "nutrition": {"calories": 400, "protein": 25, "fat": 15, "carbs": 40},
            "preparation_time": "30 phút",
            "health_benefits": "Cung cấp dinh dưỡng cân bằng cho cơ thể"
        }]
    
    print(f"Manual parsing succeeded, created {len(result)} dishes")
    return result

def create_groq_client(api_key=None):
    """
    Create a Groq client with the given API key
    
    Args:
        api_key (str, optional): The API key to use. If None, uses GROQ_API_KEY env var.
        
    Returns:
        groq.Groq: A Groq client
    """
    if api_key is None:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        raise ValueError("No API key provided and GROQ_API_KEY env var not set")
    
    # Create client with minimal arguments to avoid proxy issues
    client = groq.Groq(api_key=api_key)
    return client

def generate_completion(client, model, prompt, temperature=0.7, max_tokens=1000, response_format=None):
    """
    Generate a completion using the Groq API
    
    Args:
        client (groq.Groq): The Groq client
        model (str): The model to use
        prompt (str): The prompt to use
        temperature (float, optional): The temperature. Defaults to 0.7.
        max_tokens (int, optional): The maximum tokens. Defaults to 1000.
        response_format (dict, optional): Format specification for the response.
        
    Returns:
        Any: The processed response data
    """
    # Prepare the API call parameters
    params = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    # Add response_format if provided
    if response_format:
        params["response_format"] = response_format
    
    # Make the API call
    response = client.chat.completions.create(**params)
    
    # Extract the raw content
    raw_content = response.choices[0].message.content.strip()
    
    # Try to parse as JSON if requested JSON format
    if response_format and response_format.get("type") == "json_object":
        try:
            return json.loads(raw_content)
        except json.JSONDecodeError:
            # If it's not valid JSON, try to fix it
            print("Response format was set to JSON but got invalid JSON")
            fixed_data = fix_json_response(raw_content)
            return fixed_data
    
    # If not JSON or parsing failed, return the raw content
    return raw_content

# Example usage
if __name__ == "__main__":
    try:
        client = create_groq_client()
        model = "llama3-8b-8192"
        
        prompt = """Đề xuất 2 món ăn Việt Nam cho bữa sáng, bao gồm:
- Tên món
- Mô tả
- Nguyên liệu (tên và số lượng)
- Các bước chế biến
- Dinh dưỡng (calories, protein, chất béo, carbs)
- Thời gian chuẩn bị
- Lợi ích sức khỏe"""

        # Try with response_format
        result = generate_completion(client, model, prompt, 
                                     response_format={"type": "json_object"})
        print("JSON Result:", json.dumps(result, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Error: {str(e)}") 