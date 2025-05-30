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

# Tạo kế hoạch ăn uống
print("Đang tạo kế hoạch ăn uống cho 7 ngày...")
weekly_plan = generate_weekly_meal_plan(
    calories_target=2000,
    protein_target=100,
    fat_target=70,
    carbs_target=250,
    use_ai=False  # Không sử dụng AI để kiểm tra tính đa dạng của phương pháp ngẫu nhiên
)

# Kiểm tra tính đa dạng
print_meal_plan_variety(weekly_plan) 