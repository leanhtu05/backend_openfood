import random
from services import generate_weekly_meal_plan

def print_meal_plan_variety(weekly_plan):
    """In ra thông tin về tính đa dạng của kế hoạch ăn uống"""
    print("\n===== KIỂM TRA TÍNH ĐA DẠNG CỦA KẾ HOẠCH ĂN UỐNG =====")
    
    # Theo dõi món ăn đã sử dụng
    all_dishes = []
    dish_count_by_type = {"breakfast": [], "lunch": [], "dinner": []}
    
    # Thu thập tất cả món ăn
    for day in weekly_plan.days:
        # Bữa sáng
        breakfast_dishes = [dish.name for dish in day.breakfast.dishes]
        dish_count_by_type["breakfast"].append(len(breakfast_dishes))
        all_dishes.extend(breakfast_dishes)
        
        # Bữa trưa
        lunch_dishes = [dish.name for dish in day.lunch.dishes]
        dish_count_by_type["lunch"].append(len(lunch_dishes))
        all_dishes.extend(lunch_dishes)
        
        # Bữa tối
        dinner_dishes = [dish.name for dish in day.dinner.dishes]
        dish_count_by_type["dinner"].append(len(dinner_dishes))
        all_dishes.extend(dinner_dishes)
    
    # Đếm số lượng món ăn duy nhất
    unique_dishes = set(all_dishes)
    
    print(f"Tổng số món ăn: {len(all_dishes)}")
    print(f"Số món ăn duy nhất: {len(unique_dishes)}")
    print(f"Tỷ lệ đa dạng: {len(unique_dishes) / len(all_dishes) * 100:.1f}%")
    
    # Thống kê số lượng món ăn theo loại bữa
    for meal_type, counts in dish_count_by_type.items():
        print(f"\nSố món ăn cho {meal_type}: {sum(counts)}")
        print(f"Trung bình món ăn mỗi ngày: {sum(counts)/len(counts):.1f}")
        print(f"Chi tiết theo ngày: {counts}")
    
    # In ra chi tiết các món ăn theo ngày
    print("\n===== CHI TIẾT MÓN ĂN THEO NGÀY =====")
    for i, day in enumerate(weekly_plan.days):
        print(f"\nNgày {i+1} ({day.day_of_week}):")
        print(f"  Bữa sáng: {', '.join([dish.name for dish in day.breakfast.dishes])}")
        print(f"  Bữa trưa: {', '.join([dish.name for dish in day.lunch.dishes])}")
        print(f"  Bữa tối: {', '.join([dish.name for dish in day.dinner.dishes])}")
    
    # Kiểm tra món ăn trùng lặp
    print("\n===== KIỂM TRA MÓN ĂN TRÙNG LẶP =====")
    dish_frequency = {}
    for dish in all_dishes:
        if dish in dish_frequency:
            dish_frequency[dish] += 1
        else:
            dish_frequency[dish] = 1
    
    # Sắp xếp theo tần suất giảm dần
    sorted_dishes = sorted(dish_frequency.items(), key=lambda x: x[1], reverse=True)
    
    print("Món ăn xuất hiện nhiều nhất:")
    for dish, count in sorted_dishes[:5]:  # Top 5 món ăn xuất hiện nhiều nhất
        print(f"  {dish}: {count} lần")
    
    # Tính điểm đa dạng (càng cao càng tốt)
    variety_score = len(unique_dishes) / len(all_dishes) * 10
    print(f"\nĐiểm đa dạng (0-10): {variety_score:.1f}/10")
    
    if variety_score >= 8:
        print("Đánh giá: Rất đa dạng!")
    elif variety_score >= 6:
        print("Đánh giá: Khá đa dạng")
    else:
        print("Đánh giá: Cần cải thiện tính đa dạng")

# Tạo kế hoạch ăn uống với day_index được kích hoạt
print("Đang tạo kế hoạch ăn uống cho 7 ngày với day_index được kích hoạt...")

# Sửa đổi hàm generate_day_meal_plan trong services.py để sử dụng day_index
from services import generate_day_meal_plan

# Lưu lại hàm generate_day_meal_plan gốc
original_generate_day_meal_plan = generate_day_meal_plan

# Định nghĩa hàm generate_day_meal_plan mới để truyền day_index
def generate_day_meal_plan_with_day_index(
    day_of_week: str,
    calories_target: int,
    protein_target: int,
    fat_target: int,
    carbs_target: int,
    preferences=None,
    allergies=None,
    cuisine_style=None,
    use_ai=True
):
    # Lấy day_index từ DAYS_OF_WEEK
    from utils import DAYS_OF_WEEK
    day_index = DAYS_OF_WEEK.index(day_of_week) if day_of_week in DAYS_OF_WEEK else -1
    
    print(f"Generating meal plan for {day_of_week} with day_index={day_index}")
    
    # Gọi hàm generate_meal với day_index
    from services import generate_meal
    
    # Distribute nutrition targets across meals
    from utils import distribute_nutrition_targets
    meal_targets = distribute_nutrition_targets(
        calories_target, protein_target, fat_target, carbs_target
    )
    
    # Generate each meal with day_index
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
        day_of_week=day_of_week
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
        day_of_week=day_of_week
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
        day_of_week=day_of_week
    )
    
    # Calculate daily nutrition
    from utils import calculate_day_nutrition
    day_nutrition = calculate_day_nutrition(breakfast, lunch, dinner)
    
    # Create and return the DayMealPlan object
    from models import DayMealPlan
    return DayMealPlan(
        day_of_week=day_of_week,
        breakfast=breakfast,
        lunch=lunch,
        dinner=dinner,
        nutrition=day_nutrition
    )

# Thay thế hàm generate_day_meal_plan trong services
import services
services.generate_day_meal_plan = generate_day_meal_plan_with_day_index

# Tạo kế hoạch ăn uống
weekly_plan = generate_weekly_meal_plan(
    calories_target=2000,
    protein_target=100,
    fat_target=70,
    carbs_target=250,
    use_ai=False  # Không sử dụng AI để kiểm tra tính đa dạng của phương pháp ngẫu nhiên
)

# Kiểm tra tính đa dạng
print_meal_plan_variety(weekly_plan)

# Khôi phục lại hàm generate_day_meal_plan gốc
services.generate_day_meal_plan = original_generate_day_meal_plan

print("\nĐã hoàn thành kiểm tra tính đa dạng với day_index được kích hoạt.") 