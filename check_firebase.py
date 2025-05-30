from storage_manager import storage_manager
from firebase_integration import firebase
import os
from models import WeeklyMealPlan, DayMealPlan, Meal, Dish, NutritionInfo, Ingredient

print(f"Firebase được bật: {storage_manager.use_firebase}")
print(f"Firebase đã khởi tạo: {storage_manager.firebase_initialized}")
print(f"Firebase credentials tồn tại: {os.path.exists('firebase-credentials.json')}")

# Kiểm tra xem dữ liệu đã được lưu trữ trên Firestore chưa
try:
    # Tải meal plan từ Firestore với ID test_flutter_user
    meal_plan = firebase.load_meal_plan("default")
    
    if meal_plan:
        print("\nĐã tìm thấy kế hoạch dinh dưỡng cho 'default' trên Firestore")
        print(f"Số ngày: {len(meal_plan.days)}")
        
        # In thông tin về một vài bữa ăn
        if meal_plan.days:
            day = meal_plan.days[0]
            print(f"Ngày: {day.day_of_week}")
            print(f"Bữa sáng: {len(day.breakfast.dishes)} món")
            for dish in day.breakfast.dishes:
                print(f"  - {dish.name}: {dish.nutrition.calories} calories")
    else:
        print("\nKhông tìm thấy kế hoạch dinh dưỡng cho 'default' trên Firestore")
        
    # Thử tìm với ID test_user
    meal_plan = firebase.load_meal_plan("test_user")
    
    if meal_plan:
        print("\nĐã tìm thấy kế hoạch dinh dưỡng cho 'test_user' trên Firestore")
        print(f"Số ngày: {len(meal_plan.days)}")
        
        # In thông tin về một vài bữa ăn
        if meal_plan.days:
            day = meal_plan.days[0]
            print(f"Ngày: {day.day_of_week}")
            print(f"Bữa sáng: {len(day.breakfast.dishes)} món")
            for dish in day.breakfast.dishes:
                print(f"  - {dish.name}: {dish.nutrition.calories} calories")
    else:
        print("\nKhông tìm thấy kế hoạch dinh dưỡng cho 'test_user' trên Firestore")
        
    # Kiểm tra dữ liệu user
    user_id = "test_flutter_user"
    from services.firestore_service import firestore_service
    user = firestore_service.get_user(user_id)
    if user:
        print(f"\nTìm thấy user {user_id} trên Firestore:")
        print(f"Tên: {user.name}")
        print(f"Email: {user.email}")
    else:
        print(f"\nKhông tìm thấy user {user_id} trên Firestore")
        
except Exception as e:
    print(f"Lỗi khi kiểm tra Firestore: {e}")
    import traceback
    traceback.print_exc()

def check_firebase_connection():
    """Kiểm tra kết nối Firebase và khả năng lưu trữ dữ liệu"""
    print("=== KIỂM TRA KẾT NỐI FIREBASE ===")
    print(f"Firebase đã khởi tạo: {firebase.initialized}")
    
    # Kiểm tra file credentials tồn tại
    print(f"Firebase credentials file tồn tại: {os.path.exists('firebase-credentials.json')}")
    
    # Kiểm tra kết nối tới Firestore
    if firebase.initialized:
        print("Kết nối tới Firestore thành công!")
        
        # Tạo dữ liệu mẫu để kiểm tra
        meal_plan = create_test_meal_plan()
        
        # Thử lưu vào Firestore
        user_id = "test_firebase_connection"
        doc_id = firebase.save_meal_plan(meal_plan, user_id)
        
        if doc_id:
            print(f"Đã lưu thành công kế hoạch dinh dưỡng vào Firestore với ID: {doc_id}")
            
            # Kiểm tra đọc dữ liệu
            loaded_plan = firebase.load_meal_plan(user_id)
            if loaded_plan:
                print(f"Đã đọc thành công kế hoạch dinh dưỡng từ Firestore")
                print(f"Số ngày: {len(loaded_plan.days)}")
                print(f"Ngày đầu tiên: {loaded_plan.days[0].day_of_week}")
                return True
            else:
                print("Không thể đọc dữ liệu từ Firestore")
        else:
            print("Không thể lưu dữ liệu vào Firestore")
    else:
        print("Kết nối tới Firestore thất bại, sử dụng storage manager thay thế")
        
        # Thử lưu vào local storage
        meal_plan = create_test_meal_plan()
        user_id = "test_firebase_connection"
        file_path = storage_manager.save_meal_plan(meal_plan, user_id)
        
        if file_path:
            print(f"Đã lưu thành công kế hoạch dinh dưỡng vào file: {file_path}")
            
            # Kiểm tra đọc dữ liệu
            loaded_plan = storage_manager.load_meal_plan(user_id)
            if loaded_plan:
                print(f"Đã đọc thành công kế hoạch dinh dưỡng từ file")
                print(f"Số ngày: {len(loaded_plan.days)}")
                print(f"Ngày đầu tiên: {loaded_plan.days[0].day_of_week}")
                return True
            else:
                print("Không thể đọc dữ liệu từ file")
        else:
            print("Không thể lưu dữ liệu vào file")
    
    return False

def create_test_meal_plan():
    """Tạo kế hoạch dinh dưỡng mẫu để kiểm tra lưu trữ"""
    # Tạo thông tin dinh dưỡng
    nutrition = NutritionInfo(calories=200, protein=20, fat=10, carbs=15)
    
    # Tạo 1 món ăn đơn giản
    dish = Dish(
        name="Test Dish",
        ingredients=[Ingredient(name="Test Ingredient", amount="100g")],
        preparation="Test preparation",
        nutrition=nutrition
    )
    
    # Tạo bữa ăn
    meal = Meal(dishes=[dish], nutrition=nutrition)
    
    # Tạo kế hoạch ngày
    day = DayMealPlan(
        day_of_week="Thứ 2",
        breakfast=meal,
        lunch=meal,
        dinner=meal,
        nutrition=nutrition
    )
    
    # Tạo kế hoạch tuần
    return WeeklyMealPlan(days=[day])

if __name__ == "__main__":
    check_firebase_connection() 