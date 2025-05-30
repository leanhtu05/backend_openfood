from typing import List, Dict, Optional, Set
import random
from models import (
    NutritionTarget, ReplaceDayRequest, DayMealPlan, WeeklyMealPlan,
    Dish, Meal, NutritionInfo, Ingredient
)
from utils import (
    DAYS_OF_WEEK, SAMPLE_RECIPES, calculate_meal_nutrition,
    calculate_day_nutrition, distribute_nutrition_targets,
    adjust_dish_portions, generate_random_dishes, format_nutrition_value
)
from nutritionix import get_nutrition_fallback
from nutritionix_optimized import nutritionix_optimized_api
import os
import json
from datetime import datetime
from firebase_admin import firestore
from .services.meal_diversity_service import MealDiversityService

# Import Groq integration
try:
    from groq_integration_direct import groq_service  # Fixed version
    AI_SERVICE = groq_service
    AI_AVAILABLE = groq_service.available
except ImportError:
    # Không có dịch vụ AI
    AI_SERVICE = None
    AI_AVAILABLE = False
    print("WARNING: Groq integration not available")

# Sử dụng phiên bản API đã tối ưu
nutritionix_api = nutritionix_optimized_api

# Track used dishes to avoid repetition across days
used_dishes_tracker = {
    "breakfast": set(),
    "lunch": set(),
    "dinner": set()
}

def generate_dish(recipe_dict: Dict) -> Dish:
    """
    Generate a Dish object from a recipe dictionary.
    
    Args:
        recipe_dict: Dictionary with dish recipe information
        
    Returns:
        Dish object with nutritional information
    """
    print(f"Generating dish: {recipe_dict.get('name', 'Unnamed')}")
    
    # Convert ingredient dictionaries to Ingredient objects
    ingredients = []
    if "ingredients" in recipe_dict and recipe_dict["ingredients"]:
        ingredients = [
            Ingredient(name=ing["name"], amount=ing["amount"])
            for ing in recipe_dict["ingredients"]
        ]
        print(f"Found {len(ingredients)} ingredients")
    else:
        print(f"WARNING: No ingredients found for dish {recipe_dict.get('name', 'Unnamed')}")
    
    # Get nutrition information for the dish
    try:
        # Kiểm tra xem recipe_dict đã có thông tin dinh dưỡng chưa
        if "nutrition" in recipe_dict and isinstance(recipe_dict["nutrition"], dict):
            # Trường hợp response từ LLaMA đã có nutrition info
            nutrition_data = recipe_dict["nutrition"]
            print(f"Using nutrition data from recipe: {nutrition_data}")
            dish_nutrition = NutritionInfo(
                calories=nutrition_data.get("calories", 0),
                protein=nutrition_data.get("protein", 0),
                fat=nutrition_data.get("fat", 0),
                carbs=nutrition_data.get("carbs", 0)
            )
        elif "total_nutrition" in recipe_dict and isinstance(recipe_dict["total_nutrition"], dict):
            # Cấu trúc Groq LLaMA có thể trả về total_nutrition
            nutrition_data = recipe_dict["total_nutrition"]
            print(f"Using total_nutrition data from recipe: {nutrition_data}")
            dish_nutrition = NutritionInfo(
                calories=nutrition_data.get("calories", 0),
                protein=nutrition_data.get("protein", 0),
                fat=nutrition_data.get("fat", 0),
                carbs=nutrition_data.get("carbs", 0)
            )
        else:
            # Nếu không có sẵn thông tin dinh dưỡng và có ingredients
            if ingredients:
                print(f"Getting nutrition from Nutritionix API for {len(ingredients)} ingredients")
                # Try to get nutrition from Nutritionix API
                dish_nutrition = nutritionix_api.get_nutrition_for_ingredients(ingredients)
            else:
                print("No ingredients and no nutrition data. Using default values.")
                dish_nutrition = NutritionInfo(
                    calories=400, 
                    protein=20, 
                    fat=15, 
                    carbs=45
                )
    except Exception as e:
        # Log error details
        print(f"Error getting nutrition data: {str(e)}")
        # Fallback: Calculate nutrition from local data
        dish_nutrition = NutritionInfo(calories=0, protein=0, fat=0, carbs=0)
        for ingredient in ingredients:
            try:
                ing_nutrition = get_nutrition_fallback(ingredient.name, ingredient.amount)
                dish_nutrition.calories += ing_nutrition.calories
                dish_nutrition.protein += ing_nutrition.protein
                dish_nutrition.fat += ing_nutrition.fat
                dish_nutrition.carbs += ing_nutrition.carbs
            except Exception as ing_error:
                print(f"Error processing ingredient '{ingredient.name}': {str(ing_error)}")
        
        if dish_nutrition.calories == 0:
            print("Fallback nutrition also failed. Using default values.")
            dish_nutrition = NutritionInfo(
                calories=400, 
                protein=20, 
                fat=15, 
                carbs=45
            )
    
    # Format nutrition values
    dish_nutrition.calories = format_nutrition_value(dish_nutrition.calories)
    dish_nutrition.protein = format_nutrition_value(dish_nutrition.protein)
    dish_nutrition.fat = format_nutrition_value(dish_nutrition.fat)
    dish_nutrition.carbs = format_nutrition_value(dish_nutrition.carbs)
    
    print(f"Final dish nutrition: cal={dish_nutrition.calories}, protein={dish_nutrition.protein}, fat={dish_nutrition.fat}, carbs={dish_nutrition.carbs}")
    
    # Create and return the Dish object
    return Dish(
        name=recipe_dict.get("name", "Món ăn không tên"),
        ingredients=ingredients,
        preparation=recipe_dict.get("preparation", "Không có hướng dẫn chi tiết."),
        nutrition=dish_nutrition
    )

def generate_meal(
    meal_type: str, 
    target_calories: float, 
    target_protein: float, 
    target_fat: float, 
    target_carbs: float,
    preferences: List[str] = None,
    allergies: List[str] = None,
    cuisine_style: str = None,
    use_ai: bool = True,
    day_of_week: str = None
) -> Meal:
    """
    Generate a meal with dishes that meet nutritional targets.
    
    Args:
        meal_type: Type of meal (breakfast, lunch, dinner)
        target_calories: Target calories for the meal
        target_protein: Target protein for the meal (g)
        target_fat: Target fat for the meal (g)
        target_carbs: Target carbs for the meal (g)
        preferences: Danh sách sở thích thực phẩm (tùy chọn)
        allergies: Danh sách dị ứng thực phẩm (tùy chọn)
        cuisine_style: Phong cách ẩm thực (tùy chọn)
        use_ai: Có sử dụng AI để tạo món ăn hay không
        day_of_week: Ngày trong tuần (để tránh trùng lặp món ăn)
        
    Returns:
        Meal object with dishes and nutritional information
    """
    print(f"==== GENERATING MEAL: {meal_type} for {day_of_week or 'unknown day'} ====")
    print(f"Targets: cal={target_calories}, protein={target_protein}, fat={target_fat}, carbs={target_carbs}")
    print(f"Using AI: {use_ai}")
    
    dishes = []
    
    # Determine meal category for tracking
    meal_category = "breakfast"
    if "trưa" in meal_type.lower() or "lunch" in meal_type.lower():
        meal_category = "lunch"
    elif "tối" in meal_type.lower() or "dinner" in meal_type.lower():
        meal_category = "dinner"
    
    # Get current used dishes for this meal type
    current_used_dishes = used_dishes_tracker.get(meal_category, set())
    print(f"Currently used {meal_category} dishes: {current_used_dishes}")
    
    # Quyết định phương pháp tạo món ăn (AI hoặc ngẫu nhiên)
    if use_ai and AI_SERVICE and AI_AVAILABLE:
        # Sử dụng LLaMA 3 qua Groq để tạo món ăn
        try:
            print(f"Attempting to generate dishes using AI ({AI_SERVICE.__class__.__name__}) for {meal_type}")
            
            # Thêm tham số ngày và random seed vào yêu cầu AI để tăng tính đa dạng
            random_seed = random.randint(1, 1000)
            
            ai_dish_dicts = AI_SERVICE.generate_meal_suggestions(
                calories_target=int(target_calories),
                protein_target=int(target_protein),
                fat_target=int(target_fat),
                carbs_target=int(target_carbs),
                meal_type=meal_type,
                preferences=preferences,
                allergies=allergies,
                cuisine_style=cuisine_style,
                use_ai=use_ai,
                day_of_week=day_of_week,  # Thêm ngày vào để đa dạng hóa kết quả
                random_seed=random_seed   # Thêm seed ngẫu nhiên
            )
            
            print(f"AI returned {len(ai_dish_dicts) if ai_dish_dicts else 0} dishes")
            
            if ai_dish_dicts:
                # Chuyển đổi kết quả từ LLaMA thành Dish objects
                dishes = [generate_dish(dish_dict) for dish_dict in ai_dish_dicts]
                print(f"Successfully created {len(dishes)} dishes from AI for {meal_type}")
                
                # Track used dish names
                for dish in dishes:
                    current_used_dishes.add(dish.name)
                
                # Validation check
                if not dishes or all(len(dish.ingredients) == 0 for dish in dishes):
                    print("WARNING: AI returned dishes without ingredients. Falling back to random generation.")
                    dishes = []
            else:
                # Fallback nếu không có kết quả AI
                print(f"No results from AI, using random method for {meal_type}")
                dishes = []
        except Exception as e:
            # Xử lý lỗi khi gọi AI
            print(f"Error when using AI to generate dishes: {str(e)}")
            dishes = []
    
    # Nếu không sử dụng AI hoặc AI không thành công, dùng phương pháp ngẫu nhiên
    if not dishes:
        print(f"Using random dish generation for {meal_type}")
        dish_count = random.randint(1, 2)  # 1-2 dishes per meal
        
        # Pass used dishes to avoid repetition
        used_dish_names = list(current_used_dishes) if current_used_dishes else []
        
        # Thêm tham số ngày vào để tăng tính đa dạng
        day_index = DAYS_OF_WEEK.index(day_of_week) if day_of_week in DAYS_OF_WEEK else -1
        selected_dish_dicts = generate_random_dishes(meal_type, dish_count, used_dish_names, day_index=day_index)
        
        # Adjust portions to meet targets
        adjusted_dish_dicts = adjust_dish_portions(
            selected_dish_dicts, 
            target_calories, 
            target_protein, 
            target_fat, 
            target_carbs
        )
        
        # Convert to Dish objects
        dishes = [generate_dish(dish_dict) for dish_dict in adjusted_dish_dicts]
        print(f"Generated {len(dishes)} random dishes for {meal_type}")
        
        # Track used dish names
        for dish in dishes:
            current_used_dishes.add(dish.name)
    
    # Final validation - if we still have no dishes, create a basic dish
    if not dishes:
        print(f"WARNING: Failed to generate any dishes for {meal_type}. Creating a basic dish.")
        # Tạo món ăn mẫu dựa trên loại bữa
        if "sáng" in meal_type.lower() or "breakfast" in meal_type.lower():
            # Thêm biến thể vào tên món ăn dựa trên ngày
            day_suffix = f" {day_of_week}" if day_of_week else f" #{random.randint(1, 100)}"
            basic_dish = {
                "name": f"Bánh mì trứng{day_suffix}",
                "ingredients": [
                    {"name": "bánh mì", "amount": "2 lát"},
                    {"name": "trứng gà", "amount": "2 quả"},
                    {"name": "gia vị", "amount": "vừa đủ"}
                ],
                "preparation": "Đập trứng vào chảo, chiên vàng. Ăn kèm với bánh mì.",
                "nutrition": {
                    "calories": target_calories,
                    "protein": target_protein,
                    "fat": target_fat,
                    "carbs": target_carbs
                }
            }
        elif "trưa" in meal_type.lower() or "lunch" in meal_type.lower():
            day_suffix = f" {day_of_week}" if day_of_week else f" #{random.randint(1, 100)}"
            basic_dish = {
                "name": f"Cơm với thịt gà{day_suffix}",
                "ingredients": [
                    {"name": "gạo", "amount": "150g"},
                    {"name": "thịt gà", "amount": "150g"},
                    {"name": "rau củ", "amount": "100g"}
                ],
                "preparation": "Nấu cơm chín. Thịt gà ướp gia vị, rán chín. Ăn kèm rau củ luộc.",
                "nutrition": {
                    "calories": target_calories,
                    "protein": target_protein,
                    "fat": target_fat,
                    "carbs": target_carbs
                }
            }
        else:  # dinner
            day_suffix = f" {day_of_week}" if day_of_week else f" #{random.randint(1, 100)}"
            basic_dish = {
                "name": f"Bún với thịt bò xào{day_suffix}",
                "ingredients": [
                    {"name": "bún", "amount": "150g"},
                    {"name": "thịt bò", "amount": "100g"},
                    {"name": "rau xanh", "amount": "100g"},
                    {"name": "gia vị", "amount": "vừa đủ"}
                ],
                "preparation": "Xào thịt bò với gia vị. Trụng bún và rau. Kết hợp lại.",
                "nutrition": {
                    "calories": target_calories,
                    "protein": target_protein,
                    "fat": target_fat,
                    "carbs": target_carbs
                }
            }
        
        dishes = [generate_dish(basic_dish)]
        print(f"Created basic dish for {meal_type} as fallback")
        
        # Track the fallback dish too
        current_used_dishes.add(dishes[0].name)
    
    # Update the used dishes tracker
    used_dishes_tracker[meal_category] = current_used_dishes
    
    # Calculate total nutrition
    total_nutrition = calculate_meal_nutrition(dishes)
    
    # Create and return the meal object
    return Meal(
        meal_type=meal_type,
        dishes=dishes,
        nutrition=total_nutrition
    )

def generate_day_meal_plan(
    day_of_week: str,
    calories_target: int,
    protein_target: int,
    fat_target: int,
    carbs_target: int,
    preferences: List[str] = None,
    allergies: List[str] = None,
    cuisine_style: str = None,
    use_ai: bool = True
) -> DayMealPlan:
    """
    Generate a daily meal plan that meets nutritional targets.
    
    Args:
        day_of_week: Day of the week
        calories_target: Target calories for the day
        protein_target: Target protein for the day (g)
        fat_target: Target fat for the day (g)
        carbs_target: Target carbs for the day (g)
        preferences: Danh sách sở thích thực phẩm (tùy chọn)
        allergies: Danh sách dị ứng thực phẩm (tùy chọn)
        cuisine_style: Phong cách ẩm thực (tùy chọn)
        use_ai: Có sử dụng AI để tạo món ăn hay không
        
    Returns:
        DayMealPlan object with meals and nutritional information
    """
    print(f"==== GENERATING DAY MEAL PLAN FOR {day_of_week} ====")
    print(f"Targets: cal={calories_target}, protein={protein_target}, fat={fat_target}, carbs={carbs_target}")
    
    # Lấy day_index từ DAYS_OF_WEEK
    day_index = DAYS_OF_WEEK.index(day_of_week) if day_of_week in DAYS_OF_WEEK else -1
    
    # Phân bổ mục tiêu dinh dưỡng cho từng bữa ăn
    try:
        from services.tdee_nutrition_service import tdee_nutrition_service
        breakfast_targets = tdee_nutrition_service.distribute_nutrition_by_meal(
            calories_target, protein_target, fat_target, carbs_target, "breakfast"
        )
        lunch_targets = tdee_nutrition_service.distribute_nutrition_by_meal(
            calories_target, protein_target, fat_target, carbs_target, "lunch"
        )
        dinner_targets = tdee_nutrition_service.distribute_nutrition_by_meal(
            calories_target, protein_target, fat_target, carbs_target, "dinner"
        )
    except Exception as e:
        print(f"Lỗi khi phân bổ dinh dưỡng: {str(e)}")
        # Fallback to old distribution method
        meal_targets = distribute_nutrition_targets(
            calories_target, protein_target, fat_target, carbs_target
        )
        breakfast_targets = meal_targets["breakfast"]
        lunch_targets = meal_targets["lunch"]
        dinner_targets = meal_targets["dinner"]
    
    # Generate each meal
    breakfast = generate_meal(
        "bữa sáng",
        breakfast_targets["calories"],
        breakfast_targets["protein"],
        breakfast_targets["fat"],
        breakfast_targets["carbs"],
        preferences=preferences,
        allergies=allergies,
        cuisine_style=cuisine_style,
        use_ai=use_ai,
        day_of_week=day_of_week
    )
    
    lunch = generate_meal(
        "bữa trưa",
        lunch_targets["calories"],
        lunch_targets["protein"],
        lunch_targets["fat"],
        lunch_targets["carbs"],
        preferences=preferences,
        allergies=allergies,
        cuisine_style=cuisine_style,
        use_ai=use_ai,
        day_of_week=day_of_week
    )
    
    dinner = generate_meal(
        "bữa tối",
        dinner_targets["calories"],
        dinner_targets["protein"],
        dinner_targets["fat"],
        dinner_targets["carbs"],
        preferences=preferences,
        allergies=allergies, 
        cuisine_style=cuisine_style,
        use_ai=use_ai,
        day_of_week=day_of_week
    )
    
    # Final validation to ensure each meal has at least one dish
    if not breakfast.dishes:
        breakfast = create_fallback_meal("bữa sáng", meal_targets["breakfast"]["calories"], 
                                        meal_targets["breakfast"]["protein"],
                                        meal_targets["breakfast"]["fat"], 
                                        meal_targets["breakfast"]["carbs"],
                                        day_of_week=day_of_week)
    
    if not lunch.dishes:
        lunch = create_fallback_meal("bữa trưa", meal_targets["lunch"]["calories"], 
                                    meal_targets["lunch"]["protein"], 
                                    meal_targets["lunch"]["fat"], 
                                    meal_targets["lunch"]["carbs"],
                                    day_of_week=day_of_week)
    
    if not dinner.dishes:
        dinner = create_fallback_meal("bữa tối", meal_targets["dinner"]["calories"], 
                                     meal_targets["dinner"]["protein"], 
                                     meal_targets["dinner"]["fat"], 
                                     meal_targets["dinner"]["carbs"],
                                     day_of_week=day_of_week)
    
    # Calculate daily nutrition
    day_nutrition = calculate_day_nutrition(breakfast, lunch, dinner)
    
    # Create and return the DayMealPlan object
    return DayMealPlan(
        day_of_week=day_of_week,
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner,
        nutrition=day_nutrition
    )

def create_fallback_meal(meal_type: str, calories: float, protein: float, fat: float, carbs: float, day_of_week: str = None) -> Meal:
    """Tạo một bữa ăn dự phòng khi không thể tạo bữa ăn thông thường"""
    print(f"Creating fallback meal for {meal_type}")
    
    # Determine meal category for tracking
    meal_category = "breakfast"
    if "trưa" in meal_type.lower() or "lunch" in meal_type.lower():
        meal_category = "lunch"
    elif "tối" in meal_type.lower() or "dinner" in meal_type.lower():
        meal_category = "dinner"
    
    # Get current used dishes for this meal type
    current_used_dishes = used_dishes_tracker.get(meal_category, set())
    
    # Thêm biến thể vào tên món ăn dựa trên ngày
    day_suffix = f" ({day_of_week})" if day_of_week else f" #{random.randint(1, 100)}"
    
    if "sáng" in meal_type.lower():
        dish = Dish(
            name=f"Bánh mì trứng{day_suffix}",
            ingredients=[
                Ingredient(name="bánh mì", amount="2 lát"),
                Ingredient(name="trứng gà", amount="2 quả"),
                Ingredient(name="gia vị", amount="vừa đủ")
            ],
            preparation="Đập trứng vào chảo, chiên vàng. Ăn kèm với bánh mì.",
            nutrition=NutritionInfo(calories=calories, protein=protein, fat=fat, carbs=carbs)
        )
    elif "trưa" in meal_type.lower():
        dish = Dish(
            name=f"Cơm với thịt gà{day_suffix}",
            ingredients=[
                Ingredient(name="gạo", amount="150g"),
                Ingredient(name="thịt gà", amount="150g"),
                Ingredient(name="rau củ", amount="100g")
            ],
            preparation="Nấu cơm chín. Thịt gà ướp gia vị, rán chín. Ăn kèm rau củ luộc.",
            nutrition=NutritionInfo(calories=calories, protein=protein, fat=fat, carbs=carbs)
        )
    else:
        dish = Dish(
            name=f"Canh rau củ với thịt bò{day_suffix}",
            ingredients=[
                Ingredient(name="thịt bò", amount="100g"),
                Ingredient(name="rau củ tổng hợp", amount="200g"),
                Ingredient(name="gia vị", amount="vừa đủ")
            ],
            preparation="Thịt bò xào chín với gia vị. Rau củ nấu canh. Ăn kèm cơm trắng.",
            nutrition=NutritionInfo(calories=calories, protein=protein, fat=fat, carbs=carbs)
        )
    
    # Track the fallback dish
    current_used_dishes.add(dish.name)
    used_dishes_tracker[meal_category] = current_used_dishes
    
    return Meal(
        meal_type=meal_type,
        dishes=[dish],
        nutrition=NutritionInfo(calories=calories, protein=protein, fat=fat, carbs=carbs)
    )

def generate_weekly_meal_plan(
    calories_target: int = 1500,
    protein_target: int = 90,
    fat_target: int = 50,
    carbs_target: int = 187,
    preferences: List[str] = None,
    allergies: List[str] = None,
    cuisine_style: str = None,
    use_ai: bool = True,
    use_tdee: bool = True  # Thêm tham số use_tdee
) -> WeeklyMealPlan:
    """
    Generate a weekly meal plan that meets nutritional targets.
    
    Args:
        calories_target: Target calories per day (default 1500)
        protein_target: Target protein per day (g) (default 90)
        fat_target: Target fat per day (g) (default 50)
        carbs_target: Target carbs per day (g) (default 187)
        preferences: Danh sách sở thích thực phẩm (tùy chọn)
        allergies: Danh sách dị ứng thực phẩm (tùy chọn)
        cuisine_style: Phong cách ẩm thực (tùy chọn)
        use_ai: Có sử dụng AI để tạo món ăn hay không
        use_tdee: Có sử dụng TDEE để điều chỉnh mục tiêu dinh dưỡng hay không
        
    Returns:
        WeeklyMealPlan: Kế hoạch ăn uống hàng tuần
    """
    try:
        # Đảm bảo calories không vượt quá 1500 nếu không sử dụng TDEE
        if not use_tdee and calories_target > 1500:
            print(f"Giới hạn calories từ {calories_target} xuống 1500")
            calories_target = 1500
            # Điều chỉnh các giá trị khác theo tỷ lệ
            protein_target = 90
            fat_target = 50
            carbs_target = 187.5
        
        print("======================= GENERATING WEEKLY MEAL PLAN =======================")
        print(f"Targets: calories={calories_target}, protein={protein_target}, fat={fat_target}, carbs={carbs_target}")
        print(f"Preferences: {preferences}")
        print(f"Allergies: {allergies}")
        print(f"Cuisine style: {cuisine_style}")
        print(f"Using AI: {use_ai}")
        
        # Reset used dishes tracker to ensure fresh variety for a new weekly plan
        global used_dishes_tracker
        used_dishes_tracker = {
            "breakfast": set(),
            "lunch": set(),
            "dinner": set()
        }
        
        # Generate meal plan for each day of the week
        days = []
        for day in DAYS_OF_WEEK:
            print(f"\n----- Generating plan for {day} -----")
            
            # Thêm biến động nhỏ vào mục tiêu dinh dưỡng để tăng sự đa dạng
            variation = random.uniform(0.95, 1.05)  # Biến động 5%
            day_calories = int(calories_target * variation)
            day_protein = int(protein_target * variation)
            day_fat = int(fat_target * variation)
            day_carbs = int(carbs_target * variation)
            
            print(f"Day {day} targets with variation: cal={day_calories}, protein={day_protein}, fat={day_fat}, carbs={day_carbs}")
            
            # Reset used dishes tracker for each day to ensure maximum variety
            if day != DAYS_OF_WEEK[0]:  # Không reset cho ngày đầu tiên
                # Giữ lại một phần nhỏ món ăn đã sử dụng để tránh trùng lặp hoàn toàn
                # nhưng vẫn cho phép một số món ăn phổ biến xuất hiện lại
                for meal_type in used_dishes_tracker:
                    # Giữ lại tối đa 3 món từ mỗi loại bữa
                    if len(used_dishes_tracker[meal_type]) > 3:
                        # Chọn ngẫu nhiên 3 món để giữ lại
                        kept_dishes = random.sample(list(used_dishes_tracker[meal_type]), 3)
                        used_dishes_tracker[meal_type] = set(kept_dishes)
            
            day_plan = generate_day_meal_plan(
                day, day_calories, day_protein, day_fat, day_carbs,
                preferences=preferences, allergies=allergies, cuisine_style=cuisine_style, use_ai=use_ai
            )
            
            # Verify this day has dishes
            has_dishes = False
            if (day_plan.breakfast and day_plan.breakfast.dishes and len(day_plan.breakfast.dishes) > 0 or
                day_plan.lunch and day_plan.lunch.dishes and len(day_plan.lunch.dishes) > 0 or
                day_plan.dinner and day_plan.dinner.dishes and len(day_plan.dinner.dishes) > 0):
                has_dishes = True
            
            print(f"Day {day} has dishes: {has_dishes}")
            print(f"Breakfast dishes: {len(day_plan.breakfast.dishes)}")
            print(f"Lunch dishes: {len(day_plan.lunch.dishes)}")
            print(f"Dinner dishes: {len(day_plan.dinner.dishes)}")
            
            days.append(day_plan)
        
        # Create and return the WeeklyMealPlan object
        weekly_plan = WeeklyMealPlan(days=days)
        
        print("\n----- Weekly Plan Summary -----")
        total_dishes = 0
        for day in weekly_plan.days:
            day_dishes = (
                len(day.breakfast.dishes if day.breakfast else []) + 
                len(day.lunch.dishes if day.lunch else []) + 
                len(day.dinner.dishes if day.dinner else [])
            )
            total_dishes += day_dishes
            print(f"Day {day.day_of_week}: {day_dishes} dishes")
        
        print(f"Total dishes across all days: {total_dishes}")
        print("======================= WEEKLY MEAL PLAN GENERATED =======================")
        
        return weekly_plan
    except Exception as e:
        print(f"Error generating meal plan: {e}")
        raise

def replace_day_meal_plan(
    current_weekly_plan: Optional[WeeklyMealPlan],
    replace_request: ReplaceDayRequest,
    preferences: List[str] = None,
    allergies: List[str] = None,
    cuisine_style: str = None,
    use_ai: bool = True
) -> DayMealPlan:
    """
    Replace a specific day's meal plan in a weekly plan.
    
    Args:
        current_weekly_plan: Current weekly meal plan (optional)
        replace_request: Request with day and nutrition targets
        preferences: Danh sách sở thích thực phẩm (tùy chọn)
        allergies: Danh sách dị ứng thực phẩm (tùy chọn)
        cuisine_style: Phong cách ẩm thực (tùy chọn)
        use_ai: Có sử dụng AI để tạo món ăn hay không
        
    Returns:
        DayMealPlan object with the new meal plan for the day
    """
    # Clear the used dishes for this specific day to ensure new variety
    global used_dishes_tracker
    used_dishes_tracker = {
        "breakfast": set(),
        "lunch": set(),
        "dinner": set()
    }
    
    # Generate a new meal plan for the day
    new_day_plan = generate_day_meal_plan(
        replace_request.day_of_week,
        replace_request.calories_target,
        replace_request.protein_target,
        replace_request.fat_target,
        replace_request.carbs_target,
        preferences=preferences,
        allergies=allergies,
        cuisine_style=cuisine_style,
        use_ai=use_ai
    )
    
    # If there's an existing weekly plan, update it
    if current_weekly_plan:
        for i, day in enumerate(current_weekly_plan.days):
            if day.day_of_week == replace_request.day_of_week:
                current_weekly_plan.days[i] = new_day_plan
                break
    
    return new_day_plan

def replace_meal(request: Dict) -> Dict:
    """
    Thay thế một bữa ăn cụ thể trong kế hoạch ăn uống.
    
    Args:
        request: Thông tin yêu cầu thay thế bữa ăn, bao gồm:
            - user_id: ID người dùng
            - day_of_week: Ngày trong tuần
            - meal_type: Loại bữa ăn (breakfast, lunch, dinner)
            - calories_target: Mục tiêu calo
            - protein_target: Mục tiêu protein
            - fat_target: Mục tiêu chất béo
            - carbs_target: Mục tiêu carbs
            
    Returns:
        Dict: Kết quả thay thế bữa ăn
    """
    print(f"Replacing meal with request: {request}")
    
    user_id = request.get("user_id")
    day_of_week = request.get("day_of_week")
    meal_type = request.get("meal_type", "").lower()
    
    # Ánh xạ tên bữa ăn từ tiếng Việt sang tiếng Anh
    meal_type_mapping = {
        "bữa sáng": "breakfast",
        "buổi sáng": "breakfast",
        "sáng": "breakfast",
        "bữa trưa": "lunch",
        "buổi trưa": "lunch",
        "trưa": "lunch",
        "bữa tối": "dinner",
        "buổi tối": "dinner",
        "tối": "dinner"
    }
    
    # Nếu meal_type là tiếng Việt, chuyển đổi sang tiếng Anh
    if meal_type in meal_type_mapping:
        meal_type = meal_type_mapping[meal_type]
    
    # Đảm bảo meal_type hợp lệ
    if meal_type not in ["breakfast", "lunch", "dinner"]:
        raise ValueError(f"Invalid meal type: {meal_type}")
    
    # Đặt mặc định cho các giá trị dinh dưỡng nếu không được cung cấp
    # Sử dụng mặc định thấp hơn cho calories (1500 kcal cho cả ngày)
    meal_ratios = {"breakfast": 0.25, "lunch": 0.4, "dinner": 0.35}
    daily_calories = 1500  # Mặc định 1500 kcal cho cả ngày
    
    # Lấy giá trị calories_target từ request hoặc sử dụng mặc định
    calories_target = request.get("calories_target")
    if not calories_target:
        # Nếu không có calories_target, sử dụng tỷ lệ của bữa ăn
        calories_target = daily_calories * meal_ratios[meal_type]
    else:
        # Giới hạn calories_target nếu quá cao
        max_meal_calories = daily_calories * meal_ratios[meal_type]
        if calories_target > max_meal_calories:
            print(f"Adjusting calories target from {calories_target} to {max_meal_calories}")
            calories_target = max_meal_calories
    
    # Tính toán các mục tiêu dinh dưỡng khác nếu không được cung cấp
    protein_target = request.get("protein_target")
    if not protein_target:
        protein_target = calories_target * 0.15 / 4  # 15% calories từ protein
    
    fat_target = request.get("fat_target")
    if not fat_target:
        fat_target = calories_target * 0.3 / 9  # 30% calories từ fat
    
    carbs_target = request.get("carbs_target")
    if not carbs_target:
        carbs_target = calories_target * 0.55 / 4  # 55% calories từ carbs
    
    # Reset used_dishes_tracker cho loại bữa ăn này để tránh trùng lặp
    global used_dishes_tracker
    used_dishes_tracker[meal_type] = set()
    
    # Thêm biến thể dựa trên ngày để tăng tính đa dạng
    preferences = request.get("preferences", [])
    allergies = request.get("allergies", [])
    cuisine_style = request.get("cuisine_style")
    use_ai = request.get("use_ai", False)
    
    # Tạo bữa ăn mới
    new_meal = generate_meal(
        meal_type,
        calories_target,
        protein_target,
        fat_target,
        carbs_target,
        preferences=preferences,
        allergies=allergies,
        cuisine_style=cuisine_style,
        use_ai=use_ai,
        day_of_week=day_of_week  # Thêm day_of_week để tăng tính đa dạng
    )
    
    # Lấy kế hoạch ăn hiện tại
    from storage_manager import storage_manager
    meal_plan = storage_manager.load_meal_plan(user_id)
    
    if meal_plan:
        # Tìm ngày cần thay đổi
        for i, day in enumerate(meal_plan.days):
            if day.day_of_week == day_of_week:
                # Cập nhật bữa ăn
                if meal_type == "breakfast":
                    meal_plan.days[i].breakfast = new_meal
                elif meal_type == "lunch":
                    meal_plan.days[i].lunch = new_meal
                elif meal_type == "dinner":
                    meal_plan.days[i].dinner = new_meal
                
                # Cập nhật tổng dinh dưỡng của ngày
                meal_plan.days[i].nutrition = calculate_day_nutrition(
                    meal_plan.days[i].breakfast,
                    meal_plan.days[i].lunch,
                    meal_plan.days[i].dinner
                )
                break
        
        # Lưu kế hoạch đã cập nhật
        storage_manager.save_meal_plan(meal_plan, user_id)
    
    return {
        "day_of_week": day_of_week,
        "meal_type": meal_type,
        "new_meal": new_meal
    }

def generate_meal_plan(
    user_id: str,
    calories_target: float = 1500.0,  # Giảm mặc định xuống 1500 kcal
    protein_target: float = 90.0,     # Điều chỉnh protein
    fat_target: float = 50.0,         # Điều chỉnh fat
    carbs_target: float = 187.5,      # Điều chỉnh carbs
    preferences: Optional[str] = None,
    allergies: Optional[str] = None,
    cuisine_style: Optional[str] = None,
    use_ai: bool = True,
    ensure_diversity: bool = False,  # Thêm tham số mới
    use_tdee: bool = True            # Thêm tham số để sử dụng TDEE
) -> Dict[str, Any]:
    """
    Tạo kế hoạch ăn uống hàng tuần cho người dùng.
    
    Args:
        user_id: ID người dùng
        calories_target: Mục tiêu calo hàng ngày
        protein_target: Mục tiêu protein hàng ngày (g)
        fat_target: Mục tiêu chất béo hàng ngày (g)
        carbs_target: Mục tiêu carbs hàng ngày (g)
        preferences: Sở thích ăn uống (chuỗi, phân cách bằng dấu phẩy)
        allergies: Dị ứng thực phẩm (chuỗi, phân cách bằng dấu phẩy)
        cuisine_style: Phong cách ẩm thực ưa thích
        use_ai: Sử dụng AI để tạo kế hoạch ăn uống
        ensure_diversity: Đảm bảo đa dạng món ăn, tránh trùng lặp
        use_tdee: Sử dụng TDEE của người dùng để điều chỉnh mục tiêu dinh dưỡng
        
    Returns:
        Dict[str, Any]: Kế hoạch ăn uống hàng tuần
    """
    try:
        # Nếu sử dụng TDEE, lấy thông tin người dùng từ Firestore
        if use_tdee:
            try:
                # Import tdee_nutrition_service
                from services.tdee_nutrition_service import tdee_nutrition_service
                
                # Import firestore_service
                from services.firestore_service import firestore_service
                
                # Lấy thông tin người dùng từ Firestore
                user_profile = firestore_service.get_user(user_id)
                
                if user_profile:
                    print(f"Đã tìm thấy thông tin người dùng {user_id}, điều chỉnh mục tiêu dinh dưỡng dựa trên TDEE")
                    
                    # Lấy mục tiêu dinh dưỡng từ profile người dùng
                    calories, protein, fat, carbs = tdee_nutrition_service.get_nutrition_targets_from_user_profile(user_profile)
                    
                    print(f"Mục tiêu dinh dưỡng dựa trên TDEE: calories={calories}, protein={protein}, fat={fat}, carbs={carbs}")
                    
                    # Cập nhật các giá trị mục tiêu
                    calories_target = calories
                    protein_target = protein
                    fat_target = fat
                    carbs_target = carbs
            except Exception as e:
                print(f"Lỗi khi lấy thông tin TDEE: {str(e)}")
                print("Sử dụng giá trị mặc định")
        
        # Đảm bảo calories không vượt quá 1500 nếu không có thông tin TDEE
        if not use_tdee and calories_target > 1500:
            print(f"Giới hạn calories từ {calories_target} xuống 1500")
            calories_target = 1500
            # Điều chỉnh các giá trị khác theo tỷ lệ
            protein_target = 90
            fat_target = 50
            carbs_target = 187.5
        
        # Tạo kế hoạch ăn uống
        print(f"Tạo kế hoạch ăn uống với mục tiêu: calories={calories_target}, protein={protein_target}, fat={fat_target}, carbs={carbs_target}")
        
        # Tạo kế hoạch ăn uống (giả sử đây là phần code hiện tại của bạn)
        meal_plan = create_meal_plan_with_ai(
            calories_target=calories_target,
            protein_target=protein_target,
            fat_target=fat_target,
            carbs_target=carbs_target,
            preferences=preferences,
            allergies=allergies,
            cuisine_style=cuisine_style
        ) if use_ai else create_meal_plan(
            calories_target=calories_target,
            protein_target=protein_target,
            fat_target=fat_target,
            carbs_target=carbs_target
        )
        
        # Thêm đoạn code mới: Đảm bảo đa dạng món ăn nếu được yêu cầu
        if ensure_diversity:
            print(f"🔄 Đang đa dạng hóa kế hoạch ăn cho người dùng {user_id}...")
            
            # Kiểm tra mức độ đa dạng hiện tại
            diversity_rate = MealDiversityService.check_meal_diversity(meal_plan)
            print(f"📊 Tỷ lệ trùng lặp trước khi đa dạng hóa: {diversity_rate:.2f}")
            
            # Đa dạng hóa kế hoạch ăn
            meal_plan = MealDiversityService.ensure_meal_diversity(meal_plan)
            
            # Kiểm tra lại mức độ đa dạng
            new_diversity_rate = MealDiversityService.check_meal_diversity(meal_plan)
            print(f"📊 Tỷ lệ trùng lặp sau khi đa dạng hóa: {new_diversity_rate:.2f}")
        
        # Lưu kế hoạch ăn uống vào Firestore
        # ... existing code ...
        
        return meal_plan
    except Exception as e:
        print(f"Error generating meal plan: {e}")
        raise
