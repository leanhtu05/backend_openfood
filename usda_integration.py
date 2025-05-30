import os
import json
import requests
from typing import Dict, List, Optional, Union
from datetime import datetime
import time
import re

from config import config

# Từ điển ánh xạ từ tiếng Việt sang tiếng Anh cho các loại thực phẩm phổ biến
VI_TO_EN_FOOD_DICT = {
    # Ngũ cốc
    "gạo": "rice",
    "bánh mì": "bread",
    "mì": "noodle",
    "bún": "rice noodle",
    "phở": "pho noodle",
    "ngô": "corn",
    "bắp": "corn",
    
    # Thịt
    "thịt bò": "beef",
    "thịt gà": "chicken",
    "thịt heo": "pork",
    "thịt lợn": "pork",
    "thịt cừu": "lamb",
    "thịt vịt": "duck",
    "thịt ngan": "muscovy duck",
    
    # Hải sản
    "cá": "fish",
    "tôm": "shrimp",
    "mực": "squid",
    "cua": "crab",
    "sò": "clam",
    "hàu": "oyster",
    
    # Rau củ
    "rau": "vegetable",
    "cà chua": "tomato",
    "cà rốt": "carrot",
    "khoai tây": "potato",
    "khoai lang": "sweet potato",
    "hành tây": "onion",
    "tỏi": "garlic",
    "ớt": "chili",
    "bắp cải": "cabbage",
    "súp lơ": "broccoli",
    "bông cải xanh": "broccoli",
    "rau muống": "water spinach",
    "rau dền": "amaranth",
    "đậu đũa": "long bean",
    "đậu cove": "green bean",
    
    # Trái cây
    "táo": "apple",
    "chuối": "banana",
    "cam": "orange",
    "xoài": "mango",
    "dưa hấu": "watermelon",
    "dứa": "pineapple",
    "nho": "grape",
    "dâu tây": "strawberry",
    "mận": "plum",
    "đào": "peach",
    "lê": "pear",
    "bơ": "avocado",
    
    # Các loại đậu
    "đậu phộng": "peanut",
    "đậu nành": "soybean",
    "đậu xanh": "mung bean",
    "đậu đen": "black bean",
    "đậu đỏ": "red bean",
    
    # Các loại hạt
    "hạt điều": "cashew",
    "hạt dẻ": "chestnut",
    "hạt macca": "macadamia",
    "hạt óc chó": "walnut",
    "hạt hạnh nhân": "almond",
    
    # Các loại dầu
    "dầu ăn": "cooking oil",
    "dầu đậu nành": "soybean oil",
    "dầu olive": "olive oil",
    "dầu mè": "sesame oil",
    "dầu dừa": "coconut oil",
    
    # Các loại sữa và sản phẩm từ sữa
    "sữa": "milk",
    "phô mai": "cheese",
    "bơ sữa": "butter",
    "sữa chua": "yogurt",
    "kem": "cream",
    
    # Gia vị
    "muối": "salt",
    "tiêu": "pepper",
    "đường": "sugar",
    "bột ngọt": "msg",
    "nước mắm": "fish sauce",
    "nước tương": "soy sauce",
    "tương ớt": "chili sauce",
    "tương cà": "tomato sauce",
    "giấm": "vinegar",
    "mật ong": "honey",
    
    # Thức uống
    "nước": "water",
    "cà phê": "coffee",
    "trà": "tea",
    "bia": "beer",
    "rượu": "alcohol",
    "nước ngọt": "soda",
    
    # Thức ăn nhanh
    "pizza": "pizza",
    "hamburger": "hamburger",
    "khoai tây chiên": "french fries",
    "gà rán": "fried chicken",
    
    # Các loại bánh
    "bánh ngọt": "cake",
    "bánh quy": "cookie",
    "bánh bông lan": "sponge cake",
    
    # Các món ăn Việt Nam
    "phở bò": "beef pho",
    "bún chả": "bun cha",
    "bánh xèo": "vietnamese pancake",
    "gỏi cuốn": "spring roll",
    "chả giò": "fried spring roll",
    "cơm tấm": "broken rice"
}

# Thêm các từ đồng nghĩa phổ biến
for key, value in list(VI_TO_EN_FOOD_DICT.items()):
    # Thêm các dạng số nhiều cho tiếng Anh
    if not value.endswith('s') and not value.endswith('ese'):
        VI_TO_EN_FOOD_DICT[key + " các loại"] = value + "s"
    
    # Thêm các cụm từ phổ biến
    VI_TO_EN_FOOD_DICT[key + " tươi"] = "fresh " + value
    VI_TO_EN_FOOD_DICT[key + " hữu cơ"] = "organic " + value
    VI_TO_EN_FOOD_DICT[key + " nướng"] = "grilled " + value
    VI_TO_EN_FOOD_DICT[key + " luộc"] = "boiled " + value
    VI_TO_EN_FOOD_DICT[key + " chiên"] = "fried " + value

class USDAFoodDataAPI:
    """Lớp tương tác với USDA FoodData Central API"""
    
    BASE_URL = "https://api.nal.usda.gov/fdc/v1"
    
    def __init__(self, api_key: str = config.USDA_API_KEY):
        """
        Khởi tạo lớp tương tác với USDA API
        
        Args:
            api_key: USDA API key, lấy từ config nếu không cung cấp
        """
        self.api_key = api_key
        self.available = api_key is not None
        
        # Cache để lưu kết quả tìm kiếm
        self.search_cache = {}
        self.food_cache = {}
        self.last_request_time = 0
        self.request_delay = 0.5  # Giãn cách giữa các request (giây)
        
        # Tải cache từ file nếu có
        if config.USE_USDA_CACHE:
            self._load_cache_from_file()
    
    def _load_cache_from_file(self):
        """Tải cache từ file"""
        try:
            if os.path.exists(config.USDA_CACHE_FILE):
                with open(config.USDA_CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    
                    # Kiểm tra thời gian tạo cache
                    cache_timestamp = cache_data.get('timestamp', 0)
                    cache_age_days = (time.time() - cache_timestamp) / (60 * 60 * 24)
                    
                    # Nếu cache quá cũ, không sử dụng
                    if cache_age_days <= config.USDA_CACHE_TTL_DAYS:
                        self.search_cache = cache_data.get('search_cache', {})
                        self.food_cache = cache_data.get('food_cache', {})
                        print(f"Đã tải {len(self.search_cache)} kết quả tìm kiếm và {len(self.food_cache)} thông tin thực phẩm từ cache")
                    else:
                        print(f"Cache quá cũ ({cache_age_days:.1f} ngày), tạo cache mới")
        except Exception as e:
            print(f"Lỗi khi tải cache USDA: {str(e)}")
    
    def _save_cache_to_file(self):
        """Lưu cache vào file"""
        if not config.USE_USDA_CACHE:
            return
            
        try:
            # Tạo thư mục cache nếu không tồn tại
            os.makedirs(os.path.dirname(config.USDA_CACHE_FILE), exist_ok=True)
            
            # Tạo đối tượng cache
            cache_data = {
                'timestamp': time.time(),
                'search_cache': self.search_cache,
                'food_cache': self.food_cache
            }
            
            # Lưu vào file
            with open(config.USDA_CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
                
            print(f"Đã lưu {len(self.search_cache)} kết quả tìm kiếm và {len(self.food_cache)} thông tin thực phẩm vào cache")
        except Exception as e:
            print(f"Lỗi khi lưu cache USDA: {str(e)}")
    
    def _translate_vi_to_en(self, vietnamese_query: str) -> str:
        """
        Dịch truy vấn tiếng Việt sang tiếng Anh
        
        Args:
            vietnamese_query: Truy vấn tiếng Việt
            
        Returns:
            Truy vấn tiếng Anh tương ứng
        """
        # Chuyển về chữ thường để dễ so khớp
        query_lower = vietnamese_query.lower()
        
        # Thử tìm khớp chính xác
        if query_lower in VI_TO_EN_FOOD_DICT:
            return VI_TO_EN_FOOD_DICT[query_lower]
        
        # Thử tìm khớp một phần
        for vi_term, en_term in VI_TO_EN_FOOD_DICT.items():
            if vi_term in query_lower:
                # Thay thế từ tiếng Việt bằng từ tiếng Anh tương ứng
                return query_lower.replace(vi_term, en_term)
        
        # Nếu không tìm thấy, giữ nguyên truy vấn
        print(f"Không tìm thấy bản dịch cho: {vietnamese_query}")
        return vietnamese_query
    
    def _wait_for_rate_limit(self):
        """Đợi để không vượt quá rate limit của API"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        if elapsed < self.request_delay:
            time.sleep(self.request_delay - elapsed)
        
        self.last_request_time = time.time()
    
    def search_foods(self, query: str, vietnamese: bool = True, max_results: int = 15) -> List[Dict]:
        """
        Tìm kiếm thực phẩm trong USDA FoodData Central
        
        Args:
            query: Từ khóa tìm kiếm
            vietnamese: Có phải truy vấn tiếng Việt không
            max_results: Số kết quả tối đa trả về
            
        Returns:
            Danh sách kết quả tìm kiếm
        """
        if not self.available:
            print("USDA API key không khả dụng")
            return []
        
        # Tạo cache key
        cache_key = f"{query}_{max_results}"
        
        # Kiểm tra cache
        cache_hit = False
        if cache_key in self.search_cache:
            print(f"Trả về kết quả từ cache cho: {query}")
            cache_hit = True
            return self.search_cache[cache_key]
        
        # Dịch truy vấn nếu là tiếng Việt
        search_query = self._translate_vi_to_en(query) if vietnamese else query
        print(f"Tìm kiếm USDA với từ khóa: {search_query} (gốc: {query})")
        
        # Chờ để không vượt quá rate limit
        self._wait_for_rate_limit()
        
        # Gửi request đến USDA API
        url = f"{self.BASE_URL}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": search_query,
            "pageSize": max_results,
            "dataType": ["Survey (FNDDS)", "Foundation", "SR Legacy"]  # Các loại dữ liệu đáng tin cậy
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise exception nếu request thất bại
            
            data = response.json()
            foods = data.get("foods", [])
            
            # Lọc và chuyển đổi kết quả sang định dạng đơn giản hơn
            results = []
            for food in foods:
                food_id = food.get("fdcId")
                description = food.get("description", "")
                
                # Tính toán các giá trị dinh dưỡng trên 100g
                nutrients = {}
                for nutrient in food.get("foodNutrients", []):
                    name = nutrient.get("nutrientName", "").lower()
                    value = nutrient.get("value", 0)
                    unit = nutrient.get("unitName", "")
                    
                    if "protein" in name:
                        nutrients["protein"] = value
                    elif "carbohydrate" in name:
                        nutrients["carbs"] = value
                    elif "fat" in name and "total" in name:
                        nutrients["fat"] = value
                    elif "energy" in name:
                        nutrients["calories"] = value
                
                # Tạo một đối tượng đơn giản
                result = {
                    "id": food_id,
                    "name": description,
                    "nutrition": nutrients,
                    "source": "USDA"
                }
                results.append(result)
            
            # Lưu vào cache
            self.search_cache[cache_key] = results
            
            # Sau khi có kết quả mới, lưu cache
            if not cache_hit and config.USE_USDA_CACHE:
                self._save_cache_to_file()
            
            return results
        
        except Exception as e:
            print(f"Lỗi khi tìm kiếm thực phẩm: {str(e)}")
            return []
    
    def get_food_detail(self, food_id: int) -> Optional[Dict]:
        """
        Lấy thông tin chi tiết về một loại thực phẩm
        
        Args:
            food_id: ID của thực phẩm trong USDA FoodData Central
            
        Returns:
            Thông tin chi tiết về thực phẩm hoặc None nếu không tìm thấy
        """
        if not self.available:
            print("USDA API key không khả dụng")
            return None
        
        # Kiểm tra cache
        cache_hit = False
        if food_id in self.food_cache:
            cache_hit = True
            return self.food_cache[food_id]
        
        # Chờ để không vượt quá rate limit
        self._wait_for_rate_limit()
        
        url = f"{self.BASE_URL}/food/{food_id}"
        params = {"api_key": self.api_key}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            food_data = response.json()
            
            # Trích xuất thông tin quan trọng
            food_detail = {
                "id": food_data.get("fdcId"),
                "name": food_data.get("description", ""),
                "ingredients": food_data.get("ingredients", ""),
                "brand": food_data.get("brandName", ""),
                "nutrition": {}
            }
            
            # Trích xuất các giá trị dinh dưỡng
            for nutrient in food_data.get("foodNutrients", []):
                nutrient_data = nutrient.get("nutrient", {})
                name = nutrient_data.get("name", "").lower()
                value = nutrient.get("amount", 0)
                unit = nutrient_data.get("unitName", "")
                
                if "protein" in name:
                    food_detail["nutrition"]["protein"] = value
                elif "carbohydrate" in name and "total" in name:
                    food_detail["nutrition"]["carbs"] = value
                elif "fat" in name and "total" in name:
                    food_detail["nutrition"]["fat"] = value
                elif "energy" in name:
                    food_detail["nutrition"]["calories"] = value
                elif "fiber" in name:
                    food_detail["nutrition"]["fiber"] = value
                elif "sugar" in name and "total" in name:
                    food_detail["nutrition"]["sugar"] = value
                elif "sodium" in name:
                    food_detail["nutrition"]["sodium"] = value
            
            # Lưu vào cache
            self.food_cache[food_id] = food_detail
            
            # Sau khi có thông tin mới, lưu cache
            if not cache_hit and config.USE_USDA_CACHE:
                self._save_cache_to_file()
            
            return food_detail
        
        except Exception as e:
            print(f"Lỗi khi lấy thông tin chi tiết thực phẩm: {str(e)}")
            return None
    
    def get_nutrition_from_query(self, query: str, vietnamese: bool = True) -> Optional[Dict]:
        """
        Tìm kiếm và lấy thông tin dinh dưỡng cho một loại thực phẩm từ truy vấn
        
        Args:
            query: Truy vấn tìm kiếm
            vietnamese: Có phải truy vấn tiếng Việt không
            
        Returns:
            Thông tin dinh dưỡng hoặc None nếu không tìm thấy
        """
        # Tìm kiếm thực phẩm
        search_results = self.search_foods(query, vietnamese=vietnamese, max_results=1)
        
        if not search_results:
            return None
        
        # Lấy kết quả đầu tiên
        food = search_results[0]
        
        # Nếu đã có thông tin dinh dưỡng, trả về luôn
        if "nutrition" in food and food["nutrition"]:
            return {
                "name": food["name"],
                "calories": food["nutrition"].get("calories", 0),
                "protein": food["nutrition"].get("protein", 0),
                "fat": food["nutrition"].get("fat", 0),
                "carbs": food["nutrition"].get("carbs", 0)
            }
        
        # Nếu chưa có đủ thông tin, lấy thêm chi tiết
        food_id = food["id"]
        food_detail = self.get_food_detail(food_id)
        
        if not food_detail:
            return None
        
        # Trả về thông tin dinh dưỡng
        return {
            "name": food_detail["name"],
            "calories": food_detail["nutrition"].get("calories", 0),
            "protein": food_detail["nutrition"].get("protein", 0),
            "fat": food_detail["nutrition"].get("fat", 0),
            "carbs": food_detail["nutrition"].get("carbs", 0)
        }
    
    def extract_quantity_from_text(self, text: str) -> tuple:
        """
        Trích xuất số lượng từ văn bản
        
        Args:
            text: Văn bản chứa thông tin số lượng (vd: "100g gạo")
            
        Returns:
            Tuple (số lượng, đơn vị, nguyên liệu)
        """
        # Mẫu regex để tìm số lượng
        patterns = [
            # 100g, 100 g
            r'(\d+[.,]?\d*)\s*(g|gram|grams|kg|kilograms|ml|oz|ounce|ounces|cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons)',
            # 100 gram rice
            r'(\d+[.,]?\d*)\s*(g|gram|grams|kg|kilograms|ml|oz|ounce|ounces|cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons)\s+(.+)',
            # half cup
            r'(half|quarter|third|one|two|three|four|five)\s+(g|gram|grams|kg|kilograms|ml|oz|ounce|ounces|cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons)',
            # 1 cup of rice
            r'(\d+[.,]?\d*)\s+(g|gram|grams|kg|kilograms|ml|oz|ounce|ounces|cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons)\s+of\s+(.+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) >= 2:
                    quantity = groups[0]
                    unit = groups[1]
                    
                    # Chuyển đổi chữ sang số
                    if quantity.lower() == 'half':
                        quantity = 0.5
                    elif quantity.lower() == 'quarter':
                        quantity = 0.25
                    elif quantity.lower() == 'third':
                        quantity = 0.33
                    elif quantity.lower() == 'one':
                        quantity = 1
                    elif quantity.lower() == 'two':
                        quantity = 2
                    elif quantity.lower() == 'three':
                        quantity = 3
                    elif quantity.lower() == 'four':
                        quantity = 4
                    elif quantity.lower() == 'five':
                        quantity = 5
                    else:
                        try:
                            quantity = float(quantity.replace(',', '.'))
                        except:
                            quantity = 1
                    
                    # Lấy nguyên liệu nếu có
                    ingredient = groups[2] if len(groups) > 2 and groups[2] else text
                    
                    return quantity, unit, ingredient
        
        # Nếu không tìm thấy mẫu, giả định 100g
        return 100, 'g', text

    def get_nutrition_info(self, food_query: str, amount_text: str = None, vietnamese: bool = True) -> Dict:
        """
        Lấy thông tin dinh dưỡng cho một loại thực phẩm với số lượng cụ thể
        
        Args:
            food_query: Tên thực phẩm cần tìm
            amount_text: Văn bản chứa thông tin số lượng
            vietnamese: Có phải truy vấn tiếng Việt không
            
        Returns:
            Thông tin dinh dưỡng với số lượng đã điều chỉnh
        """
        # Nếu không có amount_text, sử dụng food_query để trích xuất
        if not amount_text:
            quantity, unit, ingredient = self.extract_quantity_from_text(food_query)
            # Sử dụng ingredient làm query mới nếu có thể tách
            if ingredient and ingredient != food_query:
                food_query = ingredient
        else:
            # Nếu có amount_text riêng, trích xuất từ đó
            quantity, unit, _ = self.extract_quantity_from_text(amount_text)
        
        # Lấy thông tin dinh dưỡng cơ bản (cho 100g)
        base_nutrition = self.get_nutrition_from_query(food_query, vietnamese)
        
        if not base_nutrition:
            # Nếu không tìm thấy, trả về một đối tượng trống với tên
            return {
                "name": food_query,
                "calories": 0,
                "protein": 0,
                "fat": 0,
                "carbs": 0,
                "amount": f"{quantity} {unit}"
            }
        
        # Tính toán lại giá trị dinh dưỡng dựa trên số lượng
        multiplier = quantity / 100  # USDA cung cấp dữ liệu cho 100g
        
        # Điều chỉnh theo đơn vị
        if unit.lower() in ['kg', 'kilograms']:
            multiplier *= 1000
        elif unit.lower() in ['oz', 'ounce', 'ounces']:
            multiplier *= 28.35  # 1 oz = 28.35g
        elif unit.lower() in ['cup', 'cups']:
            # Giả định 1 cup = khoảng 240g (khác nhau tùy loại thực phẩm)
            multiplier *= 240
        elif unit.lower() in ['tbsp', 'tablespoon', 'tablespoons']:
            # Giả định 1 tbsp = khoảng 15g
            multiplier *= 15
        elif unit.lower() in ['tsp', 'teaspoon', 'teaspoons']:
            # Giả định 1 tsp = khoảng 5g
            multiplier *= 5
        
        # Tính toán lại giá trị dinh dưỡng
        return {
            "name": base_nutrition["name"],
            "calories": round(base_nutrition["calories"] * multiplier, 1),
            "protein": round(base_nutrition["protein"] * multiplier, 1),
            "fat": round(base_nutrition["fat"] * multiplier, 1),
            "carbs": round(base_nutrition["carbs"] * multiplier, 1),
            "amount": f"{quantity} {unit}"
        }

    def clear_cache(self):
        """Xóa cache"""
        self.search_cache = {}
        self.food_cache = {}
        
        # Xóa file cache nếu tồn tại
        if os.path.exists(config.USDA_CACHE_FILE):
            try:
                os.remove(config.USDA_CACHE_FILE)
                print(f"Đã xóa file cache USDA")
            except Exception as e:
                print(f"Lỗi khi xóa file cache USDA: {str(e)}")

# Khởi tạo API với API key từ cấu hình
usda_api = USDAFoodDataAPI() 