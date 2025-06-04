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
        
# Create singleton instance
food_recognition_service = FoodRecognitionService() 