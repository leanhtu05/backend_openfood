from services import generate_weekly_meal_plan
from models import NutritionTarget
from firebase_integration import firebase

print("\n===== KIỂM TRA VIỆC SỬA LỖI =====")

# Kiểm tra xem hàm generate_weekly_meal_plan đã là phiên bản thật (không phải mock)
print("\n-- Kiểm tra hàm generate_weekly_meal_plan --")
print(f"Source module: {generate_weekly_meal_plan.__module__}")

# Kiểm tra tạo kế hoạch thực đơn với AI
print("\n-- Tạo kế hoạch thực đơn với AI --")
meal_plan = generate_weekly_meal_plan(
    calories_target=2000,
    protein_target=90,
    fat_target=65,
    carbs_target=250,
    preferences=["trái cây", "rau xanh", "thịt gà"],
    allergies=["hải sản", "đậu phộng"],
    cuisine_style="Việt Nam",
    use_ai=True
)

# Kiểm tra xem kế hoạch có món ăn không
print("\n-- Kiểm tra món ăn trong kế hoạch --")
if meal_plan and meal_plan.days:
    dish_count = 0
    for day in meal_plan.days:
        day_dishes = (
            len(day.breakfast.dishes if day.breakfast and day.breakfast.dishes else []) + 
            len(day.lunch.dishes if day.lunch and day.lunch.dishes else []) + 
            len(day.dinner.dishes if day.dinner and day.dinner.dishes else [])
        )
        dish_count += day_dishes
        print(f"Ngày {day.day_of_week}: {day_dishes} món ăn")
    
    print(f"Tổng số món ăn: {dish_count}")
    
    # Lưu vào Firestore
    print("\n-- Lưu vào Firestore --")
    user_id = "verify_fix_test"
    plan_id = firebase.save_meal_plan(meal_plan, user_id)
    
    if plan_id:
        print(f"✅ Đã lưu thành công vào Firestore với ID: {plan_id}")
        
        # Kiểm tra đọc lại
        loaded_plan = firebase.load_meal_plan(user_id)
        if loaded_plan:
            print(f"✅ Đọc lại thành công với {len(loaded_plan.days)} ngày")
        else:
            print("❌ Không đọc lại được từ Firestore")
    else:
        print("❌ Không lưu được vào Firestore")
else:
    print("❌ Không tạo được kế hoạch thực đơn")

print("\n===== KẾT THÚC KIỂM TRA =====") 