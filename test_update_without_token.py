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

def update_user_directly():
    """Cập nhật thông tin người dùng trực tiếp vào Firestore không qua API"""
    
    # Nhập ID người dùng
    user_id = input("Nhập Firebase UID của người dùng cần cập nhật: ")
    
    # Kiểm tra xem người dùng có tồn tại không
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    
    if not user_doc.exists:
        print(f"❌ Không tìm thấy người dùng với ID: {user_id}")
        create_new = input("Bạn có muốn tạo người dùng mới không? (y/n): ")
        if create_new.lower() != 'y':
            return
    else:
        print(f"✅ Tìm thấy người dùng: {user_id}")
        user_data = user_doc.to_dict()
        print(f"Thông tin hiện tại:")
        print(f"  - Tên: {user_data.get('name', 'Không có')}")
        print(f"  - Email: {user_data.get('email', 'Không có')}")
    
    # Dữ liệu cập nhật
    update_data = {
        "name": input("Nhập tên (để trống nếu không muốn cập nhật): ") or None,
        "age": input("Nhập tuổi (để trống nếu không muốn cập nhật): ") or None,
        "gender": input("Nhập giới tính (male/female/other, để trống nếu không muốn cập nhật): ") or None,
        "height": input("Nhập chiều cao (cm, để trống nếu không muốn cập nhật): ") or None,
        "weight": input("Nhập cân nặng (kg, để trống nếu không muốn cập nhật): ") or None,
        "goal": input("Nhập mục tiêu (giảm cân/tăng cân/giữ cân, để trống nếu không muốn cập nhật): ") or None,
        "activityLevel": input("Nhập mức độ hoạt động (low/moderate/high, để trống nếu không muốn cập nhật): ") or None,
        "updated_at": datetime.now().isoformat()
    }
    
    # Loại bỏ các trường None
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    # Chuyển đổi các trường số
    if "age" in update_data and update_data["age"]:
        try:
            update_data["age"] = int(update_data["age"])
        except:
            print(f"⚠️ Không thể chuyển đổi tuổi thành số nguyên, sẽ bỏ qua trường này")
            del update_data["age"]
    
    if "height" in update_data and update_data["height"]:
        try:
            update_data["height"] = float(update_data["height"])
        except:
            print(f"⚠️ Không thể chuyển đổi chiều cao thành số thực, sẽ bỏ qua trường này")
            del update_data["height"]
    
    if "weight" in update_data and update_data["weight"]:
        try:
            update_data["weight"] = float(update_data["weight"])
        except:
            print(f"⚠️ Không thể chuyển đổi cân nặng thành số thực, sẽ bỏ qua trường này")
            del update_data["weight"]
    
    # Hiển thị dữ liệu cập nhật
    print("\nDữ liệu cập nhật:")
    print(json.dumps(update_data, indent=2, ensure_ascii=False))
    
    # Xác nhận cập nhật
    confirm = input("\nXác nhận cập nhật? (y/n): ")
    if confirm.lower() != 'y':
        print("Đã hủy cập nhật")
        return
    
    # Cập nhật dữ liệu
    try:
        user_ref.set(update_data, merge=True)
        print("\n✅ Đã cập nhật thông tin người dùng thành công!")
        
        # Hiển thị dữ liệu mới
        print("\nĐang lấy dữ liệu mới...")
        new_doc = user_ref.get()
        new_data = new_doc.to_dict()
        
        print("\nDữ liệu người dùng sau khi cập nhật:")
        print(json.dumps(new_data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n❌ Lỗi khi cập nhật dữ liệu: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    update_user_directly() 