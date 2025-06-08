from services.firestore_service import firestore_service
import json
from typing import Dict, Any, List
import os
import time
from services.meal_services import generate_day_meal_plan

# ID người dùng cần kiểm tra
USER_ID = "49DhdmJHFAY40eEgaPNEJqGdDQK2"

def fix_preparation_in_dishes(data: Dict) -> Dict:
    """
    Tìm và sửa tất cả trường preparation trong dishes từ list sang string
    
    Args:
        data: Dữ liệu meal plan
        
    Returns:
        Dữ liệu đã được sửa
    """
    # Tạo bản sao để không ảnh hưởng dữ liệu gốc
    fixed_data = data.copy()
    changes_made = 0
    
    # Duyệt qua tất cả ngày
    if 'days' in fixed_data:
        for day_idx, day in enumerate(fixed_data['days']):
            # Duyệt qua tất cả bữa ăn
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                if meal_type in day:
                    # Duyệt qua tất cả món ăn
                    if 'dishes' in day[meal_type]:
                        for dish_idx, dish in enumerate(day[meal_type]['dishes']):
                            # Kiểm tra và sửa trường preparation
                            if 'preparation' in dish:
                                if isinstance(dish['preparation'], list):
                                    # Chuyển đổi từ list sang string
                                    old_value = dish['preparation']
                                    dish['preparation'] = '\n'.join(str(step) for step in dish['preparation'])
                                    print(f"✏️ Đã sửa preparation cho món {dish.get('name', f'Món {dish_idx+1}')} "
                                          f"trong {meal_type} của ngày {day.get('day_of_week', f'Ngày {day_idx+1}')} "
                                          f"từ {old_value} thành '{dish['preparation'][:30]}...'")
                                    changes_made += 1
    
    print(f"\n✅ Đã sửa {changes_made} trường preparation từ list sang string")
    return fixed_data

def fix_meal_plan():
    """
    Kiểm tra và sửa kế hoạch ăn cho người dùng cụ thể
    """
    print(f"\n=== KIỂM TRA VÀ SỬA KẾ HOẠCH ĂN CHO USER {USER_ID} ===\n")
    
    # Đọc dữ liệu trực tiếp từ Firestore
    doc_ref = firestore_service.db.collection('latest_meal_plans').document(USER_ID)
    doc = doc_ref.get()
    
    if not doc.exists:
        print(f"❌ Không tìm thấy kế hoạch ăn cho user {USER_ID} trong Firestore")
        return
    
    print(f"✅ Tìm thấy kế hoạch ăn trong Firestore")
    data = doc.to_dict()
    
    # Sửa trường preparation
    fixed_data = fix_preparation_in_dishes(data)
    
    # Hiển thị thông tin cho người dùng
    if data == fixed_data:
        print("✅ Không cần sửa, tất cả các trường preparation đã đúng định dạng string")
        return
    
    # Lưu lại dữ liệu đã sửa
    print("\n🔄 Đang lưu dữ liệu đã sửa vào Firestore...")
    doc_ref.set(fixed_data)
    print("✅ Đã lưu dữ liệu thành công!")

def test_meal_plan_generation_and_storage():
    """Kiểm tra toàn bộ quy trình từ việc tạo kế hoạch bữa ăn đến lưu trữ trong Firestore"""
    
    print("=== Bắt đầu kiểm tra quy trình kế hoạch bữa ăn ===")
    
    # Tạo kế hoạch bữa ăn cho một ngày
    print("\n1. Tạo kế hoạch bữa ăn cho một ngày...")
    day_meal_plan = generate_day_meal_plan(
        day_of_week="Thứ 2",
        calories_target=2000,
        protein_target=150,
        fat_target=67,
        carbs_target=200,
        use_ai=False  # Không sử dụng AI để tránh gọi API thật
    )
    
    # Kiểm tra xem day_meal_plan có đúng định dạng không
    print("\n2. Kiểm tra cấu trúc kế hoạch bữa ăn...")
    assert day_meal_plan is not None, "Không thể tạo kế hoạch bữa ăn"
    assert hasattr(day_meal_plan, "breakfast"), "Kế hoạch bữa ăn thiếu bữa sáng"
    assert hasattr(day_meal_plan, "lunch"), "Kế hoạch bữa ăn thiếu bữa trưa"
    assert hasattr(day_meal_plan, "dinner"), "Kế hoạch bữa ăn thiếu bữa tối"
    
    # Kiểm tra preparation_time và health_benefits trong từng món ăn
    print("\n3. Kiểm tra các trường preparation_time và health_benefits...")
    meal_types = ["breakfast", "lunch", "dinner"]
    for meal_type in meal_types:
        meal = getattr(day_meal_plan, meal_type)
        print(f"\nKiểm tra {meal_type}:")
        print(f"- Số món ăn: {len(meal.dishes)}")
        
        for i, dish in enumerate(meal.dishes):
            print(f"  Món {i+1}: {dish.name}")
            print(f"  - preparation_time: {dish.preparation_time}")
            print(f"  - health_benefits: {dish.health_benefits}")
            
            # Kiểm tra
            assert dish.preparation_time is not None, f"preparation_time bị thiếu trong món {dish.name}"
            assert dish.health_benefits is not None, f"health_benefits bị thiếu trong món {dish.name}"
    
    # Chuyển đổi kế hoạch bữa ăn thành dữ liệu để lưu vào Firestore
    print("\n4. Chuyển đổi kế hoạch bữa ăn thành dữ liệu để lưu vào Firestore...")
    day_meal_plan_dict = day_meal_plan.dict()
    
    # Tạo dữ liệu kế hoạch bữa ăn mẫu
    meal_plan_data = {
        "user_id": f"test_user_{int(time.time())}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S") + ".000000",
        "days": [day_meal_plan_dict],
    }
    
    # Lưu vào Firestore
    print("\n5. Lưu kế hoạch bữa ăn vào Firestore...")
    try:
        # Trước tiên, kiểm tra xem dữ liệu đã được chuyển đổi đúng chưa
        transformed_data = firestore_service._transform_meal_plan_data(meal_plan_data)
        
        # Kiểm tra các trường trong dữ liệu đã chuyển đổi
        print("\n6. Kiểm tra dữ liệu sau khi chuyển đổi...")
        
        # Lấy một món ăn từ bữa sáng để kiểm tra
        breakfast_dish = transformed_data["days"][0]["breakfast"]["dishes"][0]
        print(f"\nKiểm tra món ăn trong bữa sáng: {breakfast_dish.get('name')}")
        print(f"- preparation_time: {breakfast_dish.get('preparation_time')}")
        print(f"- health_benefits: {breakfast_dish.get('health_benefits')}")
        
        # Kiểm tra
        assert 'preparation_time' in breakfast_dish, "preparation_time bị mất trong dữ liệu đã chuyển đổi"
        assert 'health_benefits' in breakfast_dish, "health_benefits bị mất trong dữ liệu đã chuyển đổi"
        
        # Lưu vào Firestore
        user_id = meal_plan_data["user_id"]
        success = firestore_service.save_meal_plan(user_id, meal_plan_data)
        
        if success:
            print(f"\n7. Đã lưu kế hoạch bữa ăn vào Firestore thành công với user_id: {user_id}")
            
            # Lấy lại từ Firestore để kiểm tra
            print("\n8. Lấy lại kế hoạch bữa ăn từ Firestore...")
            retrieved_data = firestore_service.get_meal_plan(user_id)
            
            # Kiểm tra dữ liệu đã lấy lại
            print("\n9. Kiểm tra dữ liệu đã lấy lại từ Firestore...")
            if retrieved_data:
                # Lấy một món ăn từ bữa sáng để kiểm tra
                if "days" in retrieved_data and len(retrieved_data["days"]) > 0:
                    day_data = retrieved_data["days"][0]
                    if "breakfast" in day_data and "dishes" in day_data["breakfast"] and len(day_data["breakfast"]["dishes"]) > 0:
                        retrieved_dish = day_data["breakfast"]["dishes"][0]
                        print(f"\nKiểm tra món ăn đã lấy lại: {retrieved_dish.get('name')}")
                        print(f"- preparation_time: {retrieved_dish.get('preparation_time')}")
                        print(f"- health_benefits: {retrieved_dish.get('health_benefits')}")
                        
                        # Kiểm tra
                        assert 'preparation_time' in retrieved_dish, "preparation_time bị mất trong dữ liệu đã lấy lại"
                        assert 'health_benefits' in retrieved_dish, "health_benefits bị mất trong dữ liệu đã lấy lại"
                        
                        print("\n=== Tất cả kiểm tra đã hoàn thành thành công! ===")
                        return True
                    else:
                        print("Không tìm thấy món ăn trong dữ liệu đã lấy lại")
                else:
                    print("Không tìm thấy ngày trong dữ liệu đã lấy lại")
            else:
                print("Không lấy được dữ liệu từ Firestore")
        else:
            print("Lưu vào Firestore thất bại")
            
        return False
    except Exception as e:
        print(f"Lỗi khi lưu hoặc lấy lại dữ liệu: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Chạy hàm sửa
if __name__ == "__main__":
    fix_meal_plan()
    test_meal_plan_generation_and_storage() 