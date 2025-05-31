import json
import random
from typing import List, Dict, Optional, Any

# Dữ liệu mẫu cho các món ăn
SAMPLE_DISHES = {
    "breakfast": [
        {
            "name": "Phở gà",
            "ingredients": [
                {"name": "phở", "amount": "100g"},
                {"name": "ức gà", "amount": "120g"},
                {"name": "hành lá", "amount": "10g"}
            ],
            "preparation": "Nấu nước dùng, luộc phở và gà riêng, cho vào tô và rắc hành lá.",
            "nutrition": {
                "calories": 350,
                "protein": 25,
                "fat": 8,
                "carbs": 45
            }
        },
        {
            "name": "Bánh mì trứng",
            "ingredients": [
                {"name": "bánh mì", "amount": "1 ổ"},
                {"name": "trứng", "amount": "2 quả"},
                {"name": "dưa leo", "amount": "1/2 quả"}
            ],
            "preparation": "Chiên trứng, kẹp vào bánh mì với dưa leo.",
            "nutrition": {
                "calories": 400,
                "protein": 20,
                "fat": 15,
                "carbs": 50
            }
        },
        {
            "name": "Cháo thịt bằm",
            "ingredients": [
                {"name": "gạo", "amount": "50g"},
                {"name": "thịt heo bằm", "amount": "100g"},
                {"name": "hành ngò", "amount": "15g"}
            ],
            "preparation": "Nấu gạo với nước thành cháo, cho thịt bằm vào, nêm gia vị và rắc hành ngò.",
            "nutrition": {
                "calories": 300,
                "protein": 18,
                "fat": 5,
                "carbs": 40
            }
        }
    ],
    "lunch": [
        {
            "name": "Cơm gà xối mỡ",
            "ingredients": [
                {"name": "cơm trắng", "amount": "200g"},
                {"name": "gà", "amount": "150g"},
                {"name": "dưa chua", "amount": "50g"}
            ],
            "preparation": "Luộc gà, xé nhỏ và xối mỡ nóng lên trên, ăn kèm cơm và dưa chua.",
            "nutrition": {
                "calories": 500,
                "protein": 35,
                "fat": 15,
                "carbs": 60
            }
        },
        {
            "name": "Bún chả",
            "ingredients": [
                {"name": "bún", "amount": "150g"},
                {"name": "thịt heo nướng", "amount": "150g"},
                {"name": "nước mắm pha", "amount": "100ml"},
                {"name": "rau sống", "amount": "50g"}
            ],
            "preparation": "Nướng thịt, pha nước mắm, ăn kèm bún và rau sống.",
            "nutrition": {
                "calories": 450,
                "protein": 30,
                "fat": 12,
                "carbs": 55
            }
        },
        {
            "name": "Canh chua cá lóc",
            "ingredients": [
                {"name": "cá lóc", "amount": "200g"},
                {"name": "đậu bắp", "amount": "50g"},
                {"name": "dứa", "amount": "100g"},
                {"name": "cà chua", "amount": "100g"}
            ],
            "preparation": "Nấu nước dùng, cho cá và rau củ vào, nêm gia vị chua cay vừa ăn.",
            "nutrition": {
                "calories": 250,
                "protein": 25,
                "fat": 5,
                "carbs": 20
            }
        }
    ],
    "dinner": [
        {
            "name": "Cá kho tộ",
            "ingredients": [
                {"name": "cá thu", "amount": "200g"},
                {"name": "nước mắm", "amount": "30ml"},
                {"name": "thịt ba chỉ", "amount": "50g"}
            ],
            "preparation": "Kho cá với thịt ba chỉ và nước mắm trong tộ đất.",
            "nutrition": {
                "calories": 350,
                "protein": 30,
                "fat": 18,
                "carbs": 5
            }
        },
        {
            "name": "Thịt kho trứng",
            "ingredients": [
                {"name": "thịt heo", "amount": "200g"},
                {"name": "trứng", "amount": "4 quả"},
                {"name": "nước dừa", "amount": "200ml"}
            ],
            "preparation": "Kho thịt và trứng với nước dừa và nước mắm.",
            "nutrition": {
                "calories": 550,
                "protein": 40,
                "fat": 35,
                "carbs": 10
            }
        },
        {
            "name": "Rau muống xào tỏi",
            "ingredients": [
                {"name": "rau muống", "amount": "300g"},
                {"name": "tỏi", "amount": "15g"},
                {"name": "dầu ăn", "amount": "15ml"}
            ],
            "preparation": "Phi thơm tỏi, xào rau muống với lửa to.",
            "nutrition": {
                "calories": 120,
                "protein": 5,
                "fat": 8,
                "carbs": 10
            }
        }
    ]
}

def generate_dish(meal_type: str) -> Dict:
    """Tạo một món ăn ngẫu nhiên cho loại bữa ăn cụ thể"""
    # Map loại bữa ăn
    meal_map = {
        "bữa sáng": "breakfast",
        "buổi sáng": "breakfast",
        "sáng": "breakfast",
        "breakfast": "breakfast",
        
        "bữa trưa": "lunch",
        "buổi trưa": "lunch", 
        "trưa": "lunch",
        "lunch": "lunch",
        
        "bữa tối": "dinner",
        "buổi tối": "dinner",
        "tối": "dinner",
        "dinner": "dinner"
    }
    
    meal_key = meal_map.get(meal_type.lower(), "breakfast")
    dishes = SAMPLE_DISHES.get(meal_key, SAMPLE_DISHES["breakfast"])
    
    return random.choice(dishes)

def generate_meal(meal_type: str, calories: float, protein: float, fat: float, carbs: float) -> Dict:
    """Tạo một bữa ăn với các món phù hợp với yêu cầu dinh dưỡng"""
    # Quyết định số lượng món ăn
    dish_count = random.randint(1, 3)
    
    # Tạo các món ăn
    dishes = []
    for _ in range(dish_count):
        dish = generate_dish(meal_type)
        dishes.append(dish)
    
    # Tính tổng dinh dưỡng
    total_calories = sum(dish["nutrition"]["calories"] for dish in dishes)
    total_protein = sum(dish["nutrition"]["protein"] for dish in dishes)
    total_fat = sum(dish["nutrition"]["fat"] for dish in dishes)
    total_carbs = sum(dish["nutrition"]["carbs"] for dish in dishes)
    
    # Điều chỉnh tỷ lệ dinh dưỡng
    if total_calories > 0:
        scale_factor = calories / total_calories
        
        for dish in dishes:
            for key in ["calories", "protein", "fat", "carbs"]:
                dish["nutrition"][key] = round(dish["nutrition"][key] * scale_factor, 1)
    
    # Thông tin dinh dưỡng tổng
    nutrition = {
        "calories": round(sum(dish["nutrition"]["calories"] for dish in dishes), 1),
        "protein": round(sum(dish["nutrition"]["protein"] for dish in dishes), 1),
        "fat": round(sum(dish["nutrition"]["fat"] for dish in dishes), 1),
        "carbs": round(sum(dish["nutrition"]["carbs"] for dish in dishes), 1)
    }
    
    return {
        "dishes": dishes,
        "nutrition": nutrition
    }

def generate_day_plan(
    day: str, 
    calories: float = 2000, 
    protein: float = 120, 
    fat: float = 70, 
    carbs: float = 250
) -> Dict:
    """Tạo kế hoạch cho một ngày"""
    # Phân bổ dinh dưỡng cho các bữa
    breakfast_ratio = 0.25
    lunch_ratio = 0.4
    dinner_ratio = 0.35
    
    breakfast = generate_meal(
        "breakfast", 
        calories * breakfast_ratio,
        protein * breakfast_ratio,
        fat * breakfast_ratio,
        carbs * breakfast_ratio
    )
    
    lunch = generate_meal(
        "lunch", 
        calories * lunch_ratio,
        protein * lunch_ratio,
        fat * lunch_ratio,
        carbs * lunch_ratio
    )
    
    dinner = generate_meal(
        "dinner", 
        calories * dinner_ratio,
        protein * dinner_ratio,
        fat * dinner_ratio,
        carbs * dinner_ratio
    )
    
    # Tính tổng dinh dưỡng trong ngày
    day_nutrition = {
        "calories": round(breakfast["nutrition"]["calories"] + lunch["nutrition"]["calories"] + dinner["nutrition"]["calories"], 1),
        "protein": round(breakfast["nutrition"]["protein"] + lunch["nutrition"]["protein"] + dinner["nutrition"]["protein"], 1),
        "fat": round(breakfast["nutrition"]["fat"] + lunch["nutrition"]["fat"] + dinner["nutrition"]["fat"], 1),
        "carbs": round(breakfast["nutrition"]["carbs"] + lunch["nutrition"]["carbs"] + dinner["nutrition"]["carbs"], 1)
    }
    
    return {
        "day_of_week": day,
        "breakfast": breakfast,
        "lunch": lunch,
        "dinner": dinner,
        "nutrition": day_nutrition
    }

def generate_weekly_plan(
    calories: float = 2000, 
    protein: float = 120, 
    fat: float = 70, 
    carbs: float = 250,
    preferences: List[str] = None,
    allergies: List[str] = None,
    cuisine_style: str = None,
    use_ai: bool = True,
    use_tdee: bool = True
) -> Dict:
    """Tạo kế hoạch cho cả tuần"""
    days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
    
    day_plans = []
    for day in days:
        day_plan = generate_day_plan(day, calories, protein, fat, carbs)
        day_plans.append(day_plan)
    
    return {
        "days": day_plans
    }

# Hàm để test dữ liệu
if __name__ == "__main__":
    weekly_plan = generate_weekly_plan(2000, 150, 60, 200)
    print(json.dumps(weekly_plan, indent=2, ensure_ascii=False)) 