import os
import json
import time
import requests
from typing import Dict, List, Optional, Any, Union
from models import NutritionInfo, Ingredient
from config import config

# Cùng APP ID & API KEY từ file gốc
from nutritionix import NUTRITIONIX_APP_ID, NUTRITIONIX_API_KEY

class PersistentCache:
    """Lớp cache có khả năng lưu xuống ổ đĩa"""
    
    def __init__(self, cache_file=config.NUTRITION_CACHE_FILE, ttl_days=config.CACHE_TTL_DAYS):
        self.cache_file = cache_file
        self.ttl_seconds = ttl_days * 86400
        self.cache = self._load_cache()
        
    def _load_cache(self) -> Dict:
        """Đọc cache từ file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading cache: {e}")
            return {}
    
    def _save_cache(self) -> None:
        """Lưu cache xuống file"""
        try:
            # Đảm bảo thư mục tồn tại
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f)
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def get(self, key: str) -> Optional[Dict]:
        """Lấy dữ liệu từ cache nếu còn hạn"""
        if not config.USE_NUTRITIONIX_CACHE:
            return None
            
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl_seconds:
                return data
            else:
                # Cache quá hạn, xóa
                del self.cache[key]
                self._save_cache()
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Lưu dữ liệu vào cache"""
        if not config.USE_NUTRITIONIX_CACHE:
            return
            
        self.cache[key] = (value, time.time())
        # Lưu cache sau mỗi lần update
        self._save_cache()

class NutritionixAPIOptimized:
    """Phiên bản tối ưu của Nutritionix API với batch processing và caching"""
    
    BASE_URL = "https://trackapi.nutritionix.com/v2"
    
    def __init__(self, app_id: str = NUTRITIONIX_APP_ID, api_key: str = NUTRITIONIX_API_KEY):
        # Khởi tạo API
        self.app_id = app_id
        self.api_key = api_key
        self.headers = {
            "x-app-id": self.app_id,
            "x-app-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Khởi tạo cache
        self.cache = PersistentCache()
    
    def get_nutrition_by_query(self, query: str) -> Optional[NutritionInfo]:
        """
        Lấy thông tin dinh dưỡng cho một truy vấn (có cache)
        
        Args:
            query: Truy vấn ngôn ngữ tự nhiên (ví dụ: "100g chicken breast")
            
        Returns:
            NutritionInfo hoặc None nếu có lỗi
        """
        # Kiểm tra cache
        cached_result = self.cache.get(f"single_{query}")
        if cached_result:
            print(f"Using cached nutrition data for '{query}'")
            return NutritionInfo(**cached_result)
        
        endpoint = f"{self.BASE_URL}/natural/nutrients"
        payload = {"query": query}
        
        try:
            print(f"Calling Nutritionix API for '{query}'")
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            if "foods" in data and len(data["foods"]) > 0:
                food = data["foods"][0]
                result = NutritionInfo(
                    calories=food.get("nf_calories", 0),
                    protein=food.get("nf_protein", 0),
                    fat=food.get("nf_total_fat", 0),
                    carbs=food.get("nf_total_carbohydrate", 0)
                )
                
                # Lưu kết quả vào cache
                self.cache.set(f"single_{query}", {
                    "calories": result.calories,
                    "protein": result.protein,
                    "fat": result.fat,
                    "carbs": result.carbs
                })
                
                return result
            return None
        except Exception as e:
            print(f"Error getting nutrition data: {e}")
            return None
    
    def get_nutrition_for_ingredients(self, ingredients: List[Ingredient]) -> NutritionInfo:
        """
        Lấy thông tin dinh dưỡng cho danh sách nguyên liệu với tối ưu batch và cache
        
        Args:
            ingredients: Danh sách Ingredient objects
            
        Returns:
            NutritionInfo với tổng giá trị dinh dưỡng
        """
        # Nếu không có nguyên liệu, trả về dinh dưỡng rỗng
        if not ingredients:
            return NutritionInfo(calories=0, protein=0, fat=0, carbs=0)
            
        if config.USE_NUTRITIONIX_BATCH:
            # Sử dụng phương pháp batch để gộp các nguyên liệu
            return self._get_nutrition_batch(ingredients)
        else:
            # Sử dụng phương pháp cũ, gọi API cho từng nguyên liệu
            return self._get_nutrition_individual(ingredients)
    
    def _get_nutrition_individual(self, ingredients: List[Ingredient]) -> NutritionInfo:
        """Phương pháp cũ: gọi API cho từng nguyên liệu"""
        total = NutritionInfo(calories=0, protein=0, fat=0, carbs=0)
        
        for ingredient in ingredients:
            query = f"{ingredient.amount} {ingredient.name}"
            nutrition = self.get_nutrition_by_query(query)
            
            if nutrition:
                total.calories += nutrition.calories
                total.protein += nutrition.protein
                total.fat += nutrition.fat
                total.carbs += nutrition.carbs
        
        return total
    
    def _get_nutrition_batch(self, ingredients: List[Ingredient]) -> NutritionInfo:
        """Phương pháp batch: gộp tất cả nguyên liệu vào một lần gọi API"""
        # Tạo key cache dựa trên danh sách nguyên liệu
        cache_key = self._get_cache_key(ingredients)
        
        # Kiểm tra cache
        cached_result = self.cache.get(cache_key)
        if cached_result:
            print(f"Using cached batch nutrition data for {len(ingredients)} ingredients")
            return NutritionInfo(**cached_result)
        
        # Tạo batch query cho các nguyên liệu
        batch_query = self._create_batch_query(ingredients)
        
        # Gọi API
        result = self._call_nutritionix_api(batch_query)
        
        # Lưu vào cache
        if result:
            self.cache.set(cache_key, {
                "calories": result.calories,
                "protein": result.protein,
                "fat": result.fat,
                "carbs": result.carbs
            })
        
        return result if result else NutritionInfo(calories=0, protein=0, fat=0, carbs=0)
    
    def _get_cache_key(self, ingredients: List[Ingredient]) -> str:
        """Tạo key cache từ danh sách nguyên liệu"""
        # Sắp xếp để đảm bảo cùng nguyên liệu nhưng khác thứ tự vẫn cho cùng key
        sorted_ingredients = sorted([f"{ing.amount}_{ing.name}" for ing in ingredients])
        return "batch_" + "_".join(sorted_ingredients)
    
    def _create_batch_query(self, ingredients: List[Ingredient]) -> str:
        """Tạo truy vấn batch cho API Nutritionix"""
        return ", ".join([f"{ing.amount} {ing.name}" for ing in ingredients])
    
    def _call_nutritionix_api(self, query: str) -> Optional[NutritionInfo]:
        """Gọi API Nutritionix với query đã gộp"""
        endpoint = f"{self.BASE_URL}/natural/nutrients"
        payload = {"query": query}
        
        try:
            print(f"Calling Nutritionix API in batch mode for {query[:50]}...")
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            # Tính tổng dinh dưỡng
            total = NutritionInfo(calories=0, protein=0, fat=0, carbs=0)
            
            if "foods" in data:
                for food in data["foods"]:
                    total.calories += food.get("nf_calories", 0)
                    total.protein += food.get("nf_protein", 0)
                    total.fat += food.get("nf_total_fat", 0)
                    total.carbs += food.get("nf_total_carbohydrate", 0)
                
                return total
            return None
        except Exception as e:
            print(f"Error getting batch nutrition data: {e}")
            return None
    
    def get_dish_suggestions(self, 
                           target_calories: float, 
                           target_protein: float = None,
                           target_fat: float = None,
                           target_carbs: float = None) -> List[Dict]:
        """
        Lấy gợi ý món ăn dựa trên mục tiêu dinh dưỡng
        Phương thức này giữ nguyên từ phiên bản cũ để đảm bảo tương thích
        
        Args:
            target_calories: Target calories for the dish
            target_protein: Target protein in grams (optional)
            target_fat: Target fat in grams (optional)
            target_carbs: Target carbs in grams (optional)
            
        Returns:
            List of dish suggestions with their names and nutritional information
        """
        # Giữ nguyên mã gốc từ class NutritionixAPI
        suggestions = [
            {
                "name": "Grilled Chicken Salad",
                "nutrition": {
                    "calories": target_calories * 0.9,  # Close to target
                    "protein": target_protein * 1.1 if target_protein else 25,
                    "fat": target_fat * 0.8 if target_fat else 10,
                    "carbs": target_carbs * 0.9 if target_carbs else 15
                }
            },
            {
                "name": "Vegetable Stir Fry with Tofu",
                "nutrition": {
                    "calories": target_calories * 1.1,
                    "protein": target_protein * 0.9 if target_protein else 18,
                    "fat": target_fat * 0.7 if target_fat else 12,
                    "carbs": target_carbs * 1.2 if target_carbs else 25
                }
            }
        ]
        
        return suggestions

# Khởi tạo instance toàn cục để sử dụng xuyên suốt ứng dụng
nutritionix_optimized_api = NutritionixAPIOptimized() 