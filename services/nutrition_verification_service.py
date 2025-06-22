# -*- coding: utf-8 -*-
"""
Service xác minh độ chính xác của dữ liệu dinh dưỡng
Tích hợp với các API chính thức để đảm bảo tính chính xác
"""

import requests
import json
from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class NutritionVerification:
    """Kết quả xác minh dữ liệu dinh dưỡng"""
    is_verified: bool
    confidence_score: float  # 0.0 - 1.0
    source: str
    verified_data: Optional[Dict] = None
    warnings: List[str] = None

class NutritionVerificationService:
    """
    Service xác minh dữ liệu dinh dưỡng từ nhiều nguồn chính thức
    """
    
    def __init__(self):
        # API keys cho các service dinh dưỡng
        self.usda_api_key = "GJRAy2mRHxo2FiejluDsPDBhzPvUL3J8xhihsKh2"  # USDA API key
        self.edamam_app_id = "your_edamam_app_id"  # Cần đăng ký
        self.edamam_app_key = "your_edamam_app_key"  # Cần đăng ký
        
        # Threshold cho việc xác minh
        self.accuracy_threshold = 0.15  # 15% sai lệch được chấp nhận
        
    def verify_dish_nutrition(self, dish_name: str, nutrition_data: Dict) -> NutritionVerification:
        """
        Xác minh dữ liệu dinh dưỡng của một món ăn
        
        Args:
            dish_name: Tên món ăn
            nutrition_data: Dữ liệu dinh dưỡng cần xác minh
            
        Returns:
            NutritionVerification: Kết quả xác minh
        """
        print(f"🔍 Verifying nutrition data for: {dish_name}")
        
        # Thử xác minh từ USDA database
        usda_result = self._verify_with_usda(dish_name, nutrition_data)
        if usda_result.is_verified:
            return usda_result
        
        # Thử xác minh từ Edamam
        edamam_result = self._verify_with_edamam(dish_name, nutrition_data)
        if edamam_result.is_verified:
            return edamam_result
        
        # Xác minh logic cơ bản (macro balance)
        logic_result = self._verify_macro_logic(nutrition_data)
        
        return logic_result
    
    def _verify_with_usda(self, dish_name: str, nutrition_data: Dict) -> NutritionVerification:
        """Xác minh với USDA FoodData Central"""
        try:
            # Search for similar food in USDA database
            search_url = f"https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
                "query": dish_name,
                "api_key": self.usda_api_key,
                "pageSize": 5
            }
            
            response = requests.get(search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                foods = data.get("foods", [])
                
                if foods:
                    # Lấy food đầu tiên và so sánh
                    best_match = foods[0]
                    usda_nutrition = self._extract_usda_nutrition(best_match)
                    
                    if usda_nutrition:
                        confidence = self._calculate_confidence(nutrition_data, usda_nutrition)
                        
                        return NutritionVerification(
                            is_verified=confidence > 0.7,
                            confidence_score=confidence,
                            source="USDA FoodData Central",
                            verified_data=usda_nutrition,
                            warnings=self._generate_warnings(nutrition_data, usda_nutrition)
                        )
            
        except Exception as e:
            print(f"❌ USDA verification failed: {e}")
        
        return NutritionVerification(
            is_verified=False,
            confidence_score=0.0,
            source="USDA FoodData Central",
            warnings=["Could not verify with USDA database"]
        )
    
    def _verify_with_edamam(self, dish_name: str, nutrition_data: Dict) -> NutritionVerification:
        """Xác minh với Edamam Nutrition API"""
        try:
            # Edamam Recipe Analysis API
            url = "https://api.edamam.com/api/nutrition-details"
            params = {
                "app_id": self.edamam_app_id,
                "app_key": self.edamam_app_key
            }
            
            # Tạo recipe data cho Edamam
            recipe_data = {
                "title": dish_name,
                "ingr": [f"1 serving {dish_name}"]
            }
            
            response = requests.post(url, params=params, json=recipe_data, timeout=10)
            
            if response.status_code == 200:
                edamam_data = response.json()
                edamam_nutrition = self._extract_edamam_nutrition(edamam_data)
                
                if edamam_nutrition:
                    confidence = self._calculate_confidence(nutrition_data, edamam_nutrition)
                    
                    return NutritionVerification(
                        is_verified=confidence > 0.7,
                        confidence_score=confidence,
                        source="Edamam Nutrition API",
                        verified_data=edamam_nutrition,
                        warnings=self._generate_warnings(nutrition_data, edamam_nutrition)
                    )
            
        except Exception as e:
            print(f"❌ Edamam verification failed: {e}")
        
        return NutritionVerification(
            is_verified=False,
            confidence_score=0.0,
            source="Edamam Nutrition API",
            warnings=["Could not verify with Edamam API"]
        )
    
    def _verify_macro_logic(self, nutrition_data: Dict) -> NutritionVerification:
        """Xác minh logic cơ bản của macro nutrients"""
        warnings = []
        
        try:
            calories = float(nutrition_data.get('calories', 0))
            protein = float(nutrition_data.get('protein', 0))
            fat = float(nutrition_data.get('fat', 0))
            carbs = float(nutrition_data.get('carbs', 0))
            
            # Tính calories từ macro
            calculated_calories = (protein * 4) + (fat * 9) + (carbs * 4)
            
            # Kiểm tra sai lệch
            if calories > 0:
                calorie_diff = abs(calculated_calories - calories) / calories
                
                if calorie_diff > 0.2:  # Sai lệch > 20%
                    warnings.append(f"Macro mismatch: Calculated {calculated_calories:.0f} vs stated {calories:.0f} calories")
                
                # Kiểm tra tỷ lệ macro hợp lý
                if calories > 0:
                    protein_percent = (protein * 4) / calories * 100
                    fat_percent = (fat * 9) / calories * 100
                    carbs_percent = (carbs * 4) / calories * 100
                    
                    if protein_percent > 50:
                        warnings.append(f"Very high protein percentage: {protein_percent:.1f}%")
                    if fat_percent > 60:
                        warnings.append(f"Very high fat percentage: {fat_percent:.1f}%")
                    if carbs_percent > 80:
                        warnings.append(f"Very high carbs percentage: {carbs_percent:.1f}%")
            
            # Confidence dựa trên logic check
            confidence = 0.8 if len(warnings) == 0 else max(0.3, 0.8 - len(warnings) * 0.2)
            
            return NutritionVerification(
                is_verified=len(warnings) == 0,
                confidence_score=confidence,
                source="Macro Logic Verification",
                verified_data=nutrition_data,
                warnings=warnings
            )
            
        except Exception as e:
            return NutritionVerification(
                is_verified=False,
                confidence_score=0.0,
                source="Macro Logic Verification",
                warnings=[f"Logic verification failed: {e}"]
            )
    
    def _extract_usda_nutrition(self, usda_food: Dict) -> Optional[Dict]:
        """Trích xuất dữ liệu dinh dưỡng từ USDA response"""
        try:
            nutrients = usda_food.get("foodNutrients", [])
            nutrition = {}
            
            # Map USDA nutrient IDs to our format
            nutrient_map = {
                1008: "calories",  # Energy
                1003: "protein",   # Protein
                1004: "fat",       # Total lipid (fat)
                1005: "carbs",     # Carbohydrate, by difference
                1079: "fiber"      # Fiber, total dietary
            }
            
            for nutrient in nutrients:
                nutrient_id = nutrient.get("nutrientId")
                if nutrient_id in nutrient_map:
                    nutrition[nutrient_map[nutrient_id]] = nutrient.get("value", 0)
            
            return nutrition if nutrition else None
            
        except Exception as e:
            print(f"❌ Error extracting USDA nutrition: {e}")
            return None
    
    def _extract_edamam_nutrition(self, edamam_data: Dict) -> Optional[Dict]:
        """Trích xuất dữ liệu dinh dưỡng từ Edamam response"""
        try:
            total_nutrients = edamam_data.get("totalNutrients", {})
            
            nutrition = {
                "calories": total_nutrients.get("ENERC_KCAL", {}).get("quantity", 0),
                "protein": total_nutrients.get("PROCNT", {}).get("quantity", 0),
                "fat": total_nutrients.get("FAT", {}).get("quantity", 0),
                "carbs": total_nutrients.get("CHOCDF", {}).get("quantity", 0),
                "fiber": total_nutrients.get("FIBTG", {}).get("quantity", 0)
            }
            
            return nutrition
            
        except Exception as e:
            print(f"❌ Error extracting Edamam nutrition: {e}")
            return None
    
    def _calculate_confidence(self, original: Dict, verified: Dict) -> float:
        """Tính confidence score dựa trên độ tương đồng"""
        try:
            total_diff = 0
            count = 0
            
            for key in ["calories", "protein", "fat", "carbs"]:
                if key in original and key in verified:
                    orig_val = float(original[key])
                    ver_val = float(verified[key])
                    
                    if orig_val > 0:
                        diff = abs(orig_val - ver_val) / orig_val
                        total_diff += diff
                        count += 1
            
            if count > 0:
                avg_diff = total_diff / count
                confidence = max(0, 1 - avg_diff)
                return confidence
            
            return 0.0
            
        except Exception:
            return 0.0
    
    def _generate_warnings(self, original: Dict, verified: Dict) -> List[str]:
        """Tạo warnings dựa trên sự khác biệt"""
        warnings = []
        
        try:
            for key in ["calories", "protein", "fat", "carbs"]:
                if key in original and key in verified:
                    orig_val = float(original[key])
                    ver_val = float(verified[key])
                    
                    if orig_val > 0:
                        diff_percent = abs(orig_val - ver_val) / orig_val * 100
                        
                        if diff_percent > 20:
                            warnings.append(f"{key.title()}: {diff_percent:.1f}% difference (Original: {orig_val:.1f}, Verified: {ver_val:.1f})")
            
        except Exception as e:
            warnings.append(f"Error comparing data: {e}")
        
        return warnings

# Global instance
nutrition_verification_service = NutritionVerificationService()
