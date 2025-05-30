from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, EmailStr

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

class Dish(BaseModel):
    name: str
    ingredients: List[Ingredient]
    preparation: str
    nutrition: NutritionInfo

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
