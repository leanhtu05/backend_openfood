"""
Script để kiểm tra phản hồi thô từ Groq API
"""
import os
import json
import time
from groq_integration_direct import DirectGroqClient

def test_groq_raw_output():
    """Kiểm tra phản hồi thô từ Groq API"""
    
    print("\n=== TESTING GROQ RAW OUTPUT ===")
    
    # Khởi tạo client
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("ERROR: No GROQ_API_KEY found in environment variables")
        return
    
    print(f"API Key: {'***' + api_key[-4:] if api_key else 'None'}")
    
    try:
        client = DirectGroqClient(api_key=api_key)
        print("Successfully initialized DirectGroqClient")
        
        # Lấy danh sách model
        models = client.list_models()
        print(f"\nAvailable models: {', '.join(models)}")
        
        # Sử dụng model LLaMA 3
        model = "llama3-8b-8192"
        if model not in models:
            model = models[0]  # Fallback to first available model
        
        print(f"\nUsing model: {model}")
        
        # Tạo prompt đơn giản yêu cầu trả về JSON
        prompt = """You are a nutrition expert, please suggest 1 meal for breakfast with the following criteria:
- Total calories: 500kcal
- Protein amount: 30g
- Fat amount: 15g
- Carbohydrate amount: 60g

Your response MUST be a valid JSON array with EXACTLY this format:
[
  {
    "name": "Meal name",
    "description": "Brief description of the meal",
    "ingredients": [
      {"name": "Ingredient name", "amount": "Amount", "calories": 100, "protein": 10, "fat": 5, "carbs": 15}
    ],
    "total_nutrition": {"calories": 400, "protein": 20, "fat": 15, "carbs": 45}
  }
]

IMPORTANT: Return ONLY the JSON array with no additional text. Do not include markdown code blocks or any explanations.
"""
        
        print("\nSending prompt to Groq API...")
        print("\n--- PROMPT ---")
        print(prompt)
        print("--- END PROMPT ---\n")
        
        # Test với nhiều temperature khác nhau
        temperatures = [0.7, 0.5, 0.3]
        
        for temp in temperatures:
            print(f"\n=== TESTING WITH TEMPERATURE: {temp} ===")
            
            try:
                start_time = time.time()
                response = client.generate_completion(
                    model=model,
                    prompt=prompt,
                    temperature=temp,
                    max_tokens=1000,
                    top_p=0.95
                )
                end_time = time.time()
                
                print(f"Response time: {end_time - start_time:.2f} seconds")
                
                # Phân tích phản hồi
                if "choices" in response and len(response["choices"]) > 0:
                    content = response["choices"][0]["message"]["content"].strip()
                    print("\n--- RAW RESPONSE ---")
                    print(content)
                    print("--- END RAW RESPONSE ---\n")
                    
                    # Thử parse JSON
                    try:
                        # Kiểm tra nếu phản hồi bắt đầu với ```json và kết thúc với ```
                        if content.startswith("```json") and "```" in content[7:]:
                            json_content = content.split("```json", 1)[1].split("```", 1)[0].strip()
                        elif content.startswith("```") and "```" in content[3:]:
                            json_content = content.split("```", 1)[1].split("```", 1)[0].strip()
                        else:
                            json_content = content
                            
                        data = json.loads(json_content)
                        print("✅ Successfully parsed JSON")
                        print(f"JSON structure: {type(data)}")
                        if isinstance(data, list):
                            print(f"Number of items: {len(data)}")
                            if len(data) > 0:
                                print(f"First item keys: {list(data[0].keys())}")
                        print(json.dumps(data, indent=2)[:500] + "..." if len(json.dumps(data, indent=2)) > 500 else json.dumps(data, indent=2))
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse JSON: {e}")
                        
                        # Tìm chuỗi JSON bằng cách tìm [ và ]
                        json_start = content.find("[")
                        json_end = content.rfind("]") + 1
                        
                        if json_start >= 0 and json_end > json_start:
                            json_str = content[json_start:json_end]
                            print("\nAttempting to parse extracted JSON:")
                            try:
                                extracted_data = json.loads(json_str)
                                print("✅ Successfully parsed extracted JSON")
                                print(f"Extracted JSON: {json.dumps(extracted_data, indent=2)}")
                            except json.JSONDecodeError as e2:
                                print(f"❌ Failed to parse extracted JSON: {e2}")
                                print(f"Extracted string: {json_str}")
                else:
                    print("No content in response")
            
            except Exception as e:
                print(f"Error with temperature {temp}: {str(e)}")
        
        # Đóng client
        client.close()
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    print("\n=== TEST COMPLETED ===")

if __name__ == "__main__":
    test_groq_raw_output() 