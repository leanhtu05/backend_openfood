import os
import json
import time
import threading
import random
from typing import List, Dict, Optional, Tuple
from models import NutritionInfo, Dish, Ingredient

# Import fallback data
from fallback_meals import FALLBACK_MEALS

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
                
                # Khởi tạo client một cách đơn giản (phiên bản Groq 0.4.0)
                try:
                    self.client = groq.Groq(api_key=self.api_key)
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
        use_ai: bool = True  # Thêm tham số để có thể tắt AI
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
        
        # Tạo cache key
        cache_key = f"{meal_type}_{calories_target}_{protein_target}_{fat_target}_{carbs_target}"
        if preferences:
            cache_key += f"_prefs:{'|'.join(preferences)}"
        if allergies:
            cache_key += f"_allergies:{'|'.join(allergies)}"
        if cuisine_style:
            cache_key += f"_cuisine:{cuisine_style}"
        
        # Kiểm tra cache
        if cache_key in self.cache:
            print(f"Using cached meal suggestions for: {cache_key}")
            return self.cache[cache_key]
        
        # Kiểm tra rate limit
        can_request, wait_time = self.rate_limiter.can_make_request()
        if not can_request:
            print(f"Rate limit reached. Using fallback data. Try again in {wait_time} seconds.")
            return self._fallback_meal_suggestions(meal_type)
        
        # Tạo prompt cho LLaMA
        preferences_str = ", ".join(preferences) if preferences else "không có"
        allergies_str = ", ".join(allergies) if allergies else "không có"
        cuisine_style_str = cuisine_style if cuisine_style else "không có yêu cầu cụ thể"

        # Tối ưu prompt cho LLaMA 3
        prompt = f"""Bạn là chuyên gia dinh dưỡng, hãy gợi ý 5 món ăn cho {meal_type} với các tiêu chí sau:
- Tổng lượng calo: {calories_target}kcal
- Lượng protein: {protein_target}g
- Lượng chất béo: {fat_target}g
- Lượng carbohydrate: {carbs_target}g
- Sở thích: {preferences_str}
- Dị ứng (tránh): {allergies_str}
- Phong cách ẩm thực: {cuisine_style_str}

YÊU CẦU QUAN TRỌNG:
1. Tất cả tên món ăn phải HOÀN TOÀN bằng tiếng Việt
2. KHÔNG đưa tên ngày trong tuần (như "Thứ 2", "Thứ 3", "Chủ Nhật", v.v.) vào tên món ăn
3. Đảm bảo tạo ra các món ăn KHÁC NHAU. Hãy sáng tạo và đa dạng
4. Cung cấp hướng dẫn chế biến chi tiết bằng tiếng Việt với các bước cụ thể
5. Thêm thời gian chuẩn bị và nấu nướng cho mỗi món ăn
6. Thêm lợi ích sức khỏe cụ thể cho mỗi món ăn

Hãy trả về kết quả chính xác theo định dạng JSON như sau:
```json
[
  {{
    "name": "Tên món ăn",
    "description": "Mô tả ngắn gọn món ăn",
    "ingredients": [
      {{"name": "Tên nguyên liệu", "amount": "Số lượng", "calories": 100, "protein": 10, "fat": 5, "carbs": 15}},
      ...
    ],
    "preparation": "Các bước chuẩn bị và nấu món ăn",
    "preparation_time": "30 phút",
    "health_benefits": "Lợi ích sức khỏe cụ thể của món ăn này",
    "total_nutrition": {{"calories": 400, "protein": 20, "fat": 15, "carbs": 45}}
  }},
  ...
]
```

Đảm bảo dữ liệu dinh dưỡng của mỗi món phù hợp với mục tiêu và tổng số của tất cả nguyên liệu khớp với tổng dinh dưỡng từng món.
Trả về CHÍNH XÁC định dạng JSON như trên không thêm bất kỳ nội dung nào khác.
"""
        
        try:
            # Gọi API Groq
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
                    
                    # Trích xuất kết quả JSON từ phản hồi
                    result_text = response.choices[0].message.content.strip()
                    
                    # Trích xuất JSON từ kết quả (có thể có các ký tự khác)
                    json_start = result_text.find("[")
                    json_end = result_text.rfind("]") + 1
                    
                    if json_start >= 0 and json_end > json_start:
                        json_str = result_text[json_start:json_end]
                        try:
                            meal_data = json.loads(json_str)
                            
                            # Validate meal data
                            if isinstance(meal_data, list) and len(meal_data) > 0:
                                # Thêm kiểm tra chi tiết hơn để đảm bảo dữ liệu hợp lệ
                                valid_meals = []
                                for meal in meal_data:
                                    if (isinstance(meal, dict) and 
                                        'name' in meal and 
                                        'ingredients' in meal and 
                                        isinstance(meal['ingredients'], list)):
                                        
                                        # Nếu thiếu preparation, thêm một mô tả mặc định
                                        if 'preparation' not in meal or not meal['preparation']:
                                            meal['preparation'] = f"Chế biến {meal['name']} với các nguyên liệu đã liệt kê."
                                        
                                        # Thêm trường preparation_time nếu chưa có
                                        if 'preparation_time' not in meal:
                                            meal['preparation_time'] = "30 phút"
                                            
                                        # Thêm trường health_benefits nếu chưa có
                                        if 'health_benefits' not in meal:
                                            meal['health_benefits'] = f"Cung cấp dinh dưỡng cân bằng với {meal.get('total_nutrition', {}).get('protein', 0)}g protein giúp xây dựng cơ bắp."
                                        
                                        # Đảm bảo ingredients không trống
                                        if not meal['ingredients']:
                                            meal['ingredients'] = [{'name': 'Nguyên liệu chính', 'amount': '100g'}]
                                        
                                        valid_meals.append(meal)
                                
                                if valid_meals:
                                    # Lưu vào cache
                                    self.cache[cache_key] = valid_meals
                                    return valid_meals
                                else:
                                    print("Không có món ăn hợp lệ trong kết quả từ AI. Sử dụng dữ liệu dự phòng.")
                        except json.JSONDecodeError:
                            print(f"Error parsing JSON from LLaMA response. Attempt {attempt + 1}")
                    
                    # Nếu không trích xuất được dữ liệu hợp lệ, thử lại
                    print(f"Invalid response format. Retrying... ({attempt + 1}/{self.max_retries})")
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error calling Groq API: {str(e)} - Attempt {attempt + 1}/{self.max_retries}")
                    if "quota exceeded" in str(e).lower():
                        print("API quota exceeded")
                        self.quota_exceeded = True
                        self.quota_reset_time = time.time() + 3600  # Thử lại sau 1 giờ
                        break
                    time.sleep(2)
            
            # Nếu không nhận được kết quả sau tất cả các lần thử
            print("Failed to get valid response from Groq API after multiple attempts. Using fallback data.")
            return self._fallback_meal_suggestions(meal_type)
                
        except Exception as e:
            print(f"Error generating meal suggestions: {str(e)}")
            return self._fallback_meal_suggestions(meal_type)
    
    def _get_fallback_meals(self, meal_type: str) -> List[Dict]:
        """
        Lấy dữ liệu món ăn dự phòng
        
        Args:
            meal_type: Loại bữa ăn (bữa sáng, bữa trưa, bữa tối)
            
        Returns:
            Danh sách các món ăn dự phòng
        """
        meal_type_lower = meal_type.lower()
        
        if "sáng" in meal_type_lower or "sang" in meal_type_lower:
            return FALLBACK_MEALS.get("breakfast", [])
        elif "trưa" in meal_type_lower or "trua" in meal_type_lower:
            return FALLBACK_MEALS.get("lunch", [])
        elif "tối" in meal_type_lower or "toi" in meal_type_lower:
            return FALLBACK_MEALS.get("dinner", [])
        else:
            # Trả về hỗn hợp các món
            all_meals = []
            for meals_list in FALLBACK_MEALS.values():
                all_meals.extend(meals_list)
            
            # Trộn danh sách để lấy ngẫu nhiên
            random.shuffle(all_meals)
            return all_meals[:5]  # Trả về tối đa 5 món
    
    def _fallback_meal_suggestions(self, meal_type: str) -> List[Dict]:
        """
        Trả về dữ liệu dự phòng cho loại bữa ăn
        
        Args:
            meal_type: Loại bữa ăn
            
        Returns:
            Danh sách các món ăn dự phòng
        """
        return self._get_fallback_meals(meal_type)
    
    def clear_cache(self):
        """Xóa cache để buộc tạo mới dữ liệu"""
        print("Clearing Groq service cache")
        self.cache = {}
    
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