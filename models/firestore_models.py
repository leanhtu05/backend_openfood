from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

# User models
class UserProfile(BaseModel):
    """Model cho thông tin người dùng"""
    name: str = Field(..., description="Tên người dùng")
    email: str = Field(..., description="Email người dùng")
    age: Optional[int] = Field(None, description="Tuổi")
    weight: Optional[float] = Field(None, description="Cân nặng (kg)")
    height: Optional[float] = Field(None, description="Chiều cao (cm)")
    targetCalories: Optional[int] = Field(None, description="Mục tiêu calories hàng ngày")
    
    # Thông tin bổ sung từ Flutter
    gender: Optional[str] = Field(None, description="Giới tính (nam/nữ/khác)", alias="genderField")
    activity_level: Optional[str] = Field(None, description="Mức độ hoạt động (thấp/trung bình/cao)", alias="activityLevelField")
    activityLevel: Optional[str] = Field(None, description="Mức độ hoạt động - tương thích với Flutter")
    goal: Optional[str] = Field(None, description="Mục tiêu (giảm cân/tăng cân/giữ cân)")
    dietType: Optional[str] = Field(None, description="Loại chế độ ăn (omnivore/vegetarian/vegan/keto/etc)")
    preferred_cuisines: Optional[List[str]] = Field(None, description="Danh sách ẩm thực ưa thích")
    allergies: Optional[List[str]] = Field(None, description="Danh sách thực phẩm gây dị ứng")
    lastSyncTime: Optional[str] = Field(None, description="Thời gian đồng bộ cuối cùng")
    deviceInfo: Optional[Dict[str, Any]] = Field(None, description="Thông tin thiết bị")
    
    # Thông tin mục tiêu giảm cân
    tdee: Optional[int] = Field(None, description="Tổng năng lượng tiêu thụ hàng ngày (kcal)")
    weight_goal: Optional[float] = Field(None, description="Mục tiêu cân nặng (kg)")
    weight_goal_rate: Optional[float] = Field(None, description="Tốc độ giảm/tăng cân (kg/tuần)")
    weight_goal_calories: Optional[int] = Field(None, description="Calo mục tiêu để đạt được tốc độ giảm/tăng cân")
    
    # Phương thức để chuyển đổi thành dict cho Firestore
    def to_dict(self) -> Dict[str, Any]:
        # Chuẩn hóa activityLevel
        activity_level = self.activityLevel or self.activity_level
        
        data = {
            "name": self.name,
            "email": self.email,
            "age": self.age,
            "weight": self.weight,
            "height": self.height,
            "targetCalories": self.targetCalories,
            "gender": self.gender,
            "activityLevel": activity_level,
            "activity_level": activity_level,  # Lưu cả hai định dạng để tương thích
            "goal": self.goal,
            "dietType": self.dietType,
            "preferred_cuisines": self.preferred_cuisines,
            "allergies": self.allergies,
            "lastSyncTime": self.lastSyncTime or datetime.now().isoformat(),
            "deviceInfo": self.deviceInfo,
            "tdee": self.tdee,
            "weight_goal": self.weight_goal,
            "weight_goal_rate": self.weight_goal_rate,
            "weight_goal_calories": self.weight_goal_calories
        }
        
        # Loại bỏ các giá trị None
        return {k: v for k, v in data.items() if v is not None}
    
    def toJson(self):
        return self.to_dict()

    # Tạo từ dict từ Firestore
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        # Chuẩn hóa activity_level
        activity_level = data.get("activityLevel") or data.get("activity_level")
        
        return cls(
            name=data.get("name", ""),
            email=data.get("email", ""),
            age=data.get("age"),
            weight=data.get("weight"),
            height=data.get("height"),
            targetCalories=data.get("targetCalories"),
            gender=data.get("gender"),
            activityLevel=activity_level,
            activity_level=activity_level,
            goal=data.get("goal"),
            dietType=data.get("dietType"),
            preferred_cuisines=data.get("preferred_cuisines"),
            allergies=data.get("allergies"),
            lastSyncTime=data.get("lastSyncTime"),
            deviceInfo=data.get("deviceInfo"),
            tdee=data.get("tdee"),
            weight_goal=data.get("weight_goal"),
            weight_goal_rate=data.get("weight_goal_rate"),
            weight_goal_calories=data.get("weight_goal_calories")
        )

# Daily Log models
class DailyLog(BaseModel):
    """Model cho log hàng ngày của người dùng"""
    date: str = Field(..., description="Ngày (YYYY-MM-DD)")
    caloriesIntake: int = Field(0, description="Tổng lượng calories đã tiêu thụ")
    meals: List[str] = Field(default_factory=list, description="Danh sách các bữa ăn")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "caloriesIntake": self.caloriesIntake,
            "meals": self.meals
        }

    def toJson(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DailyLog':
        return cls(
            date=data.get("date", ""),
            caloriesIntake=data.get("caloriesIntake", 0),
            meals=data.get("meals", [])
        )

# Meal models
class Ingredient(BaseModel):
    """Model cho nguyên liệu"""
    name: str = Field(..., description="Tên nguyên liệu")
    amount: str = Field(..., description="Số lượng")

class Meal(BaseModel):
    """Model cho một bữa ăn"""
    name: str = Field(..., description="Tên món ăn")
    calories: int = Field(..., description="Lượng calories")
    type: str = Field(..., description="Loại bữa ăn (breakfast, lunch, dinner, snack)")
    ingredients: List[Ingredient] = Field(default_factory=list, description="Danh sách nguyên liệu")
    instructions: List[str] = Field(default_factory=list, description="Các bước chế biến")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "calories": self.calories,
            "type": self.type,
            "ingredients": [ing.dict() for ing in self.ingredients],
            "instructions": self.instructions
        }

    def toJson(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Meal':
        ingredients = [Ingredient(**ing) for ing in data.get("ingredients", [])]
        return cls(
            name=data.get("name", ""),
            calories=data.get("calories", 0),
            type=data.get("type", ""),
            ingredients=ingredients,
            instructions=data.get("instructions", [])
        )

# Meal Plan models
class MealPlan(BaseModel):
    """Model cho kế hoạch bữa ăn"""
    userId: str = Field(..., description="ID người dùng")
    date: str = Field(..., description="Ngày (YYYY-MM-DD)")
    meals: List[Meal] = Field(default_factory=list, description="Danh sách các bữa ăn")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.userId,
            "date": self.date,
            "meals": [meal.to_dict() for meal in self.meals]
        }

    def toJson(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MealPlan':
        return cls(
            userId=data.get("userId", ""),
            date=data.get("date", ""),
            meals=[Meal.from_dict(meal) for meal in data.get("meals", [])]
        )

# AI Suggestion models
class SuggestedMeal(BaseModel):
    """Model cho món ăn được gợi ý"""
    name: str = Field(..., description="Tên món ăn")
    calories: int = Field(..., description="Lượng calories")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "calories": self.calories
        }

    def toJson(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SuggestedMeal':
        return cls(
            name=data.get("name", ""),
            calories=data.get("calories", 0)
        )

class AISuggestion(BaseModel):
    """Model cho gợi ý từ AI"""
    userId: str = Field(..., description="ID người dùng")
    input: str = Field(..., description="Đầu vào của người dùng")
    suggestedMeals: List[SuggestedMeal] = Field(default_factory=list, description="Danh sách món ăn gợi ý")
    timestamp: datetime = Field(default_factory=datetime.now, description="Thời gian gợi ý")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.userId,
            "input": self.input,
            "suggestedMeals": [meal.to_dict() for meal in self.suggestedMeals],
            "timestamp": self.timestamp.isoformat()
        }

    def toJson(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AISuggestion':
        timestamp = data.get("timestamp")
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except:
                timestamp = datetime.now()
                
        return cls(
            userId=data.get("userId", ""),
            input=data.get("input", ""),
            suggestedMeals=[SuggestedMeal.from_dict(meal) for meal in data.get("suggestedMeals", [])],
            timestamp=timestamp
        )

# ===== EXERCISE MODELS =====

class Exercise(BaseModel):
    """Model cho bài tập"""
    name: str = Field(..., description="Tên bài tập")
    description: str = Field(default="", description="Mô tả bài tập")
    category: str = Field(..., description="Danh mục bài tập (ví dụ: cardio, strength, flexibility)")
    calories_burned: float = Field(default=0, description="Lượng calories đốt cháy (ước tính cho 30 phút)")
    difficulty: str = Field(default="medium", description="Độ khó (easy, medium, hard)")
    muscle_groups: List[str] = Field(default_factory=list, description="Các nhóm cơ được tác động")
    image_url: Optional[str] = Field(default=None, description="URL hình ảnh minh họa")
    video_url: Optional[str] = Field(default=None, description="URL video hướng dẫn")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Thời gian tạo")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "calories_burned": self.calories_burned,
            "difficulty": self.difficulty,
            "muscle_groups": self.muscle_groups,
            "image_url": self.image_url,
            "video_url": self.video_url,
            "created_at": self.created_at
        }
    
    def toJson(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Exercise':
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", ""),
            calories_burned=data.get("calories_burned", 0),
            difficulty=data.get("difficulty", "medium"),
            muscle_groups=data.get("muscle_groups", []),
            image_url=data.get("image_url"),
            video_url=data.get("video_url"),
            created_at=data.get("created_at", datetime.now().isoformat())
        )

class ExerciseHistory(BaseModel):
    """Model cho lịch sử bài tập của người dùng"""
    userId: str = Field(..., description="ID của người dùng")
    exerciseId: str = Field(..., description="ID của bài tập")
    exercise_name: str = Field(..., description="Tên bài tập")
    date: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'), description="Ngày thực hiện (YYYY-MM-DD)")
    duration_minutes: int = Field(..., description="Thời gian thực hiện (phút)")
    calories_burned: float = Field(default=0, description="Lượng calories đốt cháy")
    notes: str = Field(default="", description="Ghi chú của người dùng")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Thời gian ghi nhận")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.userId,
            "exerciseId": self.exerciseId,
            "exercise_name": self.exercise_name,
            "date": self.date,
            "duration_minutes": self.duration_minutes,
            "calories_burned": self.calories_burned,
            "notes": self.notes,
            "timestamp": self.timestamp
        }
    
    def toJson(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExerciseHistory':
        return cls(
            userId=data.get("userId", ""),
            exerciseId=data.get("exerciseId", ""),
            exercise_name=data.get("exercise_name", ""),
            date=data.get("date", datetime.now().strftime('%Y-%m-%d')),
            duration_minutes=data.get("duration_minutes", 0),
            calories_burned=data.get("calories_burned", 0),
            notes=data.get("notes", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat())
        )

# ===== BEVERAGE MODELS =====

class Beverage(BaseModel):
    """Model cho loại nước uống"""
    name: str = Field(..., description="Tên nước uống")
    description: str = Field(default="", description="Mô tả nước uống")
    category: str = Field(default="water", description="Danh mục (water, tea, coffee, juice, etc.)")
    calories_per_100ml: float = Field(default=0, description="Lượng calories trên 100ml")
    hydration_index: float = Field(default=1.0, description="Chỉ số hydrat hóa (nước = 1.0)")
    sugar_content: float = Field(default=0, description="Lượng đường (g per 100ml)")
    caffeine_content: float = Field(default=0, description="Lượng caffeine (mg per 100ml)")
    image_url: Optional[str] = Field(default=None, description="URL hình ảnh minh họa")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Thời gian tạo")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "calories_per_100ml": self.calories_per_100ml,
            "hydration_index": self.hydration_index,
            "sugar_content": self.sugar_content,
            "caffeine_content": self.caffeine_content,
            "image_url": self.image_url,
            "created_at": self.created_at
        }
    
    def toJson(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Beverage':
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", "water"),
            calories_per_100ml=data.get("calories_per_100ml", 0),
            hydration_index=data.get("hydration_index", 1.0),
            sugar_content=data.get("sugar_content", 0),
            caffeine_content=data.get("caffeine_content", 0),
            image_url=data.get("image_url"),
            created_at=data.get("created_at", datetime.now().isoformat())
        )

class WaterIntake(BaseModel):
    """Model cho lượng nước uống của người dùng"""
    userId: str = Field(..., description="ID của người dùng")
    date: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'), description="Ngày ghi nhận (YYYY-MM-DD)")
    beverage_id: Optional[str] = Field(default=None, description="ID của loại nước uống (nếu không phải là nước lọc)")
    beverage_name: str = Field(default="Water", description="Tên nước uống")
    amount_ml: int = Field(..., description="Lượng nước uống (ml)")
    calories: float = Field(default=0, description="Lượng calories")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Thời gian ghi nhận")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.userId,
            "date": self.date,
            "beverage_id": self.beverage_id,
            "beverage_name": self.beverage_name,
            "amount_ml": self.amount_ml,
            "calories": self.calories,
            "timestamp": self.timestamp
        }
    
    def toJson(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WaterIntake':
        return cls(
            userId=data.get("userId", ""),
            date=data.get("date", datetime.now().strftime('%Y-%m-%d')),
            beverage_id=data.get("beverage_id"),
            beverage_name=data.get("beverage_name", "Water"),
            amount_ml=data.get("amount_ml", 0),
            calories=data.get("calories", 0),
            timestamp=data.get("timestamp", datetime.now().isoformat())
        )

# ===== FOOD ITEM MODELS =====

class FoodItem(BaseModel):
    """Model cho món ăn riêng lẻ"""
    name: str = Field(..., description="Tên món ăn")
    description: str = Field(default="", description="Mô tả món ăn")
    category: str = Field(default="other", description="Danh mục (protein, carbs, vegetable, etc.)")
    calories_per_100g: float = Field(..., description="Lượng calories trên 100g")
    protein: float = Field(default=0, description="Lượng protein (g per 100g)")
    fat: float = Field(default=0, description="Lượng chất béo (g per 100g)")
    carbs: float = Field(default=0, description="Lượng carbohydrate (g per 100g)")
    fiber: float = Field(default=0, description="Lượng chất xơ (g per 100g)")
    sugar: float = Field(default=0, description="Lượng đường (g per 100g)")
    sodium: float = Field(default=0, description="Lượng sodium (mg per 100g)")
    image_url: Optional[str] = Field(default=None, description="URL hình ảnh minh họa")
    tags: List[str] = Field(default_factory=list, description="Các tag của món ăn")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Thời gian tạo")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "calories_per_100g": self.calories_per_100g,
            "protein": self.protein,
            "fat": self.fat,
            "carbs": self.carbs,
            "fiber": self.fiber,
            "sugar": self.sugar,
            "sodium": self.sodium,
            "image_url": self.image_url,
            "tags": self.tags,
            "created_at": self.created_at
        }
    
    def toJson(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FoodItem':
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", "other"),
            calories_per_100g=data.get("calories_per_100g", 0),
            protein=data.get("protein", 0),
            fat=data.get("fat", 0),
            carbs=data.get("carbs", 0),
            fiber=data.get("fiber", 0),
            sugar=data.get("sugar", 0),
            sodium=data.get("sodium", 0),
            image_url=data.get("image_url"),
            tags=data.get("tags", []),
            created_at=data.get("created_at", datetime.now().isoformat())
        )

class FoodIntake(BaseModel):
    """Model cho việc ghi nhận ăn một món ăn"""
    userId: str = Field(..., description="ID của người dùng")
    foodId: str = Field(..., description="ID của món ăn")
    food_name: str = Field(..., description="Tên món ăn")
    date: str = Field(default_factory=lambda: datetime.now().strftime('%Y-%m-%d'), description="Ngày ăn (YYYY-MM-DD)")
    meal_type: str = Field(..., description="Loại bữa ăn (breakfast, lunch, dinner, snack)")
    amount_g: float = Field(..., description="Lượng thức ăn (g)")
    calories: float = Field(..., description="Lượng calories")
    protein: float = Field(default=0, description="Lượng protein (g)")
    fat: float = Field(default=0, description="Lượng chất béo (g)")
    carbs: float = Field(default=0, description="Lượng carbohydrate (g)")
    notes: str = Field(default="", description="Ghi chú của người dùng")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Thời gian ghi nhận")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "userId": self.userId,
            "foodId": self.foodId,
            "food_name": self.food_name,
            "date": self.date,
            "meal_type": self.meal_type,
            "amount_g": self.amount_g,
            "calories": self.calories,
            "protein": self.protein,
            "fat": self.fat,
            "carbs": self.carbs,
            "notes": self.notes,
            "timestamp": self.timestamp
        }
    
    def toJson(self):
        return self.to_dict()

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FoodIntake':
        return cls(
            userId=data.get("userId", ""),
            foodId=data.get("foodId", ""),
            food_name=data.get("food_name", ""),
            date=data.get("date", datetime.now().strftime('%Y-%m-%d')),
            meal_type=data.get("meal_type", ""),
            amount_g=data.get("amount_g", 0),
            calories=data.get("calories", 0),
            protein=data.get("protein", 0),
            fat=data.get("fat", 0),
            carbs=data.get("carbs", 0),
            notes=data.get("notes", ""),
            timestamp=data.get("timestamp", datetime.now().isoformat())
        ) 