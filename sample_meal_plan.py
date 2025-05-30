from models import WeeklyMealPlan, DayMealPlan, Meal, Dish, NutritionInfo, Ingredient
import json
import requests

# Create a sample dish
def create_sample_dish(name, ingredients_list, preparation, nutrition_values):
    ingredients = [Ingredient(name=ing[0], amount=ing[1]) for ing in ingredients_list]
    nutrition = NutritionInfo(
        calories=nutrition_values[0],
        protein=nutrition_values[1],
        fat=nutrition_values[2],
        carbs=nutrition_values[3]
    )
    return Dish(name=name, ingredients=ingredients, preparation=preparation, nutrition=nutrition)

# Create breakfast dishes
breakfast_dish1 = create_sample_dish(
    "Bánh mì trứng ốp la",
    [
        ("Bánh mì", "1 ổ"),
        ("Trứng gà", "2 quả"),
        ("Dầu olive", "1 muỗng canh"),
        ("Muối", "1 nhúm"),
        ("Tiêu", "1 nhúm")
    ],
    "Đập trứng vào chảo nóng có dầu olive, rắc một chút muối và tiêu. Chiên trứng ốp la, sau đó đặt lên bánh mì đã nướng giòn.",
    [380, 15, 18, 42]
)

# Create lunch dishes
lunch_dish1 = create_sample_dish(
    "Cơm gà xối mỡ",
    [
        ("Thịt gà", "200g"),
        ("Gạo", "150g"),
        ("Hành lá", "20g"),
        ("Dầu ăn", "15ml"),
        ("Gia vị", "vừa đủ")
    ],
    "Nấu cơm với gạo. Luộc gà, xé nhỏ. Phi hành với dầu, xối lên gà. Bày cơm và gà ra đĩa.",
    [450, 30, 15, 45]
)

lunch_dish2 = create_sample_dish(
    "Canh rau cải",
    [
        ("Rau cải ngọt", "100g"),
        ("Nước dùng", "300ml"),
        ("Hành khô", "10g"),
        ("Muối", "1 nhúm")
    ],
    "Làm nóng nước dùng, thêm hành phi thơm. Cho rau cải vào nấu chín, nêm nếm vừa ăn.",
    [80, 4, 2, 12]
)

# Create dinner dishes
dinner_dish1 = create_sample_dish(
    "Cá hồi nướng mật ong",
    [
        ("Cá hồi phi lê", "180g"),
        ("Mật ong", "15ml"),
        ("Tỏi băm", "5g"),
        ("Nước cốt chanh", "10ml"),
        ("Gia vị", "vừa đủ")
    ],
    "Ướp cá hồi với hỗn hợp mật ong, tỏi băm, nước cốt chanh và gia vị trong 15 phút. Nướng cá ở 180°C trong 15 phút.",
    [320, 28, 14, 18]
)

dinner_dish2 = create_sample_dish(
    "Salad trộn dầu giấm",
    [
        ("Rau xà lách", "50g"),
        ("Cà chua", "50g"),
        ("Dưa chuột", "50g"),
        ("Dầu olive", "10ml"),
        ("Giấm", "5ml"),
        ("Muối tiêu", "vừa đủ")
    ],
    "Rửa sạch và cắt nhỏ các loại rau. Trộn đều với dầu olive, giấm, muối và tiêu.",
    [90, 2, 7, 6]
)

# Create meals
breakfast = Meal(
    dishes=[breakfast_dish1],
    nutrition=NutritionInfo(calories=380, protein=15, fat=18, carbs=42)
)

lunch = Meal(
    dishes=[lunch_dish1, lunch_dish2],
    nutrition=NutritionInfo(calories=530, protein=34, fat=17, carbs=57)
)

dinner = Meal(
    dishes=[dinner_dish1, dinner_dish2],
    nutrition=NutritionInfo(calories=410, protein=30, fat=21, carbs=24)
)

# Create day meal plan
day_plan = DayMealPlan(
    day_of_week="Thứ 2",
    breakfast=breakfast,
    lunch=lunch,
    dinner=dinner,
    nutrition=NutritionInfo(calories=1320, protein=79, fat=56, carbs=123)
)

# Create weekly meal plan with just one day for simplicity
weekly_plan = WeeklyMealPlan(days=[day_plan])

# Print the meal plan as JSON
print(json.dumps(weekly_plan.dict(), indent=2, ensure_ascii=False))

# =========================
# Ví dụ gửi POST request tự động đến FastAPI endpoint
# =========================

# Địa chỉ server FastAPI của bạn
FASTAPI_HOST = "http://localhost:8000"  # Đổi thành địa chỉ thực tế nếu chạy trên server khác

# Dữ liệu đầu vào cho endpoint
payload = {
    "calories_target": 2000,
    "protein_target": 100,
    "fat_target": 60,
    "carbs_target": 250
}

# Gửi POST request
try:
    response = requests.post(f"{FASTAPI_HOST}/generate-weekly-meal-demo", json=payload)
    print("\nKết quả từ API /generate-weekly-meal-demo:")
    print(response.status_code)
    print(response.json())
except Exception as e:
    print(f"Lỗi khi gửi request: {e}") 