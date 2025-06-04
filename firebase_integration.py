import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime
from typing import Dict, List, Optional, Any
from models import WeeklyMealPlan

# Import config để sử dụng các thông số cấu hình Firebase
from config import config

# Hàm chuyển đổi Pydantic model sang dict tương thích với cả phiên bản 1.x và 2.x
def model_to_dict(model: Any) -> Dict:
    """Chuyển đổi Pydantic model sang dict tương thích với cả phiên bản 1.x và 2.x"""
    if model is None:
        return {}
        
    try:
        # Thử phương thức model_dump() (Pydantic 2.x)
        if hasattr(model, 'model_dump'):
            return model.model_dump()
        # Thử phương thức dict() (Pydantic 1.x)
        elif hasattr(model, 'dict'):
            return model.dict()
        # Nếu là JSON-serializable object, trả về dict
        elif hasattr(model, '__dict__'):
            return model.__dict__
        # Nếu là danh sách, xử lý từng item
        elif isinstance(model, list):
            return [model_to_dict(item) for item in model]
        # Nếu là từ điển, xử lý từng giá trị
        elif isinstance(model, dict):
            return {k: model_to_dict(v) for k, v in model.items()}
        # Nếu là các kiểu dữ liệu cơ bản, trả về nguyên giá trị
        elif isinstance(model, (str, int, float, bool)) or model is None:
            return model
        # Trường hợp khác, thử chuyển đổi sang JSON rồi parse lại
        else:
            try:
                return json.loads(json.dumps(model))
            except:
                return str(model)
    except Exception as e:
        # Ghi log và trả về empty dict để không gây lỗi
        print(f"Error in model_to_dict: {str(e)}")
        return {}

class FirebaseIntegration:
    """Lớp tích hợp Firebase vào ứng dụng DietAI"""
    
    def __init__(self, credentials_path: str = "firebase-credentials.json"):
        """
        Khởi tạo kết nối Firebase
        
        Args:
            credentials_path: Đường dẫn đến file credentials của Firebase
        """
        self.initialized = False
        try:
            # Kiểm tra xem đã khởi tạo Firebase chưa
            if not firebase_admin._apps:
                # Kiểm tra file credentials tồn tại
                if os.path.exists(credentials_path):
                    # Lấy storage bucket từ config hoặc sử dụng giá trị mặc định
                    storage_bucket = config.FIREBASE_STORAGE_BUCKET
                    
                    print(f"[FIREBASE] Initializing Firebase integration")
                    print(f"[FIREBASE] Credentials file: {credentials_path}")
                    print(f"[FIREBASE] Storage bucket config: {storage_bucket}")
                    
                    # Nếu storage_bucket không được cấu hình, chỉ khởi tạo Firebase không có Storage
                    if storage_bucket:
                        # Thiết lập cấu hình với bucket storage rõ ràng
                        firebase_config = {
                            'storageBucket': storage_bucket
                        }
                        
                        print(f"[FIREBASE] Initializing Firebase with storage bucket: {storage_bucket}")
                        
                        # Khởi tạo Firebase với file credentials và cấu hình
                        cred = credentials.Certificate(credentials_path)
                        firebase_admin.initialize_app(cred, firebase_config)
                    else:
                        # Khởi tạo Firebase không có Storage
                        print("[FIREBASE] WARNING: No storage bucket configured. Storage will not be available.")
                        cred = credentials.Certificate(credentials_path)
                        firebase_admin.initialize_app(cred)
                    
                    self.initialized = True
                    print("[FIREBASE] Firebase initialized successfully with credentials file")
                else:
                    print(f"[FIREBASE] ERROR: Firebase credentials file not found at {credentials_path}")
            else:
                print("[FIREBASE] Using existing Firebase app")
                self.initialized = True
                
            # Khởi tạo Firestore
            if self.initialized:
                self.db = firestore.client()
                print(f"[FIREBASE] Firestore client initialized")
                
                try:
                    # Kiểm tra xem Firebase app có được cấu hình với storage bucket chưa
                    app_options = firebase_admin.get_app().options
                    # Khắc phục lỗi kiểu dữ liệu _AppOptions không phải iterable
                    if hasattr(app_options, 'storageBucket') and app_options.storageBucket:
                        # Thử khởi tạo storage bucket
                        self.bucket = storage.bucket()
                        print(f"[FIREBASE] Storage bucket initialized: {app_options.storageBucket}")
                    else:
                        print("[FIREBASE] WARNING: Firebase app not configured with storage bucket. Storage will not be available.")
                except Exception as storage_error:
                    print(f"[FIREBASE] ERROR initializing Storage: {storage_error}")
                    print("[FIREBASE] Continuing with Firestore (Storage unavailable)")
                
        except Exception as e:
            print(f"[FIREBASE] ERROR initializing Firebase: {e}")
            import traceback
            traceback.print_exc()
            self.initialized = False
    
    def save_meal_plan(self, meal_plan: WeeklyMealPlan, user_id: str = "default") -> str:
        """
        Lưu kế hoạch thực đơn vào Firestore
        
        Args:
            meal_plan: Đối tượng WeeklyMealPlan cần lưu
            user_id: ID của người dùng
            
        Returns:
            ID của document đã lưu
        """
        if not self.initialized:
            print(f"[FIREBASE] ERROR: Firebase not initialized when trying to save meal plan for {user_id}")
            return None
            
        try:
            print(f"[FIREBASE] Saving meal plan for user '{user_id}'")
            
            # Kiểm tra xem meal plan có rỗng không
            has_dishes = False
            dish_count = 0
            if meal_plan and meal_plan.days:
                for day in meal_plan.days:
                    day_dishes = (
                        len(day.breakfast.dishes if day.breakfast and day.breakfast.dishes else []) + 
                        len(day.lunch.dishes if day.lunch and day.lunch.dishes else []) + 
                        len(day.dinner.dishes if day.dinner and day.dinner.dishes else [])
                    )
                    dish_count += day_dishes
                    if day_dishes > 0:
                        has_dishes = True
                        break
            
            if not has_dishes:
                print(f"[FIREBASE] WARNING: Meal plan for user '{user_id}' doesn't contain any dishes.")
                print(f"[FIREBASE] Total dish count: {dish_count}")
                
                # Kiểm tra thêm các thông tin dinh dưỡng
                has_nutrition = False
                if meal_plan and meal_plan.days:
                    for day in meal_plan.days:
                        day_nutrition = day.nutrition
                        if (day_nutrition and (
                            day_nutrition.calories > 0 or 
                            day_nutrition.protein > 0 or 
                            day_nutrition.fat > 0 or 
                            day_nutrition.carbs > 0)):
                            has_nutrition = True
                            break
                
                if not has_nutrition:
                    print(f"[FIREBASE] ERROR: Meal plan for user '{user_id}' doesn't contain any nutritional information.")
                    return None
                else:
                    print(f"[FIREBASE] WARNING: Meal plan has nutritional information but no dishes.")
            
            # Tạo timestamp
            timestamp = datetime.now().isoformat()
            
            # Chuyển đổi Pydantic model thành dictionary
            meal_plan_dict = None
            try:
                meal_plan_dict = model_to_dict(meal_plan)
                print(f"[FIREBASE] Successfully converted meal plan to dictionary")
            except Exception as e:
                print(f"[FIREBASE] ERROR converting meal plan to dictionary: {str(e)}")
                # Thử phương thức khác
                try:
                    print("[FIREBASE] Trying alternate conversion method...")
                    meal_plan_dict = json.loads(meal_plan.json())
                    print("[FIREBASE] Alternate conversion successful")
                except Exception as alt_err:
                    print(f"[FIREBASE] ERROR: Alternate conversion also failed: {str(alt_err)}")
                    return None
            
            if not meal_plan_dict:
                print("[FIREBASE] ERROR: Unable to convert meal plan to dictionary. Cannot save to Firestore.")
                return None
            
            # In thống kê về kế hoạch bữa ăn
            if has_dishes:
                print(f"[FIREBASE] Saving meal plan with {dish_count} dishes across {len(meal_plan.days)} days for user '{user_id}'")
            else:
                print(f"[FIREBASE] WARNING: Attempting to save a meal plan with 0 dishes for user '{user_id}'")
            
            # Thêm metadata
            meal_plan_dict['user_id'] = user_id
            meal_plan_dict['timestamp'] = timestamp
            
            # Kiểm tra và đảm bảo trường preparation trong mỗi dish không bị mất
            for day in meal_plan_dict.get('days', []):
                for meal_type in ['breakfast', 'lunch', 'dinner']:
                    meal = day.get(meal_type, {})
                    for dish in meal.get('dishes', []):
                        if 'preparation' in dish:
                            # Đảm bảo preparation là một danh sách
                            from services import _process_preparation_steps
                            if not isinstance(dish['preparation'], list):
                                print(f"[FIREBASE] Processing preparation for dish {dish.get('name')} to list format")
                                dish['preparation'] = _process_preparation_steps(dish['preparation'])
                            print(f"[FIREBASE] Dish {dish.get('name')} has preparation instructions: {dish['preparation'][:2] if isinstance(dish['preparation'], list) else dish['preparation'][:30]}...")
                        else:
                            print(f"[FIREBASE] WARNING: Dish {dish.get('name')} missing preparation instructions!")
            
            # Lưu vào Firestore
            try:
                print("[FIREBASE] Saving to Firestore meal_plans collection...")
                meal_plans_ref = self.db.collection('meal_plans')
                doc_ref = meal_plans_ref.document()
                
                doc_ref.set(meal_plan_dict)
                doc_id = doc_ref.id
                print(f"[FIREBASE] Successfully saved to meal_plans with ID: {doc_id}")
                
                # Cập nhật document "latest" cho user này
                print(f"[FIREBASE] Updating latest_meal_plans for user {user_id}...")
                latest_ref = self.db.collection('latest_meal_plans').document(user_id)
                latest_ref.set(meal_plan_dict)
                print(f"[FIREBASE] Successfully updated latest_meal_plans")
                
                print(f"[FIREBASE] SUCCESS: Saved meal plan for user '{user_id}'")
                return doc_id
            except Exception as firebase_err:
                print(f"[FIREBASE] ERROR saving to Firestore: {str(firebase_err)}")
                import traceback
                traceback.print_exc()
                return None
                
        except Exception as e:
            print(f"[FIREBASE] ERROR saving meal plan: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def load_meal_plan(self, user_id: str = "default") -> Optional[WeeklyMealPlan]:
        """
        Lấy kế hoạch thực đơn mới nhất từ Firestore
        
        Args:
            user_id: ID của người dùng
            
        Returns:
            Đối tượng WeeklyMealPlan hoặc None nếu không tìm thấy
        """
        if not self.initialized:
            print(f"Firebase not initialized when trying to load meal plan for {user_id}")
            return None
            
        try:
            # Lấy document từ collection 'latest_meal_plans'
            doc_ref = self.db.collection('latest_meal_plans').document(user_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                print(f"No latest meal plan found for user {user_id}")
                return None
                
            data = doc.to_dict()
            if not data or 'days' not in data or not data['days']:
                print(f"Invalid meal plan data for user {user_id}")
                return None
            
            # Đảm bảo trường preparation trong mỗi dish đều là List[str]
            from services import _process_preparation_steps
            for day in data.get('days', []):
                for meal_type in ['breakfast', 'lunch', 'dinner']:
                    meal = day.get(meal_type, {})
                    for dish in meal.get('dishes', []):
                        if 'preparation' in dish:
                            # Chuyển đổi preparation thành list nếu là string
                            if not isinstance(dish['preparation'], list):
                                dish['preparation'] = _process_preparation_steps(dish['preparation'])
                                print(f"Converted preparation for dish {dish.get('name')} from string to list")
            
            try:
                # Convert dictionary to WeeklyMealPlan object
                meal_plan = WeeklyMealPlan(**data)
                print(f"Loaded meal plan for user {user_id} with {len(meal_plan.days)} days")
                return meal_plan
            except Exception as parse_err:
                print(f"Error parsing meal plan data: {str(parse_err)}")
                return None
        except Exception as e:
            print(f"Error loading meal plan from Firebase: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_meal_plan_history(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Lấy lịch sử kế hoạch thực đơn
        
        Args:
            user_id: ID của người dùng
            limit: Số lượng kế hoạch tối đa trả về
            
        Returns:
            Danh sách các kế hoạch thực đơn
        """
        if not self.initialized:
            print(f"Firebase not initialized when trying to get meal plan history for {user_id}")
            return []
            
        try:
            # Tạo query
            query = self.db.collection('meal_plans').where('user_id', '==', user_id).limit(limit)
            docs = query.stream()
            
            result = []
            for doc in docs:
                data = doc.to_dict()
                # Thêm ID vào data
                summary = {
                    'id': doc.id,
                    'timestamp': data.get('timestamp', ''),
                    'num_days': len(data.get('days', [])),
                    'user_id': data.get('user_id', '')
                }
                result.append(summary)
            
            print(f"Found {len(result)} meal plan(s) for user {user_id}")
            return result
        except Exception as e:
            print(f"Error getting meal plan history: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
        
    def get_meal_plan(self, plan_id: str) -> Optional[Dict]:
        """
        Lấy kế hoạch thực đơn theo ID
        
        Args:
            plan_id: ID của kế hoạch thực đơn
            
        Returns:
            Kế hoạch thực đơn hoặc None nếu không tìm thấy
        """
        if not self.initialized:
            print(f"Firebase not initialized when trying to get meal plan {plan_id}")
            return None
            
        try:
            doc = self.db.collection('meal_plans').document(plan_id).get()
            if doc.exists:
                data = doc.to_dict()
                
                # Đảm bảo trường preparation trong mỗi dish đều là List[str]
                from services import _process_preparation_steps
                for day in data.get('days', []):
                    for meal_type in ['breakfast', 'lunch', 'dinner']:
                        meal = day.get(meal_type, {})
                        for dish in meal.get('dishes', []):
                            if 'preparation' in dish:
                                # Chuyển đổi preparation thành list nếu là string
                                if not isinstance(dish['preparation'], list):
                                    dish['preparation'] = _process_preparation_steps(dish['preparation'])
                                    print(f"Converted preparation for dish {dish.get('name')} from string to list")
                
                return data
            else:
                print(f"Meal plan {plan_id} not found")
                return None
        except Exception as e:
            print(f"Error getting meal plan: {str(e)}")
            return None
            
    def delete_meal_plan(self, plan_id: str) -> bool:
        """
        Xóa kế hoạch thực đơn
        
        Args:
            plan_id: ID của kế hoạch thực đơn
            
        Returns:
            True nếu xóa thành công
        """
        if not self.initialized:
            print(f"Firebase not initialized when trying to delete meal plan {plan_id}")
            return False
            
        try:
            self.db.collection('meal_plans').document(plan_id).delete()
            print(f"Deleted meal plan {plan_id}")
            return True
        except Exception as e:
            print(f"Error deleting meal plan: {str(e)}")
            return False
    
    def cache_nutrition_data(self, key: str, value: Dict, ttl_days: int = 30) -> bool:
        """
        Lưu dữ liệu dinh dưỡng vào cache Firestore
        
        Args:
            key: Khóa cache
            value: Giá trị cần lưu
            ttl_days: Thời gian sống của cache (ngày)
            
        Returns:
            True nếu lưu thành công, False nếu không
        """
        if not self.initialized:
            return False
            
        try:
            # Tạo document data với thời gian hết hạn
            expiry = datetime.now().timestamp() + (ttl_days * 86400)
            data = {
                'value': value,
                'expiry': expiry
            }
            
            # Lưu vào collection nutrition_cache
            self.db.collection('nutrition_cache').document(key).set(data)
            return True
                
        except Exception as e:
            print(f"Error caching nutrition data in Firebase: {e}")
            return False
    
    def get_cached_nutrition_data(self, key: str) -> Optional[Dict]:
        """
        Lấy dữ liệu dinh dưỡng từ cache Firestore
        
        Args:
            key: Khóa cache
            
        Returns:
            Dữ liệu dinh dưỡng hoặc None nếu không tìm thấy hoặc hết hạn
        """
        if not self.initialized:
            return None
            
        try:
            # Lấy document từ collection nutrition_cache
            doc = self.db.collection('nutrition_cache').document(key).get()
            
            if doc.exists:
                data = doc.to_dict()
                
                # Kiểm tra hết hạn
                if data.get('expiry', 0) > datetime.now().timestamp():
                    return data.get('value')
                else:
                    # Xóa cache hết hạn
                    self.db.collection('nutrition_cache').document(key).delete()
            
            return None
                
        except Exception as e:
            print(f"Error getting cached nutrition data from Firebase: {e}")
            return None

    def create_user(self, user_id: str, user_data: dict) -> bool:
        if not self.initialized:
            print(f"[FIREBASE] ERROR: Firebase not initialized when trying to create user {user_id}")
            return False
        try:
            print(f"[FIREBASE] Creating user with ID: {user_id}")
            if hasattr(user_data, 'to_dict'):
                user_dict = user_data.to_dict()
            elif hasattr(user_data, 'dict'):
                user_dict = user_data.dict()
            else:
                user_dict = user_data
            from datetime import datetime
            user_dict['created_at'] = datetime.now().isoformat()
            self.db.collection('users').document(user_id).set(user_dict)
            print(f"[FIREBASE] Successfully created user {user_id}")
            return True
        except Exception as e:
            print(f"[FIREBASE] ERROR creating user: {str(e)}")
            import traceback; traceback.print_exc()
            return False

    def get_user(self, user_id: str) -> dict:
        if not self.initialized:
            print(f"[FIREBASE] ERROR: Firebase not initialized when trying to get user {user_id}")
            return None
        try:
            print(f"[FIREBASE] Getting user with ID: {user_id}")
            doc = self.db.collection('users').document(user_id).get()
            if doc.exists:
                print(f"[FIREBASE] Successfully retrieved user {user_id}")
                return doc.to_dict()
            else:
                print(f"[FIREBASE] User {user_id} not found")
                return None
        except Exception as e:
            print(f"[FIREBASE] ERROR getting user: {str(e)}")
            import traceback; traceback.print_exc()
            return None

# Tạo instance toàn cục
firebase = FirebaseIntegration() 