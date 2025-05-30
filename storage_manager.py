import os
from typing import Dict, List, Optional, Union
from models import WeeklyMealPlan
import storage

# Khởi tạo Firebase một cách an toàn
try:
    from firebase_integration import firebase
    FIREBASE_AVAILABLE = True
except ImportError:
    print("Firebase integration is not available. Using local storage only.")
    FIREBASE_AVAILABLE = False

class StorageManager:
    """
    Lớp quản lý lưu trữ hỗ trợ cả lưu trữ cục bộ và Firebase
    """
    
    def __init__(self, use_firebase: bool = False):
        """
        Khởi tạo Storage Manager
        
        Args:
            use_firebase: Sử dụng Firebase nếu True, ngược lại chỉ sử dụng lưu trữ cục bộ
        """
        self.use_firebase = use_firebase and FIREBASE_AVAILABLE
        if use_firebase and not FIREBASE_AVAILABLE:
            print("Warning: Firebase was requested but is not available.")
        
        if self.use_firebase:
            try:
                self.firebase_initialized = firebase.initialized
                if not self.firebase_initialized:
                    print("Warning: Firebase is not initialized properly.")
            except:
                self.firebase_initialized = False
                print("Error checking Firebase initialization status.")
        else:
            self.firebase_initialized = False
    
    def save_meal_plan(self, meal_plan: WeeklyMealPlan, user_id: str = "default") -> str:
        """
        Lưu kế hoạch thực đơn
        
        Args:
            meal_plan: Đối tượng WeeklyMealPlan cần lưu
            user_id: ID của người dùng
            
        Returns:
            ID của document hoặc đường dẫn đến file đã lưu
        """
        # Kiểm tra và đảm bảo meal_plan có dữ liệu hợp lệ
        if not meal_plan or not meal_plan.days:
            print(f"Warning: Attempted to save an empty meal plan for user {user_id}")
            return None
        
        # Kiểm tra số lượng món ăn
        dish_count = 0
        for day in meal_plan.days:
            if day.breakfast and day.breakfast.dishes:
                dish_count += len(day.breakfast.dishes)
            if day.lunch and day.lunch.dishes:
                dish_count += len(day.lunch.dishes)
            if day.dinner and day.dinner.dishes:
                dish_count += len(day.dinner.dishes)
        
        if dish_count == 0:
            print(f"Warning: Meal plan for user {user_id} has 0 dishes")
        
        # Luôn lưu local để đề phòng
        local_path = storage.save_meal_plan(meal_plan, user_id)
        print(f"Saved meal plan for user {user_id} to local storage: {local_path}")
        
        # Nếu sử dụng Firebase, lưu thêm vào Firestore
        if self.use_firebase and self.firebase_initialized:
            try:
                firebase_id = firebase.save_meal_plan(meal_plan, user_id)
                if firebase_id:
                    print(f"Successfully saved meal plan to Firestore with ID: {firebase_id}")
                    return firebase_id
                else:
                    print(f"Failed to save to Firestore, using local path: {local_path}")
                    return local_path
            except Exception as e:
                print(f"Error saving to Firebase: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            if not self.use_firebase:
                print("Firebase usage is disabled. Using local storage only.")
            elif not self.firebase_initialized:
                print("Firebase is not initialized. Using local storage only.")
        
        return local_path
    
    def load_meal_plan(self, user_id: str = "default") -> Optional[WeeklyMealPlan]:
        """
        Đọc kế hoạch thực đơn mới nhất
        
        Args:
            user_id: ID của người dùng
            
        Returns:
            Đối tượng WeeklyMealPlan hoặc None nếu không tìm thấy
        """
        # Thử đọc từ Firebase trước nếu đang sử dụng
        if self.use_firebase and self.firebase_initialized:
            try:
                firebase_meal_plan = firebase.load_meal_plan(user_id)
                if firebase_meal_plan:
                    return firebase_meal_plan
            except Exception as e:
                print(f"Error loading from Firebase: {e}")
        
        # Fallback về lưu trữ cục bộ
        return storage.load_meal_plan(user_id)
    
    def get_meal_plan_history(self, user_id: str = "default", limit: int = 10) -> List[Dict]:
        """
        Lấy lịch sử kế hoạch thực đơn
        
        Args:
            user_id: ID của người dùng
            limit: Số lượng kế hoạch tối đa trả về
            
        Returns:
            Danh sách các kế hoạch thực đơn
        """
        # Thử lấy từ Firebase trước nếu đang sử dụng
        if self.use_firebase and self.firebase_initialized:
            try:
                firebase_history = firebase.get_meal_plan_history(user_id, limit)
                if firebase_history:
                    return firebase_history
            except Exception as e:
                print(f"Error getting history from Firebase: {e}")
        
        # Fallback về lưu trữ cục bộ
        return storage.get_meal_plan_history(user_id, limit)
    
    def delete_meal_plan(self, id_or_filename: str) -> bool:
        """
        Xóa một kế hoạch thực đơn
        
        Args:
            id_or_filename: ID hoặc tên file cần xóa
            
        Returns:
            True nếu xóa thành công, False nếu không
        """
        # Nếu sử dụng Firebase và id có định dạng UUID, thử xóa từ Firebase
        if self.use_firebase and self.firebase_initialized and len(id_or_filename) > 20 and '/' not in id_or_filename:
            try:
                if firebase.delete_meal_plan(id_or_filename):
                    return True
            except Exception as e:
                print(f"Error deleting from Firebase: {e}")
        
        # Fallback về lưu trữ cục bộ
        return storage.delete_meal_plan(id_or_filename)
    
    def is_using_firebase(self) -> bool:
        """
        Kiểm tra xem hệ thống có đang sử dụng Firebase hay không
        
        Returns:
            True nếu đang sử dụng Firebase, False nếu chỉ sử dụng lưu trữ cục bộ
        """
        return self.use_firebase and self.firebase_initialized

# Tạo instance toàn cục, mặc định không sử dụng Firebase
storage_manager = StorageManager(use_firebase=True) 