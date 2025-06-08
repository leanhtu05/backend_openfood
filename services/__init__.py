"""
Services package for the application.
"""

# Import services for easy use
from .firestore_service import firestore_service

# Export hàm process_preparation_steps từ module riêng biệt
from .preparation_utils import process_preparation_steps

# Định nghĩa các hàm cần export
__all__ = [
    'firestore_service',
    'process_preparation_steps'
]

# Import các function sau khi đã export các module cần thiết
# để tránh circular import
from .meal_services import (
    generate_weekly_meal_plan,
    generate_day_meal_plan,
    replace_day_meal_plan,
    create_fallback_meal,
    generate_meal,
    used_dishes_tracker
)

# Cập nhật __all__ với các hàm mới import
__all__.extend([
    'generate_weekly_meal_plan', 
    'replace_day_meal_plan', 
    'generate_day_meal_plan', 
    'create_fallback_meal', 
    'generate_meal',
    'used_dishes_tracker'
])

# Print debug info to verify the correct function is being used
print(f"[DEBUG] Imported generate_weekly_meal_plan from {generate_weekly_meal_plan.__module__}")