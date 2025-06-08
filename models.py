from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# Input models
class NutritionTarget(BaseModel):
    calories_target: int = Field(..., gt=0, description="Target calories in kcal")
    protein_target: int = Field(..., gt=0, description="Target protein in grams")
    fat_target: int = Field(..., gt=0, description="Target fat in grams")
    carbs_target: int = Field(..., gt=0, description="Target carbohydrates in grams")

class ReplaceDayRequest(BaseModel):
    day_of_week: str = Field(..., description="Day to replace (e.g., 'Thứ 2', 'Thứ 3', etc.)")
    calories_target: int = Field(..., gt=0, description="Target calories in kcal")
    protein_target: int = Field(..., gt=0, description="Target protein in grams")
    fat_target: int = Field(..., gt=0, description="Target fat in grams")
    carbs_target: int = Field(..., gt=0, description="Target carbohydrates in grams")

# Output models
class Ingredient(BaseModel):
    name: str
    amount: str  # e.g. "100g", "2 tbsp"

class NutritionInfo(BaseModel):
    calories: float
    protein: float
    fat: float
    carbs: float

# Enum for dish type
class DishType:
    MAIN = "main"
    SIDE = "side"
    SOUP = "soup"
    DESSERT = "dessert"
    APPETIZER = "appetizer"

# Enum for Vietnamese regions
class VietnamRegion:
    NORTH = "north"
    CENTRAL = "central"
    SOUTH = "south"
    HIGHLANDER = "highlander"
    FOREIGN = "foreign"

class Dish(BaseModel):
    name: str
    ingredients: List[Ingredient]
    preparation: List[str]
    nutrition: NutritionInfo
    dish_type: str = DishType.MAIN  # Default to main dish
    region: str = VietnamRegion.NORTH  # Default to northern region
    image_url: Optional[str] = None
    preparation_time: Optional[str] = None  # Thời gian chuẩn bị
    health_benefits: Optional[str] = None  # Lợi ích sức khỏe

class Meal(BaseModel):
    dishes: List[Dish]
    nutrition: NutritionInfo

class DayMealPlan(BaseModel):
    day_of_week: str
    breakfast: Meal
    lunch: Meal
    dinner: Meal
    nutrition: NutritionInfo

class WeeklyMealPlan(BaseModel):
    days: List[DayMealPlan]

# API Response models
class GenerateWeeklyMealResponse(BaseModel):
    meal_plan: WeeklyMealPlan
    message: str = "Weekly meal plan generated successfully"

class ReplaceDayResponse(BaseModel):
    day_meal_plan: DayMealPlan
    message: str = "Day meal plan replaced successfully"

class ReplaceWeekResponse(BaseModel):
    meal_plan: WeeklyMealPlan
    message: str = "Weekly meal plan replaced successfully"

class ErrorResponse(BaseModel):
    detail: str

# Authentication Models
class TokenPayload(BaseModel):
    """Model để chứa thông tin từ Firebase ID Token sau khi được verify"""
    uid: str
    email: Optional[str] = None
    name: Optional[str] = None
    email_verified: Optional[bool] = False
    picture: Optional[str] = None
    auth_time: Optional[int] = None
    exp: Optional[int] = None
    iat: Optional[int] = None

class AuthRequest(BaseModel):
    """Model nhận ID Token từ client"""
    id_token: str = Field(..., description="Firebase ID Token")

class UserResponse(BaseModel):
    """Model thông tin người dùng trả về"""
    uid: str
    email: Optional[str] = None
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    email_verified: Optional[bool] = False
    created_at: Optional[str] = None
    last_login: Optional[str] = None
    is_anonymous: Optional[bool] = False

class AuthResponse(BaseModel):
    """Model phản hồi sau khi xác thực thành công"""
    user: UserResponse
    message: str = "Login successful"
    status: str = "success"

# Food Recognition Models
class RecognizedFood(BaseModel):
    """Model cho thông tin món ăn đã nhận diện"""
    food_name: str = Field(..., description="Tên món ăn đã nhận diện")
    confidence: float = Field(..., description="Độ tin cậy của nhận diện (0-1)")
    nutrition: Optional[NutritionInfo] = Field(None, description="Thông tin dinh dưỡng của món ăn")
    portion_size: Optional[str] = Field(None, description="Khẩu phần ước tính")
    image_url: Optional[str] = Field(None, description="URL của hình ảnh đã lưu")
    dish_type: Optional[str] = Field(DishType.MAIN, description="Loại món ăn")
    region: Optional[str] = Field(VietnamRegion.NORTH, description="Vùng miền")

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
