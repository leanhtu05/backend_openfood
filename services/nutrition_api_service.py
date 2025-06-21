"""
Professional Nutrition API Service
Tích hợp các API dinh dưỡng chuyên nghiệp cho chatbot
"""

import httpx
import asyncio
import json
import os
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class USDAFoodDataService:
    """
    USDA FoodData Central API Service
    - 400,000+ food items
    - Official US government data
    - Free API with rate limits
    """
    
    def __init__(self):
        self.base_url = "https://api.nal.usda.gov/fdc/v1"
        self.api_key = os.getenv("USDA_API_KEY", "GJRAy2mRHxo2FiejluDsPDBhzPvUL3J8xhihsKh2")  # Your API key
        self.cache = {}
        
    async def search_foods(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Tìm kiếm thực phẩm trong database USDA
        """
        try:
            url = f"{self.base_url}/foods/search"
            params = {
                "query": query,
                "pageSize": limit,
                "api_key": self.api_key,
                "dataType": ["Foundation", "SR Legacy"]  # High quality data
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    foods = []
                    
                    for food in data.get("foods", []):
                        food_info = {
                            "fdc_id": food.get("fdcId"),
                            "description": food.get("description"),
                            "brand": food.get("brandOwner", ""),
                            "ingredients": food.get("ingredients", ""),
                            "nutrients": self._extract_nutrients(food.get("foodNutrients", []))
                        }
                        foods.append(food_info)
                    
                    return foods
                else:
                    logger.error(f"USDA API error: {response.status_code}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching USDA foods: {e}")
            return []
    
    async def get_food_details(self, fdc_id: int) -> Optional[Dict]:
        """
        Lấy thông tin chi tiết của một thực phẩm
        """
        try:
            url = f"{self.base_url}/food/{fdc_id}"
            params = {"api_key": self.api_key}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    food = response.json()
                    return {
                        "fdc_id": food.get("fdcId"),
                        "description": food.get("description"),
                        "nutrients": self._extract_nutrients(food.get("foodNutrients", [])),
                        "portions": self._extract_portions(food.get("foodPortions", [])),
                        "category": food.get("foodCategory", {}).get("description", "")
                    }
                    
        except Exception as e:
            logger.error(f"Error getting USDA food details: {e}")
            return None
    
    def _extract_nutrients(self, nutrients: List[Dict]) -> Dict:
        """
        Trích xuất và chuẩn hóa thông tin dinh dưỡng
        """
        nutrient_map = {
            "Energy": "calories",
            "Protein": "protein", 
            "Total lipid (fat)": "fat",
            "Carbohydrate, by difference": "carbs",
            "Fiber, total dietary": "fiber",
            "Sugars, total including NLEA": "sugar",
            "Sodium, Na": "sodium",
            "Calcium, Ca": "calcium",
            "Iron, Fe": "iron",
            "Vitamin C, total ascorbic acid": "vitamin_c",
            "Vitamin D (D2 + D3)": "vitamin_d"
        }
        
        result = {}
        for nutrient in nutrients:
            name = nutrient.get("nutrient", {}).get("name", "")
            if name in nutrient_map:
                result[nutrient_map[name]] = {
                    "amount": nutrient.get("amount", 0),
                    "unit": nutrient.get("nutrient", {}).get("unitName", "")
                }
        
        return result
    
    def _extract_portions(self, portions: List[Dict]) -> List[Dict]:
        """
        Trích xuất thông tin khẩu phần
        """
        result = []
        for portion in portions:
            result.append({
                "description": portion.get("modifier", ""),
                "gram_weight": portion.get("gramWeight", 0),
                "amount": portion.get("amount", 1)
            })
        return result

class EdamamNutritionService:
    """
    Edamam Nutrition Analysis API
    - Recipe analysis
    - Meal planning
    - Dietary restrictions
    """
    
    def __init__(self):
        self.base_url = "https://api.edamam.com/api/nutrition-details"
        self.app_id = os.getenv("EDAMAM_APP_ID")
        self.app_key = os.getenv("EDAMAM_APP_KEY")
    
    async def analyze_recipe(self, ingredients: List[str], title: str = "") -> Optional[Dict]:
        """
        Phân tích dinh dưỡng của công thức nấu ăn
        """
        try:
            url = f"{self.base_url}"
            params = {
                "app_id": self.app_id,
                "app_key": self.app_key
            }
            
            data = {
                "title": title,
                "ingr": ingredients
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "calories": result.get("calories", 0),
                        "totalWeight": result.get("totalWeight", 0),
                        "nutrients": result.get("totalNutrients", {}),
                        "healthLabels": result.get("healthLabels", []),
                        "dietLabels": result.get("dietLabels", []),
                        "cautions": result.get("cautions", [])
                    }
                    
        except Exception as e:
            logger.error(f"Error analyzing recipe with Edamam: {e}")
            return None

class VietnameseFoodService:
    """
    Vietnamese Food Database Service
    Tích hợp dữ liệu món ăn Việt Nam từ nhiều nguồn
    """
    
    def __init__(self):
        self.vietnamese_foods = self._load_vietnamese_database()
    
    def _load_vietnamese_database(self) -> Dict:
        """
        Load database món ăn Việt Nam từ file JSON
        """
        try:
            with open("data/vietnamese_foods.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Vietnamese foods database not found")
            return {}
    
    async def search_vietnamese_food(self, query: str) -> List[Dict]:
        """
        Tìm kiếm món ăn Việt Nam
        """
        results = []
        query_lower = query.lower()
        
        for food_id, food_data in self.vietnamese_foods.items():
            if query_lower in food_data.get("name", "").lower():
                results.append({
                    "id": food_id,
                    "name": food_data.get("name"),
                    "region": food_data.get("region"),
                    "calories_per_100g": food_data.get("calories_per_100g"),
                    "nutrients": food_data.get("nutrients", {}),
                    "typical_serving": food_data.get("typical_serving", {}),
                    "health_benefits": food_data.get("health_benefits", []),
                    "cooking_methods": food_data.get("cooking_methods", [])
                })
        
        return results[:10]  # Limit results

class NutritionAPIAggregator:
    """
    Tổng hợp tất cả các API dinh dưỡng
    """
    
    def __init__(self):
        self.usda = USDAFoodDataService()
        self.edamam = EdamamNutritionService()
        self.vietnamese = VietnameseFoodService()
        self.cache = {}
    
    async def comprehensive_food_search(self, query: str) -> Dict:
        """
        Tìm kiếm toàn diện từ tất cả nguồn
        """
        results = {
            "query": query,
            "sources": {},
            "recommendations": []
        }
        
        # Tìm kiếm song song từ nhiều nguồn
        tasks = [
            self._search_usda(query),
            self._search_vietnamese(query),
            self._search_edamam_suggestions(query)
        ]
        
        usda_results, vietnamese_results, edamam_suggestions = await asyncio.gather(*tasks)
        
        results["sources"]["usda"] = usda_results
        results["sources"]["vietnamese"] = vietnamese_results
        results["sources"]["edamam"] = edamam_suggestions
        
        # Tạo recommendations thông minh
        results["recommendations"] = self._create_smart_recommendations(
            query, usda_results, vietnamese_results
        )
        
        return results
    
    async def _search_usda(self, query: str) -> List[Dict]:
        """Tìm kiếm USDA với error handling"""
        try:
            return await self.usda.search_foods(query, limit=5)
        except Exception as e:
            logger.error(f"USDA search failed: {e}")
            return []
    
    async def _search_vietnamese(self, query: str) -> List[Dict]:
        """Tìm kiếm món Việt với error handling"""
        try:
            return await self.vietnamese.search_vietnamese_food(query)
        except Exception as e:
            logger.error(f"Vietnamese search failed: {e}")
            return []
    
    async def _search_edamam_suggestions(self, query: str) -> List[Dict]:
        """Tìm kiếm suggestions từ Edamam"""
        # Placeholder - có thể implement recipe search
        return []
    
    def _create_smart_recommendations(self, query: str, usda_results: List, vietnamese_results: List) -> List[Dict]:
        """
        Tạo recommendations thông minh dựa trên kết quả tìm kiếm
        """
        recommendations = []
        
        # Ưu tiên món Việt nếu có
        if vietnamese_results:
            for food in vietnamese_results[:2]:
                recommendations.append({
                    "type": "vietnamese_traditional",
                    "food": food,
                    "reason": "Món ăn truyền thống Việt Nam phù hợp với khẩu vị địa phương"
                })
        
        # Thêm alternatives từ USDA
        if usda_results:
            for food in usda_results[:2]:
                recommendations.append({
                    "type": "international_alternative", 
                    "food": food,
                    "reason": "Thực phẩm tương tự với dữ liệu dinh dưỡng chính xác từ USDA"
                })
        
        return recommendations

# Global instance
nutrition_api = NutritionAPIAggregator()
