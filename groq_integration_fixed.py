import os
import json
import time
import threading
import random
from typing import List, Dict, Optional, Tuple, Any
from models import NutritionInfo, Dish, Ingredient
from datetime import datetime
import logging
from groq import Groq
import requests
import re
from groq_client_fixed import fix_json_response

def fix_meal_json(response_text):
    """
    Fix JSON response specifically for meal data from Groq API
    """
    try:
        # 1. Clean up response
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*', '', response_text)
        response_text = response_text.strip()
        
        # 2. Fix missing "name" key in objects
        fixed_text = re.sub(r'{\s*"([^"]+)",', r'{"name": "\1",', response_text)
        
        # 3. Try to parse
        meals = json.loads(fixed_text)
        return meals
    except json.JSONDecodeError as e:
        print(f"Error fixing JSON: {e}, trying manual parsing")
        
        # Manual parsing for specific patterns
        result = []
        try:
            # Split into dishes
            dish_texts = re.findall(r'{\s*(?:"[^"]+"|\s*"name":\s*"[^"]+")(.*?)},?(?=\s*{|\s*\])', response_text, re.DOTALL)
            
            for dish_text in dish_texts:
                full_text = "{" + dish_text + "}"
                dish = {}
                
                # Extract name
                name_match = re.search(r'^\s*"([^"]+)"', dish_text)
                name_key_match = re.search(r'"name":\s*"([^"]+)"', full_text)
                
                if name_match:
                    dish['name'] = name_match.group(1)
                elif name_key_match:
                    dish['name'] = name_key_match.group(1)
                else:
                    continue
                
                # Extract other fields
                for field in ["description", "preparation_time", "health_benefits"]:
                    match = re.search(fr'"{field}":\s*"([^"]+)"', full_text)
                    if match:
                        dish[field] = match.group(1)
                
                # Get nutrition
                nutrition_match = re.search(r'"nutrition":\s*{\s*(.*?)\s*}', full_text, re.DOTALL)
                if nutrition_match:
                    nutrition = {}
                    nutrition_text = nutrition_match.group(1)
                    
                    for key in ["calories", "protein", "fat", "carbs"]:
                        value_match = re.search(fr'"{key}":\s*(\d+)', nutrition_text)
                        if value_match:
                            nutrition[key] = int(value_match.group(1))
                    
                    dish["nutrition"] = nutrition
                
                # Get basic fields if not empty
                if dish.get('name') and dish.get('nutrition'):
                    if "ingredients" not in dish:
                        dish["ingredients"] = [{"name": "Nguyên liệu chính", "amount": "100g"}]
                    if "preparation" not in dish:
                        dish["preparation"] = ["Chế biến theo hướng dẫn"]
                    result.append(dish)
            
            if result:
                return result
        except Exception as e:
            print(f"Manual parsing failed: {e}")
        
        return []  # Return empty array if all parsing attempts fail

# Import fallback data
from fallback_meals import FALLBACK_MEALS

# Try to import Groq library or fallback
try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    print("Groq client package not installed. Using fallback mode.")
    GROQ_AVAILABLE = False

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Các hằng số
DAYS_OF_WEEK = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
DEFAULT_MODEL = "llama3-70b-8192"  # Hoặc model Groq khác bạn muốn sử dụng

class RateLimiter:
    """Simple rate limiter to prevent API overuse."""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_day: int = 1000):
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        self.request_timestamps = []
        self.daily_request_count = 0
        self.day_start = datetime.now().date()
    
    def can_make_request(self) -> Tuple[bool, int]:
        """
        Check if a request can be made based on rate limits.
        
        Returns:
            Tuple of (can_request: bool, wait_time: int)
        """
        # Reset daily count if it's a new day
        current_day = datetime.now().date()
        if current_day != self.day_start:
            self.day_start = current_day
            self.daily_request_count = 0
        
        # Check daily limit
        if self.daily_request_count >= self.requests_per_day:
            seconds_in_day = 24 * 60 * 60
            return False, seconds_in_day
        
        # Check per-minute limit
        current_time = time.time()
        
        # Remove timestamps older than 1 minute
        minute_ago = current_time - 60
        self.request_timestamps = [ts for ts in self.request_timestamps if ts > minute_ago]
        
        # Check if we've hit the per-minute limit
        if len(self.request_timestamps) >= self.requests_per_minute:
            oldest = min(self.request_timestamps)
            wait_time = int(60 - (current_time - oldest)) + 1
            return False, wait_time
        
        return True, 0
    
    def record_request(self):
        """Record that a request was made."""
        self.request_timestamps.append(time.time())
        self.daily_request_count += 1

class GroqService:
    """Service to interact with Groq API for meal planning."""
    
    def __init__(self, api_key: str = os.getenv("GROQ_API_KEY")):
        """
        Initialize Groq service.
        
        Args:
            api_key: Groq API key
        """
        self._api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self._api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable.")
        
        self._client = Groq(api_key=self._api_key)
        self._model = DEFAULT_MODEL
        self._cache = {}  # Simple in-memory cache
        self._rate_limiter = RateLimiter()
        
        # Log successful initialization
        logger.info("GroqService initialized successfully")
    
    def generate_meal_suggestions(
        self,
        calories_target: int,
        protein_target: int,
        fat_target: int,
        carbs_target: int,
        meal_type: str,
        preferences: List[str] = None,
        allergies: List[str] = None,
        cuisine_style: str = None,
        use_ai: bool = True,  # Parameter to disable AI
        user_data: Dict = None  # Add parameter for user data
    ) -> List[Dict]:
        """
        Generate meal suggestions based on nutritional targets and preferences.
        
        Args:
            calories_target: Target calories for the meal
            protein_target: Target protein in grams
            fat_target: Target fat in grams
            carbs_target: Target carbs in grams
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            preferences: List of food preferences
            allergies: List of food allergies
            cuisine_style: Preferred cuisine style
            use_ai: Whether to use AI or fallback to static data
            user_data: Additional user data including health conditions
            
        Returns:
            List of meal suggestions
        """
        # Normalize meal type
        meal_type = meal_type.lower()
        
        # Log function call
        logger.info(f"Generating meal suggestions for {meal_type} with targets: {calories_target}cal, {protein_target}g protein")
        
        # If AI is disabled, return fallback meals
        if not use_ai:
            logger.info("AI generation disabled, using fallback meals")
            return self._fallback_meal_suggestions(meal_type)
        
        # Check if we can make a request (rate limiting)
        can_request, wait_time = self._rate_limiter.can_make_request()
        if not can_request:
            logger.warning(f"Rate limit exceeded, wait {wait_time}s. Using fallback meals.")
            return self._fallback_meal_suggestions(meal_type)
        
        # Extract health-related information from user_data
        health_conditions = []
        diet_restrictions = []
        diet_preference = None
        fiber_target = None
        sugar_target = None
        sodium_target = None
        
        if user_data:
            health_conditions = user_data.get("health_conditions", [])
            diet_restrictions = user_data.get("diet_restrictions", [])
            diet_preference = user_data.get("diet_preference")
            fiber_target = user_data.get("fiber_target")
            sugar_target = user_data.get("sugar_target")
            sodium_target = user_data.get("sodium_target")
            
            # If allergies is empty in main args but exists in user_data, use that
            if not allergies and "allergies" in user_data:
                allergies = user_data.get("allergies", [])
        
        # Ensure lists are not None
        preferences = preferences or []
        allergies = allergies or []
        health_conditions = health_conditions or []
        diet_restrictions = diet_restrictions or []
        
        # Create cache key
        cache_key = f"{meal_type}_{calories_target}_{protein_target}_{fat_target}_{carbs_target}"
        if preferences:
            cache_key += f"_pref_{'_'.join(sorted(preferences))}"
        if allergies:
            cache_key += f"_allergy_{'_'.join(sorted(allergies))}"
        if cuisine_style:
            cache_key += f"_cuisine_{cuisine_style}"
        if health_conditions:
            cache_key += f"_health_{'_'.join(sorted(health_conditions))}"
        if diet_restrictions:
            cache_key += f"_diet_{'_'.join(sorted(diet_restrictions))}"
        if diet_preference:
            cache_key += f"_dietpref_{diet_preference}"
        
        # Check cache
        if cache_key in self._cache:
            logger.info(f"Cache hit for key: {cache_key}")
            return self._cache[cache_key]
        
        try:
            # Generate prompt
            prompt = self._generate_meal_prompt(
                calories_target=calories_target,
                protein_target=protein_target,
                fat_target=fat_target,
                carbs_target=carbs_target,
                meal_type=meal_type,
                preferences=preferences,
                allergies=allergies,
                cuisine_style=cuisine_style,
                health_conditions=health_conditions,
                diet_restrictions=diet_restrictions,
                diet_preference=diet_preference,
                fiber_target=fiber_target,
                sugar_target=sugar_target,
                sodium_target=sodium_target
            )
            
            # Make API call
            completion = self._client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a nutrition expert specializing in meal planning."},
                    {"role": "user", "content": prompt}
                ],
                model=self._model,
                temperature=0.5,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            response_text = completion.choices[0].message.content
            try:
                # First try to repair any JSON syntax issues
                fixed_json_text = fix_json_response(response_text)
                response_json = json.loads(fixed_json_text)
                
                # Process meals
                if "meals" in response_json:
                    meals = response_json["meals"]
                    
                    # Update cache
                    self._cache[cache_key] = meals
                    self._rate_limiter.record_request()
                    
                    return meals
                else:
                    logger.error("Response format error: 'meals' key missing")
                    return self._fallback_meal_suggestions(meal_type)
            except Exception as e:
                logger.error(f"Error parsing JSON response: {str(e)}")
                logger.error(f"Raw response: {response_text[:200]}")  # Log first 200 chars
                return self._fallback_meal_suggestions(meal_type)
                
        except Exception as e:
            logger.error(f"Error generating meal suggestions: {str(e)}")
            return self._fallback_meal_suggestions(meal_type)
    
    def _generate_meal_prompt(
        self,
        calories_target: int,
        protein_target: int,
        fat_target: int,
        carbs_target: int,
        meal_type: str,
        preferences: List[str],
        allergies: List[str],
        cuisine_style: str = None,
        health_conditions: List[str] = None,
        diet_restrictions: List[str] = None,
        diet_preference: str = None,
        fiber_target: int = None,
        sugar_target: int = None,
        sodium_target: int = None
    ) -> str:
        """Generate a prompt for meal suggestions based on parameters."""
        prompt = f"""Generate 2 unique meal suggestions for {meal_type} with the following nutritional targets:
- Calories: {calories_target} calories
- Protein: {protein_target} grams
- Fat: {fat_target} grams
- Carbohydrates: {carbs_target} grams
"""

        # Add additional nutrition targets if provided
        if fiber_target:
            prompt += f"- Fiber: {fiber_target} grams\n"
        if sugar_target:
            prompt += f"- Sugar: maximum {sugar_target} grams\n"
        if sodium_target:
            prompt += f"- Sodium: maximum {sodium_target} mg\n"

        # Add dietary preferences
        if preferences:
            prompt += f"\nFood preferences: {', '.join(preferences)}"
        
        # Add cuisine style
        if cuisine_style:
            prompt += f"\nPreferred cuisine style: {cuisine_style}"
        
        # Add diet preference (vegetarian, vegan, etc.)
        if diet_preference:
            prompt += f"\nDiet preference: {diet_preference}"
        
        # Add dietary restrictions
        if diet_restrictions:
            prompt += f"\nDietary restrictions: {', '.join(diet_restrictions)}"
        
        # Add allergies with STRONG EMPHASIS
        if allergies:
            prompt += f"\n\nIMPORTANT - FOOD ALLERGIES - DO NOT INCLUDE THESE INGREDIENTS: {', '.join(allergies)}"
        
        # Add health conditions with CLEAR GUIDANCE
        if health_conditions:
            prompt += f"\n\nIMPORTANT - HEALTH CONDITIONS TO CONSIDER: {', '.join(health_conditions)}"
            prompt += "\nAdjust the meal suggestions to be appropriate for these health conditions by:"
            prompt += "\n- For diabetes: lower glycemic index foods, limit simple carbs"
            prompt += "\n- For hypertension: lower sodium options"
            prompt += "\n- For heart disease: heart-healthy fats, low saturated fat"
            prompt += "\n- For kidney disease: controlled phosphorus, potassium, and protein"
            prompt += "\n- For celiac disease: strictly gluten-free options"
        
        # Additional instructions for better structured output
        prompt += """

Please respond with a JSON object with the following structure:
{
  "meals": [
    {
      "name": "Meal name",
      "ingredients": ["ingredient 1", "ingredient 2", ...],
      "recipe": "Step-by-step preparation instructions",
      "nutrition": {
        "calories": calories value,
        "protein": protein in grams,
        "fat": fat in grams,
        "carbs": carbs in grams,
        "fiber": fiber in grams (if available),
        "sugar": sugar in grams (if available),
        "sodium": sodium in mg (if available)
      }
    },
    ...
  ]
}

DO NOT use commas instead of colons between key and value. Always format as: "key": "value"
"""
        # Log prompt for debugging
        logger.debug(f"Generated prompt: {prompt}")
        return prompt
    
    def _get_fallback_meals(self, meal_type: str) -> List[Dict]:
        """Get fallback meals for when AI generation fails."""
        fallback_meals = {
            "breakfast": [
                {
                    "name": "Oatmeal with Fruit and Nuts",
                    "ingredients": ["1/2 cup rolled oats", "1 cup milk", "1 banana", "1 tbsp honey", "10g almonds"],
                    "recipe": "Cook oats with milk. Top with sliced banana, honey, and almonds.",
                    "nutrition": {
                        "calories": 350,
                        "protein": 15,
                        "fat": 10,
                        "carbs": 50,
                        "fiber": 5
                    }
                },
                {
                    "name": "Vegetable Omelette",
                    "ingredients": ["2 eggs", "30g spinach", "30g bell peppers", "20g onions", "10g cheese", "5ml olive oil"],
                    "recipe": "Sauté vegetables. Beat eggs and pour over vegetables. Add cheese and fold.",
                    "nutrition": {
                        "calories": 300,
                        "protein": 20,
                        "fat": 20,
                        "carbs": 5,
                        "fiber": 2
                    }
                }
            ],
            "lunch": [
                {
                    "name": "Grilled Chicken Salad",
                    "ingredients": ["100g chicken breast", "100g mixed greens", "30g cherry tomatoes", "30g cucumber", "10g olive oil", "5g vinegar"],
                    "recipe": "Grill chicken. Mix with vegetables and dress with olive oil and vinegar.",
                    "nutrition": {
                        "calories": 400,
                        "protein": 35,
                        "fat": 15,
                        "carbs": 10,
                        "fiber": 3
                    }
                },
                {
                    "name": "Quinoa Bowl with Vegetables",
                    "ingredients": ["100g quinoa", "100g mixed vegetables", "50g chickpeas", "10g olive oil", "Herbs and spices"],
                    "recipe": "Cook quinoa. Sauté vegetables. Mix everything together with olive oil and seasonings.",
                    "nutrition": {
                        "calories": 450,
                        "protein": 15,
                        "fat": 15,
                        "carbs": 60,
                        "fiber": 8
                    }
                }
            ],
            "dinner": [
                {
                    "name": "Baked Salmon with Sweet Potato",
                    "ingredients": ["150g salmon fillet", "150g sweet potato", "100g broccoli", "5g olive oil", "Lemon, herbs"],
                    "recipe": "Bake salmon with lemon and herbs. Roast sweet potato. Steam broccoli.",
                    "nutrition": {
                        "calories": 500,
                        "protein": 40,
                        "fat": 20,
                        "carbs": 30,
                        "fiber": 6
                    }
                },
                {
                    "name": "Turkey Stir-fry with Brown Rice",
                    "ingredients": ["100g turkey breast", "100g mixed vegetables", "50g brown rice", "10g soy sauce", "5g olive oil"],
                    "recipe": "Cook rice. Stir-fry turkey with vegetables and soy sauce. Serve over rice.",
                    "nutrition": {
                        "calories": 450,
                        "protein": 35,
                        "fat": 10,
                        "carbs": 50,
                        "fiber": 4
                    }
                }
            ],
            "snack": [
                {
                    "name": "Greek Yogurt with Berries",
                    "ingredients": ["150g Greek yogurt", "50g mixed berries", "10g honey"],
                    "recipe": "Mix yogurt with berries and drizzle with honey.",
                    "nutrition": {
                        "calories": 200,
                        "protein": 15,
                        "fat": 5,
                        "carbs": 20,
                        "fiber": 3
                    }
                },
                {
                    "name": "Apple with Almond Butter",
                    "ingredients": ["1 medium apple", "15g almond butter"],
                    "recipe": "Slice apple and serve with almond butter for dipping.",
                    "nutrition": {
                        "calories": 200,
                        "protein": 5,
                        "fat": 10,
                        "carbs": 25,
                        "fiber": 5
                    }
                }
            ]
        }
        
        return fallback_meals.get(meal_type.lower(), fallback_meals["snack"])
    
    def _fallback_meal_suggestions(self, meal_type: str) -> List[Dict]:
        """Return fallback meal suggestions."""
        logger.info(f"Using fallback meals for {meal_type}")
        return self._get_fallback_meals(meal_type)
    
    def clear_cache(self):
        """Clear the cache."""
        self._cache = {}
        return {"status": "success", "message": "Cache cleared", "cache_size": 0}
    
    def get_cache_info(self):
        """Get information about the cache."""
        return {
            "status": "success",
            "cache_size": len(self._cache),
            "cache_keys": list(self._cache.keys())
        }

# Initialize service singleton
groq_service = GroqService() 