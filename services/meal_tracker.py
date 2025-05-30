"""
Module quản lý theo dõi các món ăn đã sử dụng để tránh trùng lặp.
"""

# Biến toàn cục để theo dõi món ăn đã sử dụng
used_dishes_tracker = {
    "breakfast": set(),
    "lunch": set(),
    "dinner": set()
}

def reset_tracker():
    """Reset toàn bộ tracker về trạng thái ban đầu."""
    global used_dishes_tracker
    used_dishes_tracker = {
        "breakfast": set(),
        "lunch": set(),
        "dinner": set()
    }

def reset_meal_type(meal_type: str):
    """
    Reset tracker cho một loại bữa ăn cụ thể.
    
    Args:
        meal_type: Loại bữa ăn (breakfast, lunch, dinner)
    """
    global used_dishes_tracker
    if meal_type in used_dishes_tracker:
        used_dishes_tracker[meal_type] = set()

def add_dish(meal_type: str, dish_name: str):
    """
    Thêm một món ăn vào tracker.
    
    Args:
        meal_type: Loại bữa ăn (breakfast, lunch, dinner)
        dish_name: Tên món ăn
    """
    global used_dishes_tracker
    if meal_type in used_dishes_tracker:
        used_dishes_tracker[meal_type].add(dish_name)

def is_dish_used(meal_type: str, dish_name: str) -> bool:
    """
    Kiểm tra xem một món ăn đã được sử dụng chưa.
    
    Args:
        meal_type: Loại bữa ăn (breakfast, lunch, dinner)
        dish_name: Tên món ăn
        
    Returns:
        bool: True nếu món ăn đã được sử dụng, False nếu chưa
    """
    global used_dishes_tracker
    if meal_type in used_dishes_tracker:
        return dish_name in used_dishes_tracker[meal_type]
    return False

def get_used_dishes(meal_type: str) -> set:
    """
    Lấy danh sách các món ăn đã sử dụng cho một loại bữa ăn.
    
    Args:
        meal_type: Loại bữa ăn (breakfast, lunch, dinner)
        
    Returns:
        set: Tập hợp các tên món ăn đã sử dụng
    """
    global used_dishes_tracker
    if meal_type in used_dishes_tracker:
        return used_dishes_tracker[meal_type].copy()
    return set() 