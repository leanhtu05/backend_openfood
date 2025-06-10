"""
Service for food recognition using Gemini Vision Pro API
"""
import os
import base64
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import models
from models import RecognizedFood, NutritionInfo

# Try to import Gemini from Google Generative AI SDK
try:
    import google.generativeai as genai
    from google.generativeai.types.generation_types import GenerationConfig
    GEMINI_AVAILABLE = True
except ImportError:
    print("Google Generative AI SDK not installed. Use 'pip install google-generativeai'")
    GEMINI_AVAILABLE = False

class GeminiVisionService:
    """Service for food recognition using Google's Gemini Vision Pro"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini Vision service with API key
        
        Args:
            api_key: Gemini API key, from environment variable if not provided
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.available = GEMINI_AVAILABLE and self.api_key is not None
        
        # Initialize model
        if self.available:
            try:
                print("\n=== INITIALIZING GEMINI VISION SERVICE ===")
                print(f"API Key exists: {self.api_key is not None}")
                
                # Configure API key
                genai.configure(api_key=self.api_key)
                
                # Get Gemini Vision model
                self.model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                print("Gemini Vision service initialized successfully")
                print("=== GEMINI VISION SERVICE INITIALIZED ===\n")
            except Exception as e:
                print(f"ERROR initializing Gemini Vision: {str(e)}")
                import traceback
                traceback.print_exc()
                self.available = False
                self.model = None
        else:
            print("Gemini Vision service not available. Make sure to set GEMINI_API_KEY.")
            self.model = None
            
    def recognize_food(self, image_data: bytes) -> Tuple[List[RecognizedFood], Dict[str, Any]]:
        """
        Recognize food in an image using Gemini Vision Pro
        
        Args:
            image_data: Image bytes
            
        Returns:
            Tuple of recognized foods list and raw analysis
        """
        if not self.available or not self.model:
            raise ValueError("Gemini Vision service is not available.")
            
        try:
            # Encode image to base64 for API
            encoded_image = base64.b64encode(image_data).decode('utf-8')
            
            # Prepare prompt for Gemini Vision
            prompt = """
            Analyze this food image and provide comprehensive nutritional information:

            1. Identify all food items visible in the image
            2. For each identified food item, provide:
               - Name of the food (in Vietnamese and English)
               - Estimate of portion size
               - Comprehensive nutritional information including:
                 * Basic: calories, protein, fat, carbs
                 * Detailed: fiber, sugar, saturated fat, trans fat, cholesterol
                 * Minerals: sodium, potassium, calcium, iron
                 * Vitamins: vitamin C, vitamin A
                 * Special: caffeine (if applicable), alcohol (if applicable)
                 * Additional: glycemic index, water content

            Return your analysis in this exact JSON format:
            {
              "foods": [
                {
                  "name_vi": "Vietnamese name",
                  "name_en": "English name",
                  "confidence": 0.95,
                  "portion_size": "estimated portion (e.g., '1 cup', '200g')",
                  "nutrition": {
                    "calories": 200,
                    "protein": 10,
                    "fat": 5,
                    "carbs": 30,
                    "fiber": 3,
                    "sugar": 8,
                    "saturated_fat": 2,
                    "trans_fat": 0,
                    "cholesterol": 15,
                    "sodium": 300,
                    "potassium": 150,
                    "calcium": 50,
                    "iron": 2,
                    "vitamin_c": 10,
                    "vitamin_a": 100,
                    "caffeine": 0,
                    "alcohol": 0,
                    "glycemic_index": 55,
                    "water_content": 85
                  }
                }
              ]
            }

            Important guidelines:
            - Provide realistic estimates based on typical nutritional values for the food type
            - Use null for nutrients that are not applicable (e.g., caffeine in vegetables)
            - For glycemic index: Low (0-55), Medium (56-69), High (70-100)
            - Water content as percentage (0-100)
            - All mineral/vitamin values should be reasonable for the portion size
            - Do not include explanations or text outside the JSON
            """
            
            # Configure generation parameters
            generation_config = GenerationConfig(
                temperature=0.4,
                top_p=1.0,
                top_k=32,
                max_output_tokens=2048,
            )
            
            # Call Gemini Vision API
            response = self.model.generate_content(
                contents=[
                    {"role": "user", "parts": [
                        {"text": prompt},
                        {"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}}
                    ]}
                ],
                generation_config=generation_config
            )
            
            # Extract response text
            result_text = response.text
            
            # Parse JSON from response
            try:
                # Find JSON in response (handle if there's text around it)
                start_idx = result_text.find('{')
                end_idx = result_text.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = result_text[start_idx:end_idx]
                    result = json.loads(json_str)
                else:
                    result = {"foods": []}
            except json.JSONDecodeError:
                result = {"foods": []}
                print(f"Error parsing JSON from Gemini response: {result_text[:500]}")
                
            # Convert to RecognizedFood objects
            recognized_foods = []
            for food in result.get("foods", []):
                # Use Vietnamese name if available, fallback to English
                food_name = food.get("name_vi") or food.get("name_en") or "Không xác định"
                
                # Create NutritionInfo from response with comprehensive data (optional)
                nutrition_data = food.get("nutrition", {})

                # Helper function to safely convert to float or None
                def safe_float(value):
                    if value is None or value == "":
                        return None
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return None

                # Helper function to safely convert to int or None
                def safe_int(value):
                    if value is None or value == "":
                        return None
                    try:
                        return int(value)
                    except (ValueError, TypeError):
                        return None

                nutrition = NutritionInfo(
                    # Basic nutrition (required)
                    calories=float(nutrition_data.get("calories", 0)),
                    protein=float(nutrition_data.get("protein", 0)),
                    fat=float(nutrition_data.get("fat", 0)),
                    carbs=float(nutrition_data.get("carbs", 0)),

                    # Detailed nutrition (optional)
                    fiber=safe_float(nutrition_data.get("fiber")),
                    sugar=safe_float(nutrition_data.get("sugar")),
                    saturated_fat=safe_float(nutrition_data.get("saturated_fat")),
                    trans_fat=safe_float(nutrition_data.get("trans_fat")),
                    cholesterol=safe_float(nutrition_data.get("cholesterol")),
                    sodium=safe_float(nutrition_data.get("sodium")),
                    potassium=safe_float(nutrition_data.get("potassium")),
                    calcium=safe_float(nutrition_data.get("calcium")),
                    iron=safe_float(nutrition_data.get("iron")),
                    vitamin_c=safe_float(nutrition_data.get("vitamin_c")),
                    vitamin_a=safe_float(nutrition_data.get("vitamin_a")),
                    caffeine=safe_float(nutrition_data.get("caffeine")),
                    alcohol=safe_float(nutrition_data.get("alcohol")),
                    glycemic_index=safe_int(nutrition_data.get("glycemic_index")),
                    water_content=safe_float(nutrition_data.get("water_content"))
                )
                
                # Create RecognizedFood object
                recognized_food = RecognizedFood(
                    food_name=food_name,
                    confidence=float(food.get("confidence", 0.5)),
                    nutrition=nutrition,
                    portion_size=food.get("portion_size", "Không xác định")
                )
                
                recognized_foods.append(recognized_food)
                
            return recognized_foods, result
            
        except Exception as e:
            print(f"Error recognizing food with Gemini: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return empty results on error
            return [], {"error": str(e)}

# Create singleton instance for application
gemini_vision_service = GeminiVisionService() 