"""
A fresh implementation of a simple Groq client to work around proxy issues
"""
import os
import groq
import re
import json

def fix_json_response(response_text):
    """
    Fix common JSON syntax errors in responses from Groq
    
    Args:
        response_text (str): The raw response text from Groq
        
    Returns:
        str: Fixed JSON string
    """
    # 1. Clean up the response - remove markdown code blocks
    response_text = re.sub(r'```json\s*', '', response_text)
    response_text = re.sub(r'```\s*', '', response_text)
    response_text = response_text.strip()
    
    # 2. Fix specific error pattern: Missing "name" key for the first value in objects
    # Pattern: {"StringValue", "key": "value"} → {"name": "StringValue", "key": "value"}
    response_text = re.sub(r'{\s*"([^"]+)",', r'{"name": "\1",', response_text)
    
    # 3. Extract JSON portion if needed
    json_start = response_text.find('[')
    json_end = response_text.rfind(']') + 1
    
    if json_start != -1 and json_end != -1:
        response_text = response_text[json_start:json_end]
    
    # 4. Try to parse the fixed JSON
    try:
        json.loads(response_text)
        return response_text
    except json.JSONDecodeError as e:
        print(f"Error after first fix: {e}")
        
        # 5. Attempt more aggressive fixes
        try:
            # Create a manual structure for the meals
            result = []
            
            # Use regex to find meal objects between curly braces
            meal_pattern = r'{\s*(?:"[^"]+"|"name":\s*"[^"]+")(.*?)}'
            meals = re.finditer(meal_pattern, response_text, re.DOTALL)
            
            for meal_match in meals:
                meal_text = meal_match.group(0)
                meal = {}
                
                # Extract name
                name_match = re.search(r'{\s*"([^"]+)"', meal_text) or \
                            re.search(r'"name":\s*"([^"]+)"', meal_text)
                
                if name_match:
                    meal['name'] = name_match.group(1)
                else:
                    continue  # Skip meals without names
                
                # Extract description
                desc_match = re.search(r'"description":\s*"([^"]+)"', meal_text)
                if desc_match:
                    meal['description'] = desc_match.group(1)
                
                # Extract nutrition info
                nutrition = {}
                nutr_match = re.search(r'"nutrition":\s*{(.*?)}', meal_text, re.DOTALL)
                if nutr_match:
                    nutr_text = nutr_match.group(1)
                    
                    for key in ["calories", "protein", "fat", "carbs"]:
                        val_match = re.search(fr'"({key})":\s*(\d+)', nutr_text)
                        if val_match:
                            nutrition[val_match.group(1)] = int(val_match.group(2))
                
                if nutrition:
                    meal['nutrition'] = nutrition
                
                # Add basic fields
                if 'name' in meal:
                    # Fill in required fields if missing
                    if 'description' not in meal:
                        meal['description'] = f"Món ăn {meal['name']} thơm ngon bổ dưỡng"
                    
                    if 'ingredients' not in meal:
                        meal['ingredients'] = [{"name": "Nguyên liệu chính", "amount": "100g"}]
                    
                    if 'preparation' not in meal:
                        meal['preparation'] = ["Chế biến theo hướng dẫn"]
                    
                    if 'preparation_time' not in meal:
                        meal['preparation_time'] = "30 phút"
                    
                    if 'health_benefits' not in meal:
                        meal['health_benefits'] = f"Món ăn {meal['name']} cung cấp dinh dưỡng cân bằng"
                    
                    if 'nutrition' not in meal:
                        meal['nutrition'] = {"calories": 400, "protein": 25, "fat": 15, "carbs": 40}
                    
                    result.append(meal)
            
            if result:
                return json.dumps(result)
        except Exception as ex:
            print(f"Error during manual parsing: {ex}")
    
    # If all else fails, return an empty valid array
    return '[]'

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

def get_available_models(client):
    """
    Get available models from the Groq API
    
    Args:
        client (groq.Groq): The Groq client
        
    Returns:
        list: A list of available model IDs
    """
    models = client.models.list()
    return [model.id for model in models.data]
    
def generate_completion(client, model, prompt, temperature=0.7, max_tokens=1000):
    """
    Generate a completion using the Groq API
    
    Args:
        client (groq.Groq): The Groq client
        model (str): The model to use
        prompt (str): The prompt to use
        temperature (float, optional): The temperature. Defaults to 0.7.
        max_tokens (int, optional): The maximum tokens. Defaults to 1000.
        
    Returns:
        str: The generated text
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    
    return response.choices[0].message.content.strip()

# Example usage
if __name__ == "__main__":
    try:
        # Create client
        client = create_groq_client()
        print("Successfully created Groq client")
        
        # Get available models
        models = get_available_models(client)
        print(f"Available models: {', '.join(models)}")
        
        # Use a default model
        model = "llama3-8b-8192" if "llama3-8b-8192" in models else models[0]
        print(f"Using model: {model}")
        
        # Generate a simple completion
        prompt = "Say hello in 5 words or less"
        result = generate_completion(client, model, prompt)
        print(f"Response: {result}")
        
    except Exception as e:
        print(f"Error: {str(e)}") 