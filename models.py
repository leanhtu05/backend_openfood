from typing import List, Dict, Optional, Any, Union
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
    video_url: Optional[str] = None  # URL video hướng dẫn nấu ăn
    preparation_time: Optional[str] = None  # Thời gian chuẩn bị
    health_benefits: Optional[Union[List[str], str]] = None  # Lợi ích sức khỏe

    def model_dump(self, *args, **kwargs):
        """Pydantic v2 compatible model_dump method"""
        data = {
            "name": self.name,
            "ingredients": [ing.dict() for ing in self.ingredients],
            "preparation": self.preparation,
            "nutrition": self.nutrition.dict(),
            "dish_type": self.dish_type,
            "region": self.region,
        }
        
        if self.image_url is not None:
            data["image_url"] = self.image_url

        if self.video_url is not None:
            data["video_url"] = self.video_url

        if self.preparation_time is not None:
            data["preparation_time"] = self.preparation_time

        if self.health_benefits is not None:
            if isinstance(self.health_benefits, list):
                data["health_benefits"] = '. '.join(self.health_benefits)
            else:
                data["health_benefits"] = self.health_benefits
                
        return data
        
    def dict(self, *args, **kwargs):
        """Compatibility method for Pydantic v1"""
        return self.model_dump(*args, **kwargs)

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
    day_meal_plan: Union[DayMealPlan, Dict]
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

# AI Price Analysis Models
class PriceTrendAnalysisRequest(BaseModel):
    """Request model cho phân tích xu hướng giá"""
    category: Optional[str] = Field(None, description="Danh mục thực phẩm cần phân tích")
    days_back: int = Field(30, description="Số ngày quay lại để phân tích", ge=1, le=365)

class PricePredictionRequest(BaseModel):
    """Request model cho dự đoán giá"""
    food_name: str = Field(..., description="Tên thực phẩm cần dự đoán")
    days_ahead: int = Field(7, description="Số ngày dự đoán trước", ge=1, le=30)

class GroceryOptimizationRequest(BaseModel):
    """Request model cho tối ưu hóa grocery list"""
    grocery_items: List[Dict[str, Any]] = Field(..., description="Danh sách grocery items")
    budget_limit: Optional[float] = Field(None, description="Giới hạn ngân sách")

class SeasonalAnalysisRequest(BaseModel):
    """Request model cho phân tích mùa vụ"""
    category: Optional[str] = Field(None, description="Danh mục thực phẩm")
    current_month: Optional[int] = Field(None, description="Tháng hiện tại (1-12)")

class MarketInsightsRequest(BaseModel):
    """Request model cho market insights"""
    region: Optional[str] = Field(None, description="Khu vực địa lý")
    include_trends: bool = Field(True, description="Bao gồm phân tích xu hướng")

# AI Response Models
class AIInsight(BaseModel):
    """Model cho một insight từ AI"""
    title: str = Field(..., description="Tiêu đề insight")
    description: str = Field(..., description="Mô tả chi tiết")
    confidence: float = Field(..., description="Độ tin cậy (0-1)", ge=0, le=1)
    category: str = Field(..., description="Danh mục insight")

class PriceTrendAnalysisResponse(BaseModel):
    """Response model cho phân tích xu hướng giá"""
    analysis_date: str = Field(..., description="Ngày phân tích")
    category: str = Field(..., description="Danh mục được phân tích")
    period_days: int = Field(..., description="Số ngày phân tích")
    trend: str = Field(..., description="Xu hướng chung (increasing/decreasing/stable)")
    insights: List[AIInsight] = Field(..., description="Danh sách insights")
    recommendations: List[str] = Field(..., description="Khuyến nghị")
    price_alerts: List[Dict[str, Any]] = Field(..., description="Cảnh báo giá")

class PricePredictionResponse(BaseModel):
    """Response model cho dự đoán giá"""
    food_name: str = Field(..., description="Tên thực phẩm")
    current_price: float = Field(..., description="Giá hiện tại")
    predicted_price: float = Field(..., description="Giá dự đoán")
    prediction_days: int = Field(..., description="Số ngày dự đoán")
    confidence: float = Field(..., description="Độ tin cậy (0-100)", ge=0, le=100)
    trend: str = Field(..., description="Xu hướng (increasing/decreasing/stable)")
    factors: List[str] = Field(..., description="Yếu tố ảnh hưởng")
    recommendation: str = Field(..., description="Khuyến nghị")
    price_range: Dict[str, float] = Field(..., description="Khoảng giá dự kiến")
    generated_at: str = Field(..., description="Thời gian tạo dự đoán")

class GroceryOptimizationResponse(BaseModel):
    """Response model cho tối ưu hóa grocery"""
    total_items: int = Field(..., description="Tổng số mặt hàng")
    optimization_suggestions: List[str] = Field(..., description="Gợi ý tối ưu hóa")
    substitution_recommendations: Dict[str, str] = Field(..., description="Gợi ý thay thế")
    timing_advice: str = Field(..., description="Lời khuyên về thời điểm mua")
    budget_optimization: str = Field(..., description="Tối ưu ngân sách")
    health_insights: str = Field(..., description="Insights về dinh dưỡng")
    sustainability_tips: str = Field(..., description="Tips bền vững")
    generated_at: str = Field(..., description="Thời gian tạo")

class SeasonalAnalysisResponse(BaseModel):
    """Response model cho phân tích mùa vụ"""
    current_season: str = Field(..., description="Mùa hiện tại")
    seasonal_foods: List[str] = Field(..., description="Thực phẩm theo mùa")
    price_predictions: Dict[str, str] = Field(..., description="Dự đoán giá theo mùa")
    buying_recommendations: List[str] = Field(..., description="Khuyến nghị mua")
    avoid_buying: List[str] = Field(..., description="Nên tránh mua")
    best_deals: List[str] = Field(..., description="Deals tốt nhất")
    analysis_date: str = Field(..., description="Ngày phân tích")

class MarketInsightsResponse(BaseModel):
    """Response model cho market insights"""
    market_overview: str = Field(..., description="Tổng quan thị trường")
    trending_foods: List[str] = Field(..., description="Thực phẩm trending")
    price_volatility: Dict[str, List[str]] = Field(..., description="Biến động giá")
    regional_differences: str = Field(..., description="Khác biệt theo vùng")
    consumer_behavior: str = Field(..., description="Hành vi người tiêu dùng")
    economic_factors: str = Field(..., description="Yếu tố kinh tế")
    recommendations: List[str] = Field(..., description="Khuyến nghị")
    generated_at: str = Field(..., description="Thời gian tạo")
