import os
import json
import time
import threading
import random
import httpx
from typing import List, Dict, Optional, Tuple
from models import NutritionInfo, Dish, Ingredient

# Import fallback data
from fallback_meals import FALLBACK_MEALS

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

class DirectGroqClient:
    """
    A simple client for the Groq API using direct HTTP requests
    """
    def __init__(self, api_key=None):
        """
        Initialize the client with the given API key
        
        Args:
            api_key (str, optional): The API key to use. If None, uses GROQ_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and GROQ_API_KEY env var not set")
        
        self.base_url = "https://api.groq.com/openai/v1"
        self.client = httpx.Client(timeout=60.0)
        self.client.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def list_models(self):
        """
        List available models
        
        Returns:
            list: A list of available model IDs
        """
        response = self.client.get(f"{self.base_url}/models")
        response.raise_for_status()
        data = response.json()
        return [model["id"] for model in data["data"]]
    
    def generate_completion(self, model, prompt, temperature=0.7, max_tokens=1000, top_p=0.95):
        """
        Generate a completion using the Groq API
        
        Args:
            model (str): The model to use
            prompt (str): The prompt to use
            temperature (float, optional): The temperature. Defaults to 0.7.
            max_tokens (int, optional): The maximum tokens. Defaults to 1000.
            top_p (float, optional): The top_p value. Defaults to 0.95.
            
        Returns:
            dict: The API response
        """
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p
        }
        
        print(f"Sending request to Groq API with model: {model}")
        print(f"Temperature: {temperature}, max_tokens: {max_tokens}, top_p: {top_p}")
        
        response = self.client.post(
            f"{self.base_url}/chat/completions",
            json=payload
        )
        response.raise_for_status()
        
        data = response.json()
        print(f"Raw Groq API response: {data}")
        
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"].strip()
            print(f"Raw content from Groq:\n{content}")
        
        return data
    
    def close(self):
        """Close the HTTP client"""
        if self.client:
            self.client.close()

class GroqService:
    """Integration service with LLaMA 3 via Groq for intelligent meal planning"""
    
    def __init__(self, api_key: str = os.getenv("GROQ_API_KEY")):
        """
        Initialize Groq service with API key
        
        Args:
            api_key: Groq API key, from environment variable if not provided
        """
        self.api_key = api_key
        self.available = bool(api_key)
        
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
                
                # Initialize direct client
                try:
                    self.client = DirectGroqClient(api_key=self.api_key)
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
                        available_models = self.client.list_models()
                        
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
    
    def __del__(self):
        """Close the client when the object is deleted"""
        if hasattr(self, 'client') and self.client:
            try:
                self.client.close()
            except:
                pass
        
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
        day_of_week: str = None,  # Thêm ngày để tăng tính đa dạng
        random_seed: int = None,  # Thêm random seed để tăng tính đa dạng
        user_data: Dict = None  # Add parameter for user data
    ) -> List[Dict]:
        """
        Generate meal suggestions based on nutritional targets and preferences
        
        Args:
            calories_target: Target calories for the meal
            protein_target: Target protein for the meal (g)
            fat_target: Target fat for the meal (g)
            carbs_target: Target carbs for the meal (g)
            meal_type: Type of meal (breakfast, lunch, dinner)
            preferences: Food preferences (optional)
            allergies: Food allergies to avoid (optional)
            cuisine_style: Preferred cuisine style (optional)
            use_ai: Whether to use AI for generation
            day_of_week: Day of the week (optional, for diversity)
            random_seed: Random seed (optional, for diversity)
            user_data: Dictionary containing user demographic and goal info (optional)
            
        Returns:
            List of meal suggestion dictionaries
        """
        # Nếu không sử dụng AI hoặc dịch vụ không khả dụng, trả về fallback
        if not use_ai or not self.available:
            print(f"Not using AI for meal suggestions. use_ai={use_ai}, available={self.available}")
            return self._fallback_meal_suggestions(meal_type)
        
        # Kiểm tra xem có vượt quá quota không
        if self.quota_exceeded:
            current_time = time.time()
            if self.quota_reset_time and current_time < self.quota_reset_time:
                wait_time = int(self.quota_reset_time - current_time)
                print(f"Quota exceeded, waiting {wait_time} seconds until reset")
                return self._fallback_meal_suggestions(meal_type)
            else:
                # Reset quota status
                self.quota_exceeded = False
                self.quota_reset_time = None
        
        # Kiểm tra rate limiter
        can_request, wait_time = self.rate_limiter.can_make_request()
        if not can_request:
            print(f"Rate limit reached, waiting {wait_time} seconds")
            return self._fallback_meal_suggestions(meal_type)
        
        # Tạo cache key
        cache_key = f"{meal_type}_{calories_target}_{protein_target}_{fat_target}_{carbs_target}"
        if preferences:
            cache_key += f"_pref={'_'.join(sorted(preferences))}"
        if allergies:
            cache_key += f"_allergy={'_'.join(sorted(allergies))}"
        if cuisine_style:
            cache_key += f"_cuisine={cuisine_style}"
        if day_of_week:
            cache_key += f"_day={day_of_week}"
        if random_seed:
            cache_key += f"_seed={random_seed}"
        if user_data:
            # Add user data to cache key
            user_data_str = "_".join([f"{k}:{v}" for k, v in user_data.items() if k in ['gender', 'age', 'goal', 'activity_level']])
            cache_key += f"_user:{user_data_str}"
        
        # Thêm thời gian hiện tại vào cache key để đảm bảo luôn có kết quả mới
        current_time = int(time.time() / 300)  # Thay đổi mỗi 5 phút
        cache_key += f"_time={current_time}"
        
        # Kiểm tra cache
        if cache_key in self.cache:
            print(f"Using cached meal suggestions for {meal_type}")
            return self.cache[cache_key]
        
        # Chuẩn bị prompt
        prompt = self._prepare_meal_prompt(
            calories_target, protein_target, fat_target, carbs_target,
            meal_type, preferences, allergies, cuisine_style, day_of_week, random_seed, user_data
        )
        
        # Tăng số lần thử lại lên 5 để đảm bảo có kết quả
        max_retries = 5
        for attempt in range(max_retries):
            try:
                print(f"Generating meal suggestions for {meal_type} (attempt {attempt+1}/{max_retries})")
                
                # Thay đổi temperature và top_p mỗi lần thử lại để tăng khả năng thành công
                temperature = 0.7 + (attempt * 0.05)  # Tăng dần từ 0.7 đến 0.9
                top_p = 0.95 - (attempt * 0.05)  # Giảm dần từ 0.95 đến 0.75
                
                # Gọi API
                response = self.client.generate_completion(
                    model=self.model,
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=2000,
                    top_p=top_p
                )
                
                # Xử lý response
                if "choices" in response and len(response["choices"]) > 0:
                    content = response["choices"][0]["message"]["content"].strip()
                    
                    # Phân tích JSON từ response
                    meal_data = self._extract_json_from_response(content)
                    
                    if meal_data and isinstance(meal_data, list) and len(meal_data) > 0:
                        # Validate and process meal data
                        validated_meals = self._validate_meals(meal_data)
                        
                        if validated_meals:
                            print(f"Successfully generated {len(validated_meals)} meal suggestions")
                            # Cache kết quả
                            self.cache[cache_key] = validated_meals
                            return validated_meals
                        else:
                            print("Validation failed for meal data")
                    else:
                        print("No valid meal data in response")
                else:
                    print("No choices in response")
                
            except Exception as e:
                print(f"Error generating meal suggestions (attempt {attempt+1}): {str(e)}")
                # Kiểm tra xem có phải lỗi quota không
                if "quota exceeded" in str(e).lower() or "rate limit" in str(e).lower():
                    print("Quota exceeded or rate limit reached")
                    self.quota_exceeded = True
                    self.quota_reset_time = time.time() + 3600  # Reset sau 1 giờ
                    break
                
                # Chờ trước khi thử lại
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Waiting {wait_time} seconds before retry")
                time.sleep(wait_time)
        
        # Nếu tất cả các lần thử đều thất bại, trả về fallback
        print(f"All {max_retries} attempts failed, using fallback meals")
        fallback_meals = self._fallback_meal_suggestions(meal_type)
        
        # Thêm thông tin về ngày để tăng tính đa dạng
        if day_of_week and fallback_meals:
            for meal in fallback_meals:
                if "name" in meal and day_of_week not in meal["name"]:
                    meal["name"] = f"{meal['name']} ({day_of_week})"
        
        return fallback_meals
    
    def _validate_meals(self, meal_data: List[Dict]) -> List[Dict]:
        """
        Validate meal data and ensure it has the expected structure
        
        Args:
            meal_data: List of meal dictionaries to validate
            
        Returns:
            List of validated meal dictionaries
        """
        valid_meals = []
        
        for meal in meal_data:
            if not isinstance(meal, dict):
                print(f"Skipping non-dict meal: {meal}")
                continue
                
            if 'name' not in meal:
                print(f"Skipping meal without name: {meal}")
                continue
                
            # Ensure ingredients list exists
            if 'ingredients' not in meal or not isinstance(meal['ingredients'], list):
                print(f"Adding empty ingredients list to meal: {meal['name']}")
                meal['ingredients'] = []
                
            # Kiểm tra và chuyển đổi trường preparation thành List[str]
            if 'preparation' not in meal:
                meal['preparation'] = [f"Prepare {meal['name']} with the listed ingredients."]
            elif isinstance(meal['preparation'], str):
                # Nếu là chuỗi, chuyển thành danh sách với một phần tử
                meal['preparation'] = [meal['preparation']]
            elif isinstance(meal['preparation'], list):
                # Nếu là danh sách, đảm bảo tất cả các phần tử đều là chuỗi
                meal['preparation'] = [str(step) for step in meal['preparation']]
            else:
                # Nếu là kiểu dữ liệu khác, đặt giá trị mặc định
                print(f"Invalid preparation format for meal: {meal['name']}, replacing with default")
                meal['preparation'] = [f"Prepare {meal['name']} with the listed ingredients."]
            
            # Ensure ingredients is not empty
            if not meal['ingredients']:
                meal['ingredients'] = [{'name': 'Main ingredient', 'amount': '100g'}]
            
            # Ensure total_nutrition exists
            if 'total_nutrition' not in meal:
                print(f"Adding default nutrition to meal: {meal['name']}")
                meal['total_nutrition'] = {
                    'calories': 400, 
                    'protein': 20, 
                    'fat': 15, 
                    'carbs': 45
                }
            
            valid_meals.append(meal)
            
        print(f"Validated {len(valid_meals)} out of {len(meal_data)} meals")
        return valid_meals
    
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
    
    def _extract_json_from_response(self, response_text: str) -> List[Dict]:
        """
        Trích xuất dữ liệu JSON từ phản hồi của AI
        
        Args:
            response_text: Văn bản phản hồi từ API
            
        Returns:
            List[Dict]: Dữ liệu món ăn dạng JSON hoặc None nếu không thể phân tích
        """
        try:
            # Phương pháp 1: Thử phân tích toàn bộ phản hồi là JSON
            print("Trying to parse entire response as JSON...")
            meal_data = json.loads(response_text)
            if isinstance(meal_data, list) and len(meal_data) > 0:
                print(f"Successfully parsed entire response as JSON array with {len(meal_data)} items")
                return meal_data
        except json.JSONDecodeError:
            print("Entire response is not valid JSON, trying to extract JSON portion...")
            
            # Phương pháp 2: Trích xuất JSON sử dụng regex
            import re
            json_pattern = r'\[\s*\{.*\}\s*\]'
            matches = re.search(json_pattern, response_text, re.DOTALL)
            if matches:
                json_str = matches.group(0)
                print(f"Found JSON-like pattern: {json_str[:100]}...")
                try:
                    meal_data = json.loads(json_str)
                    if isinstance(meal_data, list) and len(meal_data) > 0:
                        print(f"Successfully parsed extracted JSON with {len(meal_data)} items")
                        return meal_data
                except json.JSONDecodeError:
                    print("Extracted pattern is not valid JSON")
            
            # Phương pháp 3: Tìm mảng JSON giữa dấu ngoặc vuông
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                print(f"Extracted JSON between brackets: {json_str[:100]}...")
                try:
                    meal_data = json.loads(json_str)
                    if isinstance(meal_data, list) and len(meal_data) > 0:
                        print(f"Successfully parsed extracted JSON array with {len(meal_data)} items")
                        return meal_data
                except json.JSONDecodeError:
                    print("Error parsing JSON from response")
        
        # Không tìm thấy JSON hợp lệ
        return None
    
    def _prepare_meal_prompt(
        self,
        calories_target: int,
        protein_target: int,
        fat_target: int,
        carbs_target: int,
        meal_type: str,
        preferences: List[str] = None,
        allergies: List[str] = None,
        cuisine_style: str = None,
        day_of_week: str = None,
        random_seed: int = None,
        user_data: Dict = None
    ) -> str:
        """
        Chuẩn bị prompt cho AI để tạo gợi ý món ăn
        
        Args:
            calories_target: Mục tiêu calo
            protein_target: Mục tiêu protein (g)
            fat_target: Mục tiêu chất béo (g)
            carbs_target: Mục tiêu carbs (g)
            meal_type: Loại bữa ăn (breakfast, lunch, dinner)
            preferences: Danh sách sở thích thực phẩm (tùy chọn)
            allergies: Danh sách dị ứng thực phẩm (tùy chọn)
            cuisine_style: Phong cách ẩm thực (tùy chọn)
            day_of_week: Ngày trong tuần (tùy chọn)
            random_seed: Seed ngẫu nhiên (tùy chọn)
            user_data: Dictionary containing user demographic and goal info (optional)
            
        Returns:
            str: Prompt cho AI
        """
        preferences_str = ", ".join(preferences) if preferences else "none"
        allergies_str = ", ".join(allergies) if allergies else "none"
        cuisine_style_str = cuisine_style if cuisine_style else "no specific requirement"
        day_str = f" for {day_of_week}" if day_of_week else ""
        
        # Thêm seed ngẫu nhiên và ngày vào prompt để tăng tính đa dạng
        diversity_str = ""
        if random_seed:
            diversity_str = f"\n- Random seed: {random_seed}"
        if day_of_week:
            diversity_str += f"\n- Day of week: {day_of_week}"
            
        # Extract user data information
        user_info = ""
        if user_data:
            gender = user_data.get('gender', 'unknown')
            age = user_data.get('age', 'unknown')
            goal = user_data.get('goal', 'unknown')
            activity_level = user_data.get('activity_level', 'unknown')
            
            user_info = f"""
- User gender: {gender}
- User age: {age}
- User goal: {goal}
- User activity level: {activity_level}"""
        
        # Tối ưu hóa prompt cho LLaMA 3
        prompt = f"""You are a nutrition expert, please suggest 3-4 Vietnamese meals for {meal_type}{day_str} with the following criteria:
- Total calories: {calories_target}kcal
- Protein amount: {protein_target}g
- Fat amount: {fat_target}g
- Carbohydrate amount: {carbs_target}g
- Preferences: {preferences_str}
- Allergies (avoid): {allergies_str}
- Cuisine style: {cuisine_style_str}{diversity_str}{user_info}

IMPORTANT REQUIREMENTS:
1. Write ALL meal names and descriptions in Vietnamese language
2. Include Vietnamese ingredients with Vietnamese names
3. Write preparation instructions in Vietnamese with detailed cooking steps
4. Make sure to create DIFFERENT meals than usual. Be creative and diverse.
5. DO NOT include day names in meal names (no "Thứ 2", "Thứ 3", etc.)
6. Consider the user's specific goals and requirements:
   - For weight loss goals: Focus on filling, high-fiber, protein-rich, lower calorie options
   - For muscle gain goals: Focus on protein-rich, nutrient-dense meals
   - For general health: Focus on balanced, nutritious meals with variety
   - Adjust spice levels and complexity based on user age
   - Consider activity level for portion sizes and recovery nutrients

Your response MUST be a valid JSON array without any additional text before or after.
Format your response like this EXACTLY:
[
  {{
    "name": "Meal name",
    "description": "Brief description of the meal",
    "ingredients": [
      {{"name": "Ingredient name", "amount": "Amount"}},
      ...
    ],
    "preparation": "Step by step preparation instructions",
    "nutrition": {{"calories": {calories_target}, "protein": {protein_target}, "fat": {fat_target}, "carbs": {carbs_target}}}
  }},
  ...
]

IMPORTANT: Return ONLY the JSON array with no additional text. Do not include markdown code blocks or any explanations.
"""
        
        return prompt

# Initialize service singleton
groq_service = GroqService() 