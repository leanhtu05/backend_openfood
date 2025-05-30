import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import sys
from datetime import datetime

# Kiểm tra xem Firebase đã được khởi tạo chưa
try:
    app = firebase_admin.get_app()
    print("Firebase đã được khởi tạo trước đó")
except ValueError:
    # Nếu chưa khởi tạo, tìm file credentials
    cred_paths = [
        "firebase-credentials.json",
        os.path.join(os.path.dirname(__file__), "firebase-credentials.json")
    ]
    
    cred = None
    for path in cred_paths:
        if os.path.exists(path):
            print(f"Sử dụng credentials từ: {path}")
            cred = credentials.Certificate(path)
            break
    
    if cred is None:
        print("Không tìm thấy file credentials Firebase!")
        sys.exit(1)
        
    firebase_admin.initialize_app(cred)
    print("Firebase đã được khởi tạo thành công")

# Khởi tạo Firestore client
db = firestore.client()

def verify_user_data(user_id=None):
    """
    Kiểm tra dữ liệu người dùng trong Firestore
    
    Args:
        user_id: ID của người dùng cần kiểm tra (nếu không cung cấp, sẽ yêu cầu nhập)
    """
    if not user_id:
        user_id = input("Nhập Firebase UID của người dùng cần kiểm tra: ")
    
    print(f"\n=== ĐANG KIỂM TRA DỮ LIỆU NGƯỜI DÙNG: {user_id} ===\n")
    
    try:
        # Lấy dữ liệu người dùng từ Firestore
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc.exists:
            print(f"❌ Không tìm thấy người dùng với ID: {user_id}")
            return False
        
        # Lấy dữ liệu người dùng
        user_data = user_doc.to_dict()
        
        # Hiển thị thông tin
        print("✅ Tìm thấy dữ liệu người dùng trong Firestore:")
        print(f"  - Tên: {user_data.get('name', 'Không có')}")
        print(f"  - Email: {user_data.get('email', 'Không có')}")
        print(f"  - Tuổi: {user_data.get('age', 'Không có')}")
        print(f"  - Giới tính: {user_data.get('gender', 'Không có')}")
        print(f"  - Chiều cao: {user_data.get('height', 'Không có')} cm")
        print(f"  - Cân nặng: {user_data.get('weight', 'Không có')} kg")
        print(f"  - Mục tiêu: {user_data.get('goal', 'Không có')}")
        print(f"  - Mức độ hoạt động: {user_data.get('activityLevel', 'Không có')}")
        
        # Kiểm tra thời gian cập nhật
        updated_at = user_data.get('updated_at')
        if updated_at:
            try:
                # Chuyển đổi chuỗi ISO thành đối tượng datetime
                updated_datetime = datetime.fromisoformat(updated_at)
                # Tính thời gian trôi qua
                time_diff = datetime.now() - updated_datetime
                
                if time_diff.total_seconds() < 3600:  # Trong vòng 1 giờ
                    print(f"✅ Dữ liệu đã được cập nhật gần đây: {updated_at}")
                else:
                    print(f"⚠️ Dữ liệu đã được cập nhật cách đây {time_diff.days} ngày {time_diff.seconds // 3600} giờ: {updated_at}")
            except:
                print(f"⚠️ Không thể phân tích thời gian cập nhật: {updated_at}")
        else:
            print("⚠️ Không tìm thấy thời gian cập nhật")
        
        # Hiển thị thông tin TDEE nếu có
        tdee_values = user_data.get('tdeeValues')
        if tdee_values:
            print("\nThông tin TDEE:")
            print(f"  - Calories: {tdee_values.get('calories', 'Không có')}")
            print(f"  - Protein: {tdee_values.get('protein', 'Không có')} g")
            print(f"  - Carbs: {tdee_values.get('carbs', 'Không có')} g")
            print(f"  - Fat: {tdee_values.get('fat', 'Không có')} g")
        
        # Hiển thị thông tin sở thích và dị ứng nếu có
        preferred_cuisines = user_data.get('preferred_cuisines', [])
        if preferred_cuisines:
            print("\nẨm thực ưa thích:")
            for cuisine in preferred_cuisines:
                print(f"  - {cuisine}")
        
        allergies = user_data.get('allergies', [])
        if allergies:
            print("\nDị ứng thực phẩm:")
            for allergy in allergies:
                print(f"  - {allergy}")
        
        # Hiển thị toàn bộ dữ liệu dưới dạng JSON
        print("\nDữ liệu đầy đủ:")
        print(json.dumps(user_data, indent=2, ensure_ascii=False))
        
        return True
    except Exception as e:
        print(f"❌ Lỗi khi kiểm tra dữ liệu người dùng: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Kiểm tra xem có tham số dòng lệnh không
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        user_id = None
    
    verify_user_data(user_id) 