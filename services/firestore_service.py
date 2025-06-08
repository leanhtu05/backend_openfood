import traceback
import json
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from firebase_config import firebase_config
from models.firestore_models import (
    UserProfile, 
    DailyLog, 
    Meal, 
    MealPlan, 
    SuggestedMeal, 
    AISuggestion,
    Exercise,
    ExerciseHistory,
    Beverage,
    WaterIntake,
    FoodItem,
    FoodIntake
)
from firebase_integration import firebase
from models import WeeklyMealPlan

class FirestoreService:
    """
    Dịch vụ tương tác với Firestore
    """
    
    def __init__(self):
        """Khởi tạo dịch vụ Firestore"""
        self.initialized = firebase.initialized
        self.db = firebase_config.get_db()
        
    # ===== USER OPERATIONS =====
    
    def create_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        Tạo người dùng mới trong Firestore
        
        Args:
            user_id (str): ID của người dùng
            user_data (Dict[str, Any]): Dữ liệu người dùng
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Đảm bảo có trường created_at
            if "created_at" not in user_data:
                user_data["created_at"] = datetime.now().isoformat()
            
            user_ref = self.db.collection('users').document(user_id)
            user_ref.set(user_data)
            return True
        except Exception as e:
            print(f"Lỗi khi tạo người dùng mới: {str(e)}")
            return False
            
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy thông tin người dùng từ Firestore
        
        Args:
            user_id (str): ID của người dùng
            
        Returns:
            Optional[Dict[str, Any]]: Thông tin người dùng hoặc None nếu không tìm thấy
        """
        try:
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                return user_doc.to_dict()
            return None
        except Exception as e:
            print(f"Lỗi khi lấy thông tin người dùng: {str(e)}")
            return None
            
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """
        Lấy thông tin profile của người dùng
        
        Args:
            user_id: ID của người dùng
            
        Returns:
            Thông tin profile của người dùng hoặc None nếu không tìm thấy
        """
        try:
            # Lấy dữ liệu người dùng từ Firestore
            user_data = self.get_user(user_id)
            
            if not user_data:
                print(f"User {user_id} not found in Firestore")
                return None
                
            # Chuyển đổi dữ liệu thành đối tượng UserProfile
            from models.firestore_models import UserProfile
            
            # Log dữ liệu để debug
            print(f"User data from Firestore: {user_data}")
            
            # Tạo đối tượng UserProfile với các trường bắt buộc
            # Nếu thiếu trường nào, sử dụng giá trị mặc định
            user_profile = UserProfile(
                name=user_data.get("name", ""),
                email=user_data.get("email", ""),
                height=user_data.get("height", 0),
                weight=user_data.get("weight", 0),
                age=user_data.get("age", 0),
                gender=user_data.get("gender", ""),
                activityLevel=user_data.get("activityLevel", ""),
                goal=user_data.get("goal", ""),
                targetCalories=user_data.get("targetCalories", 0),
                allergies=user_data.get("allergies", []),
                preferred_cuisines=user_data.get("preferred_cuisines", []),
                lastSyncTime=user_data.get("lastSyncTime", ""),
                deviceInfo=user_data.get("deviceInfo", None)
            )
            
            return user_profile
        except Exception as e:
            print(f"Error getting user profile: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
            
    def create_or_update_user_profile(self, user_id: str, user_profile: Any) -> bool:
        """
        Tạo hoặc cập nhật profile của người dùng
        
        Args:
            user_id: ID của người dùng
            user_profile: Đối tượng UserProfile hoặc Dict chứa thông tin người dùng
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            # Kiểm tra xem user_profile có phải là dict không
            if hasattr(user_profile, 'to_dict'):
                user_data = user_profile.to_dict()
            elif isinstance(user_profile, dict):
                user_data = user_profile
            else:
                print(f"Invalid user_profile type: {type(user_profile)}")
                return False
                
            # Kiểm tra xem người dùng đã tồn tại chưa
            existing_user = self.get_user(user_id)
            
            if existing_user:
                # Cập nhật người dùng hiện có
                print(f"Updating existing user: {user_id}")
                
                # Thêm trường lastSyncTime nếu chưa có
                if "lastSyncTime" not in user_data:
                    user_data["lastSyncTime"] = datetime.now().isoformat()
                    
                return self.update_user(user_id, user_data)
            else:
                # Tạo người dùng mới
                print(f"Creating new user: {user_id}")
                
                # Thêm trường lastSyncTime nếu chưa có
                if "lastSyncTime" not in user_data:
                    user_data["lastSyncTime"] = datetime.now().isoformat()
                
                # Thêm trường created_at nếu chưa có
                if "created_at" not in user_data:
                    user_data["created_at"] = datetime.now().isoformat()
                    
                return self.create_user(user_id, user_data)
        except Exception as e:
            print(f"Error creating/updating user profile: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    def update_user(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        Cập nhật thông tin người dùng trong Firestore
        
        Args:
            user_id (str): ID của người dùng
            user_data (Dict[str, Any]): Dữ liệu người dùng cần cập nhật
            
        Returns:
            bool: True nếu thành công, False nếu thất bại
        """
        try:
            # Đảm bảo có trường updated_at
            user_data["updated_at"] = datetime.now().isoformat()
            
            print(f"[FIRESTORE] Updating user {user_id} with data: {json.dumps(user_data, indent=2)[:500]}...")
            
            user_ref = self.db.collection('users').document(user_id)
            
            # Kiểm tra xem document đã tồn tại chưa
            doc = user_ref.get()
            if doc.exists:
                # Cập nhật document hiện có
                print(f"[FIRESTORE] Document exists, updating...")
                user_ref.update(user_data)
            else:
                # Tạo document mới nếu chưa tồn tại
                print(f"[FIRESTORE] Document doesn't exist, creating new document...")
                user_ref.set(user_data)
                
            # Kiểm tra xem cập nhật thành công không
            updated_doc = user_ref.get()
            if updated_doc.exists:
                updated_data = updated_doc.to_dict()
                print(f"[FIRESTORE] Update successful. New data: {json.dumps(updated_data, indent=2)[:500]}...")
                return True
            else:
                print(f"[FIRESTORE] Update failed. Document doesn't exist after update.")
                return False
                
        except Exception as e:
            print(f"[FIRESTORE] Error updating user: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    def delete_user(self, user_id: str) -> bool:
        """
        Xóa người dùng
        
        Args:
            user_id: ID của người dùng
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            # Xóa người dùng
            self.db.collection('users').document(user_id).delete()
            
            # Xóa các daily logs của người dùng
            daily_logs = self.db.collection('users').document(user_id).collection('daily_logs').get()
            for log in daily_logs:
                log.reference.delete()
                
            # Xóa các meal plans liên quan
            batch = self.db.batch()
            meal_plans = self.db.collection('meal_plans').where(
                filter=FieldFilter('userId', '==', user_id)
            ).get()
            for plan in meal_plans:
                batch.delete(plan.reference)
                
            # Xóa các AI suggestions liên quan
            ai_suggestions = self.db.collection('ai_suggestions').where(
                filter=FieldFilter('userId', '==', user_id)
            ).get()
            for suggestion in ai_suggestions:
                batch.delete(suggestion.reference)
                
            # Commit batch
            batch.commit()
            
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            traceback.print_exc()
            return False
    
    # ===== DAILY LOG OPERATIONS =====
    
    def add_daily_log(self, user_id: str, daily_log: DailyLog) -> bool:
        """
        Thêm log hàng ngày cho người dùng
        
        Args:
            user_id: ID của người dùng
            daily_log: Dữ liệu log hàng ngày
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            self.db.collection('users').document(user_id).collection('daily_logs').document(
                daily_log.date
            ).set(daily_log.to_dict())
            return True
        except Exception as e:
            print(f"Error adding daily log: {e}")
            traceback.print_exc()
            return False
            
    def get_daily_log(self, user_id: str, date: str) -> Optional[DailyLog]:
        """
        Lấy log hàng ngày của người dùng
        
        Args:
            user_id: ID của người dùng
            date: Ngày (YYYY-MM-DD)
            
        Returns:
            DailyLog hoặc None nếu không tìm thấy
        """
        try:
            doc = self.db.collection('users').document(user_id).collection('daily_logs').document(date).get()
            if doc.exists:
                return DailyLog.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting daily log: {e}")
            traceback.print_exc()
            return None
            
    def update_daily_log(self, user_id: str, date: str, data: Dict[str, Any]) -> bool:
        """
        Cập nhật log hàng ngày
        
        Args:
            user_id: ID của người dùng
            date: Ngày (YYYY-MM-DD)
            data: Dữ liệu cần cập nhật
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            self.db.collection('users').document(user_id).collection('daily_logs').document(date).update(data)
            return True
        except Exception as e:
            print(f"Error updating daily log: {e}")
            traceback.print_exc()
            return False
    
    def get_daily_logs(self, user_id: str, limit: int = 7) -> List[DailyLog]:
        """
        Lấy danh sách log hàng ngày của người dùng
        
        Args:
            user_id: ID của người dùng
            limit: Số lượng log tối đa
            
        Returns:
            Danh sách DailyLog
        """
        try:
            logs = []
            query = self.db.collection('users').document(user_id).collection('daily_logs').order_by(
                'date', direction=firestore.Query.DESCENDING
            ).limit(limit)
            
            results = query.get()
            
            for doc in results:
                logs.append(DailyLog.from_dict(doc.to_dict()))
                
            return logs
        except Exception as e:
            print(f"Error getting daily logs: {e}")
            traceback.print_exc()
            return []
    
    # ===== MEAL PLAN OPERATIONS =====
    
    def create_meal_plan(self, meal_plan: MealPlan) -> Optional[str]:
        """
        Tạo kế hoạch bữa ăn mới
        
        Args:
            meal_plan: Dữ liệu kế hoạch bữa ăn
            
        Returns:
            ID của document hoặc None nếu thất bại
        """
        try:
            doc_ref = self.db.collection('meal_plans').document()
            doc_ref.set(meal_plan.to_dict())
            return doc_ref.id
        except Exception as e:
            print(f"Error creating meal plan: {e}")
            traceback.print_exc()
            return None
            
    def get_meal_plan(self, plan_id: str) -> Optional[MealPlan]:
        """
        Lấy kế hoạch bữa ăn theo ID
        
        Args:
            plan_id: ID của kế hoạch bữa ăn
            
        Returns:
            MealPlan hoặc None nếu không tìm thấy
        """
        try:
            doc = self.db.collection('meal_plans').document(plan_id).get()
            if doc.exists:
                return MealPlan.from_dict(doc.to_dict())
            return None
        except Exception as e:
            print(f"Error getting meal plan: {e}")
            traceback.print_exc()
            return None
            
    def get_meal_plans_by_user_date(self, user_id: str, date: str) -> List[MealPlan]:
        """
        Lấy các kế hoạch bữa ăn của người dùng theo ngày
        
        Args:
            user_id: ID của người dùng
            date: Ngày (YYYY-MM-DD)
            
        Returns:
            Danh sách MealPlan
        """
        try:
            plans = []
            query = self.db.collection('meal_plans').where(
                filter=FieldFilter('userId', '==', user_id)
            ).where(
                filter=FieldFilter('date', '==', date)
            )
            
            results = query.get()
            
            for doc in results:
                plans.append(MealPlan.from_dict(doc.to_dict()))
                
            return plans
        except Exception as e:
            print(f"Error getting meal plans: {e}")
            traceback.print_exc()
            return []
            
    def delete_meal_plan(self, plan_id: str) -> bool:
        """
        Xóa kế hoạch bữa ăn
        
        Args:
            plan_id: ID của kế hoạch bữa ăn
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            self.db.collection('meal_plans').document(plan_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting meal plan: {e}")
            traceback.print_exc()
            return False
    
    # ===== AI SUGGESTION OPERATIONS =====
    
    def save_ai_suggestion(self, suggestion: AISuggestion) -> Optional[str]:
        """
        Lưu gợi ý từ AI
        
        Args:
            suggestion: Dữ liệu gợi ý
            
        Returns:
            ID của document hoặc None nếu thất bại
        """
        try:
            doc_ref = self.db.collection('ai_suggestions').document()
            doc_ref.set(suggestion.to_dict())
            return doc_ref.id
        except Exception as e:
            print(f"Error saving AI suggestion: {e}")
            traceback.print_exc()
            return None
            
    def get_ai_suggestions(self, user_id: str, limit: int = 10) -> List[AISuggestion]:
        """
        Lấy danh sách gợi ý của người dùng
        
        Args:
            user_id: ID của người dùng
            limit: Số lượng gợi ý tối đa
            
        Returns:
            Danh sách AISuggestion
        """
        try:
            suggestions = []
            query = self.db.collection('ai_suggestions').where(
                filter=FieldFilter('userId', '==', user_id)
            ).order_by(
                'timestamp', direction=firestore.Query.DESCENDING
            ).limit(limit)
            
            results = query.get()
            
            for doc in results:
                suggestions.append(AISuggestion.from_dict(doc.to_dict()))
                
            return suggestions
        except Exception as e:
            print(f"Error getting AI suggestions: {e}")
            traceback.print_exc()
            return []
            
    # ===== USER SETTINGS OPERATIONS =====
    
    def update_user_settings(self, user_id: str, settings: Dict[str, Any]) -> bool:
        """
        Cập nhật cài đặt người dùng
        
        Args:
            user_id: ID của người dùng
            settings: Dữ liệu cài đặt cần cập nhật
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            # Kiểm tra người dùng tồn tại
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                print(f"User {user_id} not found")
                return False
                
            # Cập nhật settings
            user_ref.update({
                'settings': settings
            })
            
            print(f"Successfully updated settings for user {user_id}")
            return True
        except Exception as e:
            print(f"Error updating user settings: {e}")
            traceback.print_exc()
            return False
            
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """
        Cập nhật sở thích thực phẩm của người dùng
        
        Args:
            user_id: ID của người dùng
            preferences: Dữ liệu sở thích cần cập nhật
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            # Kiểm tra người dùng tồn tại
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                print(f"User {user_id} not found")
                return False
                
            # Cập nhật preferences
            user_ref.update({
                'preferences': preferences
            })
            
            print(f"Successfully updated preferences for user {user_id}")
            return True
        except Exception as e:
            print(f"Error updating user preferences: {e}")
            traceback.print_exc()
            return False
            
    def convert_anonymous_account(self, user_id: str, email: str, display_name: str = None) -> bool:
        """
        Chuyển đổi tài khoản ẩn danh thành tài khoản chính thức
        
        Args:
            user_id: ID của người dùng
            email: Email người dùng
            display_name: Tên hiển thị
            
        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            # Kiểm tra người dùng tồn tại
            user_ref = self.db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if not user_doc.exists:
                print(f"User {user_id} not found")
                return False
                
            # Cập nhật thông tin người dùng
            update_data = {
                'email': email,
                'isAnonymous': False,
            }
            
            if display_name:
                update_data['displayName'] = display_name
                
            user_ref.update(update_data)
            
            print(f"Successfully converted anonymous account for user {user_id}")
            return True
        except Exception as e:
            print(f"Error converting anonymous account: {e}")
            traceback.print_exc()
            return False
            
    def get_latest_meal_plan(self, user_id: str) -> Optional[WeeklyMealPlan]:
        """
        Lấy kế hoạch bữa ăn mới nhất của người dùng từ collection latest_meal_plans
        
        Args:
            user_id: ID của người dùng
            
        Returns:
            Đối tượng WeeklyMealPlan hoặc None nếu không tìm thấy
        """
        if not self.initialized:
            print(f"Firestore not initialized when trying to get latest meal plan for {user_id}")
            return None
            
        try:
            print(f"[DEBUG] Getting latest meal plan for user: {user_id}")
            # Truy cập trực tiếp collection trong Firestore để kiểm tra
            doc_ref = self.db.collection('latest_meal_plans').document(user_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                print(f"[DEBUG] Document not found in latest_meal_plans collection for user: {user_id}")
                # Thử tìm kiếm trong collection meal_plans
                print(f"[DEBUG] Searching in meal_plans collection for user: {user_id}")
                query = self.db.collection('meal_plans').where('user_id', '==', user_id).limit(1)
                results = list(query.stream())
                if results:
                    print(f"[DEBUG] Found meal plan in meal_plans collection for user: {user_id}")
                    data = results[0].to_dict()
                    if data and 'days' in data:
                        try:
                            # Chuyển đổi dữ liệu trước khi parse
                            transformed_data = self._transform_meal_plan_data(data)
                            return WeeklyMealPlan(**transformed_data)
                        except Exception as e:
                            print(f"[DEBUG] Error parsing meal plan from meal_plans: {str(e)}")
                            return None
                    else:
                        print(f"[DEBUG] Invalid meal plan data from meal_plans for user: {user_id}")
                        return None
                else:
                    print(f"[DEBUG] No meal plans found for user: {user_id}")
                    return None
            
            print(f"[DEBUG] Document found in latest_meal_plans for user: {user_id}")
            data = doc.to_dict()
            if not data or 'days' not in data:
                print(f"[DEBUG] Invalid meal plan data in latest_meal_plans for user: {user_id}")
                return None
                
            try:
                # Chuyển đổi dữ liệu trước khi parse
                transformed_data = self._transform_meal_plan_data(data)
                
                # Kiểm tra một vài mẫu để xem cấu trúc dữ liệu
                if 'days' in transformed_data and len(transformed_data['days']) > 0:
                    day = transformed_data['days'][0]
                    if 'breakfast' in day and 'dishes' in day['breakfast'] and len(day['breakfast']['dishes']) > 0:
                        dish = day['breakfast']['dishes'][0]
                        print(f"[DEBUG] Sample dish after transform: {dish}")
                        if 'preparation' in dish:
                            prep = dish['preparation']
                            print(f"[DEBUG] Transformed preparation type: {type(prep)}, value: {prep}")
                
                # Chi tiết lỗi nếu xảy ra validation error
                try:
                    from pydantic import ValidationError
                    result = WeeklyMealPlan(**transformed_data)
                    print(f"[DEBUG] Successfully parsed meal plan with {len(result.days)} days")
                    return result
                except ValidationError as ve:
                    print(f"[DEBUG] Pydantic validation error: {str(ve)}")
                    
                    # In ra mẫu dữ liệu cụ thể để xác định vấn đề
                    error_fields = str(ve)
                    if "preparation" in error_fields:
                        print("[DEBUG] Validation error related to preparation field")
                        # Tìm và in ra một vài trường preparation để phân tích
                        self._find_and_print_preparation_fields(transformed_data)
                    
                    import traceback
                    traceback.print_exc()
                    return None
                    
            except Exception as e:
                # Xử lý lỗi validation và in ra để debug
                print(f"[DEBUG] Error parsing meal plan from latest_meal_plans: {str(e)}")
                
                # Log chi tiết dữ liệu để debug
                import json
                print(f"[DEBUG] Raw data structure: {json.dumps(data)[:1000]}...")
                
                # Trả về None nếu không thể chuyển đổi, để backend cũ xử lý
                return None
        except Exception as e:
            print(f"[DEBUG] Error in get_latest_meal_plan: {str(e)}")
            traceback.print_exc()
            return None

    def _find_and_print_preparation_fields(self, data: Dict) -> None:
        """
        Tìm và in ra một số trường preparation để phân tích vấn đề
        
        Args:
            data: Dữ liệu meal plan đã được transform
        """
        print("[DEBUG] Analyzing preparation fields in the data:")
        if 'days' not in data:
            print("[DEBUG] No 'days' field found")
            return
            
        for i, day in enumerate(data['days']):
            for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
                if meal_type in day and 'dishes' in day[meal_type]:
                    for j, dish in enumerate(day[meal_type]['dishes']):
                        if 'preparation' in dish:
                            prep = dish['preparation']
                            print(f"[DEBUG] Day {i}, {meal_type}, Dish {j}: preparation={prep} (type={type(prep)})")
                            # Giới hạn số lượng để tránh in quá nhiều
                            if i >= 1 and j >= 2:
                                print("[DEBUG] (more preparation fields omitted)")
                                return

    def _transform_meal_plan_data(self, data: Dict) -> Dict:
        """
        Chuyển đổi dữ liệu meal plan từ Firestore để tương thích với model Pydantic
        
        Args:
            data: Dữ liệu meal plan từ Firestore
            
        Returns:
            Dữ liệu đã được chuyển đổi
        """
        if not data:
            return None
        
        print("[DEBUG] _transform_meal_plan_data input keys:", data.keys())
        
        # Xử lý các trường đặc biệt
        if "days" in data:
            for day in data["days"]:
                if "meals" in day:
                    for meal in day["meals"]:
                        if "dishes" in meal:
                            for dish in meal["dishes"]:
                                # Chuyển đổi preparation từ chuỗi sang danh sách nếu cần
                                if "preparation" in dish and isinstance(dish["preparation"], str):
                                    dish["preparation"] = dish["preparation"].split("\n")
                                    print("[DEBUG] Đã chuyển đổi preparation từ chuỗi sang danh sách theo dấu xuống dòng")
                                    print("[DEBUG] Transformed preparation type:", type(dish["preparation"]))
        
        return data

    # ===== EXERCISE METHODS =====
    
    def create_exercise(self, exercise: Exercise) -> str:
        """
        Tạo bài tập mới
        
        Args:
            exercise: Đối tượng Exercise
            
        Returns:
            ID của bài tập đã tạo
        """
        if not self.initialized:
            return None
            
        try:
            # Tạo document mới trong collection exercises
            doc_ref = self.db.collection('exercises').document()
            exercise_data = exercise.to_dict()
            doc_ref.set(exercise_data)
            
            return doc_ref.id
        except Exception as e:
            print(f"Error creating exercise: {e}")
            return None
    
    def get_exercise(self, exercise_id: str) -> Optional[Exercise]:
        """
        Lấy thông tin chi tiết bài tập
        
        Args:
            exercise_id: ID của bài tập
            
        Returns:
            Đối tượng Exercise hoặc None nếu không tìm thấy
        """
        if not self.initialized:
            return None
            
        try:
            doc_ref = self.db.collection('exercises').document(exercise_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return Exercise.from_dict(doc.to_dict())
            else:
                return None
        except Exception as e:
            print(f"Error getting exercise: {e}")
            return None
    
    def update_exercise(self, exercise_id: str, exercise_data: Dict[str, Any]) -> bool:
        """
        Cập nhật thông tin bài tập
        
        Args:
            exercise_id: ID của bài tập
            exercise_data: Dữ liệu cần cập nhật
            
        Returns:
            True nếu cập nhật thành công, False nếu thất bại
        """
        if not self.initialized:
            return False
            
        try:
            doc_ref = self.db.collection('exercises').document(exercise_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
                
            doc_ref.update(exercise_data)
            return True
        except Exception as e:
            print(f"Error updating exercise: {e}")
            return False
    
    def delete_exercise(self, exercise_id: str) -> bool:
        """
        Xóa bài tập
        
        Args:
            exercise_id: ID của bài tập
            
        Returns:
            True nếu xóa thành công, False nếu thất bại
        """
        if not self.initialized:
            return False
            
        try:
            doc_ref = self.db.collection('exercises').document(exercise_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
                
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting exercise: {e}")
            return False
    
    def get_user_exercises(self, user_id: str, limit: int = 50) -> List[Exercise]:
        """
        Lấy danh sách bài tập của người dùng
        
        Args:
            user_id: ID của người dùng
            limit: Số lượng bài tập tối đa
            
        Returns:
            Danh sách Exercise
        """
        if not self.initialized:
            return []
            
        try:
            exercises = []
            query = self.db.collection('user_exercises').where(
                filter=FieldFilter('userId', '==', user_id)
            ).limit(limit)
            
            results = query.get()
            
            for doc in results:
                exercise_id = doc.to_dict().get('exerciseId')
                if exercise_id:
                    exercise = self.get_exercise(exercise_id)
                    if exercise:
                        exercises.append(exercise)
            
            return exercises
        except Exception as e:
            print(f"Error getting user exercises: {e}")
            return []
    
    def add_exercise_history(self, exercise_history: ExerciseHistory) -> str:
        """
        Lưu lịch sử bài tập của người dùng
        
        Args:
            exercise_history: Đối tượng ExerciseHistory
            
        Returns:
            ID của bản ghi lịch sử đã tạo
        """
        if not self.initialized:
            return None
            
        try:
            # Tạo document mới trong collection exercises
            doc_ref = self.db.collection('exercises').document()
            history_data = exercise_history.to_dict()
            doc_ref.set(history_data)
            
            return doc_ref.id
        except Exception as e:
            print(f"Error adding exercise history: {e}")
            return None
    
    def get_exercise_history(self, user_id: str, start_date: str = None, end_date: str = None, limit: int = 50) -> List[ExerciseHistory]:
        """
        Lấy lịch sử bài tập của người dùng
        
        Args:
            user_id: ID của người dùng
            start_date: Ngày bắt đầu (YYYY-MM-DD)
            end_date: Ngày kết thúc (YYYY-MM-DD)
            limit: Số lượng bản ghi tối đa
            
        Returns:
            Danh sách ExerciseHistory
        """
        if not self.initialized:
            return []
            
        try:
            history = []
            query = self.db.collection('exercises').where(
                filter=FieldFilter('userId', '==', user_id)
            )
            
            # Lọc theo ngày nếu có
            if start_date:
                query = query.where(filter=FieldFilter('date', '>=', start_date))
            if end_date:
                query = query.where(filter=FieldFilter('date', '<=', end_date))
                
            # Sắp xếp theo thời gian giảm dần
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            
            results = query.get()
            
            for doc in results:
                history.append(ExerciseHistory.from_dict(doc.to_dict()))
            
            return history
        except Exception as e:
            print(f"Error getting exercise history: {e}")
            return []
    
    # ===== BEVERAGE METHODS =====
    
    def create_beverage(self, beverage: Beverage) -> str:
        """
        Tạo loại nước uống mới
        
        Args:
            beverage: Đối tượng Beverage
            
        Returns:
            ID của nước uống đã tạo
        """
        if not self.initialized:
            return None
            
        try:
            # Tạo document mới trong collection beverages
            doc_ref = self.db.collection('beverages').document()
            beverage_data = beverage.to_dict()
            doc_ref.set(beverage_data)
            
            return doc_ref.id
        except Exception as e:
            print(f"Error creating beverage: {e}")
            return None
    
    def get_beverage(self, beverage_id: str) -> Optional[Beverage]:
        """
        Lấy thông tin chi tiết nước uống
        
        Args:
            beverage_id: ID của nước uống
            
        Returns:
            Đối tượng Beverage hoặc None nếu không tìm thấy
        """
        if not self.initialized:
            return None
            
        try:
            doc_ref = self.db.collection('beverages').document(beverage_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return Beverage.from_dict(doc.to_dict())
            else:
                return None
        except Exception as e:
            print(f"Error getting beverage: {e}")
            return None
    
    def update_beverage(self, beverage_id: str, beverage_data: Dict[str, Any]) -> bool:
        """
        Cập nhật thông tin nước uống
        
        Args:
            beverage_id: ID của nước uống
            beverage_data: Dữ liệu cần cập nhật
            
        Returns:
            True nếu cập nhật thành công, False nếu thất bại
        """
        if not self.initialized:
            return False
            
        try:
            doc_ref = self.db.collection('beverages').document(beverage_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
                
            doc_ref.update(beverage_data)
            return True
        except Exception as e:
            print(f"Error updating beverage: {e}")
            return False
    
    def delete_beverage(self, beverage_id: str) -> bool:
        """
        Xóa nước uống
        
        Args:
            beverage_id: ID của nước uống
            
        Returns:
            True nếu xóa thành công, False nếu thất bại
        """
        if not self.initialized:
            return False
            
        try:
            doc_ref = self.db.collection('beverages').document(beverage_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
                
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting beverage: {e}")
            return False
    
    def add_water_intake(self, water_intake: WaterIntake) -> str:
        """
        Ghi nhận lượng nước uống hàng ngày
        
        Args:
            water_intake: Đối tượng WaterIntake
            
        Returns:
            ID của bản ghi nước uống đã tạo
        """
        if not self.initialized:
            return None
            
        try:
            # Tạo document mới trong collection water_entries
            doc_ref = self.db.collection('water_entries').document()
            intake_data = water_intake.to_dict()
            doc_ref.set(intake_data)
            
            # Cập nhật tổng lượng nước uống trong ngày
            self._update_daily_water_total(water_intake.userId, water_intake.date, water_intake.amount_ml)
            
            return doc_ref.id
        except Exception as e:
            print(f"Error adding water intake: {e}")
            return None
    
    def _update_daily_water_total(self, user_id: str, date: str, amount_ml: int) -> None:
        """
        Cập nhật tổng lượng nước uống trong ngày
        
        Args:
            user_id: ID của người dùng
            date: Ngày ghi nhận (YYYY-MM-DD)
            amount_ml: Lượng nước uống (ml)
        """
        try:
            doc_ref = self.db.collection('daily_water_totals').document(f"{user_id}_{date}")
            doc = doc_ref.get()
            
            if doc.exists:
                current_total = doc.to_dict().get('total_ml', 0)
                doc_ref.update({
                    'total_ml': current_total + amount_ml,
                    'updated_at': datetime.now().isoformat()
                })
            else:
                doc_ref.set({
                    'userId': user_id,
                    'date': date,
                    'total_ml': amount_ml,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                })
        except Exception as e:
            print(f"Error updating daily water total: {e}")
    
    def get_water_intake_by_date(self, user_id: str, date: str) -> List[WaterIntake]:
        """
        Lấy thông tin nước uống theo ngày
        
        Args:
            user_id: ID của người dùng
            date: Ngày cần lấy (YYYY-MM-DD)
            
        Returns:
            Danh sách WaterIntake
        """
        if not self.initialized:
            return []
            
        try:
            intakes = []
            query = self.db.collection('water_entries').where(
                filter=FieldFilter('userId', '==', user_id)
            ).where(
                filter=FieldFilter('date', '==', date)
            ).order_by('timestamp', direction=firestore.Query.ASCENDING)
            
            results = query.get()
            
            for doc in results:
                intakes.append(WaterIntake.from_dict(doc.to_dict()))
            
            return intakes
        except Exception as e:
            print(f"Error getting water intake by date: {e}")
            return []
    
    def get_water_intake_history(self, user_id: str, start_date: str = None, end_date: str = None, limit: int = 30) -> List[Dict[str, Any]]:
        """
        Lấy lịch sử uống nước của người dùng
        
        Args:
            user_id: ID của người dùng
            start_date: Ngày bắt đầu (YYYY-MM-DD)
            end_date: Ngày kết thúc (YYYY-MM-DD)
            limit: Số lượng ngày tối đa
            
        Returns:
            Danh sách tổng lượng nước uống theo ngày
        """
        if not self.initialized:
            return []
            
        try:
            history = []
            query = self.db.collection('daily_water_totals')
            
            # Tìm tất cả document có tiền tố là user_id
            query = query.where(filter=FieldFilter('userId', '==', user_id))
            
            # Lọc theo ngày nếu có
            if start_date:
                query = query.where(filter=FieldFilter('date', '>=', start_date))
            if end_date:
                query = query.where(filter=FieldFilter('date', '<=', end_date))
                
            # Sắp xếp theo ngày giảm dần
            query = query.order_by('date', direction=firestore.Query.DESCENDING).limit(limit)
            
            results = query.get()
            
            for doc in results:
                history.append(doc.to_dict())
            
            return history
        except Exception as e:
            print(f"Error getting water intake history: {e}")
            return []
    
    # ===== FOOD ITEM METHODS =====
    
    def create_food(self, food: FoodItem) -> str:
        """
        Tạo món ăn mới
        
        Args:
            food: Đối tượng FoodItem
            
        Returns:
            ID của món ăn đã tạo
        """
        if not self.initialized:
            return None
            
        try:
            # Tạo document mới trong collection foods
            doc_ref = self.db.collection('foods').document()
            food_data = food.to_dict()
            doc_ref.set(food_data)
            
            return doc_ref.id
        except Exception as e:
            print(f"Error creating food: {e}")
            return None
    
    def get_food(self, food_id: str) -> Optional[FoodItem]:
        """
        Lấy thông tin chi tiết món ăn
        
        Args:
            food_id: ID của món ăn
            
        Returns:
            Đối tượng FoodItem hoặc None nếu không tìm thấy
        """
        if not self.initialized:
            return None
            
        try:
            doc_ref = self.db.collection('foods').document(food_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return FoodItem.from_dict(doc.to_dict())
            else:
                return None
        except Exception as e:
            print(f"Error getting food: {e}")
            return None
    
    def update_food(self, food_id: str, food_data: Dict[str, Any]) -> bool:
        """
        Cập nhật thông tin món ăn
        
        Args:
            food_id: ID của món ăn
            food_data: Dữ liệu cần cập nhật
            
        Returns:
            True nếu cập nhật thành công, False nếu thất bại
        """
        if not self.initialized:
            return False
            
        try:
            doc_ref = self.db.collection('foods').document(food_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
                
            doc_ref.update(food_data)
            return True
        except Exception as e:
            print(f"Error updating food: {e}")
            return False
    
    def delete_food(self, food_id: str) -> bool:
        """
        Xóa món ăn
        
        Args:
            food_id: ID của món ăn
            
        Returns:
            True nếu xóa thành công, False nếu thất bại
        """
        if not self.initialized:
            return False
            
        try:
            doc_ref = self.db.collection('foods').document(food_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
                
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting food: {e}")
            return False
    
    def get_favorite_foods(self, user_id: str, limit: int = 50) -> List[FoodItem]:
        """
        Lấy danh sách món ăn yêu thích
        
        Args:
            user_id: ID của người dùng
            limit: Số lượng món ăn tối đa
            
        Returns:
            Danh sách FoodItem
        """
        if not self.initialized:
            return []
            
        try:
            foods = []
            doc_ref = self.db.collection('favorite_foods').document(user_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return []
                
            favorite_ids = doc.to_dict().get('food_ids', [])
            
            # Lấy thông tin chi tiết của từng món ăn
            for food_id in favorite_ids[:limit]:
                food = self.get_food(food_id)
                if food:
                    foods.append(food)
            
            return foods
        except Exception as e:
            print(f"Error getting favorite foods: {e}")
            return []
    
    def add_favorite_food(self, user_id: str, food_id: str) -> bool:
        """
        Thêm món ăn vào danh sách yêu thích
        
        Args:
            user_id: ID của người dùng
            food_id: ID của món ăn
            
        Returns:
            True nếu thêm thành công, False nếu thất bại
        """
        if not self.initialized:
            return False
            
        try:
            doc_ref = self.db.collection('favorite_foods').document(user_id)
            doc = doc_ref.get()
            
            if doc.exists:
                favorite_ids = doc.to_dict().get('food_ids', [])
                if food_id not in favorite_ids:
                    favorite_ids.append(food_id)
                    doc_ref.update({
                        'food_ids': favorite_ids,
                        'updated_at': datetime.now().isoformat()
                    })
            else:
                doc_ref.set({
                    'userId': user_id,
                    'food_ids': [food_id],
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                })
            
            return True
        except Exception as e:
            print(f"Error adding favorite food: {e}")
            return False
    
    def remove_favorite_food(self, user_id: str, food_id: str) -> bool:
        """
        Xóa món ăn khỏi danh sách yêu thích
        
        Args:
            user_id: ID của người dùng
            food_id: ID của món ăn
            
        Returns:
            True nếu xóa thành công, False nếu thất bại
        """
        if not self.initialized:
            return False
            
        try:
            doc_ref = self.db.collection('favorite_foods').document(user_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return False
                
            favorite_ids = doc.to_dict().get('food_ids', [])
            if food_id in favorite_ids:
                favorite_ids.remove(food_id)
                doc_ref.update({
                    'food_ids': favorite_ids,
                    'updated_at': datetime.now().isoformat()
                })
            
            return True
        except Exception as e:
            print(f"Error removing favorite food: {e}")
            return False
    
    def add_food_intake(self, food_intake: FoodIntake) -> str:
        """
        Ghi nhận việc ăn một món ăn
        
        Args:
            food_intake: Đối tượng FoodIntake
            
        Returns:
            ID của bản ghi đã tạo
        """
        if not self.initialized:
            return None
            
        try:
            # Tạo document mới trong collection food_intake
            doc_ref = self.db.collection('food_intake').document()
            intake_data = food_intake.to_dict()
            doc_ref.set(intake_data)
            
            return doc_ref.id
        except Exception as e:
            print(f"Error adding food intake: {e}")
            return None
    
    def get_food_intake_history(self, user_id: str, start_date: str = None, end_date: str = None, limit: int = 50) -> List[FoodIntake]:
        """
        Lấy lịch sử ăn uống của người dùng
        
        Args:
            user_id: ID của người dùng
            start_date: Ngày bắt đầu (YYYY-MM-DD)
            end_date: Ngày kết thúc (YYYY-MM-DD)
            limit: Số lượng bản ghi tối đa
            
        Returns:
            Danh sách FoodIntake
        """
        if not self.initialized:
            return []
            
        try:
            intakes = []
            query = self.db.collection('food_intake').where(
                filter=FieldFilter('userId', '==', user_id)
            )
            
            # Lọc theo ngày nếu có
            if start_date:
                query = query.where(filter=FieldFilter('date', '>=', start_date))
            if end_date:
                query = query.where(filter=FieldFilter('date', '<=', end_date))
                
            # Sắp xếp theo thời gian giảm dần
            query = query.order_by('timestamp', direction=firestore.Query.DESCENDING).limit(limit)
            
            results = query.get()
            
            for doc in results:
                intakes.append(FoodIntake.from_dict(doc.to_dict()))
            
            return intakes
        except Exception as e:
            print(f"Error getting food intake history: {e}")
            return []
    
    def get_food_intake_by_date(self, user_id: str, date: str) -> List[FoodIntake]:
        """
        Lấy thông tin thức ăn theo ngày cụ thể
        
        Args:
            user_id: ID của người dùng
            date: Ngày cần lấy dữ liệu (YYYY-MM-DD)
            
        Returns:
            Danh sách FoodIntake trong ngày đó
        """
        if not self.initialized:
            return []
            
        try:
            intakes = []
            query = self.db.collection('food_intake').where(
                filter=FieldFilter('userId', '==', user_id)
            ).where(
                filter=FieldFilter('date', '==', date)
            ).order_by('timestamp', direction=firestore.Query.DESCENDING)
            
            results = query.get()
            
            for doc in results:
                intakes.append(FoodIntake.from_dict(doc.to_dict()))
            
            return intakes
        except Exception as e:
            print(f"Error getting food intake by date: {str(e)}")
            traceback.print_exc()
            return []

    def get_or_create_user(self, user_id: str) -> Dict[str, Any]:
        """
        Lấy thông tin người dùng từ Firestore hoặc tạo mới nếu chưa tồn tại
        
        Args:
            user_id: ID của người dùng
            
        Returns:
            Thông tin người dùng
        """
        try:
            # Kiểm tra xem người dùng đã tồn tại chưa
            user_data = self.get_user(user_id)
            
            if not user_data:
                # Tạo người dùng mới với thông tin cơ bản
                user_data = {
                    "user_id": user_id,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                # Tạo người dùng mới trong Firestore
                self.create_user(user_id, user_data)
                print(f"Created new user with ID: {user_id}")
            
            return user_data
        except Exception as e:
            print(f"Error in get_or_create_user: {str(e)}")
            traceback.print_exc()
            # Trả về dict rỗng trong trường hợp lỗi
            return {"user_id": user_id}

    def add_food_log(self, user_id: str, food_log_data: dict) -> str:
        """
        Thêm bản ghi nhận diện thực phẩm vào Firestore
        
        Args:
            user_id: ID của người dùng
            food_log_data: Dữ liệu bản ghi thực phẩm
            
        Returns:
            ID của document đã tạo
        """
        if not self.db:
            print("Firestore service not available")
            return None
            
        try:
            # Đảm bảo người dùng tồn tại trong Firestore
            self.get_or_create_user(user_id)
            
            # Thêm bản ghi vào collection food_records
            food_logs_ref = self.db.collection('users').document(user_id).collection('food_records')
            doc_ref = food_logs_ref.add(food_log_data)
            
            # Lấy ID của document mới
            doc_id = doc_ref[1].id
            print(f"Food log added with ID: {doc_id}")
            
            return doc_id
        except Exception as e:
            print(f"Error adding food log: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_food_logs(self, user_id: str, limit: int = 20) -> list:
        """
        Lấy danh sách các bản ghi thực phẩm của người dùng
        
        Args:
            user_id: ID của người dùng
            limit: Số lượng bản ghi tối đa trả về
            
        Returns:
            Danh sách các bản ghi thực phẩm
        """
        if not self.db:
            print("Firestore service not available")
            return []
            
        try:
            # Lấy các bản ghi, sắp xếp theo thời gian giảm dần
            food_logs_ref = self.db.collection('users').document(user_id).collection('food_records')
            query = food_logs_ref.order_by('timestamp', direction='DESCENDING').limit(limit)
            
            logs = []
            for doc in query.stream():
                log_data = doc.to_dict()
                log_data['id'] = doc.id
                logs.append(log_data)
                
            return logs
        except Exception as e:
            print(f"Error getting food logs: {str(e)}")
            return []
            
    def get_food_logs_by_date(self, user_id: str, date: str) -> list:
        """
        Lấy danh sách các bản ghi thực phẩm của người dùng theo ngày cụ thể
        
        Args:
            user_id: ID của người dùng
            date: Ngày dạng YYYY-MM-DD
            
        Returns:
            Danh sách các bản ghi thực phẩm cho ngày đó
        """
        if not self.db:
            print("Firestore service not available")
            return []
            
        try:
            # Lấy các bản ghi cho ngày cụ thể
            food_logs_ref = self.db.collection('users').document(user_id).collection('food_records')
            query = food_logs_ref.where('date', '==', date).order_by('timestamp')
            
            logs = []
            for doc in query.stream():
                log_data = doc.to_dict()
                log_data['id'] = doc.id
                logs.append(log_data)
                
            return logs
        except Exception as e:
            print(f"Error getting food logs by date: {str(e)}")
            return []
            
    def delete_food_log(self, user_id: str, log_id: str) -> bool:
        """
        Xóa một bản ghi thực phẩm
        
        Args:
            user_id: ID của người dùng
            log_id: ID của bản ghi cần xóa
            
        Returns:
            True nếu xóa thành công, False nếu thất bại
        """
        if not self.db:
            print("Firestore service not available")
            return False
            
        try:
            # Xóa bản ghi
            doc_ref = self.db.collection('users').document(user_id).collection('food_records').document(log_id)
            doc_ref.delete()
            print(f"Food log {log_id} deleted successfully")
            
            return True
        except Exception as e:
            print(f"Error deleting food log: {str(e)}")
            return False

    def save_meal_plan(self, user_id: str, meal_plan_data: Dict) -> bool:
        """
        Lưu kế hoạch bữa ăn của người dùng vào Firestore
        
        Args:
            user_id: ID của người dùng
            meal_plan_data: Dữ liệu kế hoạch bữa ăn (đã được chuyển đổi thành Dict)
            
        Returns:
            bool: True nếu lưu thành công, False nếu thất bại
        """
        if not self.initialized:
            print(f"Firestore not initialized when trying to save meal plan for {user_id}")
            return False
            
        try:
            print(f"[INFO] Saving meal plan for user: {user_id}")
            
            # Lưu vào collection latest_meal_plans
            latest_ref = self.db.collection('latest_meal_plans').document(user_id)
            latest_ref.set(meal_plan_data)
            
            # Đồng thời lưu vào collection meal_plans với timestamp
            import time
            timestamp = int(time.time())
            history_ref = self.db.collection('meal_plans').document(f"{user_id}_{timestamp}")
            history_data = meal_plan_data.copy()
            history_data['user_id'] = user_id
            history_data['created_at'] = timestamp
            history_ref.set(history_data)
            
            print(f"[INFO] Successfully saved meal plan for user: {user_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save meal plan for user {user_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

# Singleton instance
firestore_service = FirestoreService() 