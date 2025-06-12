# Import required dependencies
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field
import json
from pydantic import validator, root_validator
from datetime import datetime
from enum import Enum, auto

# Import models from firestore_models
from models.firestore_models import (
    UserProfile,
    DailyLog,
    Meal as FirestoreMeal,
    MealPlan,
    SuggestedMeal,
    AISuggestion
)

# Import TokenPayload from token module
from models.token import TokenPayload

# Enum for dish type
class DishType(str, Enum):
    MAIN = "main"
    SIDE = "side"
    SOUP = "soup"
    DESSERT = "dessert"
    APPETIZER = "appetizer"

# Enum for Vietnamese regions
class VietnamRegion(str, Enum):
    NORTH = "north"
    CENTRAL = "central"
    SOUTH = "south"
    HIGHLANDER = "highlander"
    FOREIGN = "foreign"

# Import authentication models
class AuthRequest(BaseModel):
    id_token: str

class UserResponse(BaseModel):
    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    email_verified: bool = False
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    is_anonymous: bool = False

class AuthResponse(BaseModel):
    user: UserResponse

# Input models
class NutritionTarget(BaseModel):
    calories_target: int = Field(..., gt=0, description="Target calories in kcal")
    protein_target: int = Field(..., gt=0, description="Target protein in grams")
    fat_target: int = Field(..., gt=0, description="Target fat in grams")
    carbs_target: int = Field(..., gt=0, description="Target carbohydrates in grams")

class ReplaceDayRequest(BaseModel):
    day_of_week: str = Field(..., description="Day to replace (e.g., 'Thứ 2', 'Thứ 3', etc.)")
    calories_target: Optional[int] = Field(None, description="Target calories in kcal")
    protein_target: Optional[int] = Field(None, description="Target protein in grams")
    fat_target: Optional[int] = Field(None, description="Target fat in grams")
    carbs_target: Optional[int] = Field(None, description="Target carbohydrates in grams")
    nutrition_targets: Optional[Dict[str, float]] = Field(None, description="Nutrition targets from Flutter")
    user_id: Optional[str] = Field(None, description="User ID from Flutter")
    use_ai: Optional[bool] = Field(False, description="Whether to use AI for generation")
    
    @validator('nutrition_targets', pre=True)
    def extract_nutrition_targets(cls, v, values):
        if v is not None:
            # Extract values from nutrition_targets if direct fields are not provided
            if 'calories_target' not in values or values['calories_target'] is None:
                values['calories_target'] = int(v.get('calories', 0))
            if 'protein_target' not in values or values['protein_target'] is None:
                values['protein_target'] = int(v.get('protein', 0))
            if 'fat_target' not in values or values['fat_target'] is None:
                values['fat_target'] = int(v.get('fat', 0))
            if 'carbs_target' not in values or values['carbs_target'] is None:
                values['carbs_target'] = int(v.get('carbs', 0))
        return v
    
    @root_validator(skip_on_failure=True)
    def check_nutrition_targets(cls, values):
        # Ensure nutrition targets are provided
        if (values.get('calories_target') is None or values.get('calories_target') <= 0 or
            values.get('protein_target') is None or values.get('protein_target') <= 0 or
            values.get('fat_target') is None or values.get('fat_target') <= 0 or
            values.get('carbs_target') is None or values.get('carbs_target') <= 0):
            raise ValueError("Missing nutrition targets. Please provide calories_target, protein_target, fat_target, carbs_target or nutrition_targets")
        return values

# Output models
class Ingredient(BaseModel):
    name: str
    amount: str  # e.g. "100g", "2 tbsp"

class NutritionInfo(BaseModel):
    # Thông tin dinh dưỡng cơ bản
    calories: float
    protein: float  # g
    fat: float  # g
    carbs: float  # g

    # Thông tin dinh dưỡng chi tiết
    fiber: Optional[float] = Field(None, description="Chất xơ (g)")
    sugar: Optional[float] = Field(None, description="Đường (g)")
    saturated_fat: Optional[float] = Field(None, description="Chất béo bão hòa (g)")
    trans_fat: Optional[float] = Field(None, description="Chất béo chuyển hóa (g)")
    cholesterol: Optional[float] = Field(None, description="Cholesterol (mg)")
    sodium: Optional[float] = Field(None, description="Natri (mg)")
    potassium: Optional[float] = Field(None, description="Kali (mg)")
    calcium: Optional[float] = Field(None, description="Canxi (mg)")
    iron: Optional[float] = Field(None, description="Sắt (mg)")
    vitamin_c: Optional[float] = Field(None, description="Vitamin C (mg)")
    vitamin_a: Optional[float] = Field(None, description="Vitamin A (IU)")
    caffeine: Optional[float] = Field(None, description="Caffeine (mg)")
    alcohol: Optional[float] = Field(None, description="Cồn (g)")

    # Thông tin bổ sung
    glycemic_index: Optional[int] = Field(None, description="Chỉ số đường huyết (0-100)")
    water_content: Optional[float] = Field(None, description="Hàm lượng nước (%)")

class Dish(BaseModel):
    name: str
    ingredients: List[Ingredient]
    preparation: List[str]
    nutrition: NutritionInfo
    dish_type: str = DishType.MAIN  # Default to main dish
    region: str = VietnamRegion.NORTH  # Default to northern region
    image_url: Optional[str] = None
    # video_url removed
    preparation_time: Optional[str] = None  # Thời gian chuẩn bị
    health_benefits: Optional[Union[List[str], str]] = None  # Lợi ích sức khỏe
    
    def dict(self, *args, **kwargs):
        """Custom dict method to handle health_benefits, preparation_time, and video_url"""
        # Sử dụng model_dump() cho Pydantic v2 hoặc dict() cho v1
        try:
            result = super().model_dump(*args, **kwargs)
        except AttributeError:
            result = super().dict(*args, **kwargs)

        # Đảm bảo bao gồm preparation_time và health_benefits
        if hasattr(self, 'preparation_time') and self.preparation_time is not None:
            result['preparation_time'] = self.preparation_time

        if hasattr(self, 'health_benefits') and self.health_benefits is not None:
            # Chuyển đổi health_benefits thành chuỗi nếu là danh sách
            if isinstance(self.health_benefits, list):
                result['health_benefits'] = self.health_benefits  # Giữ nguyên list
            else:
                result['health_benefits'] = self.health_benefits

        # Đảm bảo bao gồm video_url
        if hasattr(self, 'video_url') and self.video_url is not None:
            result['video_url'] = self.video_url

        return result

    def model_dump(self, *args, **kwargs):
        """Pydantic v2 compatible model_dump method"""
        return self.dict(*args, **kwargs)

class Meal(BaseModel):
    dishes: List[Dish]
    nutrition: NutritionInfo

    # video_url serialization logic removed

class DayMealPlan(BaseModel):
    day_of_week: str
    breakfast: Meal
    lunch: Meal
    dinner: Meal
    nutrition: NutritionInfo

    def dict(self, *args, **kwargs):
        """Custom dict method để đảm bảo video_url được serialize"""
        try:
            result = super().model_dump(*args, **kwargs)
        except AttributeError:
            result = super().dict(*args, **kwargs)

        # Đảm bảo tất cả meals có video_url trong dishes
        for meal_name in ['breakfast', 'lunch', 'dinner']:
            if meal_name in result and 'dishes' in result[meal_name]:
                for dish in result[meal_name]['dishes']:
                    if 'video_url' not in dish:
                        dish['video_url'] = None

        return result

    def model_dump(self, *args, **kwargs):
        """Pydantic v2 compatible model_dump method"""
        return self.dict(*args, **kwargs)

class WeeklyMealPlan(BaseModel):
    days: List[DayMealPlan]

    def dict(self, *args, **kwargs):
        """Custom dict method để đảm bảo video_url được serialize"""
        try:
            result = super().model_dump(*args, **kwargs)
        except AttributeError:
            result = super().dict(*args, **kwargs)

        # Đảm bảo tất cả dishes có video_url
        if 'days' in result:
            for day in result['days']:
                for meal_name in ['breakfast', 'lunch', 'dinner']:
                    if meal_name in day and 'dishes' in day[meal_name]:
                        for dish in day[meal_name]['dishes']:
                            if 'video_url' not in dish:
                                dish['video_url'] = None

        return result

    def model_dump(self, *args, **kwargs):
        """Pydantic v2 compatible model_dump method"""
        return self.dict(*args, **kwargs)

    # Thêm phương thức để tương thích với cả Pydantic 1.x và 2.x
    def json(self, **kwargs):
        return json.dumps(self.dict(), **kwargs)

    def model_dump_json(self, **kwargs):
        return json.dumps(self.dict(), **kwargs)

# API Response models
class GenerateWeeklyMealRequest(BaseModel):
    """Yêu cầu tạo kế hoạch bữa ăn hàng tuần"""
    calories_target: int = Field(..., description="Target calories per day (kcal)")
    protein_target: int = Field(..., description="Target protein per day (g)")
    fat_target: int = Field(..., description="Target fat per day (g)")
    carbs_target: int = Field(..., description="Target carbohydrates per day (g)")
    preferences: Optional[List[str]] = Field(None, description="Food preferences")
    allergies: Optional[List[str]] = Field(None, description="Food allergies")
    cuisine_style: Optional[str] = Field(None, description="Cuisine style preference")

class GenerateWeeklyMealResponse(BaseModel):
    """Phản hồi từ API tạo kế hoạch bữa ăn hàng tuần"""
    meal_plan: WeeklyMealPlan
    message: str = "Weekly meal plan generated successfully"

class ReplaceDayResponse(BaseModel):
    """Phản hồi từ API thay thế kế hoạch bữa ăn một ngày"""
    day_meal_plan: Union[DayMealPlan, Dict]
    message: str = "Day meal plan replaced successfully"

class ReplaceWeekResponse(BaseModel):
    meal_plan: WeeklyMealPlan
    message: str = "Weekly meal plan replaced successfully"

class ErrorResponse(BaseModel):
    detail: str 
    
# Food Recognition Models
class RecognizedFood(BaseModel):
    """Model cho thông tin món ăn đã nhận diện"""
    food_name: str = Field(..., description="Tên món ăn đã nhận diện")
    confidence: float = Field(..., description="Độ tin cậy của nhận diện (0-1)")
    nutrition: Optional[NutritionInfo] = Field(None, description="Thông tin dinh dưỡng của món ăn")
    portion_size: Optional[str] = Field(None, description="Khẩu phần ước tính")
    image_url: Optional[str] = Field(None, description="URL của hình ảnh đã lưu")

class FoodRecognitionResponse(BaseModel):
    """Model phản hồi sau khi nhận diện thực phẩm"""
    recognized_foods: List[RecognizedFood] = Field(..., description="Danh sách các món ăn đã nhận diện")
    message: str = Field("Food recognition successful", description="Thông báo trạng thái")
    raw_analysis: Optional[Dict[str, Any]] = Field(None, description="Phân tích thô từ Gemini")
    timestamp: str = Field(..., description="Thời gian nhận diện")

class FoodLogEntry(BaseModel):
    """Model để lưu trữ bản ghi thực phẩm vào Firestore"""
    user_id: str = Field(..., description="ID của người dùng")
    recognized_foods: List[RecognizedFood] = Field(..., description="Danh sách các món ăn đã nhận diện")
    meal_type: str = Field(..., description="Loại bữa ăn (breakfast, lunch, dinner, snack)")
    image_url: str = Field(..., description="URL của hình ảnh đã lưu")
    timestamp: str = Field(..., description="Thời gian nhận diện")
    date: str = Field(..., description="Ngày ghi nhận (YYYY-MM-DD)")
    total_nutrition: NutritionInfo = Field(..., description="Tổng dinh dưỡng của bữa ăn") 