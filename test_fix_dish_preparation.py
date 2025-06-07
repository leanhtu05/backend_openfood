from services.meal_services import generate_dish
from models import Dish, Ingredient, NutritionInfo

# Kiểm tra với preparation là danh sách
def test_dish_with_list_preparation():
    print("\n=== KIỂM TRA CHUYỂN ĐỔI TỪ DANH SÁCH SANG CHUỖI ===\n")
    
    # Tạo recipe_dict với preparation là danh sách
    recipe_dict = {
        "name": "Món Ăn Kiểm Tra",
        "ingredients": [
            {"name": "Thịt gà", "amount": "100g"},
            {"name": "Rau xanh", "amount": "50g"},
            {"name": "Dầu ăn", "amount": "10ml"}
        ],
        "preparation": [
            "Bước 1: Chuẩn bị nguyên liệu",
            "Bước 2: Chế biến thịt gà",
            "Bước 3: Trộn với rau xanh",
            "Bước 4: Thêm dầu ăn và đảo đều"
        ],
        "nutrition": {
            "calories": 300,
            "protein": 25,
            "fat": 15,
            "carbs": 10
        }
    }
    
    # Tạo dish từ recipe_dict
    try:
        dish = generate_dish(recipe_dict)
        
        # Kiểm tra kết quả
        print(f"Tên món: {dish.name}")
        print(f"Loại preparation: {type(dish.preparation)}")
        print(f"Nội dung preparation: {dish.preparation}")
        
        # Xác nhận preparation là string
        if isinstance(dish.preparation, str):
            print(f"✅ Chuyển đổi thành công: preparation là string")
        else:
            print(f"❌ Chuyển đổi thất bại: preparation không phải string")
            
        return True
    except Exception as e:
        print(f"❌ Lỗi khi tạo dish: {str(e)}")
        return False

# Kiểm tra với preparation đã là chuỗi
def test_dish_with_string_preparation():
    print("\n=== KIỂM TRA VỚI PREPARATION ĐÃ LÀ CHUỖI ===\n")
    
    # Tạo recipe_dict với preparation là chuỗi
    recipe_dict = {
        "name": "Món Ăn Kiểm Tra 2",
        "ingredients": [
            {"name": "Cá hồi", "amount": "150g"},
            {"name": "Rau xanh", "amount": "50g"},
        ],
        "preparation": "Chuẩn bị nguyên liệu. Chế biến cá hồi. Trộn với rau xanh.",
        "nutrition": {
            "calories": 250,
            "protein": 30,
            "fat": 12,
            "carbs": 5
        }
    }
    
    # Tạo dish từ recipe_dict
    try:
        dish = generate_dish(recipe_dict)
        
        # Kiểm tra kết quả
        print(f"Tên món: {dish.name}")
        print(f"Loại preparation: {type(dish.preparation)}")
        print(f"Nội dung preparation: {dish.preparation}")
        
        # Xác nhận preparation là string
        if isinstance(dish.preparation, str):
            print(f"✅ Hoạt động tốt: preparation là string")
        else:
            print(f"❌ Lỗi: preparation không phải string")
            
        return True
    except Exception as e:
        print(f"❌ Lỗi khi tạo dish: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n===== KIỂM TRA SỬA LỖI PREPARATION TRONG DISH =====\n")
    
    list_test_result = test_dish_with_list_preparation()
    string_test_result = test_dish_with_string_preparation()
    
    if list_test_result and string_test_result:
        print("\n✅ TẤT CẢ CÁC KIỂM TRA ĐỀU THÀNH CÔNG")
    else:
        print("\n❌ MỘT SỐ KIỂM TRA THẤT BẠI") 