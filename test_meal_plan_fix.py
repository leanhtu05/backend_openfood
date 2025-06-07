from services.firestore_service import firestore_service
import json
from typing import Dict, Any, List

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

# Chạy hàm sửa
if __name__ == "__main__":
    fix_meal_plan() 