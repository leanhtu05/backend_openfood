import os
import json
import time
import threading
import random
from typing import List, Dict, Optional, Tuple
from models import NutritionInfo, Dish, Ingredient

# Import fallback data
from fallback_meals import FALLBACK_MEALS

# Try to import Groq library or fallback
try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    print("Groq client package not installed. Using fallback mode.")
    GROQ_AVAILABLE = False

class RateLimiter:
    """Manages API rate limits"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_day: int = 1000):
        """
        Initialize rate limiter
        
        Args:
            requests_per_minute: Maximum requests per minute
            requests_per_day: Maximum requests per day
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        self.minute_requests = 0
        self.day_requests = 0
        self.minute_reset_time = time.time() + 60  # Reset after 1 minute
        self.day_reset_time = time.time() + 86400  # Reset after 1 day
        self.lock = threading.Lock()
    
    def can_make_request(self) -> Tuple[bool, int]:
        """
        Check if a request can be made
        
        Returns:
            Tuple[bool, int]: (Can make request, wait time in seconds)
        """
        with self.lock:
            current_time = time.time()
            
            # Reset minute counter if needed
            if current_time > self.minute_reset_time:
                self.minute_requests = 0
                self.minute_reset_time = current_time + 60
            
            # Reset day counter if needed
            if current_time > self.day_reset_time:
                self.day_requests = 0
                self.day_reset_time = current_time + 86400
            
            # Check limits
            if self.minute_requests < self.requests_per_minute and self.day_requests < self.requests_per_day:
                self.minute_requests += 1
                self.day_requests += 1
                return True, 0
            
            # Calculate wait time
            wait_time = min(
                self.minute_reset_time - current_time,
                self.day_reset_time - current_time
            )
            
            # Add jitter to avoid thundering herd
            wait_time += random.uniform(1, 5)
            
            return False, max(1, int(wait_time))

class GroqService:
    """Integration service with LLaMA 3 via Groq for intelligent meal planning"""
    
    def __init__(self, api_key: str = os.getenv("GROQ_API_KEY")):
        """
        Initialize Groq service with API key
        
        Args:
            api_key: Groq API key, from environment variable if not provided
        """
        self.api_key = api_key
        self.available = GROQ_AVAILABLE and api_key is not None
        
        # Initialize cache and rate limiter
        self.cache = {}
        self.rate_limiter = RateLimiter(requests_per_minute=60, requests_per_day=1000)
        self.max_retries = 3
        
        # Add variables to track quota status
        self.quota_exceeded = False
        self.quota_reset_time = None
        
        # Default model using LLaMA 3
        self.default_model = "llama3-8b-8192"
        self.client = None
        self.model = self.default_model
        
        if self.available:
            try:
                print("\n=== INITIALIZING GROQ SERVICE ===")
                print(f"API Key: {'***' + self.api_key[-4:] if self.api_key else 'None'}")
                
                # Initialize client simply (Groq 0.4.0 version)
                try:
                    # FIXED: Use dynamic import to get the class and initialize without proxies
                    from importlib import import_module
                    groq_module = import_module('groq')
                    self.client = groq_module.Groq(api_key=self.api_key)
                except Exception as e:
                    print(f"Error initializing Groq client: {str(e)}")
                    self.available = False
                    return
                
                # Priority list of models to try
                self.preferred_models = [
                    "llama3-70b-8192",  # LLaMA 3 70B - Strongest model
                    "llama3-8b-8192",   # LLaMA 3 8B - Balance of speed and performance
                    "mixtral-8x7b-32768"  # Mixtral - Fallback if LLaMA is not available
                ]
                
                # Check available models
                if self.client:
                    try:
                        print("Fetching available models...")
                        models = self.client.models.list()
                        available_models = [model.id for model in models.data]
                        
                        print("Available models:")
                        for model_name in available_models:
                            print(f"- {model_name}")
                        
                        # Find first available preferred model
                        selected_model = None
                        for model_name in self.preferred_models:
                            if model_name in available_models:
                                selected_model = model_name
                                break
                        
                        # If no preferred model found, use default model
                        if not selected_model:
                            selected_model = self.default_model
                        
                        self.model = selected_model
                        print(f"Using model: {self.model}")
                        
                    except Exception as e:
                        print(f"Error fetching models: {str(e)}")
                        print(f"Using default model: {self.default_model}")
                        self.model = self.default_model
                
                print("Groq initialization successful")
                print("=== GROQ SERVICE INITIALIZED ===\n")
            except Exception as e:
                print(f"ERROR initializing Groq: {str(e)}")
                import traceback
                traceback.print_exc()
                self.available = False
        
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
        use_ai: bool = True  # Parameter to disable AI
    ) -> List[Dict]:
        """
        Generate meal suggestions using LLaMA 3 via Groq
        
        Args:
            calories_target: Calorie target
            protein_target: Protein target (g)
            fat_target: Fat target (g)
            carbs_target: Carbs target (g)
            meal_type: Meal type (breakfast, lunch, dinner)
            preferences: List of food preferences (optional)
            allergies: List of food allergies (optional)
            cuisine_style: Cuisine style (optional)
            use_ai: Whether to use AI or use fallback data
            
        Returns:
            List of meal suggestions as dictionaries
        """
        # Check if AI is disabled or quota exceeded
        if not use_ai or self.quota_exceeded:
            # Check if quota has been reset
            if self.quota_exceeded and self.quota_reset_time:
                current_time = time.time()
                if current_time > self.quota_reset_time:
                    print("Quota reset time has passed. Trying to use API again.")
                    self.quota_exceeded = False
                    self.quota_reset_time = None
                else:
                    print(f"Quota exceeded. Using fallback data. Reset in: {int(self.quota_reset_time - current_time)} seconds")
                    return self._fallback_meal_suggestions(meal_type)
            elif not use_ai:
                print("AI usage turned off. Using fallback data.")
                return self._fallback_meal_suggestions(meal_type)
            else:
                print("Quota exceeded. Using fallback data.")
                return self._fallback_meal_suggestions(meal_type)
                
        # If AI is not available
        if not self.available:
            print("Groq API not available. Using fallback data.")
            return self._fallback_meal_suggestions(meal_type)
        
        # Create cache key
        cache_key = f"{meal_type}_{calories_target}_{protein_target}_{fat_target}_{carbs_target}"
        if preferences:
            cache_key += f"_prefs:{'|'.join(preferences)}"
        if allergies:
            cache_key += f"_allergies:{'|'.join(allergies)}"
        if cuisine_style:
            cache_key += f"_cuisine:{cuisine_style}"
        
        # Check cache
        if cache_key in self.cache:
            print(f"Using cached meal suggestions for: {cache_key}")
            return self.cache[cache_key]
        
        # Check rate limit
        can_request, wait_time = self.rate_limiter.can_make_request()
        if not can_request:
            print(f"Rate limit reached. Using fallback data. Try again in {wait_time} seconds.")
            return self._fallback_meal_suggestions(meal_type)
        
        # Create prompt for LLaMA
        preferences_str = ", ".join(preferences) if preferences else "none"
        allergies_str = ", ".join(allergies) if allergies else "none"
        cuisine_style_str = cuisine_style if cuisine_style else "no specific requirement"

        # Optimize prompt for LLaMA 3
        prompt = f"""You are a nutrition expert, please suggest 5 Vietnamese meals for {meal_type} with the following criteria:
- Total calories: {calories_target}kcal
- Protein amount: {protein_target}g
- Fat amount: {fat_target}g
- Carbohydrate amount: {carbs_target}g
- Preferences: {preferences_str}
- Allergies (avoid): {allergies_str}
- Cuisine style: {cuisine_style_str}

IMPORTANT REQUIREMENTS:
1. Write ALL meal names and descriptions in Vietnamese language
2. Include Vietnamese ingredients with Vietnamese names
3. Write detailed preparation instructions in Vietnamese with step-by-step cooking guide
4. Make sure to create DIFFERENT meals than usual. Be creative and diverse.
5. DO NOT include day names in meal names (no "Thứ 2", "Thứ 3", etc.)

Please return the result exactly in the following JSON format:
```json
[
  {{
    "name": "Meal name",
    "description": "Brief description of the meal",
    "ingredients": [
      {{"name": "Ingredient name", "amount": "Amount", "calories": 100, "protein": 10, "fat": 5, "carbs": 15}},
      ...
    ],
    "total_nutrition": {{"calories": 400, "protein": 20, "fat": 15, "carbs": 45}}
  }},
  ...
]
```

Ensure that the nutrition data for each meal is appropriate for the goals and the total of all ingredients matches the total nutrition for each meal.
Return EXACTLY the JSON format above without adding any other content.
"""
        
        try:
            # Call Groq API
            for attempt in range(self.max_retries):
                try:
                    print(f"Making request to Groq API, attempt {attempt + 1}/{self.max_retries}")
                    
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=2000,
                        top_p=0.95
                    )
                    
                    # Extract JSON result from response
                    result_text = response.choices[0].message.content.strip()
                    
                    # Extract JSON from result (may have other characters)
                    json_start = result_text.find("[")
                    json_end = result_text.rfind("]") + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = result_text[json_start:json_end]
                        try:
                            meal_data = json.loads(json_str)
                            
                            # Validate meal data
                            if isinstance(meal_data, list) and len(meal_data) > 0:
                                # Add more detailed checks to ensure valid data
                                valid_meals = []
                                for meal in meal_data:
                                    if (isinstance(meal, dict) and 
                                        'name' in meal and 
                                        'ingredients' in meal and 
                                        isinstance(meal['ingredients'], list)):
                                        
                                        # If preparation is missing, add a default description
                                        if 'preparation' not in meal or not meal['preparation']:
                                            meal['preparation'] = f"Prepare {meal['name']} with the listed ingredients."
                                        
                                        # Ensure ingredients is not empty
                                        if not meal['ingredients']:
                                            meal['ingredients'] = [{'name': 'Main ingredient', 'amount': '100g'}]
                                        
                                        valid_meals.append(meal)
                                
                                if valid_meals:
                                    # Save to cache
                                    self.cache[cache_key] = valid_meals
                                    return valid_meals
                                else:
                                    print("No valid meals in the result from AI. Using fallback data.")
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON from LLaMA response. Attempt {attempt + 1}")
                    
                    # If valid data couldn't be extracted, try again
                    print(f"Invalid response format. Retrying... ({attempt + 1}/{self.max_retries})")
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error calling Groq API: {str(e)} - Attempt {attempt + 1}/{self.max_retries}")
                    if "quota exceeded" in str(e).lower():
                        print("API quota exceeded")
                        self.quota_exceeded = True
                        self.quota_reset_time = time.time() + 3600  # Try again after 1 hour
                        break
                    time.sleep(2)
            
            # If no result after all attempts
            print("Failed to get valid response from Groq API after multiple attempts. Using fallback data.")
            return self._fallback_meal_suggestions(meal_type)
                
        except Exception as e:
            print(f"Error generating meal suggestions: {str(e)}")
            return self._fallback_meal_suggestions(meal_type)
    
    def _get_fallback_meals(self, meal_type: str) -> List[Dict]:
        """
        Get fallback meal data
        
        Args:
            meal_type: Meal type (breakfast, lunch, dinner)
            
        Returns:
            List of fallback meals
        """
        meal_type_lower = meal_type.lower()
        
        if "breakfast" in meal_type_lower or "morning" in meal_type_lower:
            return FALLBACK_MEALS.get("breakfast", [])
        elif "lunch" in meal_type_lower or "noon" in meal_type_lower:
            return FALLBACK_MEALS.get("lunch", [])
        elif "dinner" in meal_type_lower or "evening" in meal_type_lower:
            return FALLBACK_MEALS.get("dinner", [])
        else:
            # Return a mix of meals
            all_meals = []
            for meals_list in FALLBACK_MEALS.values():
                all_meals.extend(meals_list)
            
            # Shuffle the list to get random ones
            random.shuffle(all_meals)
            return all_meals[:5]  # Return maximum 5 meals
    
    def _fallback_meal_suggestions(self, meal_type: str) -> List[Dict]:
        """
        Return fallback data for meal type
        
        Args:
            meal_type: Meal type
            
        Returns:
            List of fallback meals
        """
        return self._get_fallback_meals(meal_type)
    
    def clear_cache(self):
        """Clear cache to force new data creation"""
        print("Clearing Groq service cache")
        self.cache = {}
    
    def get_cache_info(self):
        """
        Get information about the cache
        
        Returns:
            Cache information
        """
        return {
            "num_entries": len(self.cache),
            "keys": list(self.cache.keys())
        }

# Initialize service singleton
groq_service = GroqService() 