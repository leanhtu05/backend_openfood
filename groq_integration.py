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

        # Prompt được cải tiến để "ép" AI tuân thủ quy tắc JSON cho meal suggestions
        prompt = f"""Bạn là một chuyên gia dinh dưỡng. Dựa trên các thông tin sau: {meal_type} với mục tiêu dinh dưỡng {calories_target}kcal, {protein_target}g protein, {fat_target}g chất béo, {carbs_target}g carbs, sở thích: {preferences_str}, dị ứng: {allergies_str}, phong cách ẩm thực: {cuisine_style_str}, hãy tạo ra một danh sách gồm 1-2 món ăn Việt Nam.

YÊU CẦU TUYỆT ĐỐI:

Phản hồi của bạn CHỈ VÀ CHỈ được chứa một chuỗi JSON hợp lệ.

Không được thêm bất kỳ văn bản, lời chào, ghi chú hay định dạng markdown nào khác như ```json ở đầu hoặc cuối.

Chuỗi JSON phải là một mảng (array) các đối tượng (object).

Mỗi đối tượng món ăn BẮT BUỘC phải có đầy đủ các key sau với đúng kiểu dữ liệu: name (string), description (string), ingredients (array of objects), preparation (array of strings), nutrition (object), preparation_time (string), health_benefits (string).

Bên trong ingredients, mỗi đối tượng phải có name (string) và amount (string).

Bên trong nutrition, mỗi đối tượng phải có calories (number), protein (number), fat (number), và carbs (number).

Đây là một ví dụ về một đối tượng món ăn hợp lệ để bạn tuân theo:

{{
  "name": "Cơm Tấm Sườn Nướng",
  "description": "Món cơm tấm truyền thống với sườn nướng thơm ngon, chả trứng và nước mắm chua ngọt.",
  "ingredients": [
    {{"name": "Cơm tấm", "amount": "150g"}},
    {{"name": "Sườn heo", "amount": "100g"}},
    {{"name": "Trứng gà", "amount": "1 quả"}},
    {{"name": "Nước mắm", "amount": "2 thìa canh"}}
  ],
  "preparation": [
    "Ướp sườn với gia vị trong 30 phút.",
    "Nướng sườn trên than hoa đến khi chín vàng.",
    "Chiên trứng thành chả mỏng.",
    "Bày cơm tấm ra đĩa, xếp sườn và chả trứng lên trên."
  ],
  "nutrition": {{
    "calories": {calories_target},
    "protein": {protein_target},
    "fat": {fat_target},
    "carbs": {carbs_target}
  }},
  "preparation_time": "45 phút",
  "health_benefits": "Cung cấp protein chất lượng cao từ thịt heo và trứng, carbs từ cơm tấm giúp bổ sung năng lượng, phù hợp cho mục tiêu dinh dưỡng của người dùng."
}}

QUY TẮC BỔ SUNG:
1. Tất cả tên món ăn và mô tả phải bằng tiếng Việt
2. Nguyên liệu phải có tên tiếng Việt
3. Hướng dẫn chuẩn bị phải bằng tiếng Việt với các bước chi tiết
4. Tạo các món ăn KHÁC NHAU và sáng tạo
5. KHÔNG bao gồm tên ngày trong tên món ăn
6. Xem xét mục tiêu cụ thể của người dùng:
   - Giảm cân: Tập trung vào món ăn no bụng, nhiều chất xơ, protein cao, ít calo
   - Tăng cân: Tập trung vào món ăn giàu protein, dinh dưỡng dày đặc
   - Sức khỏe tổng quát: Tập trung vào món ăn cân bằng, đa dạng dinh dưỡng
7. Luôn bao gồm thời gian chuẩn bị cho mỗi món
8. Luôn bao gồm lợi ích sức khỏe của mỗi món

Bây giờ, hãy tạo danh sách món ăn của bạn."""
        
        try:
            # Gọi API Groq
            for attempt in range(self.max_retries):
                try:
                    print(f"Making request to Groq API, attempt {attempt + 1}/{self.max_retries}")
                    
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=0.7,
                        max_tokens=4000,  # Tăng max_tokens vì kế hoạch 7 ngày sẽ dài hơn
                        top_p=0.95
                    )
                    
                    # Trích xuất kết quả JSON từ phản hồi
                    result_text = response.choices[0].message.content.strip()
                    print(f"Raw content from Groq:\n{result_text}")

                    # Phân tích JSON từ response
                    meal_data = self._extract_json_from_response(result_text)

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

            # Ensure nutrition exists
            if 'nutrition' not in meal:
                print(f"Adding default nutrition to meal: {meal['name']}")
                meal['nutrition'] = {
                    'calories': 400,
                    'protein': 20,
                    'fat': 15,
                    'carbs': 45
                }

            # Kiểm tra và đặt giá trị mặc định cho trường preparation_time nếu cần
            if 'preparation_time' not in meal or not meal['preparation_time']:
                meal['preparation_time'] = "30-45 phút"
                print(f"Adding default preparation time to meal: {meal['name']}")

            # Kiểm tra và đặt giá trị mặc định cho trường health_benefits nếu cần
            if 'health_benefits' not in meal or not meal['health_benefits']:
                meal['health_benefits'] = f"Món ăn {meal['name']} cung cấp đầy đủ dinh dưỡng cần thiết và năng lượng cân bằng cho cơ thể."
                print(f"Adding default health benefits to meal: {meal['name']}")

            valid_meals.append(meal)

        print(f"Validated {len(valid_meals)} out of {len(meal_data)} meals")
        return valid_meals

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
            return all_meals[:2]  # Trả về tối đa 1-2 món
    
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