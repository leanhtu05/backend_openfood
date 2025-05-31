"""
Services package for the application.
"""

# Import services for easy use
from .firestore_service import firestore_service

# Import from meal_services with explicit relative import
from .meal_services import (
    generate_weekly_meal_plan,
    generate_day_meal_plan,
    replace_day_meal_plan,
    create_fallback_meal,
    generate_meal,
    used_dishes_tracker
)

# Define the functions we need to expose
__all__ = [
    'firestore_service', 
    'generate_weekly_meal_plan', 
    'replace_day_meal_plan', 
    'generate_day_meal_plan', 
    'create_fallback_meal', 
    'generate_meal',
    'used_dishes_tracker'
]

# Print debug info to verify the correct function is being used
print(f"[DEBUG] Imported generate_weekly_meal_plan from {generate_weekly_meal_plan.__module__}")