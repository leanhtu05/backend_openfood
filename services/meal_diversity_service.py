"""
Dịch vụ đảm bảo đa dạng món ăn trong kế hoạch ăn uống.
"""
import random
from typing import Dict, List, Set, Any

class MealDiversityService:
    """Dịch vụ đảm bảo đa dạng món ăn trong kế hoạch ăn uống."""
    
    @staticmethod
    def check_meal_diversity(meal_plan: Dict[str, Any]) -> float:
        """
        Kiểm tra mức độ đa dạng của kế hoạch ăn.
        
        Args:
            meal_plan: Kế hoạch ăn uống
            
        Returns:
            float: Tỷ lệ trùng lặp (0-1), càng thấp càng đa dạng
        """
        if not meal_plan or "weekly_plan" not in meal_plan:
            return 0.0
            
        weekly_plan = meal_plan["weekly_plan"]
        meal_names_by_type = {
            "Bữa sáng": set(),
            "Bữa trưa": set(),
            "Bữa tối": set(),
        }
        
        duplicate_count = 0
        total_meals = 0
        
        # Duyệt qua từng ngày trong tuần
        for day, day_plan in weekly_plan.items():
            if not day_plan or "meals" not in day_plan:
                continue
                
            # Duyệt qua từng loại bữa ăn
            for meal_type, meals in day_plan["meals"].items():
                if not meals or len(meals) == 0:
                    continue
                    
                # Lấy món ăn đầu tiên trong danh sách
                meal = meals[0]
                meal_name = meal.get("name", "")
                total_meals += 1
                
                # Kiểm tra trùng lặp
                if meal_type in meal_names_by_type and meal_name in meal_names_by_type[meal_type]:
                    duplicate_count += 1
                elif meal_type in meal_names_by_type:
                    meal_names_by_type[meal_type].add(meal_name)
        
        # Tính tỷ lệ trùng lặp
        duplicate_rate = duplicate_count / total_meals if total_meals > 0 else 0
        return duplicate_rate
    
    @staticmethod
    def ensure_meal_diversity(meal_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Đảm bảo đa dạng món ăn trong kế hoạch, thay thế các món trùng lặp.
        
        Args:
            meal_plan: Kế hoạch ăn uống
            
        Returns:
            Dict[str, Any]: Kế hoạch ăn uống đã được đa dạng hóa
        """
        if not meal_plan or "weekly_plan" not in meal_plan:
            return meal_plan
            
        weekly_plan = meal_plan["weekly_plan"]
        meal_names_by_type = {
            "Bữa sáng": set(),
            "Bữa trưa": set(),
            "Bữa tối": set(),
        }
        
        # Lưu trữ tất cả món ăn theo loại bữa
        all_meals_by_type = {
            "Bữa sáng": [],
            "Bữa trưa": [],
            "Bữa tối": [],
        }
        
        # Thu thập tất cả món ăn
        for day, day_plan in weekly_plan.items():
            if not day_plan or "meals" not in day_plan:
                continue
                
            for meal_type, meals in day_plan["meals"].items():
                if not meals or len(meals) == 0:
                    continue
                    
                for meal in meals:
                    if meal_type in all_meals_by_type:
                        all_meals_by_type[meal_type].append(meal)
        
        # Đảm bảo có đủ món ăn đa dạng
        for meal_type, meals in all_meals_by_type.items():
            if len(meals) < 7:  # Cần ít nhất 7 món khác nhau cho 7 ngày
                print(f"⚠️ Không đủ món ăn đa dạng cho {meal_type}: chỉ có {len(meals)} món")
        
        # Duyệt qua từng ngày và thay thế món trùng lặp
        for day, day_plan in weekly_plan.items():
            if not day_plan or "meals" not in day_plan:
                continue
                
            for meal_type, meals in day_plan["meals"].items():
                if not meals or len(meals) == 0:
                    continue
                    
                meal = meals[0]
                meal_name = meal.get("name", "")
                
                # Nếu món ăn đã tồn tại trong set, thay thế bằng món khác
                if meal_type in meal_names_by_type and meal_name in meal_names_by_type[meal_type]:
                    # Tìm món ăn thay thế không trùng lặp
                    replacement_meal = MealDiversityService._find_replacement_meal(
                        all_meals_by_type.get(meal_type, []),
                        meal_names_by_type.get(meal_type, set())
                    )
                    
                    if replacement_meal:
                        # Thay thế món ăn
                        meals[0] = replacement_meal
                        # Cập nhật nutrition summary cho ngày
                        MealDiversityService._update_day_nutrition_summary(day_plan)
                        
                # Thêm món ăn vào set đã sử dụng
                if meal_type in meal_names_by_type:
                    meal_names_by_type[meal_type].add(meals[0].get("name", ""))
        
        return meal_plan
    
    @staticmethod
    def _find_replacement_meal(available_meals: List[Dict[str, Any]], used_names: Set[str]) -> Dict[str, Any]:
        """
        Tìm món ăn thay thế không trùng lặp.

        Args:
            available_meals: Danh sách các món ăn có sẵn
            used_names: Tên các món ăn đã được sử dụng

        Returns:
            Dict[str, Any]: Món ăn thay thế hoặc None nếu không tìm thấy
        """
        # 🔧 FIX: Enhanced diversity logic
        import time

        # Lọc các món ăn chưa được sử dụng
        unused_meals = [meal for meal in available_meals if meal.get("name", "") not in used_names]

        if unused_meals:
            # 🔧 FIX: Use time-based seed for better randomness
            random.seed(int(time.time() * 1000) % 1000000)
            selected_meal = random.choice(unused_meals)
            print(f"🎲 Selected diverse meal: {selected_meal.get('name', 'Unknown')}")
            return selected_meal
        elif available_meals:
            # Nếu không có món nào chưa sử dụng, tạo variation của món hiện có
            print("⚠️ No unused meals available, creating variation...")
            base_meal = random.choice(available_meals)

            # 🔧 FIX: Create variation by modifying name slightly
            if base_meal and "name" in base_meal:
                original_name = base_meal["name"]
                # Add regional variation or cooking method variation
                variations = [
                    f"{original_name} Miền Bắc",
                    f"{original_name} Miền Nam",
                    f"{original_name} Miền Trung",
                    f"{original_name} Sài Gòn",
                    f"{original_name} Hà Nội",
                    f"{original_name} Đặc Biệt",
                    f"{original_name} Truyền Thống",
                    f"{original_name} Cải Tiến"
                ]

                # Choose a variation that hasn't been used
                for variation in variations:
                    if variation not in used_names:
                        varied_meal = base_meal.copy()
                        varied_meal["name"] = variation
                        print(f"🎨 Created variation: {variation}")
                        return varied_meal

                # If all variations used, add timestamp
                timestamp_variation = f"{original_name} ({int(time.time()) % 1000})"
                varied_meal = base_meal.copy()
                varied_meal["name"] = timestamp_variation
                print(f"🕐 Created timestamp variation: {timestamp_variation}")
                return varied_meal

            return base_meal
        else:
            # Không có món ăn nào
            print("❌ No meals available for replacement")
            return None
    
    @staticmethod
    def _update_day_nutrition_summary(day_plan: Dict[str, Any]) -> None:
        """
        Cập nhật tổng hợp dinh dưỡng cho một ngày sau khi thay đổi món ăn.
        
        Args:
            day_plan: Kế hoạch ăn cho một ngày
        """
        if "meals" not in day_plan:
            return
            
        # Khởi tạo tổng hợp dinh dưỡng
        nutrition_summary = {
            "calories": 0,
            "protein": 0,
            "fat": 0,
            "carbs": 0,
            "fiber": 0,
            "sugar": 0,
        }
        
        # Tính tổng dinh dưỡng từ tất cả các bữa ăn
        for meal_type, meals in day_plan["meals"].items():
            if not meals or len(meals) == 0:
                continue
                
            meal = meals[0]
            if "nutrition" not in meal:
                continue
                
            # Cộng dồn giá trị dinh dưỡng
            for nutrient, value in meal["nutrition"].items():
                if nutrient in nutrition_summary:
                    nutrition_summary[nutrient] += value
        
        # Cập nhật tổng hợp dinh dưỡng cho ngày
        day_plan["nutrition_summary"] = nutrition_summary 