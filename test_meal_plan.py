from models import WeeklyMealPlan, DayMealPlan, Meal, Dish, NutritionInfo, Ingredient
from storage_manager import storage_manager
import datetime

# Tạo một kế hoạch dinh dưỡng mẫu
def create_sample_meal_plan():
    # Tạo thông tin dinh dưỡng
    breakfast_nutrition = NutritionInfo(
        calories=350,
        protein=15,
        fat=20,
        carbs=30
    )
    
    lunch_nutrition = NutritionInfo(
        calories=450,
        protein=35,
        fat=20,
        carbs=30
    )
    
    dinner_nutrition = NutritionInfo(
        calories=500,
        protein=40,
        fat=25,
        carbs=25
    )
    
    day_nutrition = NutritionInfo(
        calories=1300,
        protein=90,
        fat=65,
        carbs=85
    )
    
    # Tạo các món ăn
    breakfast_dish = Dish(
        name="Trứng chiên với bánh mì",
        ingredients=[
            Ingredient(name="Trứng gà", amount="2 quả"),
            Ingredient(name="Bánh mì", amount="2 lát"),
            Ingredient(name="Dầu olive", amount="1 muỗng canh")
        ],
        preparation="Đập trứng vào bát, đánh đều. Đun nóng dầu olive trong chảo. Đổ trứng vào chảo, chiên đến khi chín vàng. Nướng bánh mì và phục vụ cùng trứng.",
        nutrition=breakfast_nutrition
    )
    
    lunch_dish = Dish(
        name="Salad gà",
        ingredients=[
            Ingredient(name="Ức gà", amount="150g"),
            Ingredient(name="Rau xà lách", amount="100g"),
            Ingredient(name="Cà chua", amount="1 quả"),
            Ingredient(name="Dầu olive", amount="1 muỗng canh")
        ],
        preparation="Nướng ức gà với gia vị. Rửa sạch và cắt nhỏ rau xà lách và cà chua. Cắt ức gà thành lát mỏng. Trộn đều tất cả nguyên liệu với dầu olive.",
        nutrition=lunch_nutrition
    )
    
    dinner_dish = Dish(
        name="Cá hồi nướng với rau củ",
        ingredients=[
            Ingredient(name="Cá hồi", amount="200g"),
            Ingredient(name="Bông cải xanh", amount="100g"),
            Ingredient(name="Cà rốt", amount="1 củ"),
            Ingredient(name="Dầu olive", amount="1 muỗng canh")
        ],
        preparation="Làm nóng lò nướng ở 180°C. Rửa sạch và cắt nhỏ rau củ. Đặt cá hồi và rau củ vào khay nướng. Nướng trong 15-20 phút đến khi cá chín.",
        nutrition=dinner_nutrition
    )
    
    # Tạo các bữa ăn
    breakfast = Meal(
        dishes=[breakfast_dish],
        nutrition=breakfast_nutrition
    )
    
    lunch = Meal(
        dishes=[lunch_dish],
        nutrition=lunch_nutrition
    )
    
    dinner = Meal(
        dishes=[dinner_dish],
        nutrition=dinner_nutrition
    )
    
    # Tạo kế hoạch cho một ngày
    day_plan = DayMealPlan(
        day_of_week="Thứ 2",
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner,
        nutrition=day_nutrition
    )
    
    # Tạo kế hoạch cho cả tuần (chỉ 1 ngày cho đơn giản)
    meal_plan = WeeklyMealPlan(
        days=[day_plan]
    )
    
    return meal_plan

# Lưu kế hoạch dinh dưỡng
def save_meal_plan_to_firebase():
    # Tạo kế hoạch dinh dưỡng mẫu
    meal_plan = create_sample_meal_plan()
    
    print("Đã tạo kế hoạch dinh dưỡng mẫu:")
    print(f"Số ngày: {len(meal_plan.days)}")
    print(f"Ngày: {meal_plan.days[0].day_of_week}")
    print(f"Tổng calories: {meal_plan.days[0].nutrition.calories}")
    
    # Lưu vào Firestore
    user_id = "test_user"
    try:
        storage_path = storage_manager.save_meal_plan(meal_plan, user_id)
        print(f"Đã lưu kế hoạch dinh dưỡng: {storage_path}")
        
        # Kiểm tra xem có lưu thành công không
        loaded_plan = storage_manager.load_meal_plan(user_id)
        if loaded_plan:
            print("Đã tải lại kế hoạch dinh dưỡng thành công!")
            print(f"Số ngày: {len(loaded_plan.days)}")
        else:
            print("Không thể tải lại kế hoạch dinh dưỡng")
            
        print(f"Firebase được sử dụng: {storage_manager.is_using_firebase()}")
        
        return True
    except Exception as e:
        print(f"Lỗi khi lưu kế hoạch dinh dưỡng: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    save_meal_plan_to_firebase() 