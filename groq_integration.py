import os
import json
import time
import threading
import random
import re
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

        # Anti-duplication tracking
        self.recent_dishes = []  # Track recent dishes to avoid duplication
        self.max_recent_dishes = 20  # Keep track of last 20 dishes

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
        
        # Tạo cache key với anti-duplication
        import hashlib
        recent_dishes_hash = hashlib.md5(str(sorted(self.recent_dishes[-5:])).encode()).hexdigest()[:8]
        cache_key = f"{meal_type}_{calories_target}_{protein_target}_{fat_target}_{carbs_target}_{recent_dishes_hash}"
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

        # DIVERSE VIETNAMESE DISH DATABASE
        diverse_dishes = self._get_diverse_dish_suggestions(meal_type, preferences, allergies)

        # ANTI-DUPLICATION: Exclude recent dishes
        recent_dishes_str = ", ".join(self.recent_dishes[-10:]) if self.recent_dishes else "không có"

        # ULTRA-STRICT JSON SCHEMA ENFORCEMENT
        required_keys = ["name", "description", "ingredients", "preparation", "nutrition", "preparation_time", "health_benefits"]
        template_json = f'{{"name":"DISH_NAME","description":"DESCRIPTION","ingredients":[{{"name":"INGREDIENT","amount":"AMOUNT"}}],"preparation":["STEP1","STEP2"],"nutrition":{{"calories":{calories_target//2 if calories_target > 400 else calories_target},"protein":{protein_target//2 if protein_target > 30 else protein_target},"fat":{fat_target//2 if fat_target > 20 else fat_target},"carbs":{carbs_target//2 if carbs_target > 50 else carbs_target}}},"preparation_time":"TIME","health_benefits":"BENEFITS"}}'

        prompt = f"""CRITICAL: Output must exactly follow this JSON schema. NO additional or missing keys allowed.

REQUIRED KEYS: {', '.join(required_keys)}

EXACT TEMPLATE:
[{template_json}]

DIVERSE VIETNAMESE DISHES TO CHOOSE FROM:
{diverse_dishes}

ANTI-DUPLICATION: DO NOT use these recent dishes:
{recent_dishes_str}

INSTRUCTIONS:
- Choose 1-2 DIFFERENT dishes from the diverse list above
- AVOID dishes from the recent list to ensure variety
- Replace DISH_NAME with chosen Vietnamese {meal_type} dish name
- Replace DESCRIPTION with brief description in Vietnamese
- Replace INGREDIENT with ingredient name
- Replace AMOUNT with amount like "100g"
- Replace STEP1, STEP2 with preparation steps in Vietnamese
- Replace TIME with time like "30 phút"
- Replace BENEFITS with health benefits in Vietnamese

NUTRITION TARGETS: {calories_target}kcal, {protein_target}g protein, {fat_target}g fat, {carbs_target}g carbs
PREFERENCES: {preferences_str}
ALLERGIES: {allergies_str}

CRITICAL: Return ONLY valid JSON array. NO markdown, NO explanations, NO other text.
If you cannot follow this exact format, return empty array []."""
        
        try:
            # Gọi API Groq
            for attempt in range(self.max_retries):
                try:
                    print(f"Making request to Groq API, attempt {attempt + 1}/{self.max_retries}")
                    
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are a JSON-only response system. Respond ONLY with valid JSON arrays, no other text."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.0,  # ULTRA-STRICT: Maximum determinism for JSON compliance
                        max_tokens=2000,  # Sufficient tokens for meal suggestions
                        top_p=0.1,       # ULTRA-STRICT: Very low top_p for format adherence
                        frequency_penalty=0.0,  # No penalties for strict JSON format
                        presence_penalty=0.0    # No penalties for strict JSON format
                    )
                    
                    # Trích xuất kết quả JSON từ phản hồi
                    result_text = response.choices[0].message.content.strip()
                    print(f"🔍 Raw response from Groq (attempt {attempt + 1}):")
                    print(f"Length: {len(result_text)} characters")
                    print(f"First 200 chars: {result_text[:200]}")
                    print(f"Last 200 chars: {result_text[-200:]}")

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

                            # ANTI-DUPLICATION: Track recent dishes
                            for meal in validated_meals:
                                dish_name = meal.get('name', '')
                                if dish_name and dish_name not in self.recent_dishes:
                                    self.recent_dishes.append(dish_name)
                                    # Keep only last N dishes
                                    if len(self.recent_dishes) > self.max_recent_dishes:
                                        self.recent_dishes.pop(0)

                            print(f"📝 Recent dishes tracked: {self.recent_dishes[-5:]}")  # Show last 5

                            # Cache kết quả
                            self.cache[cache_key] = validated_meals
                            return validated_meals
                        else:
                            print("❌ Validation failed - no valid meals after validation")
                    else:
                        print(f"❌ No valid meal data in response. meal_data type: {type(meal_data)}, length: {len(meal_data) if meal_data else 'None'}")
                    
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
                # Món nước
                "Phở Gà", "Phở Bò", "Bún Bò Huế", "Bún Riêu", "Bún Chả", "Bún Thịt Nướng",
                "Hủ Tiếu", "Mì Quảng", "Cao Lầu", "Bánh Canh", "Cháo Gà", "Cháo Lòng",
                "Cháo Đậu Xanh", "Cháo Sườn", "Súp Cua",

                # Món khô
                "Bánh Mì Thịt", "Bánh Mì Chả Cá", "Bánh Mì Xíu Mại", "Bánh Mì Chay",
                "Xôi Xéo", "Xôi Mặn", "Xôi Gấc", "Xôi Đậu Xanh", "Xôi Lạc",
                "Bánh Cuốn", "Bánh Ướt", "Bánh Bèo", "Bánh Nậm",

                # Món chay
                "Cháo Chay", "Phở Chay", "Bún Chay", "Bánh Mì Chay", "Xôi Chay"
            ],

            "bữa trưa": [
                # Cơm
                "Cơm Tấm Sườn", "Cơm Gà Xối Mỡ", "Cơm Chiên Dương Châu", "Cơm Âm Phủ",
                "Cơm Hến", "Cơm Niêu", "Cơm Dẻo", "Cơm Bò Lúc Lắc", "Cơm Gà Nướng",

                # Bún/Phở
                "Bún Bò Huế", "Bún Riêu Cua", "Bún Chả Hà Nội", "Bún Thịt Nướng",
                "Bún Mắm", "Bún Đậu Mắm Tôm", "Phở Bò", "Phở Gà", "Phở Chay",

                # Mì/Hủ tiếu
                "Mì Quảng", "Hủ Tiếu Nam Vang", "Hủ Tiếu Khô", "Cao Lầu",
                "Mì Xào Giòn", "Mì Xào Mềm", "Hủ Tiếu Xào",

                # Món nướng
                "Nem Nướng", "Chả Cá Lã Vọng", "Cá Nướng", "Thịt Nướng",
                "Tôm Nướng", "Mực Nướng", "Gà Nướng",

                # Món chay
                "Cơm Chay", "Bún Chay", "Phở Chay", "Mì Chay"
            ],

            "bữa tối": [
                # Món nhẹ
                "Chả Cá", "Nem Rán", "Bánh Xèo", "Bánh Khọt", "Bánh Tráng Nướng",
                "Bánh Căn", "Bánh Bột Lọc", "Bánh Ít", "Bánh Bao",

                # Lẩu
                "Lẩu Thái", "Lẩu Cá", "Lẩu Gà", "Lẩu Riêu Cua", "Lẩu Chay",

                # Cháo/Súp
                "Cháo Vịt", "Cháo Cá", "Cháo Trai", "Súp Cua", "Súp Măng Cua",

                # Cơm chiều
                "Cơm Chiên", "Cơm Âm Phủ", "Cơm Hến", "Cơm Niêu",

                # Món nướng
                "Bánh Tráng Nướng", "Chả Cá Nướng", "Tôm Nướng", "Mực Nướng",

                # Món chay
                "Cháo Chay", "Lẩu Chay", "Bánh Xèo Chay", "Nem Chay"
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

        # Filter out recent dishes to avoid duplication
        filtered_dishes = []
        for dish in dishes:
            if dish not in self.recent_dishes:
                filtered_dishes.append(dish)

        # If too few dishes after filtering, use all dishes
        if len(filtered_dishes) < 5:
            filtered_dishes = dishes

        # Shuffle để tăng tính ngẫu nhiên
        import random
        random.shuffle(filtered_dishes)

        # Trả về top 10-15 món để AI chọn
        selected_dishes = filtered_dishes[:15]
        return ", ".join(selected_dishes)

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
        Trích xuất dữ liệu JSON từ phản hồi của AI với strict key validation

        Args:
            response_text: Văn bản phản hồi từ API

        Returns:
            List[Dict]: Dữ liệu món ăn dạng JSON hoặc None nếu không thể phân tích
        """
        # Bước 1: Làm sạch response text
        cleaned_text = self._clean_response_text(response_text)

        try:
            # Phương pháp 1: Thử phân tích toàn bộ phản hồi là JSON với strict validation
            print("Trying to parse entire response as JSON...")
            meal_data = json.loads(cleaned_text)
            if isinstance(meal_data, list) and len(meal_data) > 0:
                # Validate each item has required keys
                valid_items = []
                for item in meal_data:
                    if isinstance(item, dict) and self._validate_required_keys(item):
                        valid_items.append(item)
                    else:
                        print(f"⚠️ Skipping invalid item: {item}")

                if valid_items:
                    print(f"✅ Successfully parsed entire response as JSON array with {len(valid_items)} valid items")
                    return valid_items
                else:
                    print("❌ No valid items found in parsed JSON")

            elif isinstance(meal_data, dict):
                if self._validate_required_keys(meal_data):
                    print(f"✅ Successfully parsed entire response as single valid JSON item")
                    return [meal_data]
                else:
                    print("❌ Single item missing required keys")
        except json.JSONDecodeError as e:
            print(f"Entire response is not valid JSON: {e}")
            print("Trying to extract JSON portion...")

            # Phương pháp 2: Trích xuất JSON sử dụng regex patterns
            import re

            # Pattern 1: Tìm array JSON hoàn chỉnh
            json_patterns = [
                r'\[\s*\{[^}]*\}(?:\s*,\s*\{[^}]*\})*\s*\]',  # Array of objects
                r'\[\s*\{.*?\}\s*(?:,\s*\{.*?\}\s*)*\]',      # More flexible array
                r'\[.*?\]',                                    # Any array
            ]

            for pattern in json_patterns:
                matches = re.search(pattern, cleaned_text, re.DOTALL)
                if matches:
                    json_str = matches.group(0)
                    print(f"Found JSON pattern: {json_str[:100]}...")
                    try:
                        meal_data = json.loads(json_str)
                        if isinstance(meal_data, list) and len(meal_data) > 0:
                            print(f"Successfully parsed extracted JSON with {len(meal_data)} items")
                            return meal_data
                    except json.JSONDecodeError:
                        print(f"Pattern {pattern} failed to parse")
                        continue

            # Phương pháp 3: Tìm mảng JSON giữa dấu ngoặc vuông
            json_start = cleaned_text.find("[")
            json_end = cleaned_text.rfind("]") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = cleaned_text[json_start:json_end]
                print(f"Extracted JSON between brackets: {json_str[:100]}...")
                try:
                    # Thử sửa JSON bị lỗi
                    fixed_json = self._fix_malformed_json(json_str)
                    meal_data = json.loads(fixed_json)
                    if isinstance(meal_data, list) and len(meal_data) > 0:
                        print(f"Successfully parsed fixed JSON array with {len(meal_data)} items")
                        return meal_data
                except json.JSONDecodeError:
                    print("Error parsing JSON from response even after fixing")

        # Phương pháp cuối cùng: Tạo JSON từ text response
        print("🔧 Attempting to create JSON from text response...")
        backup_meals = self._create_json_from_text(cleaned_text)
        if backup_meals:
            print(f"✅ Successfully created {len(backup_meals)} meals from text")
            return backup_meals

        # Không tìm thấy JSON hợp lệ - sẽ fallback ở level cao hơn
        print("❌ All JSON extraction methods failed")

        # Không tìm thấy JSON hợp lệ
        print("❌ Failed to extract valid JSON from response")
        return None

    def _create_intelligent_fallback(self, meal_type: str, calories_target: int, protein_target: int, fat_target: int, carbs_target: int) -> List[Dict]:
        """
        Tạo fallback meals thông minh dựa trên meal_type và nutrition targets
        """
        try:
            print(f"🔧 Creating intelligent fallback for {meal_type}...")

            # Định nghĩa món ăn theo meal_type
            meal_templates = {
                "bữa sáng": [
                    {"name": "Bánh Mì Trứng", "base_calories": 300, "ingredients": ["Bánh mì", "Trứng gà", "Rau thơm"]},
                    {"name": "Cháo Gà", "base_calories": 250, "ingredients": ["Gạo", "Thịt gà", "Hành lá"]},
                    {"name": "Xôi Xéo", "base_calories": 350, "ingredients": ["Gạo nếp", "Đậu xanh", "Nước dừa"]}
                ],
                "bữa trưa": [
                    {"name": "Cơm Tấm Sườn", "base_calories": 500, "ingredients": ["Cơm tấm", "Sườn nướng", "Dưa leo"]},
                    {"name": "Phở Gà", "base_calories": 400, "ingredients": ["Bánh phở", "Thịt gà", "Hành tây"]},
                    {"name": "Bún Bò Huế", "base_calories": 450, "ingredients": ["Bún", "Thịt bò", "Rau thơm"]}
                ],
                "bữa tối": [
                    {"name": "Cơm Gà Xối Mỡ", "base_calories": 400, "ingredients": ["Cơm trắng", "Thịt gà", "Rau muống"]},
                    {"name": "Bún Chả", "base_calories": 350, "ingredients": ["Bún", "Chả nướng", "Rau sống"]},
                    {"name": "Canh Chua Cá", "base_calories": 300, "ingredients": ["Cá", "Cà chua", "Dứa"]}
                ]
            }

            # Chọn template phù hợp
            templates = meal_templates.get(meal_type.lower(), meal_templates["bữa sáng"])
            selected_template = templates[0]  # Chọn món đầu tiên

            # Tính toán nutrition dựa trên targets
            scale_factor = calories_target / selected_template["base_calories"] if selected_template["base_calories"] > 0 else 1.0

            # Tạo ingredients với amounts
            ingredients = []
            for i, ingredient_name in enumerate(selected_template["ingredients"]):
                base_amount = 100 + (i * 20)  # 100g, 120g, 140g...
                scaled_amount = int(base_amount * scale_factor)
                ingredients.append({
                    "name": ingredient_name,
                    "amount": f"{scaled_amount}g"
                })

            # Tạo meal object
            meal = {
                "name": selected_template["name"],
                "description": f"Món {selected_template['name']} truyền thống Việt Nam, thơm ngon và bổ dưỡng",
                "ingredients": ingredients,
                "preparation": [
                    f"Chuẩn bị nguyên liệu cho {selected_template['name']}",
                    "Sơ chế và làm sạch nguyên liệu",
                    "Chế biến theo phương pháp truyền thống",
                    "Nêm nướng vừa ăn và trình bày đẹp mắt"
                ],
                "nutrition": {
                    "calories": calories_target,
                    "protein": protein_target,
                    "fat": fat_target,
                    "carbs": carbs_target
                },
                "preparation_time": "30 phút",
                "health_benefits": f"Món {selected_template['name']} cung cấp đầy đủ dinh dưỡng, giàu protein và vitamin, phù hợp với mục tiêu dinh dưỡng của bạn"
            }

            return [meal]

        except Exception as e:
            print(f"❌ Error creating intelligent fallback: {e}")
            return None

    def _create_json_from_text(self, text: str) -> List[Dict]:
        """
        Tạo JSON từ text response khi parsing thất bại - phương pháp mạnh mẽ hơn
        """
        try:
            print(f"🔧 Creating JSON from text response...")

            # Phương pháp 1: Tìm tên món ăn từ quotes
            dish_names = re.findall(r'"([^"]*(?:Bánh|Cơm|Phở|Bún|Cháo|Chả|Gỏi|Canh|Xôi|Nem|Gà|Heo|Bò)[^"]*)"', text, re.IGNORECASE)

            # Phương pháp 2: Tìm từ pattern Vietnamese dish names
            if not dish_names:
                dish_names = re.findall(r'([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ][a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ\s]+(?:Bánh|Cơm|Phở|Bún|Cháo|Chả|Gỏi|Canh|Xôi|Nem|Gà|Heo|Bò)[a-zàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ\s]*)', text)

            # Phương pháp 3: Fallback với common Vietnamese dishes
            if not dish_names:
                common_dishes = ["Bánh Mì Chay", "Cơm Tấm", "Phở Gà", "Bún Bò", "Cháo Gà", "Xôi Xéo"]
                dish_names = [common_dishes[0]]  # Chọn món đầu tiên
                print(f"⚠️ Using fallback dish name: {dish_names[0]}")

            print(f"🍽️ Found dish names: {dish_names}")

            # Tìm thông tin dinh dưỡng từ text nếu có
            calories_match = re.search(r'"?calories"?\s*:\s*(\d+)', text)
            protein_match = re.search(r'"?protein"?\s*:\s*(\d+)', text)
            fat_match = re.search(r'"?fat"?\s*:\s*(\d+)', text)
            carbs_match = re.search(r'"?carbs"?\s*:\s*(\d+)', text)

            # Tìm ingredients từ text
            ingredients_text = re.search(r'"?ingredients"?\s*:\s*\[(.*?)\]', text, re.DOTALL)
            ingredients = []
            if ingredients_text:
                ingredient_matches = re.findall(r'"?name"?\s*:\s*"([^"]+)".*?"?amount"?\s*:\s*"([^"]+)"', ingredients_text.group(1))
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
                calories = int(calories_match.group(1)) if calories_match else (300 + i * 50)
                protein = int(protein_match.group(1)) if protein_match else (20 + i * 5)
                fat = int(fat_match.group(1)) if fat_match else (12 + i * 3)
                carbs = int(carbs_match.group(1)) if carbs_match else (35 + i * 10)

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
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)

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

    def _fix_malformed_json(self, json_str: str) -> str:
        """
        Ultra-robust JSON fixing với nhiều pattern matching
        """
        print(f"🔧 Attempting ultra-robust JSON fixing...")
        original_json = json_str

        # Bước 1: Sửa pattern phổ biến nhất - missing "name" key
        # Pattern: { "Dish Name", "description": -> { "name": "Dish Name", "description":
        json_str = re.sub(r'\{\s*"([^"]+)",\s*"([^"]+)":', r'{"name": "\1", "description": "\2",', json_str)

        # Bước 2: Sửa pattern chỉ có tên món
        # Pattern: { "Dish Name", -> { "name": "Dish Name",
        json_str = re.sub(r'\{\s*"([^"]+)",\s*([^"])', r'{"name": "\1", \2', json_str)

        # Bước 3: Sửa missing "description" key
        # Pattern: "name": "...", "text", -> "name": "...", "description": "text",
        json_str = re.sub(r'"name":\s*"([^"]+)",\s*"([^"]+)",', r'"name": "\1", "description": "\2",', json_str)

        # Bước 4: Sửa malformed arrays - loại bỏ quotes xung quanh arrays
        json_str = re.sub(r'"\s*\[\s*', r'[', json_str)
        json_str = re.sub(r'\s*\]\s*"', r']', json_str)

        # Bước 5: Sửa missing field names cho arrays
        # Pattern: , [ -> , "ingredients": [
        json_str = re.sub(r',\s*\[\s*\{', r', "ingredients": [{', json_str)
        json_str = re.sub(r',\s*\[\s*"', r', "preparation": ["', json_str)

        # Bước 6: Sửa missing quotes cho object keys
        json_str = re.sub(r'(\w+):', r'"\1":', json_str)

        # Bước 7: Sửa trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)

        # Bước 8: Sửa single quotes thành double quotes
        json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
        json_str = re.sub(r":\s*'([^']*)'", r': "\1"', json_str)

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
            json_str = re.sub(r'\{', r'{"name": "Vietnamese Dish",', json_str, count=1)

        if '"description"' not in json_str:
            print("⚠️ Missing description field, attempting to add...")
            json_str = re.sub(r'"name":\s*"([^"]*)",', r'"name": "\1", "description": "Món ăn Việt Nam truyền thống",', json_str)

        if '"ingredients"' not in json_str:
            print("⚠️ Missing ingredients field, attempting to add...")
            json_str = re.sub(r'"description":\s*"[^"]*",', r'\g<0> "ingredients": [{"name": "Nguyên liệu", "amount": "100g"}],', json_str)

        # Bước 12: Sửa malformed nutrition objects
        if '"nutrition"' in json_str:
            # Ensure nutrition has proper structure
            nutrition_pattern = r'"nutrition":\s*\{[^}]*\}'
            if not re.search(nutrition_pattern, json_str):
                print("⚠️ Fixing malformed nutrition object...")
                json_str = re.sub(r'"nutrition":\s*[^,}]+', r'"nutrition": {"calories": 300, "protein": 20, "fat": 10, "carbs": 40}', json_str)

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
            is_valid = True

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

            # Nutrition - must be object with numeric values
            if 'nutrition' not in meal or not isinstance(meal['nutrition'], dict):
                meal['nutrition'] = {'calories': 400, 'protein': 20, 'fat': 15, 'carbs': 45}
                print(f"🔧 Added default nutrition for {meal_name}")
            else:
                # Ensure all nutrition values are numbers
                nutrition = meal['nutrition']
                for key in ['calories', 'protein', 'fat', 'carbs']:
                    if key not in nutrition:
                        nutrition[key] = {'calories': 400, 'protein': 20, 'fat': 15, 'carbs': 45}[key]
                    else:
                        try:
                            nutrition[key] = float(nutrition[key])
                        except (ValueError, TypeError):
                            nutrition[key] = {'calories': 400, 'protein': 20, 'fat': 15, 'carbs': 45}[key]
                            print(f"🔧 Fixed invalid {key} value for {meal_name}")

            # Preparation time
            if 'preparation_time' not in meal or not isinstance(meal['preparation_time'], str):
                meal['preparation_time'] = "30 phút"
                print(f"🔧 Added default preparation_time for {meal_name}")

            # Health benefits
            if 'health_benefits' not in meal or not isinstance(meal['health_benefits'], str):
                meal['health_benefits'] = f"Món {meal_name} cung cấp dinh dưỡng cân bằng và tốt cho sức khỏe"
                print(f"🔧 Added default health_benefits for {meal_name}")

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