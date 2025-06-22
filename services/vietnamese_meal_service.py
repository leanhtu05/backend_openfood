# -*- coding: utf-8 -*-
"""
Service quản lý món ăn Việt Nam với dữ liệu dinh dưỡng chính xác
Tích hợp với Vietnamese nutrition database để đảm bảo tính thực tế
"""

import random
from typing import List, Dict, Optional
from vietnamese_nutrition_database import VIETNAMESE_DISHES_NUTRITION

class VietnameseMealService:
    """
    Service quản lý món ăn Việt Nam với dữ liệu dinh dưỡng thực tế
    """
    
    def __init__(self):
        # Món ăn Việt Nam theo bữa với dữ liệu dinh dưỡng thực tế
        self.vietnamese_meals = {
            "breakfast": [
                {
                    "name": "Phở bò",
                    "region": "Bắc",
                    "ingredients": [
                        {"name": "bánh phở", "amount": "200g"},
                        {"name": "thịt bò", "amount": "120g"},
                        {"name": "hành lá", "amount": "20g"},
                        {"name": "giá đỗ", "amount": "50g"},
                        {"name": "nước dùng bò", "amount": "500ml"}
                    ],
                    "preparation": [
                        "Nấu nước dùng bò với xương, thịt và gia vị thơm",
                        "Trụng bánh phở trong nước sôi",
                        "Thái thịt bò mỏng, cho vào tô",
                        "Chan nước dùng nóng, rắc hành lá và giá đỗ"
                    ],
                    "nutrition": VIETNAMESE_DISHES_NUTRITION.get("phở bò", {
                        "calories": 420, "protein": 25.3, "fat": 12.2, "carbs": 55
                    }),
                    "cooking_time": "30 phút",
                    "difficulty": "Trung bình"
                },
                {
                    "name": "Bánh mì thịt nướng",
                    "region": "Nam",
                    "ingredients": [
                        {"name": "bánh mì", "amount": "1 ổ"},
                        {"name": "thịt heo nướng", "amount": "80g"},
                        {"name": "pate", "amount": "20g"},
                        {"name": "rau thơm", "amount": "30g"},
                        {"name": "dưa chua", "amount": "50g"}
                    ],
                    "preparation": [
                        "Nướng thịt heo ướp gia vị",
                        "Rạch bánh mì, phết pate",
                        "Nhồi thịt nướng, rau thơm và dưa chua",
                        "Ăn nóng khi vừa làm xong"
                    ],
                    "nutrition": VIETNAMESE_DISHES_NUTRITION.get("bánh mì", {
                        "calories": 320, "protein": 18, "fat": 12, "carbs": 35
                    }),
                    "cooking_time": "15 phút",
                    "difficulty": "Dễ"
                },
                {
                    "name": "Cháo gà",
                    "region": "Trung",
                    "ingredients": [
                        {"name": "gạo tẻ", "amount": "80g"},
                        {"name": "thịt gà", "amount": "100g"},
                        {"name": "hành lá", "amount": "15g"},
                        {"name": "gừng", "amount": "10g"},
                        {"name": "nước dùng gà", "amount": "600ml"}
                    ],
                    "preparation": [
                        "Nấu cháo gạo với nước dùng gà",
                        "Luộc gà, xé nhỏ",
                        "Cho gà vào cháo, nêm gia vị",
                        "Rắc hành lá và gừng thái sợi"
                    ],
                    "nutrition": {
                        "calories": 280, "protein": 22, "fat": 8, "carbs": 32
                    },
                    "cooking_time": "45 phút",
                    "difficulty": "Trung bình"
                },
                {
                    "name": "Bún bò Huế",
                    "region": "Trung",
                    "ingredients": [
                        {"name": "bún", "amount": "200g"},
                        {"name": "thịt bò", "amount": "100g"},
                        {"name": "chả cua", "amount": "50g"},
                        {"name": "huyết heo", "amount": "50g"},
                        {"name": "nước dùng cay", "amount": "500ml"}
                    ],
                    "preparation": [
                        "Nấu nước dùng bò với sả, ớt",
                        "Trụng bún, cho vào tô",
                        "Thêm thịt bò, chả cua, huyết",
                        "Chan nước dùng cay nóng"
                    ],
                    "nutrition": {
                        "calories": 450, "protein": 28, "fat": 14, "carbs": 58
                    },
                    "cooking_time": "60 phút",
                    "difficulty": "Khó"
                },
                {
                    "name": "Xôi gà",
                    "region": "Bắc",
                    "ingredients": [
                        {"name": "gạo nếp", "amount": "150g"},
                        {"name": "thịt gà", "amount": "80g"},
                        {"name": "hành phi", "amount": "15g"},
                        {"name": "nước mắm", "amount": "10ml"},
                        {"name": "đậu xanh", "amount": "30g"}
                    ],
                    "preparation": [
                        "Ngâm nếp 4-6 tiếng",
                        "Hấp xôi với đậu xanh",
                        "Luộc gà, xé nhỏ, trộn hành phi",
                        "Ăn xôi kèm gà và nước mắm"
                    ],
                    "nutrition": {
                        "calories": 380, "protein": 20, "fat": 10, "carbs": 55
                    },
                    "cooking_time": "90 phút",
                    "difficulty": "Trung bình"
                }
            ],
            "lunch": [
                {
                    "name": "Cơm tấm sườn nướng",
                    "region": "Nam",
                    "ingredients": [
                        {"name": "cơm tấm", "amount": "200g"},
                        {"name": "sườn heo", "amount": "150g"},
                        {"name": "trứng ốp la", "amount": "1 quả"},
                        {"name": "dưa chua", "amount": "50g"},
                        {"name": "nước mắm pha", "amount": "30ml"}
                    ],
                    "preparation": [
                        "Ướp sườn với gia vị, nướng chín",
                        "Chiên trứng ốp la",
                        "Nấu cơm tấm",
                        "Phục vụ với dưa chua và nước mắm pha"
                    ],
                    "nutrition": VIETNAMESE_DISHES_NUTRITION.get("cơm tấm", {
                        "calories": 520, "protein": 28.5, "fat": 18.2, "carbs": 65
                    }),
                    "cooking_time": "45 phút",
                    "difficulty": "Trung bình"
                },
                {
                    "name": "Bún chả Hà Nội",
                    "region": "Bắc",
                    "ingredients": [
                        {"name": "bún", "amount": "200g"},
                        {"name": "thịt heo nướng", "amount": "120g"},
                        {"name": "chả cá", "amount": "80g"},
                        {"name": "rau thơm", "amount": "100g"},
                        {"name": "nước mắm pha", "amount": "100ml"}
                    ],
                    "preparation": [
                        "Ướp thịt heo, nướng than hoa",
                        "Làm chả cá, nướng vàng",
                        "Trụng bún tươi",
                        "Pha nước mắm chua ngọt, ăn kèm rau thơm"
                    ],
                    "nutrition": {
                        "calories": 480, "protein": 32, "fat": 16, "carbs": 52
                    },
                    "cooking_time": "60 phút",
                    "difficulty": "Khó"
                },
                {
                    "name": "Cơm chiên dương châu",
                    "region": "Nam",
                    "ingredients": [
                        {"name": "cơm nguội", "amount": "200g"},
                        {"name": "tôm", "amount": "100g"},
                        {"name": "xúc xích", "amount": "50g"},
                        {"name": "trứng", "amount": "2 quả"},
                        {"name": "đậu Hà Lan", "amount": "50g"}
                    ],
                    "preparation": [
                        "Xào trứng tơi, vớt ra",
                        "Xào tôm và xúc xích",
                        "Cho cơm vào xào, nêm gia vị",
                        "Trộn đều với trứng và đậu Hà Lan"
                    ],
                    "nutrition": {
                        "calories": 450, "protein": 25, "fat": 18, "carbs": 48
                    },
                    "cooking_time": "20 phút",
                    "difficulty": "Dễ"
                },
                {
                    "name": "Mì Quảng",
                    "region": "Trung",
                    "ingredients": [
                        {"name": "mì Quảng", "amount": "200g"},
                        {"name": "tôm", "amount": "100g"},
                        {"name": "thịt heo", "amount": "80g"},
                        {"name": "trứng cút", "amount": "4 quả"},
                        {"name": "bánh tráng nướng", "amount": "2 cái"}
                    ],
                    "preparation": [
                        "Nấu nước dùng từ xương heo",
                        "Xào tôm, thịt với gia vị",
                        "Luộc mì, cho vào tô",
                        "Chan nước dùng, ăn kèm bánh tráng"
                    ],
                    "nutrition": {
                        "calories": 420, "protein": 28, "fat": 12, "carbs": 55
                    },
                    "cooking_time": "50 phút",
                    "difficulty": "Khó"
                },
                {
                    "name": "Cà ri gà",
                    "region": "Nam",
                    "ingredients": [
                        {"name": "thịt gà", "amount": "200g"},
                        {"name": "khoai tây", "amount": "150g"},
                        {"name": "cà rốt", "amount": "100g"},
                        {"name": "nước cốt dừa", "amount": "200ml"},
                        {"name": "cà ri bột", "amount": "20g"}
                    ],
                    "preparation": [
                        "Ướp gà với cà ri",
                        "Xào gà cho thơm",
                        "Thêm khoai tây, cà rốt",
                        "Đổ nước cốt dừa, niêu nhỏ lửa"
                    ],
                    "nutrition": {
                        "calories": 380, "protein": 30, "fat": 20, "carbs": 25
                    },
                    "cooking_time": "40 phút",
                    "difficulty": "Trung bình"
                }
            ],
            "dinner": [
                {
                    "name": "Canh chua cá",
                    "region": "Nam",
                    "ingredients": [
                        {"name": "cá bông lau", "amount": "200g"},
                        {"name": "me", "amount": "30g"},
                        {"name": "cà chua", "amount": "100g"},
                        {"name": "dứa", "amount": "100g"},
                        {"name": "rau muống", "amount": "100g"}
                    ],
                    "preparation": [
                        "Nấu nước me chua",
                        "Cho cà chua, dứa vào nấu",
                        "Thêm cá, nêm gia vị",
                        "Cuối cùng cho rau muống"
                    ],
                    "nutrition": {
                        "calories": 180, "protein": 22, "fat": 5, "carbs": 15
                    },
                    "cooking_time": "25 phút",
                    "difficulty": "Dễ"
                }
            ]
        }
    
    def get_diverse_meals(self, meal_type: str, count: int = 3, avoid_dishes: List[str] = None) -> List[Dict]:
        """
        Lấy món ăn đa dạng theo loại bữa
        
        Args:
            meal_type: Loại bữa ăn (breakfast, lunch, dinner)
            count: Số lượng món cần lấy
            avoid_dishes: Danh sách món cần tránh
            
        Returns:
            List[Dict]: Danh sách món ăn đa dạng
        """
        if avoid_dishes is None:
            avoid_dishes = []
        
        available_meals = self.vietnamese_meals.get(meal_type, [])
        
        # Lọc bỏ món đã sử dụng
        filtered_meals = [
            meal for meal in available_meals 
            if meal["name"] not in avoid_dishes
        ]
        
        # Nếu không đủ món, lấy từ các miền khác nhau
        if len(filtered_meals) < count:
            # Ưu tiên đa dạng theo miền
            regions = ["Bắc", "Trung", "Nam"]
            diverse_meals = []
            
            for region in regions:
                region_meals = [m for m in filtered_meals if m.get("region") == region]
                if region_meals and len(diverse_meals) < count:
                    diverse_meals.extend(random.sample(region_meals, min(len(region_meals), count - len(diverse_meals))))
            
            return diverse_meals[:count]
        
        # Chọn ngẫu nhiên từ danh sách đã lọc
        return random.sample(filtered_meals, min(count, len(filtered_meals)))
    
    def get_meal_by_name(self, meal_name: str) -> Optional[Dict]:
        """
        Lấy thông tin món ăn theo tên
        
        Args:
            meal_name: Tên món ăn
            
        Returns:
            Optional[Dict]: Thông tin món ăn hoặc None
        """
        for meal_type, meals in self.vietnamese_meals.items():
            for meal in meals:
                if meal["name"].lower() == meal_name.lower():
                    return meal
        return None
    
    def validate_nutrition(self, meal: Dict) -> bool:
        """
        Kiểm tra tính hợp lý của dữ liệu dinh dưỡng
        
        Args:
            meal: Thông tin món ăn
            
        Returns:
            bool: True nếu hợp lý
        """
        nutrition = meal.get("nutrition", {})
        
        calories = nutrition.get("calories", 0)
        protein = nutrition.get("protein", 0)
        fat = nutrition.get("fat", 0)
        carbs = nutrition.get("carbs", 0)
        
        # Kiểm tra giá trị hợp lý
        if calories < 50 or calories > 1000:
            return False
        
        # Kiểm tra tỷ lệ macro
        calculated_calories = (protein * 4) + (fat * 9) + (carbs * 4)
        if abs(calculated_calories - calories) > calories * 0.3:
            return False
        
        return True

# Global instance
vietnamese_meal_service = VietnameseMealService()
