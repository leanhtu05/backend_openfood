"""
Script để sửa lỗi tính toán dinh dưỡng trong food_records

Vấn đề: Thông tin dinh dưỡng (nutritionInfo) trong food_records
chỉ đang chứa thông tin của món đầu tiên thay vì tổng dinh dưỡng
của tất cả các món trong danh sách.

Script này sẽ:
1. Lấy tất cả food_records từ Firestore
2. Tính lại tổng dinh dưỡng từ danh sách items
3. Cập nhật lại thông tin dinh dưỡng trong Firestore
"""

import firebase_admin
from firebase_admin import credentials, firestore
import argparse
import time
from datetime import datetime
import traceback


def init_firebase():
    """Khởi tạo kết nối Firebase"""
    try:
        # Kiểm tra xem đã khởi tạo chưa
        firebase_admin.get_app()
        print("Firebase Admin SDK đã được khởi tạo trước đó.")
    except ValueError:
        # Nếu chưa khởi tạo, thì khởi tạo mới
        try:
            cred = credentials.Certificate("firebase-credentials.json")
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK đã được khởi tạo thành công.")
        except Exception as e:
            print(f"Lỗi khi khởi tạo Firebase Admin SDK: {e}")
            return False
    return True


def calculate_total_nutrition(food_items):
    """Tính tổng dinh dưỡng từ danh sách món ăn"""
    total_nutrition = {
        'calories': 0,
        'protein': 0,
        'carbs': 0,
        'fat': 0,
        'fiber': 0,
        'sugar': 0,
        'sodium': 0
    }
    
    for item in food_items:
        # Cộng dồn các giá trị dinh dưỡng
        total_nutrition['calories'] += item.get('calories', 0)
        total_nutrition['protein'] += item.get('protein', 0)
        total_nutrition['carbs'] += item.get('carbs', 0)
        total_nutrition['fat'] += item.get('fat', 0)
        
        # Các giá trị có thể không có trong tất cả các món
        if 'fiber' in item:
            total_nutrition['fiber'] += item.get('fiber', 0)
        if 'sugar' in item:
            total_nutrition['sugar'] += item.get('sugar', 0)
        if 'sodium' in item:
            total_nutrition['sodium'] += item.get('sodium', 0)
    
    return total_nutrition


def fix_food_logs(user_id=None, dry_run=True):
    """
    Sửa lỗi tính toán dinh dưỡng trong food_records
    
    Args:
        user_id: ID của người dùng cần sửa. Nếu None, sửa tất cả người dùng.
        dry_run: Nếu True, chỉ in ra thông tin thay đổi mà không cập nhật thực sự.
    """
    db = firestore.client()
    
    # Đếm số lượng bản ghi được xử lý
    stats = {
        'total_processed': 0,
        'updated': 0,
        'skipped': 0,
        'errors': 0
    }
    
    try:
        # Nếu có user_id, chỉ xử lý bản ghi của người dùng đó
        if user_id:
            users_ref = [db.collection('users').document(user_id)]
        else:
            # Lấy tất cả người dùng
            users_ref = db.collection('users').stream()
        
        # Duyệt qua từng người dùng
        for user_doc in users_ref:
            current_user_id = user_id if user_id else user_doc.id
            print(f"\nXử lý user_id: {current_user_id}")
            
            # Lấy tất cả food_records của người dùng
            food_logs_ref = db.collection('users').document(current_user_id).collection('food_records').stream()
            
            # Duyệt qua từng bản ghi
            for log in food_logs_ref:
                stats['total_processed'] += 1
                log_data = log.to_dict()
                log_id = log.id
                
                print(f"\nBản ghi {log_id}:")
                
                # Kiểm tra xem có items không
                if 'items' not in log_data or not isinstance(log_data['items'], list) or not log_data['items']:
                    print(f"  Bỏ qua: Không có items hoặc items rỗng")
                    stats['skipped'] += 1
                    continue
                
                # Tính lại tổng dinh dưỡng
                new_nutrition = calculate_total_nutrition(log_data['items'])
                
                # So sánh với dinh dưỡng hiện tại
                current_nutrition = log_data.get('nutritionInfo', {})
                current_calories = log_data.get('calories', 0)
                
                print(f"  Calories hiện tại: {current_calories}")
                print(f"  Calories mới tính: {new_nutrition['calories']}")
                
                # Nếu không có sự khác biệt đáng kể, bỏ qua
                if abs(current_calories - new_nutrition['calories']) < 1:
                    print(f"  Bỏ qua: Dinh dưỡng đã đúng")
                    stats['skipped'] += 1
                    continue
                
                # Cập nhật dữ liệu
                update_data = {
                    'nutritionInfo': new_nutrition,
                    'calories': new_nutrition['calories'],
                    'updated_at': datetime.now().isoformat()
                }
                
                print(f"  Cập nhật dinh dưỡng:")
                print(f"    - Protein: {current_nutrition.get('protein', 0)} -> {new_nutrition['protein']}")
                print(f"    - Carbs: {current_nutrition.get('carbs', 0)} -> {new_nutrition['carbs']}")
                print(f"    - Fat: {current_nutrition.get('fat', 0)} -> {new_nutrition['fat']}")
                
                if not dry_run:
                    try:
                        # Cập nhật vào Firestore
                        db.collection('users').document(current_user_id).collection('food_records').document(log_id).update(update_data)
                        print(f"  ✅ Đã cập nhật thành công!")
                        stats['updated'] += 1
                    except Exception as e:
                        print(f"  ❌ Lỗi khi cập nhật: {e}")
                        stats['errors'] += 1
                else:
                    print(f"  🔍 (Chế độ dry-run) Sẽ cập nhật dữ liệu")
                    stats['updated'] += 1
    
    except Exception as e:
        print(f"Lỗi khi xử lý food_records: {e}")
        traceback.print_exc()
    
    # In thống kê
    print("\n=== KẾT QUẢ ===")
    print(f"Tổng số bản ghi đã xử lý: {stats['total_processed']}")
    print(f"Số bản ghi cập nhật: {stats['updated']}")
    print(f"Số bản ghi bỏ qua: {stats['skipped']}")
    print(f"Số lỗi: {stats['errors']}")
    print(f"Mode: {'Dry-run (không cập nhật thực tế)' if dry_run else 'Cập nhật thực tế'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sửa lỗi tính toán dinh dưỡng trong food_records')
    parser.add_argument('--user-id', help='ID của người dùng cần sửa. Nếu không có, sửa tất cả người dùng.')
    parser.add_argument('--apply', action='store_true', help='Áp dụng thay đổi thực tế vào Firestore. Nếu không có, chỉ in ra thay đổi tiềm năng.')
    
    args = parser.parse_args()
    
    if init_firebase():
        fix_food_logs(user_id=args.user_id, dry_run=not args.apply)
    else:
        print("Không thể khởi tạo Firebase, hủy thao tác.") 