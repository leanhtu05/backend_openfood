"""
Service để tính toán và điều chỉnh giá trị dinh dưỡng dựa trên TDEE của người dùng.
"""
from typing import Dict, Optional, Tuple

class TDEENutritionService:
    """
    Service để tính toán và điều chỉnh giá trị dinh dưỡng dựa trên TDEE của người dùng.
    """
    
    # Giá trị mặc định khi không có TDEE
    DEFAULT_CALORIES = 1500
    DEFAULT_PROTEIN = 90
    DEFAULT_FAT = 50
    DEFAULT_CARBS = 187.5
    
    # Giới hạn tối thiểu và tối đa
    MIN_CALORIES = 1200
    MAX_CALORIES = 3000
    
    @staticmethod
    def calculate_tdee(weight_kg: float, height_cm: float, age: int, gender: str, activity_level: str) -> float:
        """
        Tính toán TDEE dựa trên các thông số của người dùng.
        
        Args:
            weight_kg: Cân nặng (kg)
            height_cm: Chiều cao (cm)
            age: Tuổi
            gender: Giới tính ('male' hoặc 'female')
            activity_level: Mức độ hoạt động ('sedentary', 'light', 'moderate', 'active', 'very_active')
            
        Returns:
            float: TDEE (Total Daily Energy Expenditure) - Tổng năng lượng tiêu thụ hàng ngày
        """
        # Tính BMR (Basal Metabolic Rate) sử dụng công thức Mifflin-St Jeor
        if gender.lower() == 'male':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        # Nhân với hệ số hoạt động (PAL - Physical Activity Level)
        activity_factors = {
            'sedentary': 1.2,      # Ít vận động (văn phòng, ít đi lại)
            'light': 1.375,        # Vận động nhẹ (tập 1-3 lần/tuần)
            'moderate': 1.55,      # Vận động vừa (tập 3-5 lần/tuần)
            'active': 1.725,       # Vận động nhiều (tập 6-7 lần/tuần)
            'very_active': 1.9     # Vận động rất nhiều (tập nặng, vận động viên)
        }
        
        # Lấy hệ số hoạt động hoặc sử dụng hệ số mặc định nếu không tìm thấy
        activity_factor = activity_factors.get(activity_level.lower(), 1.375)
        
        # Tính TDEE
        tdee = bmr * activity_factor
        
        return round(tdee)
    
    @staticmethod
    def adjust_nutrition_targets(tdee: Optional[int] = None, goal: str = 'maintain') -> Tuple[int, int, int, int]:
        """
        Điều chỉnh mục tiêu dinh dưỡng dựa trên TDEE và mục tiêu của người dùng.
        
        Args:
            tdee: TDEE của người dùng (nếu có)
            goal: Mục tiêu ('lose_weight', 'maintain', 'gain_weight')
            
        Returns:
            Tuple[int, int, int, int]: (calories, protein, fat, carbs)
        """
        # Nếu không có TDEE, sử dụng giá trị mặc định
        if not tdee:
            return (
                TDEENutritionService.DEFAULT_CALORIES,
                TDEENutritionService.DEFAULT_PROTEIN,
                TDEENutritionService.DEFAULT_FAT,
                TDEENutritionService.DEFAULT_CARBS
            )
        
        # Điều chỉnh calories dựa trên mục tiêu
        if goal == 'lose_weight':
            # Giảm 20% TDEE để giảm cân
            calories = int(tdee * 0.8)
        elif goal == 'gain_weight':
            # Tăng 15% TDEE để tăng cân
            calories = int(tdee * 1.15)
        else:  # maintain
            # Giữ nguyên TDEE để duy trì cân nặng
            calories = tdee
        
        # Đảm bảo calories nằm trong giới hạn an toàn
        calories = max(TDEENutritionService.MIN_CALORIES, min(calories, TDEENutritionService.MAX_CALORIES))
        
        # Tính toán macros dựa trên calories
        # Protein: 30% calories (4 kcal/g)
        protein = int(calories * 0.3 / 4)
        
        # Fat: 25% calories (9 kcal/g)
        fat = int(calories * 0.25 / 9)
        
        # Carbs: 45% calories (4 kcal/g)
        carbs = int(calories * 0.45 / 4)
        
        return (calories, protein, fat, carbs)
    
    @staticmethod
    def get_nutrition_targets_from_user_profile(user_profile: Dict) -> Tuple[int, int, int, int]:
        """
        Lấy mục tiêu dinh dưỡng từ profile người dùng.
        
        Args:
            user_profile: Thông tin profile người dùng
            
        Returns:
            Tuple[int, int, int, int]: (calories, protein, fat, carbs)
        """
        # Kiểm tra xem có tdeeValues trong profile không
        if "tdeeValues" in user_profile and isinstance(user_profile["tdeeValues"], dict):
            tdee_values = user_profile["tdeeValues"]
            
            calories = tdee_values.get("calories")
            protein = tdee_values.get("protein")
            fat = tdee_values.get("fat")
            carbs = tdee_values.get("carbs")
            
            # Nếu có đầy đủ giá trị, trả về
            if all([calories, protein, fat, carbs]):
                return (calories, protein, fat, carbs)
        
        # Nếu có TDEE nhưng không có tdeeValues đầy đủ
        tdee = user_profile.get("tdee")
        goal = user_profile.get("goal", "maintain")
        
        if tdee:
            return TDEENutritionService.adjust_nutrition_targets(tdee, goal)
        
        # Nếu không có TDEE, tính toán từ thông tin người dùng
        weight = user_profile.get("weightKg") or user_profile.get("weight")
        height = user_profile.get("heightCm") or user_profile.get("height")
        age = user_profile.get("age")
        gender = user_profile.get("gender", "male")
        activity_level = user_profile.get("activityLevel", "moderate")
        
        # Nếu có đủ thông tin, tính TDEE
        if all([weight, height, age]):
            calculated_tdee = TDEENutritionService.calculate_tdee(weight, height, age, gender, activity_level)
            return TDEENutritionService.adjust_nutrition_targets(calculated_tdee, goal)
        
        # Nếu không đủ thông tin, sử dụng giá trị mặc định
        return TDEENutritionService.adjust_nutrition_targets()

    @staticmethod
    def distribute_nutrition_by_meal(calories: int, protein: int, fat: int, carbs: int, meal_type: str) -> Dict[str, int]:
        """
        Phân bổ mục tiêu dinh dưỡng cho từng bữa ăn.
        
        Args:
            calories: Tổng calo mục tiêu trong ngày
            protein: Tổng protein mục tiêu trong ngày (g)
            fat: Tổng chất béo mục tiêu trong ngày (g)
            carbs: Tổng carbs mục tiêu trong ngày (g)
            meal_type: Loại bữa ăn ('breakfast', 'lunch', 'dinner')
            
        Returns:
            Dict[str, int]: Mục tiêu dinh dưỡng cho bữa ăn cụ thể
        """
        # Tỷ lệ phân bổ cho từng bữa ăn
        meal_distribution = {
            "breakfast": 0.25,  # Bữa sáng: 25% tổng calo
            "lunch": 0.40,      # Bữa trưa: 40% tổng calo
            "dinner": 0.35      # Bữa tối: 35% tổng calo
        }
        
        # Lấy tỷ lệ phân bổ cho bữa ăn cụ thể
        ratio = meal_distribution.get(meal_type.lower(), 0.33)  # Mặc định là 33% nếu không xác định được
        
        # Phân bổ mục tiêu dinh dưỡng
        return {
            "calories": int(calories * ratio),
            "protein": int(protein * ratio),
            "fat": int(fat * ratio),
            "carbs": int(carbs * ratio)
        }

# Tạo instance để sử dụng
tdee_nutrition_service = TDEENutritionService() 