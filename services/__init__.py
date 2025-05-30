"""
Services package for the application.
"""

# Import services for easy use
from services.firestore_service import firestore_service

# Import từ services.py
from services.meal_services import (
    generate_weekly_meal_plan,
    generate_day_meal_plan,
    replace_day_meal_plan,
    create_fallback_meal,
    generate_meal,
    used_dishes_tracker
)

# Fix imports by exposing symbols from the root services.py
# This avoids circular imports by not directly importing from services.py
import importlib.util
import sys
import os

# Define the functions we need to expose
__all__ = ['firestore_service', 'generate_weekly_meal_plan', 'replace_day_meal_plan', 
           'generate_day_meal_plan', 'create_fallback_meal', 'generate_meal',
           'used_dishes_tracker']

# Các mock functions đã bị xóa - Sử dụng trực tiếp các functions từ meal_services.py 