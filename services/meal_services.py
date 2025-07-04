from typing import List, Dict, Optional
import random
from models import (
    NutritionTarget, ReplaceDayRequest, DayMealPlan, WeeklyMealPlan,
    Dish, Meal, NutritionInfo, Ingredient, DishType, VietnamRegion
)
from utils import (
    DAYS_OF_WEEK, SAMPLE_RECIPES, calculate_meal_nutrition,
    calculate_day_nutrition, distribute_nutrition_targets,
    adjust_dish_portions, generate_random_dishes, format_nutrition_value
)
from services.vietnamese_meal_service import vietnamese_meal_service

# 🔧 FIX: Import Vietnamese dish generator để thay thế SAMPLE_RECIPES
try:
    from services.vietnamese_dish_generator import vietnamese_dish_generator
    VIETNAMESE_GENERATOR_AVAILABLE = True
    print("✅ Vietnamese dish generator imported successfully")
except ImportError as e:
    print(f"⚠️ Vietnamese dish generator not available: {e}")
    VIETNAMESE_GENERATOR_AVAILABLE = False
from nutritionix import get_nutrition_fallback
from nutritionix_optimized import nutritionix_optimized_api
from services.meal_tracker import (
    reset_tracker, reset_meal_type, add_dish,
    is_dish_used, get_used_dishes
)
# YouTube functionality removed - no longer adding video URLs
# Import hàm process_preparation_steps từ preparation_utils
from services.preparation_utils import process_preparation_steps
import config
from config import Config

# Import biến used_dishes_tracker để tương thích ngược
from services.meal_tracker import used_dishes_tracker

# Import Groq integration
try:
    from groq_integration import groq_service  # Enhanced version  # Fixed version
    AI_SERVICE = groq_service
    AI_AVAILABLE = groq_service.available
except ImportError:
    # Không có dịch vụ AI
    AI_SERVICE = None
    AI_AVAILABLE = False
    print("WARNING: Groq integration not available")

# Sử dụng phiên bản API đã tối ưu
nutritionix_api = nutritionix_optimized_api

def determine_dish_type(dish_name: str) -> str:
    """
    Xác định loại món dựa trên tên món ăn.
    
    Args:
        dish_name: Tên món ăn
        
    Returns:
        Loại món ăn
    """
    dish_name_lower = dish_name.lower()
    
    # Xác định món súp/canh
    if any(keyword in dish_name_lower for keyword in ['súp', 'canh', 'soup']):
        return DishType.SOUP
    
    # Xác định món tráng miệng
    if any(keyword in dish_name_lower for keyword in ['chè', 'bánh', 'dessert', 'tráng miệng', 'ngọt', 'trái cây']):
        if 'bánh mì' in dish_name_lower:  # Bánh mì là món chính
            return DishType.MAIN
        return DishType.DESSERT
    
    # Xác định món khai vị
    if any(keyword in dish_name_lower for keyword in ['khai vị', 'appetizer', 'salad', 'gỏi', 'cuốn']):
        return DishType.APPETIZER
    
    # Xác định món phụ
    if any(keyword in dish_name_lower for keyword in ['xào', 'luộc', 'hấp', 'kho', 'rau']):
        # Nếu có từ chính như cơm, bún, phở thì vẫn là món chính
        if any(main in dish_name_lower for main in ['cơm', 'bún', 'phở', 'mì', 'miến', 'cháo']):
            return DishType.MAIN
        return DishType.SIDE
    
    # Mặc định là món chính
    return DishType.MAIN

def determine_region(dish_name: str, user_data: dict = None) -> str:
    """
    Xác định vùng miền của món ăn dựa trên tên và thông tin người dùng.
    
    Args:
        dish_name: Tên món ăn
        user_data: Thông tin người dùng
        
    Returns:
        Vùng miền của món ăn
    """
    dish_name_lower = dish_name.lower()
    
    # Ưu tiên xác định từ profile người dùng nếu có
    if user_data and 'region' in user_data:
        user_region = user_data.get('region', '').lower()
        if 'bắc' in user_region or 'north' in user_region:
            return VietnamRegion.NORTH
        elif 'trung' in user_region or 'central' in user_region:
            return VietnamRegion.CENTRAL
        elif 'nam' in user_region or 'south' in user_region:
            return VietnamRegion.SOUTH
        elif 'tây nguyên' in user_region or 'highland' in user_region:
            return VietnamRegion.HIGHLANDER
    
    # Xác định từ tên món ăn
    # Món miền Bắc
    if any(keyword in dish_name_lower for keyword in ['bắc', 'hà nội', 'thái bình', 'phở', 'bún chả', 'chả cá', 'bún thang']):
        return VietnamRegion.NORTH
    
    # Món miền Trung
    if any(keyword in dish_name_lower for keyword in ['huế', 'đà nẵng', 'quảng', 'miền trung', 'bún bò', 'cơm hến', 'bánh xèo miền trung']):
        return VietnamRegion.CENTRAL
    
    # Món miền Nam
    if any(keyword in dish_name_lower for keyword in ['sài gòn', 'nam', 'hồ chí minh', 'hủ tiếu', 'bún mắm', 'cá lóc', 'cơm tấm']):
        return VietnamRegion.SOUTH
    
    # Món Tây Nguyên
    if any(keyword in dish_name_lower for keyword in ['tây nguyên', 'buôn', 'đắk', 'gia lai', 'kon tum', 'thịt rừng', 'cơm lam']):
        return VietnamRegion.HIGHLANDER
    
    # Món nước ngoài
    if any(keyword in dish_name_lower for keyword in ['pizza', 'pasta', 'sushi', 'kimchi', 'burger', 'taco', 'spaghetti']):
        return VietnamRegion.FOREIGN
    
    # Mặc định là miền Bắc nếu không xác định được
    return VietnamRegion.NORTH

def generate_dish(recipe_dict: Dict, user_data: Dict = None) -> Dish:
    """
    Generate a Dish object from a recipe dictionary.
    
    Args:
        recipe_dict: Dictionary with dish recipe information
        user_data: Thông tin người dùng để xác định vùng miền
        
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

        # 🔧 FIX: Enhanced fallback nutrition calculation
        dish_nutrition = NutritionInfo(calories=0, protein=0, fat=0, carbs=0)

        # Try to calculate from Vietnamese nutrition database first
        dish_name = recipe_dict.get("name", "").lower()
        from vietnamese_nutrition_database import get_dish_nutrition

        vietnamese_nutrition = get_dish_nutrition(dish_name)
        if vietnamese_nutrition:
            print(f"✅ Found Vietnamese nutrition data for '{dish_name}': {vietnamese_nutrition['calories']} kcal")
            dish_nutrition = NutritionInfo(
                calories=vietnamese_nutrition["calories"],
                protein=vietnamese_nutrition["protein"],
                fat=vietnamese_nutrition["fat"],
                carbs=vietnamese_nutrition["carbs"]
            )
        else:
            # Fallback: Calculate nutrition from ingredients
            print(f"⚠️ No Vietnamese nutrition data for '{dish_name}', calculating from ingredients...")
            for ingredient in ingredients:
                try:
                    ing_nutrition = get_nutrition_fallback(ingredient.name, ingredient.amount)
                    dish_nutrition.calories += ing_nutrition.calories
                    dish_nutrition.protein += ing_nutrition.protein
                    dish_nutrition.fat += ing_nutrition.fat
                    dish_nutrition.carbs += ing_nutrition.carbs
                except Exception as ing_error:
                    print(f"Error processing ingredient '{ingredient.name}': {str(ing_error)}")

            # 🔧 FIX: Sử dụng dữ liệu thực tế từ database thay vì tạo giá trị tối thiểu ảo
            if dish_nutrition.calories < 50:  # If calories too low
                print(f"⚠️ Calculated calories too low ({dish_nutrition.calories}), searching for similar dishes...")

                # Tìm món ăn tương tự trong database
                from vietnamese_nutrition_database import VIETNAMESE_DISHES_NUTRITION

                similar_dish = None
                dish_keywords = dish_name.split()

                # Tìm món có từ khóa tương tự
                for db_dish_name, db_nutrition in VIETNAMESE_DISHES_NUTRITION.items():
                    for keyword in dish_keywords:
                        if keyword.lower() in db_dish_name.lower():
                            similar_dish = db_nutrition
                            print(f"✅ Found similar dish '{db_dish_name}' with {db_nutrition['calories']} kcal")
                            break
                    if similar_dish:
                        break

                if similar_dish:
                    # Sử dụng dữ liệu thực tế từ món tương tự
                    dish_nutrition = NutritionInfo(
                        calories=similar_dish["calories"],
                        protein=similar_dish["protein"],
                        fat=similar_dish["fat"],
                        carbs=similar_dish["carbs"]
                    )
                    print(f"✅ Applied real nutrition data: {similar_dish['calories']} kcal")
                else:
                    # Fallback: Sử dụng món phổ biến nhất phù hợp với meal type
                    fallback_dishes = {
                        "sáng": VIETNAMESE_DISHES_NUTRITION.get("bánh mì", {"calories": 320, "protein": 18, "fat": 12, "carbs": 35}),
                        "trưa": VIETNAMESE_DISHES_NUTRITION.get("cơm tấm", {"calories": 520, "protein": 28.5, "fat": 18.2, "carbs": 65}),
                        "tối": VIETNAMESE_DISHES_NUTRITION.get("phở bò", {"calories": 420, "protein": 25.3, "fat": 12.2, "carbs": 55})
                    }

                    # Xác định meal type từ context
                    meal_context = "trưa"  # default
                    if any(word in dish_name.lower() for word in ["sáng", "breakfast"]):
                        meal_context = "sáng"
                    elif any(word in dish_name.lower() for word in ["tối", "dinner"]):
                        meal_context = "tối"

                    fallback_nutrition = fallback_dishes[meal_context]
                    dish_nutrition = NutritionInfo(
                        calories=fallback_nutrition["calories"],
                        protein=fallback_nutrition["protein"],
                        fat=fallback_nutrition["fat"],
                        carbs=fallback_nutrition["carbs"]
                    )
                    print(f"✅ Applied fallback real nutrition for {meal_context}: {fallback_nutrition['calories']} kcal")

        # 🔧 FIX: Final safety check với thông báo rõ ràng về độ tin cậy
        if dish_nutrition.calories < 50:
            print("🚨 All nutrition calculation methods failed.")
            print("⚠️ WARNING: Using estimated values - NOT VERIFIED NUTRITION DATA")
            print("📋 Recommendation: Verify nutrition information with official sources")

            # Sử dụng giá trị ước tính với disclaimer rõ ràng
            dish_nutrition = NutritionInfo(
                calories=300,  # Estimated - needs verification
                protein=18,    # Estimated - needs verification
                fat=10,        # Estimated - needs verification
                carbs=35       # Estimated - needs verification
            )

            # Thêm disclaimer vào recipe
            if "description" not in recipe_dict:
                recipe_dict["description"] = ""
            recipe_dict["description"] += " ⚠️ Thông tin dinh dưỡng là ước tính, cần xác minh với chuyên gia dinh dưỡng."
    
    # 🔧 FIX: Xác minh dữ liệu dinh dưỡng trước khi sử dụng
    try:
        from services.nutrition_verification_service import nutrition_verification_service

        nutrition_dict = {
            "calories": dish_nutrition.calories,
            "protein": dish_nutrition.protein,
            "fat": dish_nutrition.fat,
            "carbs": dish_nutrition.carbs
        }

        verification_result = nutrition_verification_service.verify_dish_nutrition(
            recipe_dict.get("name", "Unknown dish"),
            nutrition_dict
        )

        print(f"🔍 Nutrition verification: {verification_result.source}")
        print(f"📊 Confidence: {verification_result.confidence_score:.2f}")

        if verification_result.warnings:
            print(f"⚠️ Warnings: {verification_result.warnings}")

        # Thêm thông tin verification vào description
        if "description" not in recipe_dict:
            recipe_dict["description"] = ""

        if verification_result.is_verified:
            recipe_dict["description"] += f" ✅ Dữ liệu dinh dưỡng đã xác minh ({verification_result.source})"
        else:
            recipe_dict["description"] += f" ⚠️ Dữ liệu dinh dưỡng chưa xác minh (Confidence: {verification_result.confidence_score:.1f})"

    except Exception as e:
        print(f"❌ Nutrition verification failed: {e}")
        if "description" not in recipe_dict:
            recipe_dict["description"] = ""
        recipe_dict["description"] += " ⚠️ Không thể xác minh dữ liệu dinh dưỡng"

    # Format nutrition values
    dish_nutrition.calories = format_nutrition_value(dish_nutrition.calories)
    dish_nutrition.protein = format_nutrition_value(dish_nutrition.protein)
    dish_nutrition.fat = format_nutrition_value(dish_nutrition.fat)
    dish_nutrition.carbs = format_nutrition_value(dish_nutrition.carbs)

    print(f"Final dish nutrition: cal={dish_nutrition.calories}, protein={dish_nutrition.protein}, fat={dish_nutrition.fat}, carbs={dish_nutrition.carbs}")
    
    # Xác định loại món và vùng miền
    dish_name = recipe_dict.get("name", "Món ăn không tên")
    dish_type = recipe_dict.get("dish_type", determine_dish_type(dish_name))
    region = recipe_dict.get("region", determine_region(dish_name, user_data))
    
    # Lấy URL hình ảnh nếu có
    image_url = recipe_dict.get("image_url", None)
    
    # Lấy hướng dẫn chế biến
    preparation_raw = recipe_dict.get("preparation", "Không có hướng dẫn chi tiết.")
    
    # SỬA Ở ĐÂY: Chuyển đổi chuỗi thành danh sách các bước sử dụng hàm process_preparation_steps
    preparation_list = process_preparation_steps(preparation_raw)
    print(f"Processed preparation steps: {len(preparation_list)} steps")
    
    # Khởi tạo các biến mới
    preparation_time = None
    health_benefits = None
    
    # Truy cập biến USE_ENHANCED_DISH_INFO từ đối tượng config
    use_enhanced_info = config.config.USE_ENHANCED_DISH_INFO
    
    # Chỉ thêm thông tin preparation_time và health_benefits nếu được bật trong cấu hình
    if use_enhanced_info:
        # Lấy hoặc tính toán preparation_time nếu có
        preparation_time = recipe_dict.get("preparation_time", None)
        if not preparation_time:
            # Tạo thời gian nấu mặc định dựa trên độ phức tạp của món ăn
            steps_count = len(preparation_list)
            if steps_count <= 3:
                preparation_time = "15-20 phút"
            elif steps_count <= 5:
                preparation_time = "30-40 phút"
            else:
                preparation_time = "45-60 phút"
        
        # Lấy hoặc tạo lợi ích sức khỏe
        health_benefits_raw = recipe_dict.get("health_benefits", None)
        if health_benefits_raw:
            # Nếu là list, giữ nguyên
            if isinstance(health_benefits_raw, list):
                health_benefits = health_benefits_raw
            # Nếu là string, tách thành list bằng dấu xuống dòng hoặc dấu phẩy
            elif isinstance(health_benefits_raw, str):
                if "\n" in health_benefits_raw:
                    health_benefits = [benefit.strip() for benefit in health_benefits_raw.split("\n") if benefit.strip()]
                elif "," in health_benefits_raw:
                    health_benefits = [benefit.strip() for benefit in health_benefits_raw.split(",") if benefit.strip()]
                elif "." in health_benefits_raw:
                    health_benefits = [benefit.strip() for benefit in health_benefits_raw.split(".") if benefit.strip()]
                else:
                    health_benefits = [health_benefits_raw]
        else:
            # Tạo lợi ích sức khỏe mặc định dựa trên thành phần dinh dưỡng
            benefits = []
            if dish_nutrition.protein > 15:
                benefits.append("Giàu protein, tốt cho cơ bắp")
            if dish_nutrition.calories < 300:
                benefits.append("Ít calo, phù hợp cho người đang giảm cân")
            if dish_nutrition.carbs > 30:
                benefits.append("Cung cấp năng lượng dồi dào cho hoạt động thể chất")
            if len(benefits) > 0:
                health_benefits = benefits
                
    # In thông tin debug
    print(f"DEBUG: preparation_time = {preparation_time}")
    print(f"DEBUG: health_benefits = {health_benefits}")
    
    return Dish(
        name=dish_name,
        ingredients=ingredients,
        preparation=preparation_list,  # Truyền danh sách các bước đã xử lý
        nutrition=dish_nutrition,
        dish_type=dish_type,
        region=region,
        image_url=image_url,
        preparation_time=preparation_time,  # Thêm thời gian nấu
        health_benefits=health_benefits  # Thêm lợi ích sức khỏe
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
    day_of_week: str = None,
    user_data: Dict = None  # Add user_data parameter
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
        user_data: Dictionary containing user demographic and goal info (optional)
        
    Returns:
        Meal object with dishes and nutritional information
    """
    print(f"==== GENERATING MEAL: {meal_type} for {day_of_week or 'unknown day'} ====")
    print(f"Targets: cal={target_calories}, protein={target_protein}, fat={target_fat}, carbs={target_carbs}")
    print(f"Using AI: {use_ai}")
    if user_data:
        print(f"User data: gender={user_data.get('gender')}, age={user_data.get('age')}, goal={user_data.get('goal')}")
    
    dishes = []
    
    # Chuyển đổi day_of_week thành day_index để tăng tính đa dạng
    day_index = -1
    if day_of_week in DAYS_OF_WEEK:
        day_index = DAYS_OF_WEEK.index(day_of_week)
        print(f"Day index for {day_of_week}: {day_index}")
    
    # Thiết lập random seed dựa trên ngày và thời gian hiện tại để đảm bảo kết quả khác nhau mỗi lần
    import time
    current_time_ms = int(time.time() * 1000) % 10000  # Lấy 4 chữ số cuối của timestamp hiện tại
    
    if day_index >= 0:
        random_seed_base = day_index * 1000 + current_time_ms
        random.seed(random_seed_base)
        print(f"Set random seed based on day and time: {random_seed_base}")
    else:
        random_seed_base = current_time_ms
        random.seed(random_seed_base)
        print(f"Set random seed based on time: {random_seed_base}")
    
    # Determine meal category for tracking
    meal_category = "breakfast"
    if "trưa" in meal_type.lower() or "lunch" in meal_type.lower():
        meal_category = "lunch"
    elif "tối" in meal_type.lower() or "dinner" in meal_type.lower():
        meal_category = "dinner"
    
    # Get current used dishes for this meal type
    used_dish_names = list(get_used_dishes(meal_category))
    print(f"Currently used {meal_category} dishes: {used_dish_names}")
    
    # Quyết định phương pháp tạo món ăn (AI hoặc ngẫu nhiên)

    # DEBUG: Print use_ai information
    print(f"DEBUG_GENERATE_MEAL: use_ai={use_ai}, AI_SERVICE={AI_SERVICE is not None}, AI_AVAILABLE={AI_AVAILABLE}")
    with open("debug_generate_meal.log", "a", encoding="utf-8") as f:
        f.write(f"DEBUG_GENERATE_MEAL: use_ai={use_ai}, AI_SERVICE={AI_SERVICE is not None}, AI_AVAILABLE={AI_AVAILABLE}\n")
        f.write(f"meal_type={meal_type}, day_of_week={day_of_week}\n\n")
    
    if use_ai and AI_SERVICE and AI_AVAILABLE:
        # Sử dụng LLaMA 3 qua Groq để tạo món ăn
        try:
            print(f"Attempting to generate dishes using AI ({AI_SERVICE.__class__.__name__}) for {meal_type}")
            
            # Thêm tham số ngày và random seed vào yêu cầu AI để tăng tính đa dạng
            import time
            current_time_ms = int(time.time() * 1000) % 10000  # Lấy 4 chữ số cuối của timestamp hiện tại
            random_seed = current_time_ms + (day_index * 1000 if day_index >= 0 else 0)
            print(f"Using AI with random seed: {random_seed}")
            
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
                user_data=user_data  # Add user data for personalization
            )
            
            print(f"AI returned {len(ai_dish_dicts) if ai_dish_dicts else 0} dishes")
            
            if ai_dish_dicts:
                # Kiểm tra tổng calories của các món AI trả về
                ai_total_calories = sum(dish.get("nutrition", {}).get("calories", 0) for dish in ai_dish_dicts)
                if ai_total_calories > target_calories * 1.5:  # Nếu vượt quá 50% mục tiêu
                    print(f"WARNING: AI dishes total calories ({ai_total_calories}) exceed target ({target_calories}) by >50%")
                    print("Adjusting AI dish portions...")
                    ai_dish_dicts = adjust_dish_portions(
                        ai_dish_dicts,
                        target_calories,
                        target_protein,
                        target_fat,
                        target_carbs
                    )
                
                # Không thêm thông tin ngày vào tên món ăn nữa
                # Đảm bảo tên món ăn không chứa tên ngày
                for dish_dict in ai_dish_dicts:
                    if "name" in dish_dict:
                        # Loại bỏ các chuỗi như "(Thứ 2)", "(Thứ 3)" khỏi tên món ăn
                        import re
                        dish_dict["name"] = re.sub(r'\s*\([Tt]hứ\s+\d+\)\s*|\s*\([Cc]hủ\s+[Nn]hật\)\s*', '', dish_dict["name"]).strip()
                
                # Chuyển đổi kết quả từ LLaMA thành Dish objects
                dishes = [generate_dish(dish_dict, user_data) for dish_dict in ai_dish_dicts]
                print(f"Successfully created {len(dishes)} dishes from AI for {meal_type}")

                # YouTube functionality removed - dishes no longer have video URLs

                # Track used dish names
                for dish in dishes:
                    add_dish(meal_category, dish.name)
                
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
        finally:
            # Reset random seed
            random.seed()
    
    # Nếu không sử dụng AI hoặc AI không thành công, dùng phương pháp ngẫu nhiên
    if not dishes:
        print(f"Using random dish generation for {meal_type}")
        dish_count = random.randint(1, 2)  # 1-2 dishes per meal
        
        # Pass used dishes to avoid repetition
        used_dish_names = list(get_used_dishes(meal_category))
        print(f"Used dish names from tracker: {used_dish_names}")
        
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
        dishes = [generate_dish(dish_dict, user_data) for dish_dict in adjusted_dish_dicts]
        print(f"Generated {len(dishes)} random dishes for {meal_type}")

        # YouTube functionality removed - dishes no longer have video URLs

        # Track used dish names
        for dish in dishes:
            add_dish(meal_category, dish.name)
    
    # Final validation - if we still have no dishes, create a basic dish
    if not dishes:
        print(f"WARNING: Failed to generate any dishes for {meal_type}. Creating a basic dish.")
        # Tạo món ăn mẫu dựa trên loại bữa
        if "sáng" in meal_type.lower():
            # Không thêm tên ngày vào tên món ăn
            basic_dish = {
                "name": "Bánh mì trứng",
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
        elif "trưa" in meal_type.lower():
            basic_dish = {
                "name": "Cơm với thịt gà",
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
        else:  # Bữa tối
            basic_dish = {
                "name": "Canh rau củ với thịt bò",
                "ingredients": [
                    {"name": "thịt bò", "amount": "100g"},
                    {"name": "rau củ tổng hợp", "amount": "200g"},
                    {"name": "gia vị", "amount": "vừa đủ"}
                ],
                "preparation": "Thịt bò xào chín với gia vị. Rau củ nấu canh. Ăn kèm cơm trắng.",
                "nutrition": {
                    "calories": target_calories,
                    "protein": target_protein,
                    "fat": target_fat,
                    "carbs": target_carbs
                }
            }
        dishes = [generate_dish(basic_dish, user_data)]
        print(f"Created fallback dish: {basic_dish['name']}")

        # YouTube functionality removed - dishes no longer have video URLs

        # Track used dish names
        for dish in dishes:
            add_dish(meal_category, dish.name)
    
    # Calculate meal nutrition
    meal_nutrition = calculate_meal_nutrition(dishes)
    
    # Kiểm tra và điều chỉnh nếu tổng calories vượt quá mục tiêu quá nhiều
    calories_diff_percent = abs(meal_nutrition.calories - target_calories) / target_calories * 100
    if calories_diff_percent > 20:  # Nếu chênh lệch >20%
        print(f"WARNING: Meal calories ({meal_nutrition.calories:.1f}) differ from target ({target_calories:.1f}) by {calories_diff_percent:.1f}%")
        
        # Điều chỉnh calories và các giá trị dinh dưỡng khác theo tỷ lệ
        adjustment_factor = target_calories / meal_nutrition.calories
        print(f"Adjusting nutrition values with factor: {adjustment_factor:.2f}")
        
        meal_nutrition.calories = target_calories
        meal_nutrition.protein *= adjustment_factor
        meal_nutrition.fat *= adjustment_factor
        meal_nutrition.carbs *= adjustment_factor
    
    print(f"Final meal nutrition: cal={meal_nutrition.calories:.1f}, protein={meal_nutrition.protein:.1f}, fat={meal_nutrition.fat:.1f}, carbs={meal_nutrition.carbs:.1f}")
    
    # Create and return the Meal object
    return Meal(dishes=dishes, nutrition=meal_nutrition)

def generate_day_meal_plan(
    day_of_week: str,
    calories_target: int,
    protein_target: int,
    fat_target: int,
    carbs_target: int,
    preferences: List[str] = None,
    allergies: List[str] = None,
    cuisine_style: str = None,
    use_ai: bool = True,
    user_data: Dict = None  # Add user_data parameter
) -> DayMealPlan:
    """
    Generate a day meal plan with breakfast, lunch, and dinner.
    
    Args:
        day_of_week: Day of the week
        calories_target: Target calories for the day
        protein_target: Target protein for the day (g)
        fat_target: Target fat for the day (g)
        carbs_target: Target carbs for the day (g)
        preferences: Food preferences (optional)
        allergies: Food allergies to avoid (optional)
        cuisine_style: Preferred cuisine style (optional)
        use_ai: Whether to use AI for generation
        user_data: Dictionary containing user demographic and goal info (optional)
        
    Returns:
        DayMealPlan object with meals for the day
    """
    print(f"==== GENERATING DAY MEAL PLAN FOR {day_of_week} ====")
    print(f"Targets: cal={calories_target}, protein={protein_target}, fat={fat_target}, carbs={carbs_target}")
    print(f"Using AI in day meal plan: {use_ai}")
    
    # Distribute nutrition targets across meals
    meal_targets = distribute_nutrition_targets(
        calories_target, protein_target, fat_target, carbs_target
    )
    
    # Generate each meal
    breakfast = generate_meal(
        "bữa sáng",
        meal_targets["breakfast"]["calories"],
        meal_targets["breakfast"]["protein"],
        meal_targets["breakfast"]["fat"],
        meal_targets["breakfast"]["carbs"],
        preferences=preferences,
        allergies=allergies,
        cuisine_style=cuisine_style,
        use_ai=use_ai,
        day_of_week=day_of_week,
        user_data=user_data
    )
    
    lunch = generate_meal(
        "bữa trưa",
        meal_targets["lunch"]["calories"],
        meal_targets["lunch"]["protein"],
        meal_targets["lunch"]["fat"],
        meal_targets["lunch"]["carbs"],
        preferences=preferences,
        allergies=allergies,
        cuisine_style=cuisine_style,
        use_ai=use_ai,
        day_of_week=day_of_week,
        user_data=user_data
    )
    
    dinner = generate_meal(
        "bữa tối",
        meal_targets["dinner"]["calories"],
        meal_targets["dinner"]["protein"],
        meal_targets["dinner"]["fat"],
        meal_targets["dinner"]["carbs"],
        preferences=preferences,
        allergies=allergies, 
        cuisine_style=cuisine_style,
        use_ai=use_ai,
        day_of_week=day_of_week,
        user_data=user_data
    )
    
    # Final validation to ensure each meal has at least one dish
    if not breakfast.dishes:
        breakfast = create_fallback_meal("bữa sáng", meal_targets["breakfast"]["calories"], 
                                        meal_targets["breakfast"]["protein"],
                                        meal_targets["breakfast"]["fat"], 
                                        meal_targets["breakfast"]["carbs"], day_of_week)
    
    if not lunch.dishes:
        lunch = create_fallback_meal("bữa trưa", meal_targets["lunch"]["calories"], 
                                    meal_targets["lunch"]["protein"], 
                                    meal_targets["lunch"]["fat"], 
                                    meal_targets["lunch"]["carbs"], day_of_week)
    
    if not dinner.dishes:
        dinner = create_fallback_meal("bữa tối", meal_targets["dinner"]["calories"], 
                                     meal_targets["dinner"]["protein"], 
                                     meal_targets["dinner"]["fat"], 
                                     meal_targets["dinner"]["carbs"], day_of_week)
    
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
    
    if "sáng" in meal_type.lower():
        dish = Dish(
            name="Bánh mì trứng",
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
            name="Cơm với thịt gà",
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
            name="Canh rau củ với thịt bò",
            ingredients=[
                Ingredient(name="thịt bò", amount="100g"),
                Ingredient(name="rau củ tổng hợp", amount="200g"),
                Ingredient(name="gia vị", amount="vừa đủ")
            ],
            preparation="Thịt bò xào chín với gia vị. Rau củ nấu canh. Ăn kèm cơm trắng.",
            nutrition=NutritionInfo(calories=calories, protein=protein, fat=fat, carbs=carbs)
        )
    
    return Meal(
        dishes=[dish],
        nutrition=NutritionInfo(calories=calories, protein=protein, fat=fat, carbs=carbs)
    )

def generate_weekly_meal_plan(
    calories_target: int,
    protein_target: int,
    fat_target: int,
    carbs_target: int,
    preferences: List[str] = None,
    allergies: List[str] = None,
    cuisine_style: str = None,
    use_ai: bool = True,
    use_tdee: bool = True,  # Thêm tham số use_tdee
    user_data: Dict = None  # Add user_data parameter
) -> WeeklyMealPlan:
    """
    Generate a weekly meal plan with daily meals that meet nutritional targets.
    
    Args:
        calories_target: Target calories per day
        protein_target: Target protein per day (g)
        fat_target: Target fat per day (g)
        carbs_target: Target carbs per day (g)
        preferences: Food preferences (optional)
        allergies: Food allergies to avoid (optional)
        cuisine_style: Preferred cuisine style (optional)
        use_ai: Whether to use AI for generation
        use_tdee: Whether to use TDEE for calorie adjustment
        user_data: Dictionary containing user demographic and goal info (optional)
        
    Returns:
        WeeklyMealPlan object with daily meal plans
    """
    print("======================= GENERATING WEEKLY MEAL PLAN =======================")
    print(f"Targets: calories={calories_target}, protein={protein_target}, fat={fat_target}, carbs={carbs_target}")
    print(f"Preferences: {preferences}")
    print(f"Allergies: {allergies}")
    print(f"Cuisine style: {cuisine_style}")
    print(f"Using AI: {use_ai}")
    
    # Reset used dishes tracker to ensure fresh variety for a new weekly plan
    reset_tracker()
    
    # Generate meal plan for each day of the week
    days = []
    for day_idx, day in enumerate(DAYS_OF_WEEK):
        print(f"\n----- Generating plan for {day} (Day {day_idx+1}/7) -----")
        
        # Thêm biến động nhỏ vào mục tiêu dinh dưỡng để tăng sự đa dạng
        # Sử dụng day_idx để tạo biến động khác nhau cho mỗi ngày
        # Biến động từ -5% đến +5% dựa trên ngày
        variation_factor = 0.95 + (day_idx * 0.015)  # 0.95, 0.965, 0.98, 0.995, 1.01, 1.025, 1.04
        
        day_calories = int(calories_target * variation_factor)
        day_protein = int(protein_target * variation_factor)
        day_fat = int(fat_target * variation_factor)
        day_carbs = int(carbs_target * variation_factor)
        
        print(f"Day {day} targets with variation ({variation_factor:.3f}): cal={day_calories}, protein={day_protein}, fat={day_fat}, carbs={day_carbs}")
        
        # Thêm random seed dựa trên ngày để đảm bảo mỗi ngày có món ăn khác nhau
        random.seed(day_idx * 1000 + calories_target % 100)
        
        day_plan = generate_day_meal_plan(
            day, day_calories, day_protein, day_fat, day_carbs,
            preferences=preferences, allergies=allergies, cuisine_style=cuisine_style, use_ai=use_ai,
            user_data=user_data
        )
        
        # Reset random seed
        random.seed()
        
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
        
        # Kiểm tra tổng calories của ngày có vượt quá mục tiêu không
        day_total_calories = day_plan.nutrition.calories
        calories_diff = abs(day_total_calories - day_calories)
        calories_percent_diff = (calories_diff / day_calories) * 100
        
        print(f"Day {day} total calories: {day_total_calories:.1f}, target: {day_calories}, diff: {calories_percent_diff:.1f}%")
        
        # Nếu chênh lệch quá lớn (>10%), tạo lại kế hoạch cho ngày đó
        if calories_percent_diff > 10:
            print(f"WARNING: Day {day} calories {day_total_calories:.1f} differ from target {day_calories} by {calories_percent_diff:.1f}%")
            print("Regenerating day plan with stricter controls...")
            
            # Tạo lại kế hoạch ngày với mục tiêu chính xác
            day_plan = generate_day_meal_plan(
                day, calories_target, protein_target, fat_target, carbs_target,
                preferences=preferences, allergies=allergies, cuisine_style=cuisine_style, use_ai=use_ai,
                user_data=user_data
            )
            
            print(f"Regenerated day {day} calories: {day_plan.nutrition.calories:.1f}")
        
        days.append(day_plan)
        
        # In ra thông tin về các món đã sử dụng trong tuần
        print(f"Weekly tracking - Breakfast dishes used so far: {len(used_dishes_tracker['breakfast'])}")
        print(f"Weekly tracking - Lunch dishes used so far: {len(used_dishes_tracker['lunch'])}")
        print(f"Weekly tracking - Dinner dishes used so far: {len(used_dishes_tracker['dinner'])}")
    
    # Create and return the WeeklyMealPlan object
    weekly_plan = WeeklyMealPlan(days=days)
    
    print("\n----- Weekly Plan Summary -----")
    total_dishes = 0
    total_calories = 0
    unique_dishes = set()
    
    for day in weekly_plan.days:
        day_dishes = []
        if day.breakfast and day.breakfast.dishes:
            day_dishes.extend([dish.name for dish in day.breakfast.dishes])
        if day.lunch and day.lunch.dishes:
            day_dishes.extend([dish.name for dish in day.lunch.dishes])
        if day.dinner and day.dinner.dishes:
            day_dishes.extend([dish.name for dish in day.dinner.dishes])
            
        total_dishes += len(day_dishes)
        unique_dishes.update(day_dishes)
        total_calories += day.nutrition.calories
        print(f"Day {day.day_of_week}: {len(day_dishes)} dishes, {day.nutrition.calories:.1f} calories")
    
    avg_daily_calories = total_calories / len(weekly_plan.days) if weekly_plan.days else 0
    print(f"Total dishes across all days: {total_dishes}")
    print(f"Unique dishes in the plan: {len(unique_dishes)} of {total_dishes} ({len(unique_dishes)/total_dishes*100:.1f}% unique)")
    print(f"Average daily calories: {avg_daily_calories:.1f} (target: {calories_target})")
    print("======================= WEEKLY MEAL PLAN GENERATED =======================")
    
    return weekly_plan

def replace_meal(
    current_weekly_plan: Optional[WeeklyMealPlan],
    replace_request: ReplaceDayRequest,
    preferences: List[str] = None,
    allergies: List[str] = None,
    cuisine_style: str = None,
    use_ai: bool = True,
    user_data: Dict = None  # Add user_data parameter
) -> DayMealPlan:
    """
    Replace a specific day in the meal plan with a new day plan.
    
    Args:
        current_weekly_plan: Current weekly meal plan
        replace_request: Request with day and nutrition targets
        preferences: Food preferences (optional)
        allergies: Food allergies to avoid (optional)
        cuisine_style: Cuisine style (optional)
        use_ai: Whether to use AI for generation
        user_data: Dictionary containing user demographic and goal info (optional)
        
    Returns:
        New DayMealPlan for the specified day
        
    Raises:
        ValueError: If the weekly meal plan doesn't exist or can't find the specified day
    """
    # Kiểm tra xem kế hoạch tuần có tồn tại không
    if current_weekly_plan is None:
        error_msg = "Không thể thay thế bữa ăn: Kế hoạch ăn tuần không tồn tại"
        print(f"⚠️ {error_msg}")
        raise ValueError(error_msg)
    
    # Kiểm tra xem ngày cần thay thế có tồn tại trong kế hoạch không
    day_exists = False
    for day in current_weekly_plan.days:
        if day.day_of_week == replace_request.day_of_week:
            day_exists = True
            break
    
    if not day_exists:
        error_msg = f"Không thể thay thế bữa ăn: Ngày {replace_request.day_of_week} không tồn tại trong kế hoạch"
        print(f"⚠️ {error_msg}")
        raise ValueError(error_msg)
    
    # Clear the used dishes for this specific day to ensure new variety
    reset_tracker()
    
    # Reset cache trong Groq service để đảm bảo luôn tạo mới
    if use_ai and AI_SERVICE and AI_AVAILABLE:
        try:
            # Xoá cache để luôn tạo món mới
            print("🔄 Đang xóa cache để tạo món mới...")
            AI_SERVICE.clear_cache()
            print("✅ Đã xóa cache AI thành công")
        except Exception as e:
            print(f"⚠️ Không thể xóa cache AI: {e}")
    
    # Scale down the daily nutrition targets based on meal type
    if replace_request.meal_type:
        print(f"Scaling down daily nutrition targets for specific meal: {replace_request.meal_type}")
        # Get the distribution of nutrition targets for all meals
        meal_targets = distribute_nutrition_targets(
            replace_request.calories_target,
            replace_request.protein_target,
            replace_request.fat_target,
            replace_request.carbs_target
        )
        
        # Get the specific meal target based on meal_type
        meal_type = replace_request.meal_type.lower()
        if "breakfast" in meal_type or "sáng" in meal_type:
            meal_specific_targets = meal_targets["breakfast"]
            print(f"Using breakfast targets: {meal_specific_targets}")
        elif "lunch" in meal_type or "trưa" in meal_type:
            meal_specific_targets = meal_targets["lunch"]  
            print(f"Using lunch targets: {meal_specific_targets}")
        elif "dinner" in meal_type or "tối" in meal_type:
            meal_specific_targets = meal_targets["dinner"]
            print(f"Using dinner targets: {meal_specific_targets}")
        else:
            # Default to evenly distributed if meal type is unknown
            print(f"Unknown meal type: {meal_type}, using evenly distributed targets")
            meal_specific_targets = {
                "calories": replace_request.calories_target / 3,
                "protein": replace_request.protein_target / 3,
                "fat": replace_request.fat_target / 3,
                "carbs": replace_request.carbs_target / 3
            }
        
        # Generate meal with scaled targets
        new_meal = generate_meal(
            replace_request.meal_type,
            meal_specific_targets["calories"],
            meal_specific_targets["protein"],
            meal_specific_targets["fat"],
            meal_specific_targets["carbs"],
            preferences=preferences,
            allergies=allergies,
            cuisine_style=cuisine_style,
            use_ai=use_ai,
            day_of_week=replace_request.day_of_week,
            user_data=user_data
        )
        
        # Create a new day meal plan with the replaced meal
        if current_weekly_plan:
            # Find the current day plan
            current_day = None
            for day in current_weekly_plan.days:
                if day.day_of_week == replace_request.day_of_week:
                    current_day = day
                    break
                    
            if current_day:
                # Create a new day plan with the replaced meal
                if "breakfast" in meal_type or "sáng" in meal_type:
                    new_day_plan = DayMealPlan(
                        day_of_week=replace_request.day_of_week,
                        breakfast=new_meal,
                        lunch=current_day.lunch,
                        dinner=current_day.dinner,
                        nutrition=calculate_day_nutrition(new_meal, current_day.lunch, current_day.dinner)
                    )
                elif "lunch" in meal_type or "trưa" in meal_type:
                    new_day_plan = DayMealPlan(
                        day_of_week=replace_request.day_of_week,
                        breakfast=current_day.breakfast,
                        lunch=new_meal,
                        dinner=current_day.dinner,
                        nutrition=calculate_day_nutrition(current_day.breakfast, new_meal, current_day.dinner)
                    )
                elif "dinner" in meal_type or "tối" in meal_type:
                    new_day_plan = DayMealPlan(
                        day_of_week=replace_request.day_of_week,
                        breakfast=current_day.breakfast,
                        lunch=current_day.lunch,
                        dinner=new_meal,
                        nutrition=calculate_day_nutrition(current_day.breakfast, current_day.lunch, new_meal)
                    )
                else:
                    # Default - replace breakfast if meal type unknown
                    new_day_plan = DayMealPlan(
                        day_of_week=replace_request.day_of_week,
                        breakfast=new_meal,
                        lunch=current_day.lunch,
                        dinner=current_day.dinner,
                        nutrition=calculate_day_nutrition(new_meal, current_day.lunch, current_day.dinner)
                    )
                
                # Update the weekly plan with the new day plan
                for i, day in enumerate(current_weekly_plan.days):
                    if day.day_of_week == replace_request.day_of_week:
                        current_weekly_plan.days[i] = new_day_plan
                        break
                        
                return new_day_plan
    
    # Trả về lỗi nếu không thể tạo bữa ăn
    error_msg = f"Không thể thay thế {replace_request.meal_type} cho ngày {replace_request.day_of_week}: Loại bữa ăn không hợp lệ"
    print(f"⚠️ {error_msg}")
    raise ValueError(error_msg)

def replace_day_meal_plan(
    current_weekly_plan: Optional[WeeklyMealPlan],
    replace_request: ReplaceDayRequest,
    preferences: List[str] = None,
    allergies: List[str] = None,
    cuisine_style: str = None,
    use_ai: bool = True,
    user_data: Dict = None
) -> DayMealPlan:
    """
    Tạo ra một kế hoạch ăn mới hoàn toàn cho một ngày cụ thể.
    
    Args:
        current_weekly_plan: Kế hoạch tuần hiện tại
        replace_request: Yêu cầu thay thế ngày với mục tiêu dinh dưỡng
        preferences: Món ăn ưa thích (tùy chọn)
        allergies: Dị ứng thực phẩm cần tránh (tùy chọn)
        cuisine_style: Phong cách ẩm thực (tùy chọn)
        use_ai: Có sử dụng AI để tạo món ăn không
        user_data: Thông tin người dùng (tùy chọn)
        
    Returns:
        DayMealPlan: Kế hoạch ăn mới cho ngày được chỉ định
    """
    print(f"Bắt đầu tạo kế hoạch mới cho ngày: {replace_request.day_of_week}")
    
    # Reset bộ đếm các món ăn đã dùng để đảm bảo có sự đa dạng tối đa cho ngày mới
    reset_tracker()
    
    # 🔧 FIX: Enhanced cache clearing và diversity enforcement
    if use_ai and AI_SERVICE and AI_AVAILABLE:
        try:
            # Xoá cache để luôn tạo món mới
            print("🔄 Đang xóa cache để tạo món mới...")
            AI_SERVICE.clear_cache()

            # 🔧 FIX: Thêm random seed để đảm bảo diversity
            import time
            import random
            random.seed(int(time.time()))

            print("✅ Đã xóa cache AI và reset random seed thành công")
        except Exception as e:
            print(f"⚠️ Không thể xóa cache AI: {e}")

    # 🔧 FIX: Force diversity by adding timestamp to meal generation
    diversity_timestamp = int(time.time())
    print(f"🎲 Diversity timestamp: {diversity_timestamp}")
    
    # Gọi hàm tạo kế hoạch cho một ngày
    new_day_plan = generate_day_meal_plan(
        day_of_week=replace_request.day_of_week,
        calories_target=replace_request.calories_target,
        protein_target=replace_request.protein_target,
        fat_target=replace_request.fat_target,
        carbs_target=replace_request.carbs_target,
        preferences=preferences,
        allergies=allergies,
        cuisine_style=cuisine_style,
        use_ai=use_ai,
        user_data=user_data
    )
    
    return new_day_plan

def get_vietnamese_dishes(meal_type: str, count: int = 10, avoid_dishes: List[str] = None) -> List[Dict]:
    """
    🔧 FIX: Tạo món ăn Việt Nam thay thế SAMPLE_RECIPES

    Args:
        meal_type: Loại bữa ăn (breakfast, lunch, dinner)
        count: Số lượng món cần tạo
        avoid_dishes: Danh sách món cần tránh

    Returns:
        List[Dict]: Danh sách món ăn Việt Nam với dữ liệu dinh dưỡng chính xác
    """
    if not VIETNAMESE_GENERATOR_AVAILABLE:
        print("⚠️ Vietnamese generator not available, using fallback SAMPLE_RECIPES")
        return SAMPLE_RECIPES.get(meal_type, [])

    try:
        print(f"🔧 Generating {count} Vietnamese dishes for {meal_type}")

        # Generate dishes từ các miền khác nhau
        dishes = []
        regions = ["miền_bắc", "miền_trung", "miền_nam"]
        dishes_per_region = count // len(regions)

        for region in regions:
            for i in range(dishes_per_region):
                try:
                    dish = vietnamese_dish_generator.generate_single_dish(meal_type, region)

                    # Kiểm tra avoid_dishes
                    if avoid_dishes and dish["name"] in avoid_dishes:
                        continue

                    # Convert format để tương thích với hệ thống hiện tại
                    converted_dish = {
                        "name": dish["name"],
                        "ingredients": [
                            {"name": ing["name"], "amount": f"{ing['amount']}g"}
                            for ing in dish["ingredients"]
                        ],
                        "preparation": dish["preparation"],
                        "nutrition": dish["nutrition"],
                        "region": dish["region"],
                        "cooking_time": dish["cooking_time"],
                        "difficulty": dish["difficulty"]
                    }

                    dishes.append(converted_dish)

                except Exception as e:
                    print(f"❌ Error generating dish: {e}")
                    continue

        print(f"✅ Generated {len(dishes)} Vietnamese dishes for {meal_type}")
        return dishes[:count]

    except Exception as e:
        print(f"❌ Error in get_vietnamese_dishes: {e}")
        print("⚠️ Falling back to SAMPLE_RECIPES")
        return SAMPLE_RECIPES.get(meal_type, [])

# Global instances
# meal_service = MealService()  # Commented out as MealService class not defined in this file
