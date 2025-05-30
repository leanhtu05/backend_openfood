import time
import uuid
from datetime import datetime
from firebase_integration import firebase
from models.firestore_models import UserProfile, DailyLog, FoodIntake

def test_firebase_direct():
    """Kiểm tra trực tiếp Firebase Integration"""
    
    # Tạo ID người dùng test ngẫu nhiên
    user_id = f"firebase_test_{int(time.time())}"
    print(f"\n=== BẮT ĐẦU KIỂM TRA TRỰC TIẾP VỚI USER_ID: {user_id} ===")
    
    # BƯỚC 1: Tạo người dùng
    print("\n--- BƯỚC 1: Tạo người dùng mới ---")
    user_data = UserProfile(
        name="Người dùng Test Firebase",
        email=f"test_{user_id}@example.com",
        height=170,
        weight=65,
        age=30,
        gender="male",
        activityLevel="moderate",
        goal="maintain_weight",
        targetCalories=2000,
        allergies=["tôm", "cua"],
        preferred_cuisines=["Việt Nam", "Nhật Bản"]
    )
    
    try:
        success = firebase.create_user(user_id, user_data)
        if success:
            print("✅ Đã tạo người dùng thành công!")
            user_created = True
        else:
            print("❌ Không thể tạo người dùng")
            user_created = False
    except Exception as e:
        print(f"❌ Lỗi khi tạo người dùng: {str(e)}")
        user_created = False
    
    # BƯỚC 2: Đọc thông tin người dùng
    print("\n--- BƯỚC 2: Đọc thông tin người dùng ---")
    try:
        user_info = firebase.get_user(user_id)
        if user_info:
            print(f"Thông tin người dùng: {user_info}")
            print("✅ Đã đọc thông tin người dùng thành công!")
            user_verified = True
        else:
            print("❌ Không thể đọc thông tin người dùng")
            user_verified = False
    except Exception as e:
        print(f"❌ Lỗi khi đọc thông tin người dùng: {str(e)}")
        user_verified = False
    
    # Trực tiếp truy cập Firestore để thêm dữ liệu nếu cần
    # Thêm bản ghi nhật ký hàng ngày
    if firebase.db:
        print("\n--- BƯỚC 3: Thêm bản ghi nhật ký hàng ngày ---")
        today = datetime.now().strftime("%Y-%m-%d")
        try:
            daily_log = DailyLog(
                date=today,
                caloriesIntake=1850,
                meals=["Cơm gà", "Phở bò", "Salad rau"]
            )
            
            firebase.db.collection('users').document(user_id).collection('daily_logs').document(today).set(daily_log.to_dict())
            print("✅ Đã thêm bản ghi nhật ký hàng ngày thành công!")
            log_created = True
        except Exception as e:
            print(f"❌ Không thể thêm bản ghi nhật ký: {str(e)}")
            log_created = False
            
        # Đọc bản ghi nhật ký
        print("\n--- BƯỚC 4: Đọc bản ghi nhật ký hàng ngày ---")
        try:
            doc = firebase.db.collection('users').document(user_id).collection('daily_logs').document(today).get()
            if doc.exists:
                log_data = doc.to_dict()
                print(f"Bản ghi nhật ký: {log_data}")
                print("✅ Đã đọc bản ghi nhật ký thành công!")
                log_verified = True
            else:
                print("❌ Không tìm thấy bản ghi nhật ký")
                log_verified = False
        except Exception as e:
            print(f"❌ Không thể đọc bản ghi nhật ký: {str(e)}")
            log_verified = False
            
        # Thêm thông tin tiêu thụ thực phẩm
        print("\n--- BƯỚC 5: Thêm thông tin tiêu thụ thực phẩm ---")
        try:
            food_intake = FoodIntake(
                userId=user_id,
                foodId=str(uuid.uuid4())[:8],
                food_name="Phở bò tái chín",
                date=today,
                meal_type="lunch",
                amount_g=350,
                calories=480,
                protein=25,
                fat=12,
                carbs=65,
                notes="Ăn tại nhà hàng"
            )
            
            doc_ref = firebase.db.collection('food_intake').document()
            doc_ref.set(food_intake.to_dict())
            food_id = doc_ref.id
            print(f"Đã thêm thông tin tiêu thụ thực phẩm với ID: {food_id}")
            print("✅ Đã thêm thông tin tiêu thụ thực phẩm thành công!")
            food_intake_created = True
        except Exception as e:
            print(f"❌ Không thể thêm thông tin tiêu thụ thực phẩm: {str(e)}")
            food_intake_created = False
            
        # Đọc thông tin tiêu thụ thực phẩm
        print("\n--- BƯỚC 6: Đọc thông tin tiêu thụ thực phẩm ---")
        try:
            docs = firebase.db.collection('food_intake').where("userId", "==", user_id).get()
            if docs:
                intakes = [doc.to_dict() for doc in docs]
                print(f"Số lượng bản ghi tiêu thụ thực phẩm: {len(intakes)}")
                if intakes:
                    print(f"Thông tin tiêu thụ thực phẩm đầu tiên: {intakes[0]}")
                print("✅ Đã đọc thông tin tiêu thụ thực phẩm thành công!")
                food_intake_verified = True
            else:
                print("❌ Không tìm thấy thông tin tiêu thụ thực phẩm")
                food_intake_verified = False
        except Exception as e:
            print(f"❌ Không thể đọc thông tin tiêu thụ thực phẩm: {str(e)}")
            food_intake_verified = False
    else:
        print("\n❌ Không thể kết nối với Firestore")
        log_created = log_verified = food_intake_created = food_intake_verified = False
    
    # Tổng kết
    print("\n=== KẾT QUẢ KIỂM TRA ===")
    print(f"ID người dùng: {user_id}")
    print(f"Tạo người dùng: {'✅ THÀNH CÔNG' if user_created else '❌ THẤT BẠI'}")
    print(f"Đọc thông tin người dùng: {'✅ THÀNH CÔNG' if user_verified else '❌ THẤT BẠI'}")
    print(f"Thêm bản ghi nhật ký: {'✅ THÀNH CÔNG' if log_created else '❌ THẤT BẠI'}")
    print(f"Đọc bản ghi nhật ký: {'✅ THÀNH CÔNG' if log_verified else '❌ THẤT BẠI'}")
    print(f"Thêm thông tin tiêu thụ thực phẩm: {'✅ THÀNH CÔNG' if food_intake_created else '❌ THẤT BẠI'}")
    print(f"Đọc thông tin tiêu thụ thực phẩm: {'✅ THÀNH CÔNG' if food_intake_verified else '❌ THẤT BẠI'}")
    
    return {
        "user_id": user_id,
        "user_created": user_created,
        "user_verified": user_verified,
        "log_created": log_created,
        "log_verified": log_verified,
        "food_intake_created": food_intake_created,
        "food_intake_verified": food_intake_verified
    }
    
if __name__ == "__main__":
    # Chạy kiểm tra
    test_result = test_firebase_direct()
    
    # Đánh giá tổng thể
    success_count = sum(1 for v in test_result.values() if isinstance(v, bool) and v)
    total_count = sum(1 for v in test_result.values() if isinstance(v, bool))
    
    print(f"\n=== ĐÁNH GIÁ TỔNG THỂ ===")
    print(f"Thành công: {success_count}/{total_count} kiểm tra ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("✅ TUYỆT VỜI! Tất cả các kiểm tra đều thành công.")
        print("✅ Firebase integration hoạt động tốt với dữ liệu Flutter!")
    elif success_count >= total_count/2:
        print("⚠️ KẾT QUẢ TRUNG BÌNH. Một số kiểm tra thất bại.")
        print("⚠️ Firebase integration hoạt động nhưng có vấn đề cần khắc phục.")
    else:
        print("❌ KẾT QUẢ KÉM. Phần lớn kiểm tra thất bại.")
        print("❌ Firebase integration cần được sửa chữa để làm việc với dữ liệu Flutter.") 