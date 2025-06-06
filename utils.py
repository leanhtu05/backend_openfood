import random
from typing import List, Dict, Tuple
from models import Ingredient, NutritionInfo, Dish, Meal, DayMealPlan

# Vietnamese days of the week
DAYS_OF_WEEK = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

# Sample recipes data (in a real app, this would come from a database)
SAMPLE_RECIPES = {
    "breakfast": [
        {
            "name": "Bột yến mạch với chuối và hạt",
            "ingredients": [
                {"name": "yến mạch", "amount": "50g"},
                {"name": "chuối", "amount": "1 quả"},
                {"name": "hạt chia", "amount": "10g"},
                {"name": "sữa hạnh nhân", "amount": "200ml"}
            ],
            "preparation": "Nấu yến mạch với sữa hạnh nhân, thêm chuối thái lát và rắc hạt chia lên trên."
        },
        {
            "name": "Bánh mì nguyên cám kẹp trứng",
            "ingredients": [
                {"name": "bánh mì nguyên cám", "amount": "2 lát"},
                {"name": "trứng", "amount": "2 quả"},
                {"name": "rau bina", "amount": "20g"},
                {"name": "cà chua", "amount": "50g"}
            ],
            "preparation": "Chiên trứng, đặt lên bánh mì cùng với rau bina và cà chua thái lát."
        },
        {
            "name": "Sinh tố dâu với sữa chua",
            "ingredients": [
                {"name": "dâu tây", "amount": "100g"},
                {"name": "sữa chua", "amount": "150g"},
                {"name": "mật ong", "amount": "10g"},
                {"name": "hạt lanh", "amount": "5g"}
            ],
            "preparation": "Xay dâu tây với sữa chua và mật ong. Rắc hạt lanh lên trên khi phục vụ."
        },
        {
            "name": "Bánh pancake chuối",
            "ingredients": [
                {"name": "bột mì nguyên cám", "amount": "80g"},
                {"name": "chuối", "amount": "1 quả"},
                {"name": "trứng", "amount": "1 quả"},
                {"name": "sữa", "amount": "100ml"},
                {"name": "mật ong", "amount": "15g"}
            ],
            "preparation": "Trộn bột mì, trứng, sữa và chuối nghiền. Đổ từng muỗng vào chảo nóng, chiên vàng hai mặt. Phục vụ với mật ong."
        },
        {
            "name": "Cháo yến mạch với quả mọng",
            "ingredients": [
                {"name": "yến mạch", "amount": "50g"},
                {"name": "quả mọng hỗn hợp", "amount": "80g"},
                {"name": "sữa", "amount": "200ml"},
                {"name": "hạt óc chó", "amount": "15g"},
                {"name": "quế", "amount": "1 nhúm"}
            ],
            "preparation": "Nấu yến mạch với sữa, thêm quế. Khi chín, cho quả mọng và hạt óc chó lên trên."
        },
        {
            "name": "Bánh mì nướng bơ với trứng luộc",
            "ingredients": [
                {"name": "bánh mì", "amount": "2 lát"},
                {"name": "bơ", "amount": "15g"},
                {"name": "trứng", "amount": "2 quả"},
                {"name": "muối và tiêu", "amount": "1 nhúm"}
            ],
            "preparation": "Luộc trứng, nướng bánh mì và phết bơ. Thái trứng thành lát và đặt lên bánh mì."
        },
        {
            "name": "Sữa chua Hy Lạp với hạt và mật ong",
            "ingredients": [
                {"name": "sữa chua Hy Lạp", "amount": "200g"},
                {"name": "hạt bí ngô", "amount": "15g"},
                {"name": "hạt hướng dương", "amount": "15g"},
                {"name": "mật ong", "amount": "10g"}
            ],
            "preparation": "Cho sữa chua vào bát, rắc hạt bí ngô và hạt hướng dương lên trên, rưới mật ong."
        },
        {
            "name": "Bánh mì sandwich cá hồi xông khói",
            "ingredients": [
                {"name": "bánh mì", "amount": "2 lát"},
                {"name": "cá hồi xông khói", "amount": "50g"},
                {"name": "phô mai kem", "amount": "30g"},
                {"name": "dưa chuột", "amount": "50g"},
                {"name": "hành lá", "amount": "10g"}
            ],
            "preparation": "Phết phô mai kem lên bánh mì, xếp cá hồi xông khói, dưa chuột thái lát và hành lá thái nhỏ."
        },
        {
            "name": "Trứng khuấy với rau củ",
            "ingredients": [
                {"name": "trứng", "amount": "3 quả"},
                {"name": "ớt chuông", "amount": "50g"},
                {"name": "hành tây", "amount": "30g"},
                {"name": "cà chua", "amount": "50g"},
                {"name": "phô mai", "amount": "30g"}
            ],
            "preparation": "Xào hành tây, ớt chuông và cà chua. Đổ trứng đã khuấy vào, thêm phô mai và khuấy đều."
        },
        {
            "name": "Bánh waffle với trái cây tươi",
            "ingredients": [
                {"name": "bột waffle", "amount": "100g"},
                {"name": "trứng", "amount": "1 quả"},
                {"name": "sữa", "amount": "150ml"},
                {"name": "dâu tây", "amount": "50g"},
                {"name": "việt quất", "amount": "50g"},
                {"name": "si-rô cây phong", "amount": "20ml"}
            ],
            "preparation": "Trộn bột waffle với trứng và sữa. Nướng trong máy làm waffle. Phục vụ với trái cây tươi và si-rô cây phong."
        }
    ],
    "lunch": [
        {
            "name": "Salad gà nướng",
            "ingredients": [
                {"name": "ức gà", "amount": "150g"},
                {"name": "rau xà lách", "amount": "100g"},
                {"name": "cà chua bi", "amount": "50g"},
                {"name": "dầu ô liu", "amount": "10ml"},
                {"name": "nước cốt chanh", "amount": "5ml"}
            ],
            "preparation": "Nướng ức gà, thái lát. Trộn với rau xà lách, cà chua bi, dầu ô liu và nước cốt chanh."
        },
        {
            "name": "Cơm gạo lứt với đậu hũ và rau củ",
            "ingredients": [
                {"name": "gạo lứt", "amount": "100g"},
                {"name": "đậu hũ", "amount": "100g"},
                {"name": "bông cải xanh", "amount": "80g"},
                {"name": "cà rốt", "amount": "50g"},
                {"name": "dầu mè", "amount": "5ml"}
            ],
            "preparation": "Nấu gạo lứt. Xào đậu hũ với bông cải xanh và cà rốt, nêm gia vị và dầu mè. Phục vụ đậu hũ xào với cơm gạo lứt."
        },
        {
            "name": "Bún trộn rau thơm",
            "ingredients": [
                {"name": "bún", "amount": "150g"},
                {"name": "đậu hũ", "amount": "100g"},
                {"name": "giá đỗ", "amount": "50g"},
                {"name": "rau thơm hỗn hợp", "amount": "50g"},
                {"name": "nước mắm pha", "amount": "30ml"}
            ],
            "preparation": "Trụng bún, giá đỗ. Trộn với đậu hũ thái lát và rau thơm. Phục vụ kèm nước mắm pha."
        },
        {
            "name": "Cơm chiên rau củ",
            "ingredients": [
                {"name": "gạo", "amount": "150g"},
                {"name": "đậu Hà Lan", "amount": "50g"},
                {"name": "bắp", "amount": "50g"},
                {"name": "cà rốt", "amount": "50g"},
                {"name": "trứng", "amount": "1 quả"}
            ],
            "preparation": "Nấu cơm trước. Xào trứng với rau củ, thêm cơm và nêm gia vị. Xào đều tay đến khi thơm."
        },
        {
            "name": "Mì trộn kiểu Nhật",
            "ingredients": [
                {"name": "mì soba", "amount": "120g"},
                {"name": "nấm shiitake", "amount": "50g"},
                {"name": "cà rốt", "amount": "50g"},
                {"name": "đậu phụ", "amount": "80g"},
                {"name": "xì dầu", "amount": "15ml"},
                {"name": "dầu mè", "amount": "5ml"}
            ],
            "preparation": "Luộc mì soba. Xào nấm, cà rốt và đậu phụ, nêm với xì dầu. Trộn mì với hỗn hợp rau củ và dầu mè."
        },
        {
            "name": "Sandwich cá ngừ",
            "ingredients": [
                {"name": "bánh mì", "amount": "2 lát"},
                {"name": "cá ngừ đóng hộp", "amount": "100g"},
                {"name": "mayonnaise", "amount": "20g"},
                {"name": "hành tây", "amount": "30g"},
                {"name": "dưa chuột", "amount": "30g"}
            ],
            "preparation": "Trộn cá ngừ với mayonnaise, hành tây thái nhỏ. Đặt hỗn hợp lên bánh mì cùng với dưa chuột thái lát."
        },
        {
            "name": "Súp đậu lăng với rau củ",
            "ingredients": [
                {"name": "đậu lăng", "amount": "100g"},
                {"name": "cà rốt", "amount": "50g"},
                {"name": "cần tây", "amount": "30g"},
                {"name": "hành tây", "amount": "50g"},
                {"name": "nước dùng rau củ", "amount": "500ml"}
            ],
            "preparation": "Xào hành tây, cà rốt và cần tây. Thêm đậu lăng và nước dùng, nấu cho đến khi đậu lăng mềm."
        },
        {
            "name": "Salad quinoa với rau củ",
            "ingredients": [
                {"name": "quinoa", "amount": "100g"},
                {"name": "dưa chuột", "amount": "50g"},
                {"name": "cà chua", "amount": "50g"},
                {"name": "ớt chuông", "amount": "50g"},
                {"name": "dầu ô liu", "amount": "10ml"},
                {"name": "nước cốt chanh", "amount": "5ml"}
            ],
            "preparation": "Nấu quinoa, để nguội. Trộn với rau củ thái nhỏ, dầu ô liu và nước cốt chanh."
        },
        {
            "name": "Phở gà",
            "ingredients": [
                {"name": "bánh phở", "amount": "200g"},
                {"name": "thịt gà", "amount": "150g"},
                {"name": "hành lá", "amount": "20g"},
                {"name": "giá đỗ", "amount": "50g"},
                {"name": "nước dùng gà", "amount": "500ml"}
            ],
            "preparation": "Nấu nước dùng gà với các loại gia vị. Luộc thịt gà, xé nhỏ. Trụng bánh phở, cho vào tô cùng với thịt gà, giá đỗ, hành lá và chan nước dùng."
        },
        {
            "name": "Bún riêu cua",
            "ingredients": [
                {"name": "bún", "amount": "200g"},
                {"name": "thịt cua", "amount": "100g"},
                {"name": "đậu hũ", "amount": "50g"},
                {"name": "cà chua", "amount": "100g"},
                {"name": "rau sống", "amount": "50g"}
            ],
            "preparation": "Nấu nước dùng cua với cà chua. Trụng bún, cho vào tô cùng với thịt cua, đậu hũ và rau sống. Chan nước dùng lên trên."
        }
    ],
    "dinner": [
        {
            "name": "Cá hồi nướng với khoai lang và rau củ",
            "ingredients": [
                {"name": "cá hồi", "amount": "150g"},
                {"name": "khoai lang", "amount": "100g"},
                {"name": "măng tây", "amount": "80g"},
                {"name": "dầu ô liu", "amount": "10ml"}
            ],
            "preparation": "Nướng cá hồi với dầu ô liu. Hấp khoai lang và măng tây. Phục vụ cùng nhau."
        },
        {
            "name": "Súp đậu lăng với rau củ",
            "ingredients": [
                {"name": "đậu lăng", "amount": "80g"},
                {"name": "cà rốt", "amount": "50g"},
                {"name": "hành tây", "amount": "30g"},
                {"name": "tỏi", "amount": "5g"},
                {"name": "nước dùng rau củ", "amount": "300ml"}
            ],
            "preparation": "Phi thơm tỏi và hành. Thêm cà rốt, đậu lăng và nước dùng rau củ. Nấu cho đến khi đậu lăng mềm."
        },
        {
            "name": "Gà kho gừng",
            "ingredients": [
                {"name": "đùi gà", "amount": "200g"},
                {"name": "gừng", "amount": "20g"},
                {"name": "hành tây", "amount": "50g"},
                {"name": "nước tương", "amount": "15ml"},
                {"name": "cơm", "amount": "150g"}
            ],
            "preparation": "Kho gà với gừng, hành tây và nước tương. Nấu nhỏ lửa đến khi gà mềm. Phục vụ với cơm."
        },
        {
            "name": "Canh bí đỏ thịt bò",
            "ingredients": [
                {"name": "bí đỏ", "amount": "200g"},
                {"name": "thịt bò", "amount": "100g"},
                {"name": "hành tây", "amount": "50g"},
                {"name": "nước dùng", "amount": "400ml"}
            ],
            "preparation": "Thái bí đỏ và hành tây. Xào thịt bò, thêm rau củ và nước dùng. Nấu đến khi bí đỏ mềm."
        },
        {
            "name": "Cá kho cà chua",
            "ingredients": [
                {"name": "cá rô phi", "amount": "200g"},
                {"name": "cà chua", "amount": "100g"},
                {"name": "hành tím", "amount": "30g"},
                {"name": "nước mắm", "amount": "15ml"},
                {"name": "đường", "amount": "10g"}
            ],
            "preparation": "Phi thơm hành tím, thêm cà chua xào mềm. Đặt cá vào, thêm nước mắm và đường. Kho nhỏ lửa đến khi cá chín mềm."
        },
        {
            "name": "Thịt heo nướng với rau củ",
            "ingredients": [
                {"name": "thịt heo thăn", "amount": "200g"},
                {"name": "khoai tây", "amount": "100g"},
                {"name": "cà rốt", "amount": "50g"},
                {"name": "hành tây", "amount": "50g"},
                {"name": "dầu ô liu", "amount": "15ml"}
            ],
            "preparation": "Ướp thịt heo với gia vị, nướng chín. Xào khoai tây, cà rốt và hành tây với dầu ô liu. Phục vụ cùng nhau."
        },
        {
            "name": "Cơm chiên hải sản",
            "ingredients": [
                {"name": "gạo", "amount": "150g"},
                {"name": "tôm", "amount": "100g"},
                {"name": "mực", "amount": "50g"},
                {"name": "đậu Hà Lan", "amount": "30g"},
                {"name": "trứng", "amount": "1 quả"}
            ],
            "preparation": "Nấu cơm trước. Xào hải sản với trứng, thêm cơm và đậu Hà Lan, nêm gia vị. Xào đều tay đến khi thơm."
        },
        {
            "name": "Bún chả",
            "ingredients": [
                {"name": "thịt heo", "amount": "200g"},
                {"name": "bún", "amount": "150g"},
                {"name": "rau sống", "amount": "100g"},
                {"name": "nước mắm pha", "amount": "50ml"}
            ],
            "preparation": "Ướp thịt heo với gia vị, nướng chín. Trụng bún, phục vụ với rau sống và nước mắm pha."
        },
        {
            "name": "Đậu hũ sốt cà chua",
            "ingredients": [
                {"name": "đậu hũ", "amount": "200g"},
                {"name": "cà chua", "amount": "150g"},
                {"name": "hành tây", "amount": "50g"},
                {"name": "tỏi", "amount": "10g"},
                {"name": "cơm", "amount": "150g"}
            ],
            "preparation": "Chiên đậu hũ vàng. Phi thơm tỏi và hành tây, thêm cà chua xào mềm. Cho đậu hũ vào, nêm gia vị. Phục vụ với cơm."
        },
        {
            "name": "Cá thu kho dứa",
            "ingredients": [
                {"name": "cá thu", "amount": "200g"},
                {"name": "dứa", "amount": "100g"},
                {"name": "hành tây", "amount": "50g"},
                {"name": "nước dừa", "amount": "100ml"},
                {"name": "cơm", "amount": "150g"}
            ],
            "preparation": "Kho cá thu với dứa, hành tây và nước dừa. Nấu nhỏ lửa đến khi cá chín mềm. Phục vụ với cơm."
        }
    ]
}

def calculate_meal_nutrition(dishes: List[Dish]) -> NutritionInfo:
    """
    Calculate the total nutrition for a meal from its dishes.
    
    Args:
        dishes: List of Dish objects
        
    Returns:
        NutritionInfo with total nutritional values
    """
    total = NutritionInfo(calories=0, protein=0, fat=0, carbs=0)
    
    for dish in dishes:
        total.calories += dish.nutrition.calories
        total.protein += dish.nutrition.protein
        total.fat += dish.nutrition.fat
        total.carbs += dish.nutrition.carbs
    
    return total

def calculate_day_nutrition(breakfast: Meal, lunch: Meal, dinner: Meal) -> NutritionInfo:
    """
    Calculate total nutrition for a day.
    
    Args:
        breakfast: Breakfast meal
        lunch: Lunch meal
        dinner: Dinner meal
        
    Returns:
        NutritionInfo object with total nutrition
    """
    # Validate input meals to avoid None values
    breakfast_nutrition = breakfast.nutrition if breakfast and breakfast.nutrition else NutritionInfo(calories=0, protein=0, fat=0, carbs=0)
    lunch_nutrition = lunch.nutrition if lunch and lunch.nutrition else NutritionInfo(calories=0, protein=0, fat=0, carbs=0)
    dinner_nutrition = dinner.nutrition if dinner and dinner.nutrition else NutritionInfo(calories=0, protein=0, fat=0, carbs=0)
    
    # Calculate totals
    total_calories = breakfast_nutrition.calories + lunch_nutrition.calories + dinner_nutrition.calories
    total_protein = breakfast_nutrition.protein + lunch_nutrition.protein + dinner_nutrition.protein
    total_fat = breakfast_nutrition.fat + lunch_nutrition.fat + dinner_nutrition.fat
    total_carbs = breakfast_nutrition.carbs + lunch_nutrition.carbs + dinner_nutrition.carbs
    
    # Log the calculation for debugging
    print(f"Day nutrition calculation:")
    print(f"  Breakfast: cal={breakfast_nutrition.calories:.1f}, p={breakfast_nutrition.protein:.1f}, f={breakfast_nutrition.fat:.1f}, c={breakfast_nutrition.carbs:.1f}")
    print(f"  Lunch: cal={lunch_nutrition.calories:.1f}, p={lunch_nutrition.protein:.1f}, f={lunch_nutrition.fat:.1f}, c={lunch_nutrition.carbs:.1f}")
    print(f"  Dinner: cal={dinner_nutrition.calories:.1f}, p={dinner_nutrition.protein:.1f}, f={dinner_nutrition.fat:.1f}, c={dinner_nutrition.carbs:.1f}")
    print(f"  TOTAL: cal={total_calories:.1f}, p={total_protein:.1f}, f={total_fat:.1f}, c={total_carbs:.1f}")
    
    return NutritionInfo(
        calories=total_calories,
        protein=total_protein,
        fat=total_fat,
        carbs=total_carbs
    )

def distribute_nutrition_targets(
    total_calories: int, 
    total_protein: int, 
    total_fat: int, 
    total_carbs: int
) -> Dict[str, Dict[str, float]]:
    """
    Distribute daily nutrition targets across meals.
    
    Args:
        total_calories: Total daily calories target
        total_protein: Total daily protein target (g)
        total_fat: Total daily fat target (g)
        total_carbs: Total daily carbs target (g)
        
    Returns:
        Dictionary with meal targets
    """
    # Ensure total_calories doesn't exceed 1500
    if total_calories > 3000:
        print(f"WARNING: Reducing calories target from {total_calories} to 3000")
        # Adjust other nutrients proportionally
        reduction_factor = 3000 / total_calories
        total_calories = 3000
        total_protein = int(total_protein * reduction_factor)
        total_fat = int(total_fat * reduction_factor)
        total_carbs = int(total_carbs * reduction_factor)
    
    # Tỷ lệ phân bổ cho từng bữa ăn
    breakfast_ratio = 0.25  # Bữa sáng: 25% tổng calo
    lunch_ratio = 0.40      # Bữa trưa: 40% tổng calo
    dinner_ratio = 0.35     # Bữa tối: 35% tổng calo
    
    # Calculate targets for each meal
    breakfast_calories = int(total_calories * breakfast_ratio)
    breakfast_protein = int(total_protein * breakfast_ratio)
    breakfast_fat = int(total_fat * breakfast_ratio)
    breakfast_carbs = int(total_carbs * breakfast_ratio)
    
    lunch_calories = int(total_calories * lunch_ratio)
    lunch_protein = int(total_protein * lunch_ratio)
    lunch_fat = int(total_fat * lunch_ratio)
    lunch_carbs = int(total_carbs * lunch_ratio)
    
    dinner_calories = total_calories - breakfast_calories - lunch_calories
    dinner_protein = total_protein - breakfast_protein - lunch_protein
    dinner_fat = total_fat - breakfast_fat - lunch_fat
    dinner_carbs = total_carbs - breakfast_carbs - lunch_carbs
    
    return {
        "breakfast": {
            "calories": breakfast_calories,
            "protein": breakfast_protein,
            "fat": breakfast_fat,
            "carbs": breakfast_carbs
        },
        "lunch": {
            "calories": lunch_calories,
            "protein": lunch_protein,
            "fat": lunch_fat,
            "carbs": lunch_carbs
        },
        "dinner": {
            "calories": dinner_calories,
            "protein": dinner_protein,
            "fat": dinner_fat,
            "carbs": dinner_carbs
        }
    }

def adjust_dish_portions(
    dishes: List[Dict], 
    target_calories: float,
    target_protein: float,
    target_fat: float,
    target_carbs: float
) -> List[Dict]:
    """
    Adjust portion sizes to meet nutritional targets.
    This is a simplified implementation.
    
    Args:
        dishes: List of dish dictionaries
        target_calories: Target calories for the meal
        target_protein: Target protein for the meal
        target_fat: Target fat for the meal
        target_carbs: Target carbs for the meal
        
    Returns:
        Adjusted dishes
    """
    if not dishes:
        return dishes
        
    # Calculate current totals
    current_calories = sum(dish["nutrition"]["calories"] for dish in dishes)
    current_protein = sum(dish["nutrition"]["protein"] for dish in dishes)
    current_fat = sum(dish["nutrition"]["fat"] for dish in dishes)
    current_carbs = sum(dish["nutrition"]["carbs"] for dish in dishes)
    
    # Avoid division by zero
    if current_calories <= 0:
        print("WARNING: Current calories is zero or negative. Using default values.")
        for dish in dishes:
            dish["nutrition"]["calories"] = target_calories / len(dishes)
            dish["nutrition"]["protein"] = target_protein / len(dishes)
            dish["nutrition"]["fat"] = target_fat / len(dishes)
            dish["nutrition"]["carbs"] = target_carbs / len(dishes)
        return dishes
    
    # Calculate scaling factors (prioritize calories)
    calorie_factor = target_calories / current_calories
    
    # Log adjustment details
    print(f"Adjusting dish portions: current calories={current_calories:.1f}, target={target_calories:.1f}, factor={calorie_factor:.2f}")
    
    # Limit extreme scaling to prevent unreasonable portion sizes
    if calorie_factor > 3.0:
        print(f"WARNING: Scaling factor {calorie_factor:.2f} is too high. Limiting to 3.0")
        calorie_factor = 3.0
    elif calorie_factor < 0.33:
        print(f"WARNING: Scaling factor {calorie_factor:.2f} is too low. Limiting to 0.33")
        calorie_factor = 0.33
    
    # Apply scaling to all dishes
    for dish in dishes:
        for nutrient in ["calories", "protein", "fat", "carbs"]:
            dish["nutrition"][nutrient] *= calorie_factor
    
    # Verify the adjustment worked correctly
    adjusted_calories = sum(dish["nutrition"]["calories"] for dish in dishes)
    adjusted_protein = sum(dish["nutrition"]["protein"] for dish in dishes)
    adjusted_fat = sum(dish["nutrition"]["fat"] for dish in dishes)
    adjusted_carbs = sum(dish["nutrition"]["carbs"] for dish in dishes)
    
    print(f"After adjustment: calories={adjusted_calories:.1f}, protein={adjusted_protein:.1f}, fat={adjusted_fat:.1f}, carbs={adjusted_carbs:.1f}")
    
    # If still significantly off target, make a second adjustment for precision
    calories_diff_percent = abs(adjusted_calories - target_calories) / target_calories * 100
    if calories_diff_percent > 5:  # If more than 5% off target
        correction_factor = target_calories / adjusted_calories
        print(f"Making secondary adjustment with correction factor {correction_factor:.2f}")
        
        for dish in dishes:
            for nutrient in ["calories", "protein", "fat", "carbs"]:
                dish["nutrition"][nutrient] *= correction_factor
    
    return dishes

def generate_random_dishes(meal_type: str, count: int = 1, used_dishes: List[str] = None, day_index: int = -1) -> List[Dict]:
    """
    Generate random dishes for a meal type, avoiding previously used dishes if possible.
    
    Args:
        meal_type: Type of meal (breakfast, lunch, dinner)
        count: Number of dishes to generate
        used_dishes: List of dish names that have already been used
        day_index: Index of the day in the week (0-6) for adding variety
        
    Returns:
        List of dish dictionaries
    """
    # Map tiếng Việt sang tiếng Anh
    meal_type_map = {
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
    
    # Log cho debugging
    print(f"Generating random dishes for meal type: '{meal_type}', day index: {day_index}")
    if used_dishes:
        print(f"Avoiding previously used dishes: {used_dishes}")
    
    # Chuyển đổi meal_type sang dạng chuẩn
    normalized_meal_type = meal_type_map.get(meal_type.lower(), "breakfast")
    print(f"Normalized to: '{normalized_meal_type}'")
    
    # Lấy món ăn từ SAMPLE_RECIPES
    available_dishes = SAMPLE_RECIPES.get(normalized_meal_type, [])
    print(f"Available dishes: {len(available_dishes)}")
    
    if len(available_dishes) == 0:
        print("WARNING: No dishes available for this meal type!")
        # Fallback to breakfast if empty
        available_dishes = SAMPLE_RECIPES.get("breakfast", [])
    
    # Tạo bản sao của các món ăn để tránh thay đổi dữ liệu gốc
    available_dishes = [dish.copy() for dish in available_dishes]
    
    # Filter out previously used dishes if possible
    unused_dishes = available_dishes
    if used_dishes:
        unused_dishes = [dish for dish in available_dishes if dish["name"] not in used_dishes]
        print(f"Unused dishes after filtering: {len(unused_dishes)}")
        
        # If we've used all dishes already or can't avoid repeats due to small selection
        if len(unused_dishes) < count:
            print("WARNING: Not enough unique dishes available, some dishes may repeat")
            # Use all available dishes but prioritize unused ones
            unused_dishes = available_dishes
            
            # Nếu buộc phải dùng lại món đã dùng, thêm biến thể vào tên
            for dish in unused_dishes:
                if dish["name"] in used_dishes:
                    variation = f" (Biến thể {random.randint(1, 100)})"
                    dish["name"] = dish["name"] + variation
    
    # Sử dụng day_index để tạo sự đa dạng
    if day_index >= 0 and day_index < 7:
        # Sử dụng day_index để xáo trộn danh sách món ăn theo một cách nhất quán cho mỗi ngày
        # nhưng khác nhau giữa các ngày
        random.seed(day_index * 100 + len(meal_type) + hash(normalized_meal_type) % 1000)
        random.shuffle(unused_dishes)
        
        # Thêm biến thể vào tên món ăn dựa trên ngày để tránh trùng lặp
        day_name = DAYS_OF_WEEK[day_index] if day_index < len(DAYS_OF_WEEK) else f"Ngày {day_index+1}"
        for dish in unused_dishes:
            if not day_name in dish["name"]:
                dish["name"] = f"{dish['name']} ({day_name})"
        
        # Đặt lại random seed sau khi sử dụng
        random.seed()
    
    # Lấy ngẫu nhiên món ăn
    if len(unused_dishes) <= count:
        # If we don't have enough, use all available and possibly add some from other meal types
        selected_dishes = unused_dishes.copy()
        remaining = count - len(selected_dishes)
        
        if remaining > 0:
            # Get dishes from other meal types to avoid repeats
            other_types = [t for t in SAMPLE_RECIPES.keys() if t != normalized_meal_type]
            other_dishes = []
            for other_type in other_types:
                other_dishes.extend([dish.copy() for dish in SAMPLE_RECIPES[other_type]])
            
            # Avoid used dishes in other types too
            if used_dishes:
                other_dishes = [dish for dish in other_dishes if dish["name"] not in used_dishes]
            
            # Thêm biến thể vào tên món ăn từ loại bữa khác
            for dish in other_dishes:
                dish["name"] = f"{dish['name']} (Từ {normalized_meal_type})"
            
            # Add random dishes from other types
            if other_dishes:
                # Sử dụng day_index để xáo trộn danh sách
                if day_index >= 0:
                    random.seed(day_index * 200 + hash(normalized_meal_type) % 1000)
                    random.shuffle(other_dishes)
                    random.seed()
                
                additional_dishes = other_dishes[:min(remaining, len(other_dishes))]
                selected_dishes.extend(additional_dishes)
    else:
        # Randomly sample if we have enough
        selected_dishes = random.sample(unused_dishes, count)
    
    # Thêm thông tin dinh dưỡng nếu cần
    for dish in selected_dishes:
        if "nutrition" not in dish:
            # Thêm biến động nhỏ vào giá trị dinh dưỡng dựa trên day_index
            variation = 1.0
            if day_index >= 0:
                variation = 0.9 + (day_index * 0.05)  # Biến động từ 0.9 đến 1.2
            
            dish["nutrition"] = {
                "calories": int(300 * variation),  # Giảm xuống từ 400
                "protein": int(15 * variation),    # Giảm xuống từ 20
                "fat": int(10 * variation),        # Giảm xuống từ 15
                "carbs": int(35 * variation)       # Giảm xuống từ 45
            }
        
        # Thêm ngày vào tên món ăn để tạo sự đa dạng nếu cần và chưa có
        if day_index >= 0:
            day_name = DAYS_OF_WEEK[day_index] if day_index < len(DAYS_OF_WEEK) else f"Ngày {day_index+1}"
            if "name" in dish and not day_name in dish["name"]:
                dish["name"] = f"{dish['name']} ({day_name})"
    
    # Log kết quả
    dish_names = [dish["name"] for dish in selected_dishes]
    print(f"Selected dishes: {dish_names}")
            
    return selected_dishes

def format_nutrition_value(value, precision=1):
    """
    Làm tròn giá trị dinh dưỡng với độ chính xác phù hợp.
    
    Args:
        value: Giá trị cần làm tròn
        precision: Số chữ số sau dấu phẩy (mặc định: 1)
    
    Returns:
        Giá trị đã làm tròn phù hợp
    """
    if value is None:
        return 0

    # Chuyển về float để đảm bảo
    try:
        value = float(value)
    except (TypeError, ValueError):
        return 0
    
    # Làm tròn theo logic:
    # - Giá trị < 1: giữ 2 số thập phân
    # - Giá trị 1-10: giữ 1 số thập phân
    # - Giá trị > 10: làm tròn thành số nguyên
    if value < 1:
        return round(value, 2)
    elif value < 10:
        return round(value, 1)
    else:
        return int(round(value))
