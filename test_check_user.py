from services.firestore_service import firestore_service

def check_user(user_id):
    """Kiểm tra thông tin người dùng cụ thể"""
    
    print(f"\n=== KIỂM TRA THÔNG TIN NGƯỜI DÙNG: {user_id} ===")
    
    # Đọc thông tin người dùng
    try:
        user_info = firestore_service.get_user(user_id)
        if user_info:
            print(f"\nThông tin người dùng: {user_info}")
            print("✅ Đã đọc thông tin người dùng thành công!")
            
            # Kiểm tra các trường thông tin dinh dưỡng và thông tin cá nhân
            nutrition_fields = ['targetCalories', 'targetProtein', 'targetCarbs', 'targetFat']
            physical_fields = ['height', 'weight', 'age', 'gender', 'activityLevel', 'goal']
            
            print("\n--- THÔNG TIN DINH DƯỠNG ---")
            for field in nutrition_fields:
                if field in user_info:
                    print(f"{field}: {user_info[field]}")
                else:
                    print(f"{field}: Không có dữ liệu")
                    
            print("\n--- THÔNG TIN CÁ NHÂN ---")
            for field in physical_fields:
                if field in user_info:
                    print(f"{field}: {user_info[field]}")
                else:
                    print(f"{field}: Không có dữ liệu")
        else:
            print("❌ Không thể đọc thông tin người dùng")
    except Exception as e:
        print(f"❌ Lỗi khi đọc thông tin người dùng: {str(e)}")
    
if __name__ == "__main__":
    # ID người dùng cần kiểm tra
    user_id = "49DhdmJHFAY40eEgaPNEJqGdDQK2"
    check_user(user_id) 