import os
import json
import time
import threading
import random
from typing import List, Dict, Optional, Tuple
from models import NutritionInfo, Dish, Ingredient

# Ensure re module is globally accessible to prevent "cannot access local variable 're'" error
import re as regex_module

# Helper function to ensure regex operations work
def safe_regex_sub(pattern, replacement, text, flags=0, count=0):
    """Safe regex substitution to prevent 're' variable access errors"""
    try:
        import re as local_re
        if count > 0:
            return local_re.sub(pattern, replacement, text, count=count, flags=flags)
        else:
            return local_re.sub(pattern, replacement, text, flags=flags)
    except Exception as e:
        print(f"⚠️ Regex substitution failed: {e}")
        return text

def safe_regex_findall(pattern, text, flags=0):
    """Safe regex findall to prevent 're' variable access errors"""
    try:
        import re as local_re
        return local_re.findall(pattern, text, flags)
    except Exception as e:
        print(f"⚠️ Regex findall failed: {e}")
        return []

def safe_regex_search(pattern, text, flags=0):
    """Safe regex search to prevent 're' variable access errors"""
    try:
        import re as local_re
        return local_re.search(pattern, text, flags)
    except Exception as e:
        print(f"⚠️ Regex search failed: {e}")
        return None

# Import fallback data
from fallback_meals import FALLBACK_MEALS

# 🔧 FIX: Import rich Vietnamese traditional dishes database
from vietnamese_traditional_dishes import ALL_TRADITIONAL_DISHES
from vietnamese_nutrition_extended import (
    VEGETABLES_NUTRITION, FRUITS_NUTRITION, MEAT_NUTRITION,
    SEAFOOD_NUTRITION, EGGS_NUTRITION, DAIRY_NUTRITION
)

# Import enhanced JSON prompt templates
from json_prompt_templates import (
    get_strict_json_prompt,
    get_one_shot_example_prompt,
    get_validation_retry_prompt,
    get_fallback_prompt,
    get_temperature_settings,
    get_system_message,
    validate_json_response
)

# Import Vietnamese specialty dishes
from vietnamese_specialty_dishes import get_specialty_dish_names, get_specialty_dish

# Import official Vietnamese nutrition database
from vietnamese_nutrition_database import (
    get_ingredient_nutrition,
    get_dish_nutrition,
    calculate_dish_nutrition_from_ingredients,
    get_nutrition_sources
)

# Thử import thư viện Groq hoặc fallback
try:
    import groq
    GROQ_AVAILABLE = True
except ImportError:
    print("Groq client package not installed. Using fallback mode.")
    GROQ_AVAILABLE = False

class RateLimiter:
    """Quản lý giới hạn tốc độ gọi API"""
    
    def __init__(self, requests_per_minute: int = 60, requests_per_day: int = 1000):
        """
        Khởi tạo bộ giới hạn tốc độ
        
        Args:
            requests_per_minute: Số yêu cầu tối đa mỗi phút
            requests_per_day: Số yêu cầu tối đa mỗi ngày
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_day = requests_per_day
        self.minute_requests = 0
        self.day_requests = 0
        self.minute_reset_time = time.time() + 60  # Reset sau 1 phút
        self.day_reset_time = time.time() + 86400  # Reset sau 1 ngày
        self.lock = threading.Lock()
    
    def can_make_request(self) -> Tuple[bool, int]:
        """
        Kiểm tra xem có thể thực hiện yêu cầu không
        
        Returns:
            Tuple[bool, int]: (Có thể gọi không, thời gian chờ tính bằng giây)
        """
        with self.lock:
            current_time = time.time()
            
            # Đặt lại bộ đếm phút nếu cần
            if current_time > self.minute_reset_time:
                self.minute_requests = 0
                self.minute_reset_time = current_time + 60
            
            # Đặt lại bộ đếm ngày nếu cần
            if current_time > self.day_reset_time:
                self.day_requests = 0
                self.day_reset_time = current_time + 86400
            
            # Kiểm tra giới hạn
            if self.minute_requests < self.requests_per_minute and self.day_requests < self.requests_per_day:
                self.minute_requests += 1
                self.day_requests += 1
                return True, 0
            
            # Tính thời gian chờ
            wait_time = min(
                self.minute_reset_time - current_time,
                self.day_reset_time - current_time
            )
            
            # Thêm jitter để tránh thundering herd
            wait_time += random.uniform(1, 5)
            
            return False, max(1, int(wait_time))

class GroqService:
    """Dịch vụ tích hợp với LLaMA 3 qua Groq để tạo kế hoạch thực đơn thông minh"""
    
    def __init__(self, api_key: str = os.getenv("GROQ_API_KEY")):
        """
        Khởi tạo dịch vụ Groq với API key
        
        Args:
            api_key: Groq API key, lấy từ biến môi trường nếu không cung cấp
        """
        self.api_key = api_key
        self.available = GROQ_AVAILABLE and api_key is not None
        
        # Khởi tạo cache và rate limiter
        self.cache = {}
        self.rate_limiter = RateLimiter(requests_per_minute=60, requests_per_day=1000)
        self.max_retries = 3

        # 🔧 ENHANCED Anti-duplication tracking với force diversity
        self.recent_dishes = []  # Track recent dishes to avoid duplication
        self.max_recent_dishes = 100  # Tăng lên 100 để track nhiều món hơn
        self.force_diversity = True  # Force diversity mode

        # Thêm biến để theo dõi trạng thái quota
        self.quota_exceeded = False
        self.quota_reset_time = None
        
        # Mô hình mặc định sử dụng LLaMA 3
        self.default_model = "llama3-8b-8192"
        self.client = None
        self.model = self.default_model
        
        if self.available:
            try:
                print("\n=== INITIALIZING GROQ SERVICE ===")
                print(f"API Key: {'***' + self.api_key[-4:] if self.api_key else 'None'}")
                
                # Khởi tạo client với timeout cho Render (phiên bản Groq 0.4.0)
                try:
                    self.client = groq.Groq(
                        api_key=self.api_key,
                        timeout=60.0  # 60 second timeout for Render
                    )
                    print(f"✅ Groq client initialized with timeout=60s")
                except Exception as e:
                    print(f"Error initializing Groq client: {str(e)}")
                    self.available = False
                    return
                
                # Danh sách model để thử theo thứ tự ưu tiên
                self.preferred_models = [
                    "llama3-70b-8192",  # LLaMA 3 70B - Model mạnh nhất
                    "llama3-8b-8192",   # LLaMA 3 8B - Cân bằng tốc độ và hiệu năng
                    "mixtral-8x7b-32768"  # Mixtral - Fallback nếu LLaMA không khả dụng
                ]
                
                # Kiểm tra các model có sẵn
                if self.client:
                    try:
                        print("Fetching available models...")
                        models = self.client.models.list()
                        available_models = [model.id for model in models.data]
                        
                        print("Available models:")
                        for model_name in available_models:
                            print(f"- {model_name}")
                        
                        # Tìm model ưu tiên đầu tiên có sẵn
                        selected_model = None
                        for model_name in self.preferred_models:
                            if model_name in available_models:
                                selected_model = model_name
                                break
                        
                        # Nếu không tìm thấy model ưu tiên nào, sử dụng model mặc định
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
        use_ai: bool = True,  # Thêm tham số để có thể tắt AI
        day_of_week: str = None,  # Thêm ngày để tăng tính đa dạng
        random_seed: int = None,  # Thêm random seed để tăng tính đa dạng
        user_data: Dict = None  # Add parameter for user data
    ) -> List[Dict]:
        """
        Tạo gợi ý món ăn sử dụng LLaMA 3 qua Groq

        Args:
            calories_target: Mục tiêu calo
            protein_target: Mục tiêu protein (g)
            fat_target: Mục tiêu chất béo (g)
            carbs_target: Mục tiêu carbs (g)
            meal_type: Loại bữa ăn (bữa sáng, bữa trưa, bữa tối)
            preferences: Danh sách sở thích thực phẩm (tùy chọn)
            allergies: Danh sách dị ứng thực phẩm (tùy chọn)
            cuisine_style: Phong cách ẩm thực (tùy chọn)
            use_ai: Có sử dụng AI không hay dùng dữ liệu dự phòng
            day_of_week: Ngày trong tuần (tùy chọn, để tăng tính đa dạng)
            random_seed: Random seed (tùy chọn, để tăng tính đa dạng)
            user_data: Dictionary chứa thông tin người dùng (tùy chọn)

        Returns:
            Danh sách các gợi ý món ăn dưới dạng từ điển
        """
        # Kiểm tra nếu AI bị tắt hoặc đã vượt quá quota
        if not use_ai or self.quota_exceeded:
            # Kiểm tra xem quota đã được reset chưa
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
                
        # Nếu AI không khả dụng
        if not self.available:
            print("Groq API not available. Using fallback data.")
            return self._fallback_meal_suggestions(meal_type)
        
        # 🔧 FORCE DIVERSITY: Tạo cache key với timestamp để đảm bảo unique
        import hashlib
        import time

        # Add timestamp để đảm bảo mỗi lần gọi đều unique
        diversity_timestamp = int(time.time() * 1000) % 100000  # 5 chữ số cuối
        recent_dishes_hash = hashlib.md5(str(sorted(self.recent_dishes[-5:])).encode()).hexdigest()[:8]
        cache_key = f"{meal_type}_{calories_target}_{protein_target}_{fat_target}_{carbs_target}_{recent_dishes_hash}_{diversity_timestamp}"
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

        # 🔧 FORCE DIVERSITY: Disable cache để luôn tạo món mới
        # if cache_key in self.cache:
        #     print(f"Using cached meal suggestions for: {cache_key}")
        #     return self.cache[cache_key]
        print(f"🎲 FORCE DIVERSITY: Bypassing cache, generating new meals for: {cache_key[:50]}...")
        
        # Kiểm tra rate limit
        can_request, wait_time = self.rate_limiter.can_make_request()
        if not can_request:
            print(f"Rate limit reached. Using fallback data. Try again in {wait_time} seconds.")
            return self._fallback_meal_suggestions(meal_type)
        
        # Tạo prompt cho LLaMA
        preferences_str = ", ".join(preferences) if preferences else "không có"
        allergies_str = ", ".join(allergies) if allergies else "không có"
        cuisine_style_str = cuisine_style if cuisine_style else "không có yêu cầu cụ thể"

        # ENHANCED: Tạo món ăn kết hợp thực tế
        combination_dishes = self._generate_realistic_combination_dishes(meal_type, preferences, allergies)

        # ANTI-DUPLICATION: Exclude recent dishes
        recent_dishes_str = ", ".join(self.recent_dishes[-10:]) if self.recent_dishes else "không có"

        # ENHANCED PROMPT GENERATION với combination dishes
        prompt_strategies = [
            ("Combination Dishes Prompt", self._get_combination_dishes_prompt(
                meal_type, calories_target, protein_target, fat_target, carbs_target,
                preferences_str, allergies_str, combination_dishes, recent_dishes_str
            )),
            ("Strict JSON Prompt", get_strict_json_prompt(
                meal_type, calories_target, protein_target, fat_target, carbs_target,
                preferences_str, allergies_str, combination_dishes, recent_dishes_str
            )),
            ("One-shot Example Prompt", get_one_shot_example_prompt(
                meal_type, calories_target, protein_target, fat_target, carbs_target
            )),
            ("Fallback Simple Prompt", get_fallback_prompt(meal_type))
        ]

        # Prompt strategies sẽ được sử dụng trong retry loop
        
        try:
            # Gọi API Groq với enhanced retry logic
            for attempt in range(self.max_retries):
                try:
                    print(f"Making request to Groq API, attempt {attempt + 1}/{self.max_retries}")

                    # Chọn prompt strategy dựa trên attempt
                    current_prompt = prompt_strategies[min(attempt, len(prompt_strategies)-1)][1]
                    strategy_name = prompt_strategies[min(attempt, len(prompt_strategies)-1)][0]
                    print(f"Using strategy: {strategy_name}")

                    # Lấy cài đặt temperature tối ưu
                    temp_settings = get_temperature_settings()

                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": get_system_message()},
                            {"role": "user", "content": current_prompt}
                        ],
                        temperature=temp_settings["temperature"],
                        max_tokens=2000,
                        top_p=temp_settings["top_p"],
                        frequency_penalty=temp_settings["frequency_penalty"],
                        presence_penalty=temp_settings["presence_penalty"],
                        timeout=60  # Explicit timeout for each request
                    )
                    
                    # Trích xuất kết quả JSON từ phản hồi
                    result_text = response.choices[0].message.content.strip()
                    print(f"🔍 Raw response from Groq (attempt {attempt + 1}):")
                    print(f"Length: {len(result_text)} characters")
                    print(f"First 200 chars: {result_text[:200]}")
                    print(f"Last 200 chars: {result_text[-200:]}")

                    # Validate JSON response trước khi extract
                    is_valid, error_msg = validate_json_response(result_text)
                    if is_valid:
                        print(f"✅ Response passed initial JSON validation")
                    else:
                        print(f"⚠️ Response failed validation: {error_msg}")

                        # Nếu không phải attempt cuối, thử retry với validation prompt
                        if attempt < self.max_retries - 1:
                            print(f"🔄 Retrying with validation-corrected prompt...")
                            retry_prompt = get_validation_retry_prompt(result_text, error_msg)

                            retry_response = self.client.chat.completions.create(
                                model=self.model,
                                messages=[
                                    {"role": "system", "content": get_system_message()},
                                    {"role": "user", "content": retry_prompt}
                                ],
                                temperature=0.0,  # Maximum strictness for correction
                                max_tokens=2000,
                                top_p=0.1
                            )

                            result_text = retry_response.choices[0].message.content.strip()
                            print(f"🔧 Retry response: {result_text[:100]}...")

                    # Phân tích JSON từ response
                    print(f"🔧 Extracting JSON from response...")
                    meal_data = self._extract_json_from_response(result_text)

                    if meal_data and isinstance(meal_data, list) and len(meal_data) > 0:
                        print(f"✅ Successfully extracted {len(meal_data)} meals from JSON")

                        # Validate and process meal data
                        print(f"🔍 Validating meal data...")
                        validated_meals = self._validate_meals(meal_data)

                        if validated_meals:
                            print(f"🎉 Successfully generated {len(validated_meals)} validated meal suggestions")

                            # 🔧 ENHANCED ANTI-DUPLICATION: Track recent dishes với similarity checking
                            for meal in validated_meals:
                                dish_name = meal.get('name', '')
                                if dish_name:
                                    # Check if similar dish already exists in recent dishes
                                    is_similar_to_existing = False
                                    dish_name_lower = dish_name.lower()

                                    for existing_dish in self.recent_dishes:
                                        if self._are_dishes_similar(dish_name_lower, existing_dish.lower()):
                                            is_similar_to_existing = True
                                            print(f"⚠️ Detected similar dish: '{dish_name}' ~ '{existing_dish}'")
                                            break

                                    # Only add if not similar to existing dishes
                                    if not is_similar_to_existing:
                                        self.recent_dishes.append(dish_name)
                                        print(f"📝 Added to recent dishes: {dish_name}")
                                        # Keep only last N dishes
                                        if len(self.recent_dishes) > self.max_recent_dishes:
                                            self.recent_dishes.pop(0)
                                    else:
                                        print(f"🚫 Skipped similar dish: {dish_name}")

                            print(f"📝 Recent dishes tracked ({len(self.recent_dishes)}): {self.recent_dishes[-5:]}")  # Show last 5

                            # Kiểm tra và bổ sung calories nếu cần
                            final_meals = self._ensure_adequate_calories(validated_meals, calories_target, meal_type)

                            # 🔧 FORCE DIVERSITY: Không cache kết quả để luôn tạo mới
                            # self.cache[cache_key] = final_meals
                            print(f"🎲 FORCE DIVERSITY: Not caching results to ensure variety")
                            return final_meals
                        else:
                            print("❌ Validation failed - no valid meals after validation")
                    else:
                        print(f"❌ No valid meal data in response. meal_data type: {type(meal_data)}, length: {len(meal_data) if meal_data else 'None'}")
                    
                    # Nếu không trích xuất được dữ liệu hợp lệ, thử lại với exponential backoff
                    print(f"Invalid response format. Retrying... ({attempt + 1}/{self.max_retries})")
                    backoff_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    print(f"Waiting {backoff_time}s before retry...")
                    time.sleep(backoff_time)
                    
                except Exception as e:
                    print(f"Error calling Groq API: {str(e)} - Attempt {attempt + 1}/{self.max_retries}")
                    if "quota exceeded" in str(e).lower():
                        print("API quota exceeded")
                        self.quota_exceeded = True
                        self.quota_reset_time = time.time() + 3600  # Thử lại sau 1 giờ
                        break

                    # Exponential backoff for API errors
                    backoff_time = 2 ** attempt  # 1s, 2s, 4s
                    print(f"Waiting {backoff_time}s before retry...")
                    time.sleep(backoff_time)
            
            # Nếu không nhận được kết quả sau tất cả các lần thử
            print("Failed to get valid response from Groq API after multiple attempts.")
            print("🔧 Using intelligent fallback meal generation...")

            # Thử intelligent fallback trước
            fallback_meals = self._create_intelligent_fallback(meal_type, calories_target, protein_target, fat_target, carbs_target)
            if fallback_meals:
                print(f"✅ Successfully created {len(fallback_meals)} intelligent fallback meals")
                return fallback_meals

            # Nếu intelligent fallback thất bại, dùng static fallback
            print("🔧 Using static fallback data...")
            return self._fallback_meal_suggestions(meal_type)
                
        except Exception as e:
            print(f"Error generating meal suggestions: {str(e)}")
            return self._fallback_meal_suggestions(meal_type)

    def _get_diverse_dish_suggestions(self, meal_type: str, preferences: List[str], allergies: List[str]) -> str:
        """
        Tạo danh sách món ăn Việt Nam đa dạng theo meal_type
        """
        # Database món ăn Việt Nam phong phú
        vietnamese_dishes = {
            "bữa sáng": [
                # Món nước truyền thống
                "Phở Gà", "Phở Bò", "Bún Bò Huế", "Bún Riêu", "Bún Chả", "Bún Thịt Nướng",
                "Hủ Tiếu", "Mì Quảng", "Cao Lầu", "Bánh Canh", "Cháo Gà", "Cháo Lòng",
                "Cháo Đậu Xanh", "Cháo Sườn", "Súp Cua",

                # Món nước mới lạ
                "Cháo Cá Hồi Nấu Dừa", "Bún Măng Vịt", "Phở Cuốn Tôm Thịt", "Bánh Canh Cua Đồng",
                "Hủ Tiếu Mì Tôm Cua", "Cháo Trai Nấu Riêu", "Bún Sứa", "Mì Quảng Tôm Càng",
                "Cháo Nghêu Hến", "Bánh Canh Chả Cá", "Phở Chua", "Bún Mắm Nêm",

                # Món khô truyền thống
                "Bánh Mì Thịt", "Bánh Mì Chả Cá", "Bánh Mì Xíu Mái", "Bánh Mì Chay",
                "Xôi Xéo", "Xôi Mặn", "Xôi Gấc", "Xôi Đậu Xanh", "Xôi Lạc",
                "Bánh Cuốn", "Bánh Ướt", "Bánh Bèo", "Bánh Nậm",

                # Món khô mới lạ
                "Bánh Mì Chả Cá Nha Trang", "Xôi Chiên Phồng", "Bánh Cuốn Thanh Trì",
                "Bánh Ướt Lòng Gà", "Bánh Bèo Chén", "Bánh Căn", "Bánh Khọt Vũng Tàu",
                "Xôi Ngũ Sắc", "Bánh Tráng Nướng", "Bánh Tráng Phơi Sương",

                # Món chay đặc sắc
                "Cháo Chay", "Phở Chay", "Bún Chay", "Bánh Mì Chay", "Xôi Chay",
                "Cháo Hạt Sen", "Bún Riêu Chay", "Bánh Cuốn Chay", "Xôi Đậu Đen"
            ],

            "bữa trưa": [
                # Cơm truyền thống
                "Cơm Tấm Sườn", "Cơm Gà Xối Mỡ", "Cơm Chiên Dương Châu", "Cơm Âm Phủ",
                "Cơm Hến", "Cơm Niêu", "Cơm Dẻo", "Cơm Bò Lúc Lắc", "Cơm Gà Nướng",

                # Cơm đặc sắc
                "Cơm Âm Phủ Huế", "Cơm Hến Huế", "Cơm Niêu Sài Gòn", "Cơm Tấm Bì Chả",
                "Cơm Gà Hội An", "Cơm Chiên Hải Sản", "Cơm Chiên Cá Mặn", "Cơm Rang Dưa Bò",
                "Cơm Âm Phủ Chay", "Cơm Cháy Chà Bông", "Cơm Lam", "Cơm Nắm",

                # Bún/Phở truyền thống
                "Bún Bò Huế", "Bún Riêu Cua", "Bún Chả Hà Nội", "Bún Thịt Nướng",
                "Bún Mắm", "Bún Đậu Mắm Tôm", "Phở Bò", "Phở Gà", "Phở Chay",

                # Bún/Phở đặc sắc
                "Bún Bò Huế Chay", "Bún Riêu Cua Đồng", "Bún Chả Cá", "Bún Ốc",
                "Bún Măng Vịt", "Bún Sứa", "Phở Cuốn", "Phở Xào", "Phở Áp Chảo",
                "Bún Thái", "Bún Mắm Nêm", "Bún Cá Kiên Giang",

                # Mì/Hủ tiếu
                "Mì Quảng", "Hủ Tiếu Nam Vang", "Hủ Tiếu Khô", "Cao Lầu",
                "Mì Xào Giòn", "Mì Xào Mềm", "Hủ Tiếu Xào",
                "Mì Quảng Tôm Cua", "Hủ Tiếu Gò Vấp", "Cao Lầu Hội An", "Mì Vịt Tiềm",

                # Món nướng
                "Nem Nướng", "Chả Cá Lã Vọng", "Cá Nướng", "Thịt Nướng",
                "Tôm Nướng", "Mực Nướng", "Gà Nướng",
                "Nem Nướng Ninh Hòa", "Chả Cá Nha Trang", "Cá Nướng Lá Chuối",

                # Món chay đặc sắc
                "Cơm Chay", "Bún Chay", "Phở Chay", "Mì Chay",
                "Cơm Âm Phủ Chay", "Bún Riêu Chay", "Mì Quảng Chay"
            ],

            "bữa tối": [
                # Món nhẹ truyền thống
                "Chả Cá", "Nem Rán", "Bánh Xèo", "Bánh Khọt", "Bánh Tráng Nướng",
                "Bánh Căn", "Bánh Bột Lọc", "Bánh Ít", "Bánh Bao",

                # Món nhẹ đặc sắc
                "Bánh Xèo Miền Tây", "Bánh Khọt Vũng Tàu", "Bánh Căn Phan Thiết",
                "Bánh Bột Lọc Huế", "Bánh Ít Lá Gai", "Bánh Tráng Phơi Sương",
                "Nem Chua Rán", "Chả Ram Tôm Đất", "Bánh Tôm Hồ Tây",
                "Bánh Cuốn Tôm Chấy", "Bánh Flan Nướng", "Chè Cung Đình",

                # Lẩu truyền thống
                "Lẩu Thái", "Lẩu Cá", "Lẩu Gà", "Lẩu Riêu Cua", "Lẩu Chay",

                # Lẩu đặc sắc
                "Lẩu Mắm", "Lẩu Cá Kèo", "Lẩu Cá Linh", "Lẩu Ếch", "Lẩu Gà Lá É",
                "Lẩu Cá Đuối", "Lẩu Hến", "Lẩu Cá Bông Lau", "Lẩu Măng Chua",
                "Lẩu Cá Tầm", "Lẩu Nấm", "Lẩu Đuôi Bò",

                # Cháo/Súp
                "Cháo Vịt", "Cháo Cá", "Cháo Trai", "Súp Cua", "Súp Măng Cua",
                "Cháo Ếch Singapore", "Cháo Cá Chép", "Súp Bào Ngư", "Cháo Hến",
                "Súp Cua Đồng", "Cháo Sò Huyết", "Súp Gà Ác Tần",

                # Cơm chiều
                "Cơm Chiên", "Cơm Âm Phủ", "Cơm Hến", "Cơm Niêu",
                "Cơm Chiên Hải Sản", "Cơm Chiên Cá Mặn", "Cơm Cháy Chà Bông",

                # Món nướng đặc sắc
                "Bánh Tráng Nướng", "Chả Cá Nướng", "Tôm Nướng", "Mực Nướng",
                "Cá Nướng Lá Chuối", "Thịt Nướng Lá Lốt", "Tôm Nướng Muối Ớt",
                "Mực Nướng Sa Tế", "Gà Nướng Lá Chanh", "Cá Saba Nướng",

                # Món chay đặc sắc
                "Cháo Chay", "Lẩu Chay", "Bánh Xèo Chay", "Nem Chay",
                "Lẩu Nấm Chay", "Cháo Hạt Sen", "Bánh Căn Chay", "Cơm Âm Phủ Chay"
            ]
        }

        # Lấy danh sách món theo meal_type
        meal_type_lower = meal_type.lower()
        if "sáng" in meal_type_lower:
            dishes = vietnamese_dishes["bữa sáng"]
        elif "trưa" in meal_type_lower:
            dishes = vietnamese_dishes["bữa trưa"]
        elif "tối" in meal_type_lower:
            dishes = vietnamese_dishes["bữa tối"]
        else:
            # Mix tất cả món
            dishes = []
            for dish_list in vietnamese_dishes.values():
                dishes.extend(dish_list)

        # Filter theo preferences
        if preferences:
            filtered_dishes = []
            for dish in dishes:
                dish_lower = dish.lower()

                # Healthy preference
                if "healthy" in [p.lower() for p in preferences]:
                    if any(keyword in dish_lower for keyword in ["cháo", "súp", "chay", "gà", "cá"]):
                        filtered_dishes.append(dish)

                # High protein preference
                elif "high-protein" in [p.lower() for p in preferences]:
                    if any(keyword in dish_lower for keyword in ["bò", "gà", "cá", "tôm", "thịt", "trứng"]):
                        filtered_dishes.append(dish)

                # Vegetarian preference
                elif "vegetarian" in [p.lower() for p in preferences] or "chay" in [p.lower() for p in preferences]:
                    if "chay" in dish_lower:
                        filtered_dishes.append(dish)

                # Low carb preference
                elif "low-carb" in [p.lower() for p in preferences]:
                    if not any(keyword in dish_lower for keyword in ["cơm", "xôi", "bánh", "bún", "phở", "mì"]):
                        filtered_dishes.append(dish)

                else:
                    filtered_dishes.append(dish)

            if filtered_dishes:
                dishes = filtered_dishes

        # Filter theo allergies
        if allergies:
            filtered_dishes = []
            for dish in dishes:
                dish_lower = dish.lower()
                has_allergen = False

                for allergy in allergies:
                    allergy_lower = allergy.lower()
                    if allergy_lower in ["seafood", "hải sản"]:
                        if any(keyword in dish_lower for keyword in ["cá", "tôm", "cua", "mực", "hến", "trai"]):
                            has_allergen = True
                            break
                    elif allergy_lower in ["dairy", "sữa"]:
                        if any(keyword in dish_lower for keyword in ["sữa", "kem", "phô mai"]):
                            has_allergen = True
                            break
                    elif allergy_lower in ["gluten", "gluten"]:
                        if any(keyword in dish_lower for keyword in ["bánh", "mì", "bún", "phở"]):
                            has_allergen = True
                            break

                if not has_allergen:
                    filtered_dishes.append(dish)

            if filtered_dishes:
                dishes = filtered_dishes

        # 🔧 FIX: Enhanced anti-duplication với fuzzy matching
        filtered_dishes = []
        for dish in dishes:
            # Exact match check
            if dish not in self.recent_dishes:
                # Fuzzy match check - tránh các món tương tự
                is_similar = False
                dish_lower = dish.lower()

                for recent_dish in self.recent_dishes:
                    recent_lower = recent_dish.lower()

                    # Check for similar base dishes
                    if self._are_dishes_similar(dish_lower, recent_lower):
                        is_similar = True
                        break

                if not is_similar:
                    filtered_dishes.append(dish)

        # If too few dishes after filtering, gradually relax restrictions
        if len(filtered_dishes) < 8:  # Increased from 5 to 8
            print(f"⚠️ Only {len(filtered_dishes)} unique dishes found, relaxing restrictions...")

            # First relaxation: only avoid exact matches from last 5 dishes
            filtered_dishes = []
            recent_5 = self.recent_dishes[-5:] if len(self.recent_dishes) >= 5 else self.recent_dishes

            for dish in dishes:
                if dish not in recent_5:
                    filtered_dishes.append(dish)

            # Second relaxation: if still too few, use all dishes
            if len(filtered_dishes) < 5:
                print(f"⚠️ Still only {len(filtered_dishes)} dishes, using all available dishes")
                filtered_dishes = dishes

        # Thêm món ăn đặc sắc từ database riêng
        try:
            specialty_names = get_specialty_dish_names(meal_type)
            if specialty_names:
                # Thêm một số món đặc sắc vào danh sách
                filtered_dishes.extend(specialty_names[:5])  # Thêm tối đa 5 món đặc sắc
                print(f"🍽️ Added {len(specialty_names[:5])} specialty dishes: {specialty_names[:5]}")
        except Exception as e:
            print(f"⚠️ Could not load specialty dishes: {e}")

        # Shuffle để tăng tính ngẫu nhiên
        import random
        random.shuffle(filtered_dishes)

        # Trả về top 15-20 món để AI chọn (tăng từ 15 lên 20 để có thêm món đặc sắc)
        selected_dishes = filtered_dishes[:20]
        return ", ".join(selected_dishes)

    def _are_dishes_similar(self, dish1: str, dish2: str) -> bool:
        """
        🔧 ENHANCED: Kiểm tra xem 2 món ăn có tương tự nhau không (improved detection)

        Args:
            dish1, dish2: Tên món ăn đã lowercase

        Returns:
            bool: True nếu tương tự
        """
        # Exact match
        if dish1 == dish2:
            return True

        # 🔧 FIX: Enhanced similarity detection

        # 1. Remove regional variations and check core similarity
        dish1_core = self._remove_regional_variations(dish1)
        dish2_core = self._remove_regional_variations(dish2)

        # 🔧 RELAXED: Chỉ coi là trùng nếu core dish hoàn toàn giống nhau VÀ không có biến thể vùng miền
        if dish1_core == dish2_core:
            # Kiểm tra xem có phải chỉ khác vùng miền không
            dish1_has_region = dish1 != dish1_core
            dish2_has_region = dish2 != dish2_core

            # Nếu cả hai đều có vùng miền khác nhau, cho phép
            if dish1_has_region and dish2_has_region:
                print(f"🔧 Allowing regional variation: '{dish1}' vs '{dish2}'")
                return False  # Không coi là trùng lặp

            # Nếu một món có vùng miền, một món không có, coi là trùng
            return True

        # 2. Extract base dish names
        base1 = self._extract_base_dish_name(dish1)
        base2 = self._extract_base_dish_name(dish2)

        # Same base dish
        if base1 == base2:
            return True

        # 3. Check for word overlap (if >70% words are same, consider similar)
        words1 = set(dish1.split())
        words2 = set(dish2.split())

        if len(words1) > 0 and len(words2) > 0:
            overlap = len(words1.intersection(words2))
            total_unique = len(words1.union(words2))
            similarity_ratio = overlap / total_unique

            if similarity_ratio > 0.7:  # 70% word overlap
                return True

        # 4. Enhanced pattern matching
        similar_patterns = [
            # Cơm tấm variations (more specific)
            (["cơm tấm", "sườn"], ["cơm tấm", "sườn"]),
            # Bánh mì variations
            (["bánh mì", "chả cá"], ["bánh mì", "chả cá"]),
            # Phở variations
            (["phở", "gà"], ["phở", "gà"]),
            (["phở", "bò"], ["phở", "bò"]),
            # Cháo variations
            (["cháo", "gà"], ["cháo", "gà"]),
            (["cháo", "tôm"], ["cháo", "tôm"]),
        ]

        for pattern1, pattern2 in similar_patterns:
            if all(p in dish1 for p in pattern1) and all(p in dish2 for p in pattern2):
                return True

        return False

    def _remove_regional_variations(self, dish_name: str) -> str:
        """
        🔧 ENHANCED: Remove regional variations to detect core dish similarity

        Args:
            dish_name: Tên món ăn

        Returns:
            str: Tên món ăn đã loại bỏ variations
        """
        # 🔧 EXPANDED: More comprehensive regional indicators
        regional_terms = [
            # Vùng miền
            "miền tây", "miền bắc", "miền trung", "miền nam",
            # Thành phố
            "sài gòn", "hà nội", "huế", "đà nẵng", "nha trang", "cà mau",
            "đồng nai", "an giang", "cần thơ", "vũng tàu", "hải phòng",
            # Đặc tính
            "đặc biệt", "truyền thống", "cổ điển", "đặc sản", "cải tiến",
            "nguyên bản", "chính gốc", "authentic", "original",
            # Phong cách nấu
            "nướng than", "nướng lò", "chiên giòn", "luộc", "hấp",
            # Mức độ
            "cay", "ngọt", "mặn", "chua", "đậm đà", "nhẹ nhàng"
        ]

        dish_clean = dish_name.lower()

        for term in regional_terms:
            dish_clean = dish_clean.replace(term, "").strip()

        # Remove extra spaces and normalize
        dish_clean = " ".join(dish_clean.split())

        return dish_clean

    def _create_dish_variation(self, original_name: str) -> str:
        """
        🔧 NEW: Tạo biến thể của món ăn để tránh trùng lặp

        Args:
            original_name: Tên món ăn gốc

        Returns:
            str: Tên món ăn biến thể
        """
        # Danh sách các biến thể có thể
        variations = [
            "Đặc Biệt", "Truyền Thống", "Cải Tiến", "Nguyên Bản",
            "Miền Bắc", "Miền Nam", "Miền Trung", "Miền Tây",
            "Sài Gòn", "Hà Nội", "Huế", "Đà Nẵng",
            "Nướng Than", "Nướng Lò", "Chiên Giòn", "Hấp",
            "Cay", "Ngọt", "Đậm Đà", "Nhẹ Nhàng"
        ]

        import random

        # Chọn ngẫu nhiên một biến thể
        variation = random.choice(variations)

        # Tạo tên mới
        if "miền" in variation.lower() or variation in ["Sài Gòn", "Hà Nội", "Huế", "Đà Nẵng"]:
            return f"{original_name} {variation}"
        else:
            return f"{original_name} {variation}"

    def _extract_base_dish_name(self, dish_name: str) -> str:
        """
        Extract base dish name (e.g., "Cơm Tấm Sườn Nướng Mật Ong Sài Gòn" -> "cơm tấm")
        """
        dish_lower = dish_name.lower()

        # Common base dishes
        base_dishes = [
            "cơm tấm", "bánh mì", "phở", "cháo", "bún", "hủ tiếu",
            "mì quảng", "bánh xèo", "bánh khọt", "nem", "chả cá",
            "lẩu", "xôi", "bánh cuốn", "bánh căn"
        ]

        for base in base_dishes:
            if base in dish_lower:
                return base

        # If no base found, return first 2 words
        words = dish_lower.split()
        return " ".join(words[:2]) if len(words) >= 2 else dish_lower

    def _get_official_nutrition(self, dish_name: str, ingredients: List[Dict]) -> Dict:
        """
        Lấy thông tin dinh dưỡng chính thức từ database Việt Nam
        Hỗ trợ phân tích tên món chi tiết như "Cơm gạo lứt với cá hấp và rau luộc"

        Args:
            dish_name: Tên món ăn (có thể chi tiết)
            ingredients: Danh sách nguyên liệu

        Returns:
            Dict chứa thông tin dinh dưỡng chính thức
        """
        try:
            print(f"🔍 Getting nutrition for: {dish_name}")

            # Bước 1: Thử tìm món ăn hoàn chỉnh trong database (tên đơn giản)
            simple_dish_name = self._extract_simple_dish_name(dish_name)
            dish_nutrition = get_dish_nutrition(simple_dish_name)

            if dish_nutrition:
                print(f"✅ Found exact match in database: {simple_dish_name}")
                return {
                    "calories": dish_nutrition["calories"],
                    "protein": dish_nutrition["protein"],
                    "fat": dish_nutrition["fat"],
                    "carbs": dish_nutrition["carbs"],
                    "fiber": dish_nutrition.get("fiber", 0),
                    "source": dish_nutrition["source"],
                    "reference_code": dish_nutrition["reference_code"],
                    "serving_size": dish_nutrition["serving_size"]
                }

            # Bước 2: Phân tích tên món chi tiết và tính từ thành phần
            detailed_ingredients = self._parse_detailed_dish_components(dish_name)
            if detailed_ingredients:
                print(f"🔧 Parsing detailed dish components: {len(detailed_ingredients)} items")
                calculated_nutrition = calculate_dish_nutrition_from_ingredients(detailed_ingredients)

                if calculated_nutrition and calculated_nutrition["calories"] > 0:
                    return self._adjust_calculated_nutrition(calculated_nutrition, dish_name)

            # Bước 3: Nếu có ingredients được cung cấp, tính từ đó
            if ingredients and len(ingredients) > 0:
                print(f"🔧 Calculating from provided ingredients: {len(ingredients)} items")
                calculated_nutrition = calculate_dish_nutrition_from_ingredients(ingredients)

                if calculated_nutrition and calculated_nutrition["calories"] > 0:
                    return self._adjust_calculated_nutrition(calculated_nutrition, dish_name)

            # 🔧 FIX: Fallback nutrition dựa trên loại món ăn
            print(f"⚠️ No official nutrition found for {dish_name}, using meal-type based fallback")

            # Fallback nutrition theo loại bữa ăn
            if "sáng" in dish_name.lower() or any(keyword in dish_name.lower() for keyword in ["bánh mì", "cháo", "xôi"]):
                return {
                    "calories": 350,
                    "protein": 18,
                    "fat": 12,
                    "carbs": 45,
                    "fiber": 3,
                    "source": "Estimated breakfast nutrition",
                    "calculated_from_ingredients": False
                }
            elif any(keyword in dish_name.lower() for keyword in ["cơm", "phở", "bún"]):
                return {
                    "calories": 450,
                    "protein": 25,
                    "fat": 15,
                    "carbs": 55,
                    "fiber": 4,
                    "source": "Estimated main meal nutrition",
                    "calculated_from_ingredients": False
                }
            else:
                return {
                    "calories": 400,
                    "protein": 20,
                    "fat": 15,
                    "carbs": 50,
                    "fiber": 3,
                    "source": "Default estimated nutrition",
                    "calculated_from_ingredients": False
                }

        except Exception as e:
            print(f"⚠️ Error getting official nutrition for {dish_name}: {e}")
            # Emergency fallback
            return {
                "calories": 350,
                "protein": 18,
                "fat": 12,
                "carbs": 45,
                "fiber": 3,
                "source": "Emergency fallback nutrition",
                "calculated_from_ingredients": False
            }

    def _extract_simple_dish_name(self, detailed_dish_name: str) -> str:
        """
        Trích xuất tên món đơn giản từ tên món chi tiết

        Args:
            detailed_dish_name: Tên món chi tiết như "Cơm gạo lứt với cá hấp và rau luộc"

        Returns:
            str: Tên món đơn giản như "cơm cá"
        """
        dish_lower = detailed_dish_name.lower()

        # Mapping các từ khóa chính
        base_foods = ["cơm", "bún", "phở", "mì", "bánh mì", "xôi", "cháo", "hủ tiếu"]
        proteins = ["bò", "gà", "heo", "thịt", "cá", "tôm", "trứng", "chả"]

        # Tìm base food
        found_base = None
        for base in base_foods:
            if base in dish_lower:
                found_base = base
                break

        # Tìm protein
        found_protein = None
        for protein in proteins:
            if protein in dish_lower:
                found_protein = protein
                break

        # Tạo tên đơn giản
        if found_base and found_protein:
            return f"{found_base} {found_protein}"
        elif found_base:
            return found_base
        else:
            # Fallback: lấy 2 từ đầu
            words = dish_lower.split()
            return " ".join(words[:2]) if len(words) >= 2 else dish_lower

    def _parse_detailed_dish_components(self, detailed_dish_name: str) -> List[Dict]:
        """
        Phân tích tên món chi tiết thành danh sách nguyên liệu

        Args:
            detailed_dish_name: Tên món chi tiết

        Returns:
            List[Dict]: Danh sách nguyên liệu với amount
        """
        dish_lower = detailed_dish_name.lower()
        ingredients = []

        # Mapping nguyên liệu và khối lượng ước tính
        ingredient_mapping = {
            # Base foods
            "cơm": {"name": "gạo tẻ", "amount": "150g"},
            "gạo lứt": {"name": "gạo tẻ", "amount": "150g"},  # Tương tự gạo tẻ
            "gạo st25": {"name": "gạo tẻ", "amount": "150g"},
            "bún": {"name": "bún tươi", "amount": "100g"},
            "phở": {"name": "bánh phở", "amount": "100g"},
            "mì": {"name": "bún tươi", "amount": "100g"},  # Tương tự bún
            "bánh mì": {"name": "bánh mì", "amount": "1 ổ"},
            "xôi": {"name": "gạo nếp", "amount": "120g"},
            "cháo": {"name": "gạo tẻ", "amount": "50g"},  # Ít hơn vì nấu cháo

            # Proteins
            "thịt bò": {"name": "thịt bò", "amount": "100g"},
            "thịt heo": {"name": "thịt heo", "amount": "100g"},
            "thịt gà": {"name": "thịt gà", "amount": "120g"},
            "gà": {"name": "thịt gà", "amount": "120g"},
            "cá": {"name": "cá lóc", "amount": "100g"},
            "tôm": {"name": "tôm sú", "amount": "80g"},
            "trứng": {"name": "trứng gà", "amount": "2 quả"},
            "đậu hũ": {"name": "đậu phụ", "amount": "100g"},

            # Vegetables
            "rau muống": {"name": "rau muống", "amount": "100g"},
            "cải thảo": {"name": "cải bắp", "amount": "100g"},
            "bắp cải": {"name": "cải bắp", "amount": "100g"},
            "rau": {"name": "rau muống", "amount": "80g"},  # Default rau

            # Seasonings
            "nước mắm": {"name": "nước mắm", "amount": "1 tbsp"},
            "dầu ăn": {"name": "dầu ăn", "amount": "1 tbsp"}
        }

        # Tìm các nguyên liệu trong tên món
        for keyword, ingredient_info in ingredient_mapping.items():
            if keyword in dish_lower:
                ingredients.append({
                    "name": ingredient_info["name"],
                    "amount": ingredient_info["amount"]
                })

        # Thêm gia vị cơ bản nếu chưa có
        has_seasoning = any("nước mắm" in ing["name"] or "dầu" in ing["name"] for ing in ingredients)
        if not has_seasoning:
            ingredients.extend([
                {"name": "nước mắm", "amount": "1 tbsp"},
                {"name": "dầu ăn", "amount": "1 tbsp"}
            ])

        print(f"🔧 Parsed {len(ingredients)} ingredients from detailed dish name")
        for ing in ingredients:
            print(f"   - {ing['name']}: {ing['amount']}")

        return ingredients

    def _adjust_calculated_nutrition(self, calculated_nutrition: Dict, dish_name: str) -> Dict:
        """
        Điều chỉnh nutrition đã tính toán để đảm bảo hợp lý

        Args:
            calculated_nutrition: Nutrition đã tính từ nguyên liệu
            dish_name: Tên món ăn

        Returns:
            Dict: Nutrition đã điều chỉnh
        """
        # Đảm bảo calories tối thiểu hợp lý cho bữa ăn
        min_calories = 250 if "sáng" in dish_name.lower() else 350

        if calculated_nutrition["calories"] < min_calories:
            print(f"⚠️ Calculated calories too low ({calculated_nutrition['calories']:.1f}), adjusting to minimum {min_calories}")
            # Scale up nutrition proportionally
            scale_factor = min_calories / calculated_nutrition["calories"]
            calculated_nutrition["calories"] *= scale_factor
            calculated_nutrition["protein"] *= scale_factor
            calculated_nutrition["fat"] *= scale_factor
            calculated_nutrition["carbs"] *= scale_factor
            calculated_nutrition["fiber"] *= scale_factor

        return {
            "calories": round(calculated_nutrition["calories"], 1),
            "protein": round(calculated_nutrition["protein"], 1),
            "fat": round(calculated_nutrition["fat"], 1),
            "carbs": round(calculated_nutrition["carbs"], 1),
            "fiber": round(calculated_nutrition["fiber"], 1),
            "source": "Calculated from official Vietnamese ingredients database",
            "sources": calculated_nutrition.get("sources", []),
            "calculated_from_ingredients": True
        }

    def _generate_detailed_health_benefits(self, dish_name: str, ingredients: List[Dict], nutrition: Dict) -> str:
        """
        Tạo lợi ích sức khỏe chi tiết dựa trên nguyên liệu và dinh dưỡng

        Args:
            dish_name: Tên món ăn
            ingredients: Danh sách nguyên liệu
            nutrition: Thông tin dinh dưỡng

        Returns:
            str: Lợi ích sức khỏe chi tiết
        """
        benefits = []

        # Phân tích nguyên liệu để tạo lợi ích cụ thể
        ingredient_names = [ing.get('name', '').lower() for ing in ingredients if ing.get('name')]

        # Lợi ích từ protein
        protein = nutrition.get('protein', 0)
        if protein >= 20:
            benefits.append(f"Giàu protein ({protein}g) giúp xây dựng và phục hồi cơ bắp")
        elif protein >= 15:
            benefits.append(f"Cung cấp protein ({protein}g) hỗ trợ phát triển cơ thể")

        # Lợi ích từ nguyên liệu cụ thể
        if any(keyword in ' '.join(ingredient_names) for keyword in ['gà', 'thịt gà']):
            benefits.append("Thịt gà cung cấp vitamin B6 và niacin tốt cho hệ thần kinh")

        if any(keyword in ' '.join(ingredient_names) for keyword in ['cá', 'tôm', 'cua']):
            benefits.append("Hải sản giàu omega-3 tốt cho tim mạch và não bộ")

        if any(keyword in ' '.join(ingredient_names) for keyword in ['gạo', 'cơm']):
            benefits.append("Gạo cung cấp carbohydrate phức hợp cho năng lượng bền vững")

        if any(keyword in ' '.join(ingredient_names) for keyword in ['rau', 'cải', 'muống']):
            benefits.append("Rau xanh giàu vitamin A, C và chất xơ tốt cho tiêu hóa")

        if any(keyword in ' '.join(ingredient_names) for keyword in ['nước dừa', 'dừa']):
            benefits.append("Nước dừa cung cấp kali và điện giải tự nhiên")

        if any(keyword in ' '.join(ingredient_names) for keyword in ['hạt sen', 'sen']):
            benefits.append("Hạt sen giàu magie và phosphor tốt cho xương khớp")

        if any(keyword in ' '.join(ingredient_names) for keyword in ['nấm']):
            benefits.append("Nấm cung cấp vitamin D và chất chống oxy hóa")

        # Lợi ích từ calories
        calories = nutrition.get('calories', 0)
        if calories <= 300:
            benefits.append("Ít calories phù hợp cho người muốn kiểm soát cân nặng")
        elif calories >= 500:
            benefits.append("Cung cấp năng lượng cao phù hợp cho hoạt động thể chất")

        # Lợi ích từ carbs
        carbs = nutrition.get('carbs', 0)
        if carbs >= 50:
            benefits.append("Carbohydrate cao cung cấp năng lượng nhanh cho cơ thể")
        elif carbs <= 20:
            benefits.append("Ít carbohydrate phù hợp cho chế độ ăn low-carb")

        # Lợi ích chung theo loại món
        if 'cháo' in dish_name.lower():
            benefits.append("Dễ tiêu hóa, phù hợp cho người bệnh và trẻ em")
        elif 'nướng' in dish_name.lower():
            benefits.append("Chế biến nướng giữ nguyên dinh dưỡng và ít dầu mỡ")
        elif 'chay' in dish_name.lower():
            benefits.append("Thực phẩm chay giảm cholesterol và tốt cho môi trường")

        # Nếu không có lợi ích cụ thể, thêm lợi ích chung
        if not benefits:
            benefits.append("Cung cấp dinh dưỡng cân bằng cho cơ thể")
            benefits.append("Món ăn truyền thống Việt Nam tốt cho sức khỏe")

        # Kết hợp thành chuỗi
        if len(benefits) == 1:
            return benefits[0]
        elif len(benefits) == 2:
            return f"{benefits[0]}. {benefits[1]}"
        else:
            return f"{benefits[0]}. {benefits[1]}. {benefits[2] if len(benefits) > 2 else ''}"

    def _ensure_adequate_calories(self, meals: List[Dict], target_calories: int, meal_type: str) -> List[Dict]:
        """
        Đảm bảo tổng calories đạt target, gen thêm món nếu cần

        Args:
            meals: Danh sách món ăn hiện tại
            target_calories: Target calories cần đạt
            meal_type: Loại bữa ăn

        Returns:
            List[Dict]: Danh sách món ăn đã bổ sung
        """
        if not meals:
            return meals

        # Tính tổng calories hiện tại
        total_calories = sum(meal.get('nutrition', {}).get('calories', 0) for meal in meals)
        print(f"📊 Current total calories: {total_calories}, Target: {target_calories}")

        # 🔧 FIX: THỰC TẾ VÀ AN TOÀN - Không tạo dữ liệu dinh dưỡng ảo
        # Chấp nhận sai lệch hợp lý thay vì tạo dữ liệu giả
        acceptable_range = target_calories * 0.15  # Chấp nhận sai lệch 15%

        if abs(total_calories - target_calories) <= acceptable_range:
            print(f"✅ Calories within acceptable range: {total_calories}/{target_calories} (±{acceptable_range:.0f})")
            return meals

        # Tính calories còn thiếu/thừa
        calorie_difference = target_calories - total_calories
        print(f"📊 Calorie difference: {calorie_difference:.0f} calories")

        # 🔧 FIX: Điều chỉnh portion size của món hiện có thay vì tạo món ảo
        if meals and abs(calorie_difference) < target_calories * 0.3:  # Chỉ điều chỉnh nếu sai lệch < 30%
            print(f"🔧 Adjusting portion sizes of existing dishes (realistic approach)")

            # Tính adjustment factor hợp lý
            adjustment_factor = target_calories / total_calories if total_calories > 0 else 1.0

            # Giới hạn adjustment factor trong khoảng hợp lý (0.8 - 1.3)
            # Điều này đảm bảo không thay đổi quá nhiều so với thực tế
            adjustment_factor = max(0.8, min(1.3, adjustment_factor))

            print(f"📊 Applying realistic adjustment factor: {adjustment_factor:.2f}")

            # Điều chỉnh nutrition của các món hiện có
            for meal in meals:
                if 'nutrition' in meal:
                    # Cập nhật portion size trong description
                    if 'description' in meal:
                        if adjustment_factor > 1.05:
                            meal['description'] += " (phần lớn)"
                        elif adjustment_factor < 0.95:
                            meal['description'] += " (phần nhỏ)"

                    # Điều chỉnh nutrition theo tỷ lệ thực tế
                    meal['nutrition']['calories'] *= adjustment_factor
                    meal['nutrition']['protein'] *= adjustment_factor
                    meal['nutrition']['fat'] *= adjustment_factor
                    meal['nutrition']['carbs'] *= adjustment_factor

            new_total = sum(meal.get('nutrition', {}).get('calories', 0) for meal in meals)
            print(f"✅ Adjusted portions realistically. New total: {new_total:.1f} calories")

            return meals

        # 🔧 FIX: Nếu sai lệch quá lớn, thông báo và giữ nguyên thay vì tạo dữ liệu ảo
        if abs(calorie_difference) >= target_calories * 0.3:
            print(f"⚠️ Large calorie difference ({calorie_difference:.0f}). Keeping realistic values instead of creating fake data.")
            print(f"📊 Actual total: {total_calories:.0f} calories vs Target: {target_calories:.0f} calories")

            # Thêm note vào meal để user biết
            for meal in meals:
                if 'description' in meal:
                    if calorie_difference > 0:
                        meal['description'] += f" (Lưu ý: Thực tế ít hơn mục tiêu {abs(calorie_difference):.0f} kcal)"
                    else:
                        meal['description'] += f" (Lưu ý: Thực tế nhiều hơn mục tiêu {abs(calorie_difference):.0f} kcal)"

            return meals

        return meals

    def _create_smart_additional_meal(self, calories: int, protein: int, fat: int, carbs: int, meal_type: str) -> Dict:
        """
        Tạo món ăn bổ sung thông minh dựa trên calories còn thiếu

        Args:
            calories: Calories cần bổ sung
            protein, fat, carbs: Macro targets
            meal_type: Loại bữa ăn

        Returns:
            Dict: Món ăn bổ sung
        """
        # 🔧 FIX: Đảm bảo calories tối thiểu để tránh món quá nhỏ
        min_calories = max(150, calories)  # Minimum 150 calories
        print(f"🔧 Adjusted calories from {calories} to {min_calories} (minimum 150)")

        # Chọn món phù hợp theo calories range (đã điều chỉnh)
        if min_calories <= 200:
            # Món nhẹ nhưng đủ chất
            dish_templates = {
                "bữa sáng": ["Bánh Mì Trứng", "Cháo Yến Mạch", "Sữa Chua Granola"],
                "bữa trưa": ["Cơm Chiên Trứng", "Bún Chả Nhỏ", "Mì Xào Rau"],
                "bữa tối": ["Bánh Xèo Nhỏ", "Gỏi Cuốn", "Chả Giò"]
            }
        elif calories <= 250:
            # Món vừa
            dish_templates = {
                "bữa sáng": ["Bánh Mì Trứng", "Xôi Đậu Xanh", "Cháo Trứng"],
                "bữa trưa": ["Cơm Chiên Trứng", "Bún Chả Nhỏ", "Mì Xào Rau"],
                "bữa tối": ["Bánh Xèo Nhỏ", "Nem Rán", "Chả Giò"]
            }
        else:
            # Món no
            dish_templates = {
                "bữa sáng": ["Phở Gà", "Bánh Mì Thịt", "Cháo Gà"],
                "bữa trưa": ["Cơm Tấm", "Bún Bò", "Mì Quảng"],
                "bữa tối": ["Cơm Chiên", "Bánh Xèo", "Lẩu Nhỏ"]
            }

        # Chọn template phù hợp
        meal_type_key = meal_type.lower()
        if "sáng" in meal_type_key:
            templates = dish_templates.get("bữa sáng", dish_templates["bữa sáng"])
        elif "trưa" in meal_type_key:
            templates = dish_templates.get("bữa trưa", dish_templates["bữa trưa"])
        else:
            templates = dish_templates.get("bữa tối", dish_templates["bữa tối"])

        # Chọn món ngẫu nhiên
        import random
        selected_dish = random.choice(templates)

        # Tạo ingredients phù hợp
        base_ingredients = self._get_ingredients_for_dish(selected_dish, calories)

        # Tạo tên món không trùng với recent dishes
        base_name = selected_dish
        counter = 1
        final_name = base_name

        # Tránh trùng lặp với recent dishes
        while final_name in self.recent_dishes:
            final_name = f"{base_name} Phiên Bản {counter}"
            counter += 1

        # 🔧 FIX: Tính toán lại nutrition với min_calories
        adjusted_protein = max(8, min_calories * 0.15 / 4)  # 15% from protein, min 8g
        adjusted_fat = max(5, min_calories * 0.25 / 9)      # 25% from fat, min 5g
        adjusted_carbs = max(15, min_calories * 0.60 / 4)   # 60% from carbs, min 15g

        print(f"🔧 Adjusted nutrition: {min_calories} kcal, {adjusted_protein:.1f}g protein, {adjusted_fat:.1f}g fat, {adjusted_carbs:.1f}g carbs")

        # Tạo meal object với nutrition đã điều chỉnh
        additional_meal = {
            "name": final_name,
            "description": f"Món {base_name} bổ sung để đạt đủ mục tiêu dinh dưỡng",
            "ingredients": base_ingredients,
            "preparation": [
                f"Chuẩn bị nguyên liệu cho {base_name}",
                "Chế biến theo phương pháp truyền thống",
                "Nêm nướng vừa ăn",
                "Trình bày đẹp mắt"
            ],
            "nutrition": {
                "calories": min_calories,      # 🔧 FIX: Use adjusted calories
                "protein": adjusted_protein,   # 🔧 FIX: Use adjusted protein
                "fat": adjusted_fat,          # 🔧 FIX: Use adjusted fat
                "carbs": adjusted_carbs       # 🔧 FIX: Use adjusted carbs
            },
            "preparation_time": "20 phút",
            "health_benefits": self._generate_detailed_health_benefits(base_name, base_ingredients, {
                "calories": min_calories, "protein": adjusted_protein, "fat": adjusted_fat, "carbs": adjusted_carbs
            })
        }

        # Thêm vào recent dishes để tránh trùng lặp trong tương lai
        self.recent_dishes.append(final_name)
        if len(self.recent_dishes) > self.max_recent_dishes:
            self.recent_dishes.pop(0)

        return additional_meal

    def _get_ingredients_for_dish(self, dish_name: str, target_calories: int) -> List[Dict]:
        """
        Tạo danh sách nguyên liệu phù hợp cho món ăn

        Args:
            dish_name: Tên món ăn
            target_calories: Target calories

        Returns:
            List[Dict]: Danh sách nguyên liệu
        """
        # Base ingredients theo loại món
        if "trứng" in dish_name.lower():
            return [
                {"name": "Trứng gà", "amount": "2 quả"},
                {"name": "Dầu ăn", "amount": "1 tsp"},
                {"name": "Muối", "amount": "1 tsp"}
            ]
        elif "bánh mì" in dish_name.lower():
            return [
                {"name": "Bánh mì", "amount": "1 ổ"},
                {"name": "Thịt", "amount": "50g"},
                {"name": "Rau thơm", "amount": "20g"}
            ]
        elif "cháo" in dish_name.lower():
            return [
                {"name": "Gạo", "amount": "50g"},
                {"name": "Thịt gà", "amount": "80g"},
                {"name": "Hành lá", "amount": "10g"}
            ]
        elif "cơm" in dish_name.lower():
            return [
                {"name": "Cơm", "amount": "150g"},
                {"name": "Thịt", "amount": "100g"},
                {"name": "Rau", "amount": "50g"}
            ]
        else:
            # Default ingredients
            return [
                {"name": "Nguyên liệu chính", "amount": "100g"},
                {"name": "Gia vị", "amount": "vừa đủ"},
                {"name": "Rau thơm", "amount": "20g"}
            ]

    def _validate_required_keys(self, data: Dict) -> bool:
        """
        Validate that all required keys are present in the meal data
        """
        required_keys = ["name", "description", "ingredients", "preparation", "nutrition", "preparation_time", "health_benefits"]

        for key in required_keys:
            if key not in data:
                print(f"❌ Missing required key: {key}")
                return False

        print(f"✅ All required keys present: {required_keys}")
        return True

    def _extract_json_from_response(self, response_text: str) -> List[Dict]:
        """
        Enhanced JSON extraction with multiple fallback strategies

        Args:
            response_text: Văn bản phản hồi từ API

        Returns:
            List[Dict]: Dữ liệu món ăn dạng JSON hoặc None nếu không thể phân tích
        """
        print(f"🔍 Starting enhanced JSON extraction...")

        # Bước 1: Làm sạch response text
        cleaned_text = self._clean_response_text(response_text)
        print(f"📝 Cleaned text length: {len(cleaned_text)}")

        # Bước 2: Thử các phương pháp parsing theo thứ tự ưu tiên
        extraction_methods = [
            ("Direct JSON parsing", self._try_direct_json_parse),
            ("Regex JSON extraction", self._try_regex_json_extract),
            ("Bracket-based extraction", self._try_bracket_extraction),
            ("Advanced JSON fixing", self._try_advanced_json_fix),
            ("Text-to-JSON conversion", self._try_text_to_json)
        ]

        for method_name, method_func in extraction_methods:
            print(f"🔧 Trying {method_name}...")
            try:
                result = method_func(cleaned_text)
                if result and isinstance(result, list) and len(result) > 0:
                    print(f"✅ {method_name} succeeded with {len(result)} items")
                    return result
                else:
                    print(f"❌ {method_name} failed or returned empty result")
            except Exception as e:
                print(f"❌ {method_name} threw exception: {e}")
                continue

        print("❌ All JSON extraction methods failed")
        return None

    def _try_direct_json_parse(self, text: str) -> List[Dict]:
        """Thử parse JSON trực tiếp"""
        meal_data = json.loads(text)
        if isinstance(meal_data, list):
            return self._validate_and_filter_meals(meal_data)
        elif isinstance(meal_data, dict):
            return self._validate_and_filter_meals([meal_data])
        return None

    def _try_regex_json_extract(self, text: str) -> List[Dict]:
        """Sử dụng regex để trích xuất JSON"""
        # Các pattern regex để tìm JSON
        patterns = [
            r'\[\s*\{.*?\}\s*(?:,\s*\{.*?\}\s*)*\]',  # Array of objects
            r'\[.*?\]',                                # Any array
            r'\{.*?\}',                               # Single object
        ]

        for pattern in patterns:
            matches = safe_regex_findall(pattern, text, 16)  # re.DOTALL = 16
            for match in matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, list):
                        result = self._validate_and_filter_meals(data)
                        if result:
                            return result
                    elif isinstance(data, dict):
                        result = self._validate_and_filter_meals([data])
                        if result:
                            return result
                except json.JSONDecodeError:
                    continue
        return None

    def _try_bracket_extraction(self, text: str) -> List[Dict]:
        """Trích xuất JSON giữa dấu ngoặc vuông"""
        start = text.find("[")
        end = text.rfind("]") + 1

        if start >= 0 and end > start:
            json_str = text[start:end]
            try:
                data = json.loads(json_str)
                return self._validate_and_filter_meals(data if isinstance(data, list) else [data])
            except json.JSONDecodeError:
                # Bước 1: Thử fix missing name key trước
                name_fixed = self._fix_missing_name_key(json_str)
                try:
                    data = json.loads(name_fixed)
                    return self._validate_and_filter_meals(data if isinstance(data, list) else [data])
                except json.JSONDecodeError:
                    # Bước 2: Thử sửa JSON toàn diện
                    fixed_json = self._fix_malformed_json(name_fixed)
                    try:
                        data = json.loads(fixed_json)
                        return self._validate_and_filter_meals(data if isinstance(data, list) else [data])
                    except json.JSONDecodeError:
                        pass
        return None

    def _try_advanced_json_fix(self, text: str) -> List[Dict]:
        """Sử dụng advanced JSON fixing"""
        fixed_json = self._advanced_json_repair(text)
        if fixed_json:
            try:
                data = json.loads(fixed_json)
                return self._validate_and_filter_meals(data if isinstance(data, list) else [data])
            except json.JSONDecodeError:
                pass
        return None

    def _try_text_to_json(self, text: str) -> List[Dict]:
        """Chuyển đổi text thành JSON"""
        return self._create_json_from_text(text)

    def _validate_and_filter_meals(self, meal_data: List[Dict]) -> List[Dict]:
        """Validate và filter meals với required keys"""
        if not meal_data:
            return None

        valid_meals = []
        for item in meal_data:
            if isinstance(item, dict) and self._validate_required_keys(item):
                valid_meals.append(item)

        return valid_meals if valid_meals else None

    def _advanced_json_repair(self, text: str) -> str:
        """
        Advanced JSON repair với nhiều kỹ thuật sửa lỗi
        """
        print(f"🔧 Starting advanced JSON repair...")

        # Bước 1: Tìm và sửa pattern thiếu "name" key phổ biến
        # Pattern: { "Bánh Mì Chay", "description": -> { "name": "Bánh Mì Chay", "description":
        text = safe_regex_sub(r'\{\s*"([^"]+)",\s*"description":', r'{"name": "\1", "description":', text)

        # Bước 2: Sửa pattern object đầu tiên thiếu name
        # Pattern: [{ "Dish Name", -> [{ "name": "Dish Name",
        text = safe_regex_sub(r'\[\s*\{\s*"([^"]+)",', r'[{"name": "\1",', text)

        # Bước 3: Sửa missing quotes cho keys
        text = safe_regex_sub(r'(\w+):', r'"\1":', text)

        # Bước 4: Sửa trailing commas
        text = safe_regex_sub(r',\s*}', '}', text)
        text = safe_regex_sub(r',\s*]', ']', text)

        # Bước 5: Đảm bảo cân bằng brackets
        open_brackets = text.count('[')
        close_brackets = text.count(']')
        if open_brackets > close_brackets:
            text += ']' * (open_brackets - close_brackets)

        open_braces = text.count('{')
        close_braces = text.count('}')
        if open_braces > close_braces:
            text += '}' * (open_braces - close_braces)

        return text

    def _create_intelligent_fallback(self, meal_type: str, calories_target: int, protein_target: int, fat_target: int, carbs_target: int) -> List[Dict]:
        """
        🔧 ENHANCED: Tạo intelligent fallback từ database 200+ món ăn truyền thống Việt Nam
        """
        try:
            print(f"🔧 Creating intelligent fallback for {meal_type} from traditional Vietnamese dishes...")

            # Map meal_type to traditional dish categories
            meal_type_lower = meal_type.lower()

            if "sáng" in meal_type_lower:
                target_meal_types = ["breakfast"]
                preferred_categories = ["xôi", "bánh mì", "cháo", "bánh cuốn", "bánh bao"]
            elif "trưa" in meal_type_lower:
                target_meal_types = ["lunch", "dinner"]
                preferred_categories = ["cơm", "bún", "phở", "mì quảng", "hủ tiếu"]
            else:  # dinner
                target_meal_types = ["dinner", "lunch"]
                preferred_categories = ["cơm", "canh", "lẩu", "thịt nướng", "cá kho"]

            # Filter suitable dishes from traditional database
            suitable_dishes = []

            for dish_name, dish_info in ALL_TRADITIONAL_DISHES.items():
                dish_meal_types = dish_info.get("meal_type", [])

                # Check if dish is suitable for this meal type
                if any(mt in dish_meal_types for mt in target_meal_types):
                    # Check if not recently used
                    if dish_name not in self.recent_dishes:
                        suitable_dishes.append((dish_name, dish_info))

            # If no suitable dishes, use any dishes
            if not suitable_dishes:
                suitable_dishes = [(name, info) for name, info in ALL_TRADITIONAL_DISHES.items()
                                 if name not in self.recent_dishes]

            # If still no dishes, use all dishes
            if not suitable_dishes:
                suitable_dishes = list(ALL_TRADITIONAL_DISHES.items())

            # Select random dish
            import random
            selected_dish_name, selected_dish_info = random.choice(suitable_dishes)

            print(f"   📋 Selected traditional dish: {selected_dish_name}")

            # Create intelligent meal from traditional dish
            intelligent_meal = self._create_meal_from_traditional_dish(
                selected_dish_name,
                selected_dish_info,
                calories_target,
                meal_type
            )

            return [intelligent_meal]

        except Exception as e:
            print(f"❌ Intelligent fallback creation failed: {e}")
            # Emergency fallback to simple meal
            return self._create_emergency_fallback_meal(meal_type, calories_target)

    def _create_meal_from_traditional_dish(self, dish_name: str, dish_info: Dict, calories_target: int, meal_type: str) -> Dict:
        """
        🔧 NEW: Tạo meal object từ traditional Vietnamese dish

        Args:
            dish_name: Tên món ăn
            dish_info: Thông tin món ăn từ database
            calories_target: Target calories
            meal_type: Loại bữa ăn

        Returns:
            Dict: Meal object hoàn chỉnh
        """
        try:
            # Get basic info from traditional dish
            description = dish_info.get("description", f"Món {dish_name} truyền thống Việt Nam")
            ingredients = dish_info.get("ingredients", [])
            preparation = dish_info.get("preparation", [])
            region = dish_info.get("region", "Việt Nam")

            # Convert ingredients to proper format
            formatted_ingredients = []
            for ing in ingredients:
                if isinstance(ing, str):
                    formatted_ingredients.append({"name": ing, "amount": "100g"})
                elif isinstance(ing, dict):
                    formatted_ingredients.append({
                        "name": ing.get("name", "Nguyên liệu"),
                        "amount": ing.get("amount", "100g")
                    })

            if not formatted_ingredients:
                formatted_ingredients = [{"name": "Nguyên liệu chính", "amount": "100g"}]

            # Get nutrition from Vietnamese database
            nutrition = self._get_official_nutrition(dish_name, formatted_ingredients)

            if not nutrition:
                # Fallback nutrition based on meal type
                if "sáng" in meal_type.lower():
                    nutrition = {"calories": 350, "protein": 18, "fat": 12, "carbs": 45}
                elif "trưa" in meal_type.lower():
                    nutrition = {"calories": 500, "protein": 28, "fat": 18, "carbs": 60}
                else:
                    nutrition = {"calories": 400, "protein": 22, "fat": 15, "carbs": 50}

            # Create meal object
            meal = {
                "name": dish_name,
                "description": description,
                "ingredients": formatted_ingredients,
                "preparation": preparation if preparation else [
                    f"Chuẩn bị nguyên liệu cho {dish_name}",
                    "Sơ chế và làm sạch nguyên liệu",
                    "Chế biến theo phương pháp truyền thống",
                    "Nêm nướng vừa ăn và trình bày đẹp mắt"
                ],
                "nutrition": nutrition,
                "preparation_time": dish_info.get("preparation_time", "30 phút"),
                "health_benefits": dish_info.get("health_benefits", f"Món {dish_name} cung cấp dinh dưỡng cân bằng, giàu protein và vitamin, tốt cho sức khỏe"),
                "region": region,
                "is_traditional": True,
                "source": "Vietnamese Traditional Dishes Database"
            }

            return meal

        except Exception as e:
            print(f"❌ Error creating meal from traditional dish: {e}")
            return self._create_simple_fallback_meal(dish_name, meal_type, calories_target)

    def _create_emergency_fallback_meal(self, meal_type: str, calories_target: int) -> List[Dict]:
        """
        🔧 NEW: Tạo emergency fallback meal khi tất cả methods khác fail
        """
        try:
            if "sáng" in meal_type.lower():
                dish_name = "Bánh Mì Trứng"
                ingredients = [{"name": "Bánh mì", "amount": "1 ổ"}, {"name": "Trứng gà", "amount": "2 quả"}]
                nutrition = {"calories": 350, "protein": 18, "fat": 12, "carbs": 45}
            elif "trưa" in meal_type.lower():
                dish_name = "Cơm Tấm Sườn"
                ingredients = [{"name": "Cơm tấm", "amount": "150g"}, {"name": "Sườn heo", "amount": "100g"}]
                nutrition = {"calories": 500, "protein": 28, "fat": 18, "carbs": 60}
            else:
                dish_name = "Canh Chua Cá"
                ingredients = [{"name": "Cá tra", "amount": "150g"}, {"name": "Cà chua", "amount": "2 quả"}]
                nutrition = {"calories": 400, "protein": 22, "fat": 15, "carbs": 50}

            meal = {
                "name": dish_name,
                "description": f"Món {dish_name} truyền thống Việt Nam",
                "ingredients": ingredients,
                "preparation": [f"Chuẩn bị {dish_name} theo hướng dẫn truyền thống"],
                "nutrition": nutrition,
                "preparation_time": "30 phút",
                "health_benefits": f"Món {dish_name} cung cấp dinh dưỡng cân bằng",
                "is_emergency_fallback": True
            }

            return [meal]

        except Exception as e:
            print(f"❌ Emergency fallback failed: {e}")
            return []

    def _create_simple_fallback_meal(self, dish_name: str, meal_type: str, calories_target: int) -> Dict:
        """
        🔧 NEW: Tạo simple fallback meal cho một món cụ thể
        """
        return {
            "name": dish_name,
            "description": f"Món {dish_name} truyền thống Việt Nam",
            "ingredients": [{"name": "Nguyên liệu chính", "amount": "100g"}],
            "preparation": [f"Chuẩn bị {dish_name} theo hướng dẫn"],
            "nutrition": {"calories": calories_target, "protein": 20, "fat": 15, "carbs": 45},
            "preparation_time": "30 phút",
            "health_benefits": f"Món {dish_name} cung cấp dinh dưỡng cân bằng",
            "is_simple_fallback": True
        }

    def _create_json_from_text(self, text: str) -> List[Dict]:
        """
        Tạo JSON từ text response khi parsing thất bại - phương pháp mạnh mẽ hơn
        """
        try:
            print(f"🔧 Creating JSON from text response...")

            # Phương pháp 1: Tìm tên món ăn từ quotes
            dish_names = safe_regex_findall(r'"([^"]*(?:Bánh|Cơm|Phở|Bún|Cháo|Chả|Gỏi|Canh|Xôi|Nem|Gà|Heo|Bò)[^"]*)"', text, 2)  # re.IGNORECASE = 2

            # Phương pháp 2: Tìm từ pattern Vietnamese dish names
            if not dish_names:
                dish_names = safe_regex_findall(r'([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ\s]+(?:Bánh|Cơm|Phở|Bún|Cháo|Chả|Gỏi|Canh|Xôi|Nem|Gà|Heo|Bò)[a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ\s]*)', text)

            # Phương pháp 3: Fallback với common Vietnamese dishes
            if not dish_names:
                common_dishes = ["Bánh Mì Chay", "Cơm Tấm", "Phở Gà", "Bún Bò", "Cháo Gà", "Xôi Xéo"]
                dish_names = [common_dishes[0]]  # Chọn món đầu tiên
                print(f"⚠️ Using fallback dish name: {dish_names[0]}")

            print(f"🍽️ Found dish names: {dish_names}")

            # Tìm thông tin dinh dưỡng từ text nếu có
            calories_match = safe_regex_search(r'"?calories"?\s*:\s*(\d+)', text)
            protein_match = safe_regex_search(r'"?protein"?\s*:\s*(\d+)', text)
            fat_match = safe_regex_search(r'"?fat"?\s*:\s*(\d+)', text)
            carbs_match = safe_regex_search(r'"?carbs"?\s*:\s*(\d+)', text)

            # Tìm ingredients từ text
            ingredients_text = safe_regex_search(r'"?ingredients"?\s*:\s*\[(.*?)\]', text, 16)  # re.DOTALL = 16
            ingredients = []
            if ingredients_text:
                ingredient_matches = safe_regex_findall(r'"?name"?\s*:\s*"([^"]+)".*?"?amount"?\s*:\s*"([^"]+)"', ingredients_text.group(1))
                ingredients = [{"name": name, "amount": amount} for name, amount in ingredient_matches[:4]]

            if not ingredients:
                ingredients = [
                    {"name": "Nguyên liệu chính", "amount": "100g"},
                    {"name": "Gia vị", "amount": "vừa đủ"},
                    {"name": "Rau thơm", "amount": "20g"}
                ]

            meals = []
            for i, name in enumerate(dish_names[:2]):  # Tối đa 2 món
                # Sử dụng nutrition từ text nếu có, nếu không thì dùng default
                # CRITICAL: Ensure values are NEVER zero to prevent division by zero
                calories = max(int(calories_match.group(1)), 200) if calories_match else (300 + i * 50)
                protein = max(int(protein_match.group(1)), 10) if protein_match else (20 + i * 5)
                fat = max(int(fat_match.group(1)), 5) if fat_match else (12 + i * 3)
                carbs = max(int(carbs_match.group(1)), 20) if carbs_match else (35 + i * 10)

                meal = {
                    "name": name.strip(),
                    "description": f"Món {name.strip()} thơm ngon và bổ dưỡng theo phong cách Việt Nam",
                    "ingredients": ingredients,
                    "preparation": [
                        f"Chuẩn bị nguyên liệu cho {name.strip()}",
                        "Sơ chế và làm sạch nguyên liệu",
                        "Chế biến theo hướng dẫn truyền thống",
                        "Nêm nướng vừa ăn và trình bày đẹp mắt"
                    ],
                    "nutrition": {
                        "calories": calories,
                        "protein": protein,
                        "fat": fat,
                        "carbs": carbs
                    },
                    "preparation_time": "30 phút",
                    "health_benefits": f"Món {name.strip()} cung cấp dinh dưỡng cân bằng, giàu protein và vitamin, tốt cho sức khỏe"
                }
                meals.append(meal)

            print(f"✅ Successfully created {len(meals)} meals from text")
            return meals if meals else None

        except Exception as e:
            print(f"❌ Error creating JSON from text: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _clean_response_text(self, text: str) -> str:
        """
        Làm sạch response text để cải thiện khả năng parse JSON
        """
        # Loại bỏ markdown code blocks
        text = safe_regex_sub(r'```json\s*', '', text)
        text = safe_regex_sub(r'```\s*', '', text)

        # Loại bỏ các ký tự không cần thiết ở đầu và cuối
        text = text.strip()

        # Loại bỏ các dòng text không phải JSON ở đầu
        lines = text.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('[') or line.strip().startswith('{'):
                start_idx = i
                break

        if start_idx > 0:
            text = '\n'.join(lines[start_idx:])

        return text

    def _fix_missing_name_key(self, json_str: str) -> str:
        """
        Đặc biệt xử lý trường hợp missing "name" key - vấn đề phổ biến nhất
        """
        print(f"🔧 Fixing missing 'name' key specifically...")

        # Pattern 1: { "Bánh Mì Chay", "description": -> { "name": "Bánh Mì Chay", "description":
        fixed = safe_regex_sub(r'\{\s*"([^"]+)",\s*"description":', r'{"name": "\1", "description":', json_str)

        # Pattern 2: [ { "Dish Name", -> [ { "name": "Dish Name",
        fixed = safe_regex_sub(r'\[\s*\{\s*"([^"]+)",', r'[{"name": "\1",', fixed)

        # Pattern 3: { "Bánh Mì Chay", "Món bánh mì..." -> { "name": "Bánh Mì Chay", "description": "Món bánh mì..."
        fixed = safe_regex_sub(r'\{\s*"([^"]+)",\s*"([^"]*[a-z][^"]*)",', r'{"name": "\1", "description": "\2",', fixed)

        # Pattern 4: }, { "Next Dish", -> }, { "name": "Next Dish",
        fixed = safe_regex_sub(r'\},\s*\{\s*"([^"]+)",', r'}, {"name": "\1",', fixed)

        if fixed != json_str:
            print(f"✅ Successfully fixed missing 'name' key patterns")
            return fixed
        else:
            print(f"⚠️ No missing 'name' key patterns found")
            return json_str

    def _fix_malformed_json(self, json_str: str) -> str:
        """
        Ultra-robust JSON fixing với nhiều pattern matching - Enhanced version
        """
        print(f"🔧 Attempting ultra-robust JSON fixing...")
        original_json = json_str

        # Bước 0: Làm sạch cơ bản
        json_str = json_str.strip()

        # Bước 1: Sửa pattern phổ biến nhất - missing "name" key
        # Pattern cực kỳ cụ thể: { "Bánh Mì Chay", "description": -> { "name": "Bánh Mì Chay", "description":
        json_str = safe_regex_sub(r'\{\s*"([^"]+)",\s*"description":', r'{"name": "\1", "description":', json_str)

        # Pattern: { "Dish Name", "Món ăn..." -> { "name": "Dish Name", "description": "Món ăn..."
        json_str = safe_regex_sub(r'\{\s*"([^"]+)",\s*"(Món [^"]*)"', r'{"name": "\1", "description": "\2"', json_str)

        # Pattern đặc biệt cho trường hợp chỉ có tên món: { "Bánh Mì Chay", -> { "name": "Bánh Mì Chay",
        json_str = safe_regex_sub(r'\{\s*"([^"]+)",\s*([^"])', r'{"name": "\1", \2', json_str)

        # Pattern: [ { "Dish Name", -> [ { "name": "Dish Name",
        json_str = safe_regex_sub(r'\[\s*\{\s*"([^"]+)",', r'[{"name": "\1",', json_str)

        # Pattern đặc biệt cho trường hợp không có field name: { "Bánh Mì Chay", [array]
        json_str = safe_regex_sub(r'\{\s*"([^"]+)",\s*\[', r'{"name": "\1", "ingredients": [', json_str)

        # Pattern mới: Xử lý trường hợp có text description nhưng không có key
        # { "Bánh Mì Chay", "Bánh mì chay thơm ngon..." -> { "name": "Bánh Mì Chay", "description": "Bánh mì chay thơm ngon..."
        json_str = safe_regex_sub(r'\{\s*"([^"]+)",\s*"([^"]*[a-z][^"]*)",', r'{"name": "\1", "description": "\2",', json_str)

        # Bước 2: Sửa missing field names cho các trường hợp phức tạp
        # Pattern: "name": "...", "text without field", -> "name": "...", "description": "text",
        json_str = safe_regex_sub(r'"name":\s*"([^"]+)",\s*"([^"]+)",\s*\[', r'"name": "\1", "description": "\2", "ingredients": [', json_str)

        # Sửa trường hợp thiếu key cho ingredients, preparation, etc.
        json_str = safe_regex_sub(r'",\s*\[\s*\{', r'", "ingredients": [{', json_str)
        json_str = safe_regex_sub(r'\],\s*\[\s*"', r'], "preparation": ["', json_str)
        json_str = safe_regex_sub(r'"\],\s*\{', r'"], "nutrition": {', json_str)
        json_str = safe_regex_sub(r'\},\s*"([^"]+)",\s*"([^"]+)"\s*\}', r'}, "preparation_time": "\1", "health_benefits": "\2"}', json_str)

        # Bước 4: Sửa malformed arrays - loại bỏ quotes xung quanh arrays
        json_str = safe_regex_sub(r'"\s*\[\s*', r'[', json_str)
        json_str = safe_regex_sub(r'\s*\]\s*"', r']', json_str)

        # Bước 5: Sửa missing field names cho arrays
        # Pattern: , [ -> , "ingredients": [
        json_str = safe_regex_sub(r',\s*\[\s*\{', r', "ingredients": [{', json_str)
        json_str = safe_regex_sub(r',\s*\[\s*"', r', "preparation": ["', json_str)

        # Bước 6: Sửa missing quotes cho object keys
        json_str = safe_regex_sub(r'(\w+):', r'"\1":', json_str)

        # Bước 7: Sửa trailing commas
        json_str = safe_regex_sub(r',\s*}', '}', json_str)
        json_str = safe_regex_sub(r',\s*]', ']', json_str)

        # Bước 8: Sửa single quotes thành double quotes
        json_str = safe_regex_sub(r"'([^']*)':", r'"\1":', json_str)
        json_str = safe_regex_sub(r":\s*'([^']*)'", r': "\1"', json_str)

        # Bước 9: Sửa broken objects - thêm missing closing braces
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
            print(f"⚠️ Added {open_braces - close_braces} missing closing braces")

        # Bước 10: Sửa broken arrays - thêm missing closing brackets
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')
        if open_brackets > close_brackets:
            json_str += ']' * (open_brackets - close_brackets)
            print(f"⚠️ Added {open_brackets - close_brackets} missing closing brackets")

        # Bước 11: Đảm bảo có đủ required fields
        if '"name"' not in json_str:
            print("⚠️ Missing name field, attempting to add...")
            json_str = safe_regex_sub(r'\{', r'{"name": "Vietnamese Dish",', json_str, count=1)

        if '"description"' not in json_str:
            print("⚠️ Missing description field, attempting to add...")
            json_str = safe_regex_sub(r'"name":\s*"([^"]*)",', r'"name": "\1", "description": "Món ăn Việt Nam truyền thống",', json_str)

        if '"ingredients"' not in json_str:
            print("⚠️ Missing ingredients field, attempting to add...")
            json_str = safe_regex_sub(r'"description":\s*"[^"]*",', r'\g<0> "ingredients": [{"name": "Nguyên liệu", "amount": "100g"}],', json_str)

        # Bước 12: Sửa malformed nutrition objects
        if '"nutrition"' in json_str:
            # Ensure nutrition has proper structure
            nutrition_pattern = r'"nutrition":\s*\{[^}]*\}'
            if not safe_regex_search(nutrition_pattern, json_str):
                print("⚠️ Fixing malformed nutrition object...")
                json_str = safe_regex_sub(r'"nutrition":\s*[^,}]+', r'"nutrition": {"calories": 300, "protein": 20, "fat": 10, "carbs": 40}', json_str)

        if original_json != json_str:
            print(f"🔧 JSON was extensively modified during fixing")
            print(f"Original length: {len(original_json)}")
            print(f"Fixed length: {len(json_str)}")

            # Show key changes
            if '"name":' in json_str and '"name":' not in original_json:
                print("✅ Added missing 'name' field")
            if '"description":' in json_str and '"description":' not in original_json:
                print("✅ Added missing 'description' field")

        return json_str

    def _validate_meals(self, meal_data: List[Dict]) -> List[Dict]:
        """
        Validate meal data with strict schema validation

        Args:
            meal_data: List of meal dictionaries to validate

        Returns:
            List of validated meal dictionaries
        """
        valid_meals = []
        required_fields = ['name', 'description', 'ingredients', 'preparation', 'nutrition', 'preparation_time', 'health_benefits']

        for i, meal in enumerate(meal_data):
            print(f"Validating meal {i+1}: {meal}")

            if not isinstance(meal, dict):
                print(f"❌ Skipping non-dict meal: {meal}")
                continue

            # Strict validation - meal must have name
            if 'name' not in meal or not meal['name'] or not isinstance(meal['name'], str):
                print(f"❌ Skipping meal without valid name: {meal}")
                continue

            meal_name = meal['name']
            print(f"✅ Validating meal: {meal_name}")

            # Validate and fix each required field
            # Description
            if 'description' not in meal or not isinstance(meal['description'], str):
                meal['description'] = f"Món ăn {meal_name} ngon và bổ dưỡng"
                print(f"🔧 Fixed description for {meal_name}")

            # Ingredients - must be array of objects with name and amount
            if 'ingredients' not in meal or not isinstance(meal['ingredients'], list):
                meal['ingredients'] = [{'name': 'Nguyên liệu chính', 'amount': '100g'}]
                print(f"🔧 Fixed ingredients for {meal_name}")
            else:
                # Validate each ingredient
                fixed_ingredients = []
                for ing in meal['ingredients']:
                    if isinstance(ing, dict) and 'name' in ing and 'amount' in ing:
                        fixed_ingredients.append({
                            'name': str(ing['name']),
                            'amount': str(ing['amount'])
                        })
                    elif isinstance(ing, str):
                        # If ingredient is just a string, convert to proper format
                        fixed_ingredients.append({'name': ing, 'amount': '100g'})

                if not fixed_ingredients:
                    fixed_ingredients = [{'name': 'Nguyên liệu chính', 'amount': '100g'}]

                meal['ingredients'] = fixed_ingredients
                print(f"🔧 Fixed {len(fixed_ingredients)} ingredients for {meal_name}")

            # Preparation - must be array of strings
            if 'preparation' not in meal:
                meal['preparation'] = [f"Chuẩn bị {meal_name} theo hướng dẫn"]
                print(f"🔧 Added default preparation for {meal_name}")
            elif isinstance(meal['preparation'], str):
                meal['preparation'] = [meal['preparation']]
                print(f"🔧 Converted preparation string to array for {meal_name}")
            elif isinstance(meal['preparation'], list):
                meal['preparation'] = [str(step) for step in meal['preparation'] if step]
                if not meal['preparation']:
                    meal['preparation'] = [f"Chuẩn bị {meal_name} theo hướng dẫn"]
            else:
                meal['preparation'] = [f"Chuẩn bị {meal_name} theo hướng dẫn"]
                print(f"🔧 Fixed invalid preparation format for {meal_name}")

            # Nutrition - use official Vietnamese database when possible
            official_nutrition = self._get_official_nutrition(meal_name, meal.get('ingredients', []))

            if official_nutrition:
                meal['nutrition'] = official_nutrition
                print(f"🏛️ Using official Vietnamese nutrition data for {meal_name}")
                print(f"   Source: {official_nutrition.get('source', 'Official database')}")
            else:
                # Fallback to default values if no official data
                default_nutrition = {'calories': 400, 'protein': 20, 'fat': 15, 'carbs': 45}
                if 'nutrition' not in meal or not isinstance(meal['nutrition'], dict):
                    meal['nutrition'] = default_nutrition.copy()
                    print(f"🔧 Added default nutrition for {meal_name}")
                else:
                    # Ensure all nutrition values are numbers and NOT zero
                    nutrition = meal['nutrition']
                    for key in ['calories', 'protein', 'fat', 'carbs']:
                        if key not in nutrition:
                            nutrition[key] = default_nutrition[key]
                        else:
                            try:
                                value = float(nutrition[key])
                                # CRITICAL: Ensure value is never zero to prevent division by zero
                                if value <= 0:
                                    nutrition[key] = default_nutrition[key]
                                    print(f"🔧 Fixed zero/negative {key} value for {meal_name}")
                                else:
                                    nutrition[key] = value
                            except (ValueError, TypeError):
                                nutrition[key] = default_nutrition[key]
                                print(f"🔧 Fixed invalid {key} value for {meal_name}")

            # Preparation time
            if 'preparation_time' not in meal or not isinstance(meal['preparation_time'], str):
                meal['preparation_time'] = "30 phút"
                print(f"🔧 Added default preparation_time for {meal_name}")

            # Health benefits - enhanced with detailed benefits
            if 'health_benefits' not in meal or not isinstance(meal['health_benefits'], str) or len(meal['health_benefits']) < 50:
                meal['health_benefits'] = self._generate_detailed_health_benefits(meal_name, meal.get('ingredients', []), meal.get('nutrition', {}))
                print(f"🔧 Added detailed health_benefits for {meal_name}")

            # Final validation - ensure all required fields exist
            missing_fields = [field for field in required_fields if field not in meal]
            if missing_fields:
                print(f"❌ Meal {meal_name} still missing fields: {missing_fields}")
                continue

            valid_meals.append(meal)
            print(f"✅ Successfully validated meal: {meal_name}")

        print(f"📊 Validation complete: {len(valid_meals)} out of {len(meal_data)} meals are valid")
        return valid_meals

    def _get_fallback_meals(self, meal_type: str) -> List[Dict]:
        """
        🔧 FIX: Lấy dữ liệu món ăn dự phòng đa dạng

        Args:
            meal_type: Loại bữa ăn (bữa sáng, bữa trưa, bữa tối)

        Returns:
            Danh sách các món ăn dự phòng (nhiều món hơn)
        """
        meal_type_lower = meal_type.lower()

        # 🔧 FIX: Sử dụng key mapping chính xác
        if "sáng" in meal_type_lower or "sang" in meal_type_lower:
            meals = FALLBACK_MEALS.get("bữa sáng", [])
        elif "trưa" in meal_type_lower or "trua" in meal_type_lower:
            meals = FALLBACK_MEALS.get("bữa trưa", [])
        elif "tối" in meal_type_lower or "toi" in meal_type_lower:
            meals = FALLBACK_MEALS.get("bữa tối", [])
        else:
            # Trả về hỗn hợp các món
            all_meals = []
            for meals_list in FALLBACK_MEALS.values():
                all_meals.extend(meals_list)

            # Trộn danh sách để lấy ngẫu nhiên
            random.shuffle(all_meals)
            return all_meals[:3]  # Trả về tối đa 3 món

        print(f"🔧 Found {len(meals)} fallback meals for {meal_type}")
        return meals

    def _generate_realistic_combination_dishes(self, meal_type: str, preferences: List[str], allergies: List[str]) -> List[str]:
        """
        Tạo danh sách món ăn kết hợp thực tế theo meal_type

        Args:
            meal_type: Loại bữa ăn
            preferences: Sở thích
            allergies: Dị ứng

        Returns:
            List[str]: Danh sách món ăn kết hợp
        """
        # Định nghĩa các thành phần cơ bản
        base_foods = {
            "breakfast": ["cơm", "cháo", "bánh mì", "xôi", "phở"],
            "lunch": ["cơm", "bún", "mì", "hủ tiếu", "phở"],
            "dinner": ["cơm", "bún", "mì", "canh", "lẩu"]
        }

        proteins = {
            "breakfast": ["trứng", "thịt", "gà", "chả", "giò"],
            "lunch": ["thịt", "gà", "cá", "tôm", "bò", "heo", "chả cá"],
            "dinner": ["thịt", "gà", "cá", "tôm", "bò", "canh chua", "lẩu"]
        }

        vegetables = ["rau muống", "cải thảo", "bắp cải", "cà rót", "đậu bắp", "rau dền"]

        # Lấy thành phần theo meal_type
        meal_bases = base_foods.get(meal_type.lower(), base_foods["lunch"])
        meal_proteins = proteins.get(meal_type.lower(), proteins["lunch"])

        # Tạo các món ăn kết hợp chi tiết
        combination_dishes = []

        # Tạo món chính với protein chi tiết
        for base in meal_bases[:3]:  # Lấy 3 base foods phổ biến nhất
            for protein in meal_proteins[:4]:  # Lấy 4 proteins phổ biến nhất
                detailed_dish_name = self._create_detailed_dish_name(base, protein, meal_type)
                combination_dishes.append(detailed_dish_name)

        # Thêm món rau
        for veg in vegetables[:3]:
            combination_dishes.append(f"Rau {veg.title()}")
            combination_dishes.append(f"{veg.title()} Xào")

        # Thêm canh/soup cho bữa tối
        if meal_type.lower() == "dinner":
            soups = ["Canh Chua", "Canh Rau", "Canh Thịt", "Canh Cá"]
            combination_dishes.extend(soups)

        # Lọc theo preferences và allergies
        if preferences:
            # Ưu tiên các món có chứa preferences
            preferred_dishes = [dish for dish in combination_dishes
                             if any(pref.lower() in dish.lower() for pref in preferences)]
            if preferred_dishes:
                combination_dishes = preferred_dishes + combination_dishes

        if allergies:
            # Loại bỏ các món có chứa allergies
            combination_dishes = [dish for dish in combination_dishes
                                if not any(allergy.lower() in dish.lower() for allergy in allergies)]

        # Loại bỏ trùng lặp và giới hạn số lượng
        combination_dishes = list(dict.fromkeys(combination_dishes))[:20]

        return combination_dishes

    def _create_detailed_dish_name(self, base_food: str, protein_type: str, meal_type: str) -> str:
        """
        Tạo tên món ăn chi tiết và cụ thể như "Cơm gạo lứt với cá hấp và rau luộc"

        Args:
            base_food: Thực phẩm cơ bản
            protein_type: Loại protein
            meal_type: Loại bữa ăn

        Returns:
            str: Tên món ăn chi tiết
        """
        import random

        # Các biến thể chi tiết cho thực phẩm cơ bản
        base_food_details = {
            "cơm": [
                "Cơm trắng", "Cơm gạo lứt", "Cơm tấm", "Cơm dẻo",
                "Cơm niêu", "Cơm gạo thơm", "Cơm gạo tám", "Cơm gạo ST25"
            ],
            "bún": [
                "Bún tươi", "Bún khô", "Bún tàu", "Bún gạo",
                "Bún mềm", "Bún dai", "Bún tròn"
            ],
            "phở": [
                "Phở tươi", "Phở khô", "Phở bánh dày",
                "Phở bánh mỏng", "Phở Hà Nội", "Phở Nam Định"
            ],
            "mì": [
                "Mì tươi", "Mì khô", "Mì trứng", "Mì gạo",
                "Mì vàng", "Mì sợi nhỏ", "Mì Ý"
            ],
            "bánh mì": [
                "Bánh mì Việt Nam", "Bánh mì giòn", "Bánh mì tươi",
                "Bánh mì nướng", "Bánh mì Sài Gòn", "Bánh mì que"
            ],
            "xôi": [
                "Xôi nếp", "Xôi dẻo", "Xôi trắng", "Xôi thơm",
                "Xôi nước cốt dừa", "Xôi lá dứa"
            ],
            "cháo": [
                "Cháo trắng", "Cháo gạo tẻ", "Cháo sánh",
                "Cháo loãng", "Cháo dinh dưỡng", "Cháo hến"
            ]
        }

        # Các cách chế biến protein chi tiết
        protein_cooking_methods = {
            "thịt": [
                "thịt nướng than", "thịt luộc", "thịt xào lăn", "thịt rim mặn",
                "thịt áp chảo", "thịt chiên giòn", "thịt nướng mật ong"
            ],
            "thịt heo": [
                "thịt heo nướng", "thịt heo luộc", "thịt heo quay",
                "thịt heo xào", "thịt heo rim", "thịt heo áp chảo"
            ],
            "thịt bò": [
                "thịt bò nướng lá lốt", "thịt bò xào", "thịt bò lúc lắc",
                "thịt bò áp chảo", "thịt bò tái", "thịt bò nướng mỡ chài"
            ],
            "gà": [
                "gà nướng", "gà luộc", "gà chiên giòn", "gà quay",
                "gà hấp", "gà xào sả ớt", "gà nướng mật ong"
            ],
            "cá": [
                "cá hấp", "cá nướng", "cá chiên", "cá kho tộ",
                "cá áp chảo", "cá sốt cà chua", "cá nướng lá chuối"
            ],
            "tôm": [
                "tôm hấp", "tôm nướng", "tôm chiên", "tôm xào",
                "tôm luộc", "tôm rang me", "tôm nướng muối ớt"
            ],
            "trứng": [
                "trứng chiên", "trứng luộc", "trứng ốp la",
                "trứng hấp", "trứng xào", "trứng cuộn"
            ]
        }

        # Các loại rau/món phụ chi tiết
        side_dishes_by_meal = {
            "breakfast": [
                "rau sống", "dưa chua", "cà chua", "dưa leo"
            ],
            "lunch": [
                "rau luộc", "rau xào tỏi", "canh rau", "súp rau",
                "rau muống xào", "cải thảo luộc", "bắp cải xào",
                "đậu bắp xào", "mướp xào", "bí đỏ hầm"
            ],
            "dinner": [
                "canh chua", "canh rau", "rau luộc chấm mắm",
                "salad rau thơm", "rau muống luộc", "cải thảo cuộn",
                "súp bí đỏ", "canh khổ qua"
            ]
        }

        # Chọn biến thể ngẫu nhiên
        base_options = base_food_details.get(base_food.lower(), [base_food.title()])
        protein_options = protein_cooking_methods.get(protein_type.lower(), [protein_type])
        side_options = side_dishes_by_meal.get(meal_type.lower(), side_dishes_by_meal["lunch"])

        selected_base = random.choice(base_options)
        selected_protein = random.choice(protein_options)

        # Tạo tên món chi tiết
        dish_name = f"{selected_base} với {selected_protein}"

        # Thêm món phụ (80% cơ hội)
        if random.random() < 0.8:
            selected_side = random.choice(side_options)
            dish_name += f" và {selected_side}"

        # Thêm chi tiết bổ sung cho một số món (30% cơ hội)
        if random.random() < 0.3:
            extras = [
                "chấm nước mắm", "ăn kèm dưa chua", "có bánh tráng",
                "nước dùng trong", "gia vị đậm đà", "thơm ngon"
            ]
            selected_extra = random.choice(extras)
            dish_name += f" ({selected_extra})"

        return dish_name

    def _get_combination_dishes_prompt(self, meal_type: str, calories_target: int, protein_target: int,
                                     fat_target: int, carbs_target: int, preferences_str: str,
                                     allergies_str: str, combination_dishes: List[str], recent_dishes_str: str) -> str:
        """
        Tạo prompt cho việc tạo món ăn kết hợp thực tế

        Args:
            meal_type: Loại bữa ăn
            calories_target, protein_target, fat_target, carbs_target: Mục tiêu dinh dưỡng
            preferences_str: Sở thích
            allergies_str: Dị ứng
            combination_dishes: Danh sách món ăn kết hợp
            recent_dishes_str: Món ăn gần đây

        Returns:
            str: Prompt cho AI
        """
        combination_dishes_str = ", ".join(combination_dishes[:15])  # Lấy 15 món đầu

        prompt = f"""
        Bạn là chuyên gia dinh dưỡng Việt Nam. Hãy tạo kế hoạch {meal_type} với các món ăn kết hợp THỰC TẾ và CỤ THỂ.

        QUAN TRỌNG: Tạo tên món ăn CHI TIẾT và CỤ THỂ theo cách người Việt thường gọi:
        - "Cơm gạo lứt với thịt heo nướng và rau luộc" thay vì "Cơm thịt"
        - "Bún tươi với gà nướng mật ong và rau thơm" thay vì "Bún gà"
        - "Phở tươi với thịt bò tái và rau sống" thay vì "Phở bò"
        - "Cháo trắng với cá hấp và rau muống luộc" thay vì "Cháo cá"
        - "Mì trứng xào với tôm và cải thảo" thay vì "Mì tôm"

        Gợi ý món ăn kết hợp phù hợp: {combination_dishes_str}

        Mục tiêu dinh dưỡng:
        - Calories: {calories_target} kcal
        - Protein: {protein_target}g
        - Fat: {fat_target}g
        - Carbs: {carbs_target}g

        Sở thích: {preferences_str}
        Dị ứng: {allergies_str}
        Tránh lặp lại: {recent_dishes_str}

        Hãy trả về JSON với format chính xác:
        [
            {{
                "name": "Cơm gạo lứt với thịt heo nướng và rau luộc",
                "description": "Cơm gạo lứt thơm ngon ăn kèm thịt heo nướng vàng ươm, rau luộc tươi xanh và nước mắm chấm",
                "ingredients": [
                    {{"name": "Cơm trắng", "amount": "150g"}},
                    {{"name": "Thịt heo nướng", "amount": "100g"}},
                    {{"name": "Rau sống", "amount": "30g"}},
                    {{"name": "Nước mắm", "amount": "1 tbsp"}}
                ],
                "preparation": [
                    "Nướng thịt heo với gia vị đến vàng ươm",
                    "Chuẩn bị cơm trắng và rau sống",
                    "Pha nước mắm chấm",
                    "Trình bày đẹp mắt"
                ],
                "nutrition": {{
                    "calories": 450,
                    "protein": 28,
                    "fat": 15,
                    "carbs": 52
                }},
                "preparation_time": "25 phút",
                "health_benefits": "Cung cấp protein chất lượng cao từ thịt, carbohydrate từ cơm, vitamin từ rau sống"
            }}
        ]

        Lưu ý:
        - Tạo 2-3 món ăn đa dạng
        - Tên món phải cụ thể và thực tế
        - Bao gồm cả món chính và món phụ (rau, canh)
        - Dinh dưỡng phải chính xác và cân bằng
        - Nguyên liệu và cách chế biến phải chi tiết
        """

        return prompt

    def _fallback_meal_suggestions(self, meal_type: str) -> List[Dict]:
        """
        🔧 ENHANCED: Fallback với món ăn kết hợp thực tế
        """
        try:
            print(f"🔧 Creating realistic combination fallback meals for {meal_type}...")

            # Tạo món ăn kết hợp thực tế
            combination_dishes = self._generate_realistic_combination_dishes(meal_type, [], [])

            # Chọn ngẫu nhiên 2-3 món từ danh sách
            import random
            selected_count = min(3, len(combination_dishes))
            selected_dishes = random.sample(combination_dishes, selected_count)

            fallback_meals = []
            for dish_name in selected_dishes:
                # Tạo meal object từ tên món kết hợp
                meal = self._create_realistic_combination_meal(dish_name, meal_type)
                fallback_meals.append(meal)

            print(f"✅ Created {len(fallback_meals)} realistic combination fallback meals")
            return fallback_meals

        except Exception as e:
            print(f"❌ Realistic combination fallback failed: {e}")
            # Emergency fallback to traditional method
            return self._traditional_fallback_meal_suggestions(meal_type)

    def _create_realistic_combination_meal(self, dish_name: str, meal_type: str) -> Dict:
        """
        Tạo meal object từ tên món ăn kết hợp thực tế

        Args:
            dish_name: Tên món ăn kết hợp (ví dụ: "Cơm Thịt Nướng")
            meal_type: Loại bữa ăn

        Returns:
            Dict: Meal object hoàn chỉnh
        """
        try:
            # Phân tích tên món để xác định thành phần
            base_food, protein_type = self._parse_combination_dish_name(dish_name)

            # Tạo ingredients
            ingredients = self._create_combination_ingredients(base_food, protein_type, [])

            # Tạo preparation steps
            preparation = self._create_combination_preparation(base_food, protein_type)

            # Tính toán nutrition
            calories_target = 400 if meal_type.lower() == "breakfast" else 500
            nutrition = self._calculate_combination_nutrition(base_food, protein_type, calories_target)

            # Tạo description
            description = self._create_combination_description(base_food, protein_type)

            # Tạo health benefits
            health_benefits = self._create_combination_health_benefits(base_food, protein_type)

            meal = {
                "name": dish_name,
                "description": description,
                "ingredients": ingredients,
                "preparation": preparation,
                "nutrition": nutrition,
                "preparation_time": "25 phút",
                "health_benefits": health_benefits,
                "dish_type": "combination",
                "source": "realistic_combination"
            }

            return meal

        except Exception as e:
            print(f"❌ Error creating realistic combination meal: {e}")
            # Fallback to simple meal
            return self._create_simple_fallback_meal(dish_name, meal_type, 400)

    def _parse_combination_dish_name(self, dish_name: str) -> Tuple[str, str]:
        """
        Phân tích tên món ăn kết hợp để xác định base food và protein

        Args:
            dish_name: Tên món ăn (ví dụ: "Cơm Thịt Nướng")

        Returns:
            Tuple[str, str]: (base_food, protein_type)
        """
        dish_lower = dish_name.lower()

        # Xác định base food
        if dish_lower.startswith("cơm"):
            base_food = "cơm"
        elif dish_lower.startswith("bún"):
            base_food = "bún"
        elif dish_lower.startswith("phở"):
            base_food = "phở"
        elif dish_lower.startswith("mì"):
            base_food = "mì"
        elif dish_lower.startswith("bánh mì"):
            base_food = "bánh mì"
        elif dish_lower.startswith("xôi"):
            base_food = "xôi"
        elif dish_lower.startswith("cháo"):
            base_food = "cháo"
        elif dish_lower.startswith("rau"):
            base_food = "rau"
            # Đối với món rau, protein_type là loại rau
            if "muống" in dish_lower:
                return "rau", "muống"
            elif "cải" in dish_lower:
                return "rau", "cải"
            else:
                return "rau", "xanh"
        else:
            base_food = "cơm"  # Default

        # Xác định protein type
        if "thịt" in dish_lower:
            protein_type = "thịt"
        elif "gà" in dish_lower:
            protein_type = "gà"
        elif "cá" in dish_lower:
            protein_type = "cá"
        elif "tôm" in dish_lower:
            protein_type = "tôm"
        elif "trứng" in dish_lower:
            protein_type = "trứng"
        elif "bò" in dish_lower:
            protein_type = "thịt bò"
        elif "heo" in dish_lower:
            protein_type = "thịt heo"
        elif "chả" in dish_lower:
            protein_type = "chả cá"
        else:
            protein_type = "thịt"  # Default

        return base_food, protein_type

    def _create_combination_ingredients(self, base_food: str, protein_type: str, additional_components: List[str] = None) -> List[Dict]:
        """
        Tạo danh sách nguyên liệu cho món ăn kết hợp

        Args:
            base_food: Thực phẩm cơ bản
            protein_type: Loại protein
            additional_components: Thành phần bổ sung

        Returns:
            List[Dict]: Danh sách nguyên liệu
        """
        ingredients = []

        # Thêm thực phẩm cơ bản
        base_amounts = {
            "cơm": "150g",
            "bún": "100g",
            "phở": "100g",
            "mì": "100g",
            "bánh mì": "1 ổ",
            "xôi": "120g",
            "cháo": "1 tô",
            "hủ tiếu": "100g",
            "rau": "100g"
        }

        ingredients.append({
            "name": base_food.title(),
            "amount": base_amounts.get(base_food.lower(), "100g")
        })

        # Thêm protein
        protein_amounts = {
            "thịt": "100g",
            "thịt heo": "100g",
            "thịt bò": "100g",
            "gà": "120g",
            "cá": "100g",
            "tôm": "80g",
            "trứng": "2 quả",
            "đậu hũ": "100g",
            "chả cá": "80g",
            "nem": "3 viên",
            "xíu mại": "4 viên",
            "muống": "100g",
            "cải": "100g",
            "xanh": "100g"
        }

        ingredients.append({
            "name": protein_type.title(),
            "amount": protein_amounts.get(protein_type.lower(), "100g")
        })

        # Thêm gia vị cơ bản
        basic_seasonings = [
            {"name": "Nước mắm", "amount": "1 tbsp"},
            {"name": "Dầu ăn", "amount": "1 tbsp"}
        ]
        ingredients.extend(basic_seasonings)

        return ingredients

    def _create_combination_preparation(self, base_food: str, protein_type: str) -> List[str]:
        """
        Tạo các bước chế biến cho món ăn kết hợp

        Args:
            base_food: Thực phẩm cơ bản
            protein_type: Loại protein

        Returns:
            List[str]: Các bước chế biến
        """
        preparation_steps = []

        # Bước 1: Chuẩn bị nguyên liệu
        preparation_steps.append("Chuẩn bị và làm sạch tất cả nguyên liệu")

        # Bước 2: Chế biến protein
        protein_cooking = {
            "thịt": "Thái thịt thành miếng vừa ăn, ướp gia vị 15 phút rồi nướng/chiên",
            "thịt heo": "Thái thịt heo thành lát mỏng, ướp gia vị rồi nướng",
            "thịt bò": "Thái thịt bò thành miếng, ướp gia vị rồi xào nhanh",
            "gà": "Thái thịt gà thành miếng, ướp gia vị rồi chiên/nướng",
            "cá": "Làm sạch cá, ướp gia vị rồi chiên/nướng",
            "tôm": "Bóc vỏ tôm, ướp gia vị rồi xào",
            "trứng": "Đập trứng, đánh đều rồi chiên thành trứng ốp la hoặc trứng chiên",
            "đậu hũ": "Cắt đậu hũ thành miếng, chiên vàng",
            "chả cá": "Cắt chả cá thành lát, chiên qua",
            "muống": "Nhặt rau muống, rửa sạch rồi xào với tỏi",
            "cải": "Rửa sạch cải, cắt khúc rồi xào",
            "xanh": "Rửa sạch rau, cắt khúc rồi xào"
        }

        preparation_steps.append(protein_cooking.get(protein_type.lower(), f"Chế biến {protein_type} theo cách truyền thống"))

        # Bước 3: Chuẩn bị thực phẩm cơ bản
        base_preparation = {
            "cơm": "Nấu cơm chín tơi, để nguội",
            "bún": "Luộc bún trong nước sôi 2-3 phút, vớt ra để ráo",
            "phở": "Luộc bánh phở trong nước sôi, vớt ra bát",
            "mì": "Luộc mì trong nước sôi cho đến khi mềm",
            "bánh mì": "Nướng bánh mì cho giòn",
            "xôi": "Nấu xôi chín mềm",
            "cháo": "Nấu cháo sánh mịn",
            "hủ tiếu": "Luộc hủ tiếu trong nước sôi",
            "rau": "Chuẩn bị rau sạch"
        }

        preparation_steps.append(base_preparation.get(base_food.lower(), f"Chuẩn bị {base_food}"))

        # Bước 4: Trình bày
        if base_food.lower() in ["phở", "bún", "hủ tiếu"]:
            preparation_steps.append(f"Cho {base_food} vào tô, xếp {protein_type} lên trên")
            preparation_steps.append("Rắc hành lá, ngò gai và ăn kèm rau sống")
        else:
            preparation_steps.append(f"Xếp {protein_type} lên {base_food}")
            preparation_steps.append("Trang trí với rau thơm và ăn kèm nước chấm")

        return preparation_steps

    def _traditional_fallback_meal_suggestions(self, meal_type: str) -> List[Dict]:
        """
        Traditional fallback khi realistic combination thất bại
        """
        try:
            print(f"🔧 Using traditional fallback for {meal_type}...")
            import random

            fallback_meals = self._get_fallback_meals(meal_type)

            if not fallback_meals:
                return []

            # Random selection để tránh lặp lại
            random.shuffle(fallback_meals)

            # Trả về 1-2 món ngẫu nhiên thay vì luôn cùng món
            num_meals = min(2, len(fallback_meals))
            selected_meals = fallback_meals[:num_meals]

            print(f"🔧 Selected {len(selected_meals)} traditional fallback meals for {meal_type}")
            for meal in selected_meals:
                print(f"   - {meal.get('name', 'Unknown')}")

            return selected_meals

        except Exception as e:
            print(f"❌ Traditional fallback failed: {e}")
            return []

    def _create_simple_fallback_meal(self, dish_name: str, meal_type: str, calories_target: int) -> Dict:
        """
        Tạo meal object đơn giản khi các phương thức khác thất bại

        Args:
            dish_name: Tên món ăn
            meal_type: Loại bữa ăn
            calories_target: Mục tiêu calories

        Returns:
            Dict: Meal object đơn giản
        """
        return {
            "name": dish_name,
            "description": f"Món {dish_name} đơn giản và ngon miệng",
            "ingredients": [
                {"name": "Nguyên liệu chính", "amount": "100g"},
                {"name": "Gia vị", "amount": "vừa đủ"},
                {"name": "Rau thơm", "amount": "20g"}
            ],
            "preparation": [
                f"Chuẩn bị nguyên liệu cho {dish_name}",
                "Chế biến theo phương pháp truyền thống",
                "Nêm nướng vừa ăn",
                "Trình bày đẹp mắt"
            ],
            "nutrition": {
                "calories": calories_target,
                "protein": calories_target * 0.15 / 4,  # 15% from protein
                "fat": calories_target * 0.25 / 9,      # 25% from fat
                "carbs": calories_target * 0.60 / 4     # 60% from carbs
            },
            "preparation_time": "25 phút",
            "health_benefits": f"Món {dish_name} cung cấp dinh dưỡng cân bằng cho cơ thể",
            "dish_type": "simple",
            "source": "simple_fallback"
        }

    def clear_cache(self):
        """Xóa cache và recent dishes để buộc tạo mới dữ liệu hoàn toàn"""
        print("🗑️ Clearing Groq service cache")
        self.cache = {}
        print("🗑️ Clearing recent dishes to allow dish repetition")
        self.recent_dishes = []

        # 🔧 FIX: Enhanced diversity enforcement
        import time
        import random

        # Reset random seed với timestamp để đảm bảo diversity
        diversity_seed = int(time.time() * 1000) % 1000000
        random.seed(diversity_seed)

        # Clear any internal tracking
        if hasattr(self, 'used_dishes_tracker'):
            self.used_dishes_tracker = {}

        print(f"🎲 Reset random seed for diversity: {diversity_seed}")
        print("✅ Cache cleared completely for maximum diversity")
    
    def get_cache_info(self):
        """
        Lấy thông tin về cache
        
        Returns:
            Thông tin về cache
        """
        return {
            "num_entries": len(self.cache),
            "keys": list(self.cache.keys())
        }

# Khởi tạo service singleton
groq_service = GroqService() 