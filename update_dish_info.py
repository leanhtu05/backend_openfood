#!/usr/bin/env python3
"""
Script để cập nhật tất cả các bản ghi Dish trong Firestore với thông tin
preparation_time và health_benefits.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys
import time
import random
from typing import Dict, List, Any

# Cấu hình Firebase
FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
MEAL_PLANS_COLLECTION = "meal_plans"
LATEST_MEAL_PLANS_COLLECTION = "latest_meal_plans"

def initialize_firebase():
    """Khởi tạo kết nối Firebase."""
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        return db
    except Exception as e:
        print(f"Lỗi khi khởi tạo Firebase: {e}")
        sys.exit(1)

def get_all_meal_plans(db):
    """Lấy tất cả các bản ghi meal plan từ Firestore."""
    meal_plans = {}
    
    # Lấy từ collection meal_plans
    try:
        meal_plans_docs = db.collection(MEAL_PLANS_COLLECTION).stream()
        for doc in meal_plans_docs:
            meal_plans[f"{MEAL_PLANS_COLLECTION}/{doc.id}"] = doc.to_dict()
            print(f"Đã tải meal plan: {doc.id}")
    except Exception as e:
        print(f"Lỗi khi tải meal_plans: {e}")
    
    # Lấy từ collection latest_meal_plans
    try:
        latest_meal_plans_docs = db.collection(LATEST_MEAL_PLANS_COLLECTION).stream()
        for doc in latest_meal_plans_docs:
            meal_plans[f"{LATEST_MEAL_PLANS_COLLECTION}/{doc.id}"] = doc.to_dict()
            print(f"Đã tải latest meal plan: {doc.id}")
    except Exception as e:
        print(f"Lỗi khi tải latest_meal_plans: {e}")
    
    return meal_plans

def update_dish_info(dish_data: Dict[str, Any]):
    """Cập nhật thông tin preparation_time và health_benefits cho một dish."""
    if not dish_data:
        return dish_data
    
    # Kiểm tra xem dish đã có preparation_time chưa
    if "preparation_time" not in dish_data or not dish_data["preparation_time"]:
        # Tạo preparation_time ngẫu nhiên
        preparation_times = ["15-20 phút", "20-30 phút", "30-40 phút", "40-50 phút", "50-60 phút"]
        dish_data["preparation_time"] = random.choice(preparation_times)
    
    # Kiểm tra xem dish đã có health_benefits chưa
    if "health_benefits" not in dish_data or not dish_data["health_benefits"]:
        # Tạo health_benefits ngẫu nhiên
        possible_benefits = [
            "Giàu protein, tốt cho cơ bắp và sửa chữa các mô",
            "Cung cấp chất chống oxy hóa giúp tăng cường hệ miễn dịch",
            "Chứa các vitamin thiết yếu cho sức khỏe tổng thể",
            "Cung cấp năng lượng dồi dào cho hoạt động thể chất",
            "Giàu chất xơ, tốt cho hệ tiêu hóa",
            "Chứa các axit béo omega-3 tốt cho sức khỏe tim mạch",
            "Hỗ trợ quá trình trao đổi chất",
            "Giúp duy trì cân nặng lý tưởng",
            "Cung cấp canxi và vitamin D cho xương chắc khỏe",
            "Chứa chất chống viêm tự nhiên"
        ]
        
        # Chọn ngẫu nhiên 2-4 lợi ích
        num_benefits = random.randint(2, 4)
        dish_data["health_benefits"] = random.sample(possible_benefits, num_benefits)
    
    return dish_data

def update_dishes_in_meal_plan(meal_plan_data: Dict[str, Any]):
    """Cập nhật tất cả các dishes trong một meal plan."""
    if not meal_plan_data:
        return meal_plan_data
    
    # Xử lý cấu trúc dữ liệu mới (days)
    if "days" in meal_plan_data and isinstance(meal_plan_data["days"], list):
        for day_index, day in enumerate(meal_plan_data["days"]):
            # Cập nhật các bữa ăn
            for meal_type in ["breakfast", "lunch", "dinner"]:
                if meal_type in day and "dishes" in day[meal_type]:
                    for dish_index, dish in enumerate(day[meal_type]["dishes"]):
                        updated_dish = update_dish_info(dish)
                        meal_plan_data["days"][day_index][meal_type]["dishes"][dish_index] = updated_dish
    
    # Xử lý cấu trúc dữ liệu cũ (weekly_plan)
    if "weekly_plan" in meal_plan_data and isinstance(meal_plan_data["weekly_plan"], dict):
        for day_key, day_data in meal_plan_data["weekly_plan"].items():
            if "meals" in day_data and isinstance(day_data["meals"], dict):
                for meal_type, meals in day_data["meals"].items():
                    for meal_index, meal in enumerate(meals):
                        if "dishes" in meal and isinstance(meal["dishes"], list):
                            for dish_index, dish in enumerate(meal["dishes"]):
                                updated_dish = update_dish_info(dish)
                                meal_plan_data["weekly_plan"][day_key]["meals"][meal_type][meal_index]["dishes"][dish_index] = updated_dish
    
    return meal_plan_data

def update_firestore_documents(db, meal_plans):
    """Cập nhật lại tất cả các document trong Firestore."""
    for path, meal_plan_data in meal_plans.items():
        try:
            # Tách collection và document ID từ path
            collection_name, doc_id = path.split("/")
            
            # Cập nhật dữ liệu
            updated_data = update_dishes_in_meal_plan(meal_plan_data)
            
            # Ghi lại vào Firestore
            db.collection(collection_name).document(doc_id).set(updated_data)
            print(f"Đã cập nhật: {path}")
            
            # Đợi một chút để tránh quá tải Firestore
            time.sleep(0.2)
        except Exception as e:
            print(f"Lỗi khi cập nhật {path}: {e}")

def main():
    """Hàm chính để chạy script."""
    print("Bắt đầu cập nhật thông tin dish trong Firestore...")
    
    # Khởi tạo Firebase
    db = initialize_firebase()
    
    # Lấy tất cả các meal plan
    meal_plans = get_all_meal_plans(db)
    print(f"Đã tải {len(meal_plans)} meal plans")
    
    # Cập nhật thông tin dish
    update_firestore_documents(db, meal_plans)
    
    print("Hoàn thành cập nhật!")

if __name__ == "__main__":
    main() 