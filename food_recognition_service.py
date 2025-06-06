"""
Food Recognition Service combining Gemini Vision API with Firebase storage and Firestore
"""
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Import models
from models import RecognizedFood, NutritionInfo, FoodLogEntry, FoodRecognitionResponse

# Import services
from gemini_vision import gemini_vision_service
from firebase_storage_service import firebase_storage_service
from services.firestore_service import firestore_service

class FoodRecognitionService:
    """Service for recognizing food items in images and storing data"""
    
    def __init__(self):
        """Initialize the Food Recognition Service"""
        # Check availability of required services
        self.gemini_available = gemini_vision_service.available
        self.firebase_storage_available = firebase_storage_service.available
        self.firestore_available = firestore_service is not None
        
        # Service is available if at least Gemini is available
        # (Storage and Firestore are optional but useful)
        self.available = self.gemini_available
        
        print(f"\n=== FOOD RECOGNITION SERVICE ===")
        print(f"Gemini Vision available: {self.gemini_available}")
        print(f"Firebase Storage available: {self.firebase_storage_available}")
        print(f"Firestore available: {self.firestore_available}")
        print(f"Service available: {self.available}")
        print(f"=== FOOD RECOGNITION SERVICE INITIALIZED ===\n")
        
    async def recognize_food_from_image(self, 
                                  image_data: bytes, 
                                  user_id: str,
                                  meal_type: str = "snack",
                                  save_to_firebase: bool = True) -> FoodRecognitionResponse:
        """
        Recognize food from image data, store image, and log to Firestore
        
        Args:
            image_data: Raw image bytes
            user_id: ID of the user
            meal_type: Type of meal (breakfast, lunch, dinner, snack)
            save_to_firebase: Whether to save results to Firebase
            
        Returns:
            FoodRecognitionResponse with recognition results
        """
        if not self.available:
            raise ValueError("Food recognition service is not available")
            
        # Step 1: Upload image to Firebase Storage (if available)
        image_url = None
        if self.firebase_storage_available and save_to_firebase:
            image_url = firebase_storage_service.upload_image(
                image_data=image_data,
                user_id=user_id,
                folder="food_images"
            )
            
        # Step 2: Use Gemini Vision to recognize food items
        recognized_foods, raw_analysis = gemini_vision_service.recognize_food(image_data)
        
        # Add image URL to recognized foods
        for food in recognized_foods:
            food.image_url = image_url
            
        # Step 3: Calculate total nutrition values across all recognized foods
        total_nutrition = NutritionInfo(calories=0, protein=0, fat=0, carbs=0)
        for food in recognized_foods:
            if food.nutrition:
                total_nutrition.calories += food.nutrition.calories
                total_nutrition.protein += food.nutrition.protein
                total_nutrition.fat += food.nutrition.fat
                total_nutrition.carbs += food.nutrition.carbs
                
        # Step 4: Save to Firestore if requested
        if self.firestore_available and save_to_firebase:
            # Get current timestamp and date
            timestamp = datetime.now().isoformat()
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Create the food log entry
            food_log = FoodLogEntry(
                user_id=user_id,
                recognized_foods=recognized_foods,
                meal_type=meal_type,
                image_url=image_url or "",
                timestamp=timestamp,
                date=current_date,
                total_nutrition=total_nutrition
            )
            
            # Save to Firestore
            try:
                # Convert to dictionary for Firestore
                log_data = food_log.dict()
                
                # Add to Firestore
                firestore_service.add_food_log(user_id, log_data)
                print(f"Food log saved to Firestore for user {user_id}")
            except Exception as e:
                print(f"Error saving food log to Firestore: {str(e)}")
                
        # Step 5: Return the recognition response
        timestamp = datetime.now().isoformat()
        recognition_response = FoodRecognitionResponse(
            recognized_foods=recognized_foods,
            message="Food recognition completed successfully" if recognized_foods else "No food items recognized",
            raw_analysis=raw_analysis,
            timestamp=timestamp
        )
        
        return recognition_response
        
    async def add_dish_to_meal_log(
        user_id: str,
        meal_type: str,
        dish: Dict,
        replace_existing: bool = False
    ) -> bool:
        """
        Thêm một món ăn vào bản ghi bữa ăn hiện tại
        
        Args:
            user_id: ID của người dùng
            meal_type: Loại bữa ăn (breakfast, lunch, dinner, snack)
            dish: Thông tin món ăn
            replace_existing: Có thay thế bản ghi hiện tại không
            
        Returns:
            True nếu thành công, False nếu không
        """
        try:
            print(f"Adding dish to meal log: {dish.get('name', 'Unknown')} for {user_id} - {meal_type}")
            
            # Lấy ngày hiện tại
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Tạo đối tượng RecognizedFood từ dữ liệu món ăn
            recognized_food = RecognizedFood(
                food_name=dish.get('name', 'Unknown dish'),
                confidence=1.0,  # Đây là món ăn được chọn nên tin cậy cao
                nutrition=NutritionInfo(
                    calories=dish.get('nutrition', {}).get('calories', 0),
                    protein=dish.get('nutrition', {}).get('protein', 0),
                    fat=dish.get('nutrition', {}).get('fat', 0),
                    carbs=dish.get('nutrition', {}).get('carbs', 0)
                ),
                portion_size=dish.get('portion_size', '1 serving'),
                image_url=dish.get('image_url', None),
                dish_type=dish.get('dish_type', 'main'),
                region=dish.get('region', 'north')
            )
            
            # Lấy bản ghi hiện tại của ngày hôm nay nếu có
            current_logs = firestore_service.get_food_logs_by_date(user_id, today)
            
            # Lọc bản ghi theo loại bữa ăn
            meal_logs = [log for log in current_logs if log.get('meal_type', '') == meal_type]
            
            if meal_logs and not replace_existing:
                # Đã có bản ghi cho bữa ăn này - thêm món mới vào
                log_id = meal_logs[0].get('id')
                existing_foods = meal_logs[0].get('recognized_foods', [])
                
                # Kiểm tra xem món ăn đã tồn tại chưa
                food_exists = False
                for food in existing_foods:
                    if food.get('food_name') == recognized_food.food_name:
                        food_exists = True
                        break
                
                if not food_exists:
                    # Chỉ thêm vào nếu chưa có món này
                    existing_foods.append(recognized_food.dict())
                    
                    # Tính toán lại tổng dinh dưỡng
                    total_nutrition = {
                        'calories': sum(food.get('nutrition', {}).get('calories', 0) for food in existing_foods),
                        'protein': sum(food.get('nutrition', {}).get('protein', 0) for food in existing_foods),
                        'fat': sum(food.get('nutrition', {}).get('fat', 0) for food in existing_foods),
                        'carbs': sum(food.get('nutrition', {}).get('carbs', 0) for food in existing_foods)
                    }
                    
                    # Cập nhật bản ghi
                    return firestore_service.update_food_log(
                        user_id=user_id,
                        log_id=log_id,
                        recognized_foods=existing_foods,
                        total_nutrition=total_nutrition
                    )
            else:
                # Tạo bản ghi mới
                timestamp = datetime.now().isoformat()
                
                # Tạo dữ liệu bản ghi
                log_entry = {
                    'user_id': user_id,
                    'recognized_foods': [recognized_food.dict()],
                    'meal_type': meal_type,
                    'image_url': dish.get('image_url', ''),
                    'timestamp': timestamp,
                    'date': today,
                    'total_nutrition': {
                        'calories': recognized_food.nutrition.calories,
                        'protein': recognized_food.nutrition.protein,
                        'fat': recognized_food.nutrition.fat,
                        'carbs': recognized_food.nutrition.carbs
                    }
                }
                
                # Lưu vào Firestore
                return firestore_service.add_food_log(log_entry)
            
        except Exception as e:
            print(f"Error adding dish to meal log: {e}")
            return False

# Create singleton instance
food_recognition_service = FoodRecognitionService() 