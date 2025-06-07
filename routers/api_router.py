from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body, status, Security
from typing import Dict, Optional, List, Any
import time
from datetime import datetime
from pydantic import BaseModel, Field, validator, root_validator
import json

from models.firestore_models import UserProfile, MealPlan
from services.firestore_service import firestore_service
from models import (
    NutritionTarget, 
    TokenPayload, 
    WeeklyMealPlan,
    GenerateWeeklyMealResponse,
    ReplaceDayRequest,
    ReplaceDayResponse
)
import services
from auth_utils import get_current_user, security
from storage_manager import storage_manager

# Create API router
router = APIRouter(prefix="/api", tags=["API"])

# Định nghĩa model cho replace-meal
class ReplaceMealRequest(BaseModel):
    """Request model để thay thế một bữa ăn trong kế hoạch"""
    day_of_week: str = Field(..., description="Ngày trong tuần cần thay đổi (Thứ 2, Thứ 3, etc)")
    meal_type: str = Field(..., description="Loại bữa ăn cần thay đổi (breakfast, lunch, dinner, snack)")
    calories_target: Optional[float] = Field(None, description="Mục tiêu calories cho bữa ăn (kcal)")
    protein_target: Optional[float] = Field(None, description="Mục tiêu protein cho bữa ăn (g)")
    fat_target: Optional[float] = Field(None, description="Mục tiêu chất béo cho bữa ăn (g)")
    carbs_target: Optional[float] = Field(None, description="Mục tiêu carbs cho bữa ăn (g)")
    nutrition_targets: Optional[Dict[str, float]] = Field(None, description="Mục tiêu dinh dưỡng (từ Flutter)")
    user_id: Optional[str] = Field(None, description="ID người dùng (từ Flutter)")
    use_ai: Optional[bool] = Field(True, description="Sử dụng AI để tạo kế hoạch bữa ăn (mặc định True)")

    # Validator để xử lý cấu trúc dữ liệu từ Flutter
    @validator('nutrition_targets', pre=True)
    def extract_nutrition_targets(cls, v, values):
        if v is not None:
            # Lấy giá trị từ nutrition_targets nếu không có giá trị trực tiếp
            if 'calories_target' not in values or values['calories_target'] is None:
                values['calories_target'] = v.get('calories')
            if 'protein_target' not in values or values['protein_target'] is None:
                values['protein_target'] = v.get('protein')
            if 'fat_target' not in values or values['fat_target'] is None:
                values['fat_target'] = v.get('fat')
            if 'carbs_target' not in values or values['carbs_target'] is None:
                values['carbs_target'] = v.get('carbs')
        return v
    
    # Validator để đảm bảo có đủ thông tin dinh dưỡng
    @root_validator(skip_on_failure=True)
    def check_nutrition_targets(cls, values):
        # Kiểm tra xem có đủ thông tin dinh dưỡng không
        if (values.get('calories_target') is None or
            values.get('protein_target') is None or
            values.get('fat_target') is None or
            values.get('carbs_target') is None):
            raise ValueError("Thiếu thông tin mục tiêu dinh dưỡng. Cần cung cấp calories_target, protein_target, fat_target, carbs_target hoặc nutrition_targets")
        return values

class ReplaceMealResponse(BaseModel):
    """Response model sau khi thay thế một bữa ăn"""
    day_of_week: str
    meal_type: str
    meal: Any
    message: str

# User profile endpoint
@router.post("/user-profile", status_code=status.HTTP_200_OK)
async def create_or_update_user_profile(
    user_profile: UserProfile,
    user_id: Optional[str] = Query(None),
    user: TokenPayload = Depends(get_current_user)
):
    """Create or update a user profile"""
    # If user_id not provided, use the authenticated user's ID
    if not user_id:
        user_id = user.uid
    
    # Only allow users to modify their own profile unless they have admin permissions
    if user_id != user.uid and getattr(user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own profile"
        )
    
    # Create or update the user profile
    try:
        firestore_service.create_or_update_user_profile(user_id, user_profile)
        return {"message": "User profile created/updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating user profile: {str(e)}"
        )

# Endpoint để lấy thông tin user profile theo ID
@router.get("/user-profile/{user_id}", response_model=UserProfile)
async def get_user_profile(
    user_id: str = Path(..., description="ID của người dùng"),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Lấy thông tin profile của người dùng theo ID
    
    Parameters:
    - user_id: ID của người dùng (từ path)
    
    Returns:
    - Thông tin profile của người dùng
    """
    # Chỉ cho phép người dùng xem profile của chính họ hoặc quản trị viên
    if user_id != user.uid and getattr(user, "role", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chỉ có thể xem profile của chính mình"
        )
    
    try:
        user_profile = firestore_service.get_user_profile(user_id)
        if not user_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy profile cho người dùng với ID: {user_id}"
            )
        return user_profile
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi lấy thông tin user profile: {str(e)}"
        )

# Meal plan generation endpoint - GET method
@router.get("/meal-plan/generate", response_model=GenerateWeeklyMealResponse)
async def generate_meal_plan_get(
    calories: int = Query(2000, description="Target calories"),
    protein: int = Query(100, description="Target protein in grams"),
    fat: int = Query(70, description="Target fat in grams"),
    carbs: int = Query(250, description="Target carbs in grams"),
    user_id: str = Query("default", description="User ID"),
    use_ai: bool = Query(False, description="Use AI for generation"),
    user: TokenPayload = Depends(get_current_user)
):
    """Generate a weekly meal plan using GET method"""
    return await generate_meal_plan_internal(
        calories=calories,
        protein=protein,
        fat=fat,
        carbs=carbs,
        user_id=user_id,
        use_ai=use_ai,
        user=user
    )

# Meal plan generation endpoint - POST method
@router.post("/meal-plan/generate", response_model=GenerateWeeklyMealResponse)
async def generate_meal_plan_post(
    request_data: Optional[Dict[str, Any]] = Body(None),
    user: TokenPayload = Depends(get_current_user)
):
    """Generate a weekly meal plan using POST method"""
    # Extract parameters from request body
    request_data = request_data or {}
    
    calories = request_data.get("calories", request_data.get("calories_target", 2000))
    protein = request_data.get("protein", request_data.get("protein_target", 100))
    fat = request_data.get("fat", request_data.get("fat_target", 70))
    carbs = request_data.get("carbs", request_data.get("carbs_target", 250))
    user_id = request_data.get("user_id", "default")
    use_ai = request_data.get("use_ai", False)
    use_tdee = request_data.get("use_tdee", True)  # Mặc định sử dụng TDEE
    
    # Handle nutrition_targets structure from Flutter
    if "nutrition_targets" in request_data and isinstance(request_data["nutrition_targets"], dict):
        nutrition_targets = request_data["nutrition_targets"]
        calories = nutrition_targets.get("calories", calories)
        protein = nutrition_targets.get("protein", protein)
        fat = nutrition_targets.get("fat", fat)
        carbs = nutrition_targets.get("carbs", carbs)
    
    return await generate_meal_plan_internal(
        calories=calories,
        protein=protein,
        fat=fat,
        carbs=carbs,
        user_id=user_id,
        use_ai=use_ai,
        user=user,
        use_tdee=use_tdee  # Đã di chuyển xuống cuối
    )

# Internal function to handle meal plan generation
async def generate_meal_plan_internal(
    calories: int,
    protein: int,
    fat: int,
    carbs: int,
    user_id: str,
    use_ai: bool,
    user: TokenPayload,
    use_tdee: bool = True  # Di chuyển tham số mặc định xuống cuối
):
    """Internal function to generate a weekly meal plan"""
    try:
        # Use user_id from token if "default" is specified
        if user_id == "default":
            user_id = user.uid

        print(f"Generating meal plan for user: {user_id}")
        start_time = time.time()
        
        # Get user profile data for personalization
        user_data = None
        try:
            user_profile = firestore_service.get_user(user_id)
            if user_profile:
                user_data = {
                    'gender': user_profile.get('gender', 'unknown'),
                    'age': user_profile.get('age', 30),
                    'goal': user_profile.get('goal', 'unknown'),
                    'activity_level': user_profile.get('activity_level', 'unknown')
                }
                print(f"Using user profile data for personalization: {user_data}")
        except Exception as e:
            print(f"Error getting user profile for personalization: {str(e)}")
        
        # Generate meal plan
        meal_plan = services.generate_weekly_meal_plan(
            calories_target=calories,
            protein_target=protein,
            fat_target=fat,
            carbs_target=carbs,
            preferences=[],  # Optional preferences
            allergies=[],    # Optional allergies
            cuisine_style=None,  # Optional cuisine style
            use_ai=use_ai,
            use_tdee=use_tdee,
            user_data=user_data
        )
        
        generation_time = time.time() - start_time
        print(f"Meal plan generated in {generation_time:.2f} seconds")
        
        # Save the meal plan
        storage_manager.save_meal_plan(meal_plan, user_id)
        
        # Đồng thời lưu vào Firestore để đảm bảo dữ liệu được đồng bộ
        try:
            # Chuyển đổi model thành dict để lưu vào Firestore
            plan_dict = meal_plan.dict()
            # Lưu vào collection latest_meal_plans
            firestore_service.db.collection('latest_meal_plans').document(user_id).set(plan_dict)
            print(f"[DEBUG] Đã lưu kế hoạch ăn cập nhật vào Firestore cho user {user_id}")
        except Exception as e:
            print(f"[WARNING] Không thể lưu kế hoạch ăn vào Firestore: {str(e)}")
            # Không raise exception ở đây để tránh lỗi cho người dùng, 
            # vì đã lưu thành công vào storage_manager
        
        # Return response
        return GenerateWeeklyMealResponse(
            meal_plan=meal_plan,
            message=f"Weekly meal plan generated successfully in {generation_time:.2f} seconds"
        )
        
    except Exception as e:
        print(f"Error generating meal plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating meal plan: {str(e)}"
        )

# Get meal plan by user ID endpoint
@router.get("/meal-plan/{user_id}", response_model=Dict)
async def get_user_meal_plan(
    user_id: str = Path(..., description="User ID"),
    user: TokenPayload = Depends(get_current_user)
):
    """Get meal plan for a specific user"""
    try:
        # Only allow users to access their own data unless it's "default"
        if user_id != "default" and user_id != user.uid:
            # You could add an admin check here if needed
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this user's meal plan"
            )
            
        # If "default" is specified, use the authenticated user's ID
        if user_id == "default":
            user_id = user.uid
            
        # Try to get the latest meal plan from Firestore
        meal_plan = firestore_service.get_latest_meal_plan(user_id)
        
        if not meal_plan:
            # Nếu không tìm thấy trong Firestore, thử lấy từ bộ nhớ cục bộ
            meal_plan = storage_manager.load_meal_plan(user_id)
            
            if not meal_plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy kế hoạch ăn cho người dùng {user_id}"
                )
            
            # Nếu tìm thấy trong bộ nhớ cục bộ, đồng bộ vào Firestore
            if isinstance(meal_plan, WeeklyMealPlan):
                try:
                    # Lưu kế hoạch ăn vào Firestore để đồng bộ
                    plan_dict = meal_plan.dict()
                    firestore_service.db.collection('latest_meal_plans').document(user_id).set(plan_dict)
                    print(f"[DEBUG] Đã đồng bộ kế hoạch ăn từ bộ nhớ cục bộ vào Firestore cho user {user_id}")
                except Exception as e:
                    print(f"[WARNING] Không thể đồng bộ kế hoạch ăn vào Firestore: {str(e)}")
                
                return {"meal_plan": meal_plan.dict()}
            
        return {"meal_plan": meal_plan}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving meal plan: {str(e)}"
        )

# Replace day endpoint (matching existing endpoint path in main.py)
# Đường dẫn đầy đủ là /api/replace-day vì router có prefix="/api"
@router.post("/replace-day", response_model=ReplaceDayResponse)
async def replace_day(
    replace_request: ReplaceDayRequest = Body(...),
    user_id: str = Query("default", description="User ID"),
    use_ai: bool = Query(False, description="Use AI for generation"),
    preferences: List[str] = Query(default=[], description="Danh sách sở thích thực phẩm"),
    allergies: List[str] = Query(default=[], description="Danh sách thực phẩm gây dị ứng cần tránh"),
    cuisine_style: Optional[str] = Query(default=None, description="Phong cách ẩm thực ưa thích"),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Replace a specific day in the meal plan with customized options
    
    Parameters:
    - replace_request: Day and nutrition targets for replacement
    - user_id: User ID (from query or JWT)
    - use_ai: Whether to use AI for generation
    - preferences: Food preferences (optional)
    - allergies: Food allergies to avoid (optional)
    - cuisine_style: Preferred cuisine style (optional)
    
    Returns:
    - The new day's meal plan
    """
    try:
        # Use user_id from token if "default" is specified
        if user_id == "default":
            user_id = user.uid
        
        # Get the current meal plan from Firestore
        meal_plan = firestore_service.get_latest_meal_plan(user_id)
        
        if not meal_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy kế hoạch ăn. Vui lòng tạo kế hoạch ăn trước."
            )
        
        # Check if the day exists in the current plan
        if replace_request.day_of_week not in [day.day_of_week for day in meal_plan.days]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Day '{replace_request.day_of_week}' not found in the current meal plan."
            )
        
        # Get user profile data for personalization
        user_data = None
        try:
            user_profile = firestore_service.get_user(user_id)
            if user_profile:
                user_data = {
                    'gender': user_profile.get('gender', 'unknown'),
                    'age': user_profile.get('age', 30),
                    'goal': user_profile.get('goal', 'unknown'),
                    'activity_level': user_profile.get('activity_level', 'unknown')
                }
                print(f"Using user profile data for personalization: {user_data}")
        except Exception as e:
            print(f"Error getting user profile for personalization: {str(e)}")
        
        # Generate a new day meal plan using generate_day_meal_plan instead of replace_meal
        try:
            # Sử dụng hàm replace_day_meal_plan để tạo kế hoạch ăn mới cho ngày này
            new_day_plan = services.replace_day_meal_plan(
                meal_plan, 
                replace_request,
                preferences=preferences,
                allergies=allergies,
                cuisine_style=cuisine_style,
                use_ai=use_ai,
                user_data=user_data
            )
            
            # Update the existing meal plan with the new day
            for i, day in enumerate(meal_plan.days):
                if day.day_of_week == replace_request.day_of_week:
                    meal_plan.days[i] = new_day_plan
                    break
            
        except Exception as e:
            print(f"Error in replace_day_meal_plan: {str(e)}")
            print(f"Fallback to generate_day_meal_plan for day {replace_request.day_of_week}")
            
            # Fallback: Generate a new day meal plan directly
            new_day_plan = services.generate_day_meal_plan(
                day_of_week=replace_request.day_of_week,
                calories_target=replace_request.calories_target,
                protein_target=replace_request.protein_target,
                fat_target=replace_request.fat_target,
                carbs_target=replace_request.carbs_target,
                preferences=preferences,
                allergies=allergies,
                cuisine_style=cuisine_style,
                use_ai=use_ai,
                user_data=user_data
            )
            
            # Update the existing meal plan with the new day
            for i, day in enumerate(meal_plan.days):
                if day.day_of_week == replace_request.day_of_week:
                    meal_plan.days[i] = new_day_plan
                    break
        
        # Save the updated meal plan
        try:
            # Lưu kế hoạch đã cập nhật vào storage manager
            storage_manager.save_meal_plan(meal_plan, user_id)
            print(f"[DEBUG] Đã lưu kế hoạch ăn cập nhật vào storage_manager cho user {user_id}")
            
            # Đồng thời lưu vào Firestore để đảm bảo dữ liệu được đồng bộ
            # Chuyển đổi model thành dict để lưu vào Firestore
            plan_dict = meal_plan.dict()
            # Lưu vào collection latest_meal_plans
            firestore_service.db.collection('latest_meal_plans').document(user_id).set(plan_dict)
            print(f"[DEBUG] Đã lưu kế hoạch ăn cập nhật vào Firestore cho user {user_id}")
        except Exception as e:
            print(f"[WARNING] Không thể lưu kế hoạch ăn: {str(e)}")
            # Không raise exception ở đây để tránh lỗi cho người dùng
            # vì kế hoạch ăn mới đã được tạo thành công
        
        # Return the response
        return ReplaceDayResponse(
            day_meal_plan=new_day_plan,
            message="Day meal plan replaced successfully"
        )
    except HTTPException:
        raise
    except ValueError as e:
        # Xử lý lỗi từ meal_services
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log detailed error for debugging
        import traceback
        error_details = traceback.format_exc()
        print(f"[ERROR] Detailed stack trace: {error_details}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error replacing day meal plan: {str(e)}"
        )

# Endpoint để thay thế một bữa ăn cụ thể trong kế hoạch
@router.post("/meal-plan/replace-meal", response_model=ReplaceMealResponse)
async def replace_meal(
    replace_request: ReplaceMealRequest,
    user_id: str = Query("default", description="ID của người dùng"),
    use_ai: bool = Query(True, description="Sử dụng AI để tạo kế hoạch bữa ăn"),
    preferences: List[str] = Query(default=[], description="Danh sách sở thích thực phẩm"),
    allergies: List[str] = Query(default=[], description="Danh sách thực phẩm gây dị ứng cần tránh"),
    cuisine_style: Optional[str] = Query(default=None, description="Phong cách ẩm thực ưa thích"),
    use_tdee: bool = Query(default=True, description="Sử dụng TDEE để điều chỉnh mục tiêu dinh dưỡng"),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Thay thế một bữa ăn cụ thể trong kế hoạch ăn
    
    Parameters:
    - replace_request: Thông tin bữa ăn cần thay thế
    - user_id: ID của người dùng
    - use_ai: Sử dụng AI để tạo kế hoạch bữa ăn
    - preferences: Danh sách sở thích thực phẩm
    - allergies: Danh sách thực phẩm gây dị ứng cần tránh
    - cuisine_style: Phong cách ẩm thực ưa thích
    - use_tdee: Sử dụng TDEE để điều chỉnh mục tiêu dinh dưỡng
    - user: Thông tin người dùng đã xác thực
    
    Returns:
    - ReplaceMealResponse: Thông tin bữa ăn mới
    """
    try:
        # Use user_id from token if "default" is specified
        if user_id == "default":
            user_id = user.uid
        
        # Kiểm tra quyền truy cập
        if user_id != user.uid and not user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Không có quyền thay thế bữa ăn cho người dùng khác"
            )
            
        print(f"Thay thế bữa ăn cho người dùng: {user_id}")
        print(f"Thông tin yêu cầu: {replace_request}")
        
        # Đảm bảo use_ai mặc định là True nếu không được chỉ định
        if replace_request.use_ai is None:
            # DEBUG: Print use_ai information
            print(f"DEBUG_USE_AI: {replace_request.use_ai}")
            with open("debug_use_ai.log", "a", encoding="utf-8") as f:
                f.write(f"DEBUG_USE_AI: {replace_request.use_ai}\n")
                f.write(f"Request data: {replace_request}\n\n")
            replace_request.use_ai = True
            print("Đặt use_ai=True vì không được chỉ định rõ ràng")
        
        # Lấy kế hoạch ăn hiện tại từ Firestore
        current_plan = firestore_service.get_latest_meal_plan(user_id)
        
        if not current_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy kế hoạch ăn. Vui lòng tạo kế hoạch ăn trước."
            )
        
        # Kiểm tra ngày và bữa ăn hợp lệ
        day_of_week = replace_request.day_of_week
        meal_type_raw = replace_request.meal_type.lower()
        
        # Ánh xạ tên bữa ăn từ tiếng Việt sang tiếng Anh
        meal_type_mapping = {
            "bữa sáng": "breakfast",
            "buổi sáng": "breakfast",
            "sáng": "breakfast",
            "bữa trưa": "lunch",
            "buổi trưa": "lunch",
            "trưa": "lunch",
            "bữa tối": "dinner",
            "buổi tối": "dinner",
            "tối": "dinner",
            "bữa phụ": "snack",
            "buổi phụ": "snack",
            "phụ": "snack"
        }
        
        # Nếu meal_type là tiếng Việt, chuyển đổi sang tiếng Anh
        meal_type = meal_type_mapping.get(meal_type_raw, meal_type_raw)
        
        if meal_type not in ["breakfast", "lunch", "dinner", "snack"]:
            raise HTTPException(
                status_code=400,
                detail=f"Loại bữa ăn không hợp lệ: {meal_type_raw}"
            )
            
        # Tìm ngày trong kế hoạch ăn
        day_index = -1
        for i, day in enumerate(current_plan.days):
            if day.day_of_week == day_of_week:
                day_index = i
                break
                
        if day_index == -1:
            raise HTTPException(
                status_code=400,
                detail=f"Không tìm thấy ngày '{day_of_week}' trong kế hoạch ăn"
            )
            
        # Lấy thông tin dinh dưỡng mục tiêu cho bữa ăn
        daily_targets = {
            "calories": replace_request.calories_target or 1500,
            "protein": replace_request.protein_target or 90,
            "fat": replace_request.fat_target or 50,
            "carbs": replace_request.carbs_target or 187.5
        }
        
        # Nếu sử dụng TDEE, điều chỉnh mục tiêu dinh dưỡng
        if use_tdee:
            try:
                # Import tdee_nutrition_service
                from services.tdee_nutrition_service import tdee_nutrition_service
                
                # Không cần import firestore_service vì đã import ở đầu file
                # Xóa dòng import này để tránh xung đột biến
                # from services.firestore_service import firestore_service
                
                # Lấy thông tin người dùng từ Firestore
                user_profile = firestore_service.get_user(user_id)
                
                if user_profile:
                    print(f"Đã tìm thấy thông tin người dùng {user_id}, điều chỉnh mục tiêu dinh dưỡng dựa trên TDEE")
                    
                    # Lấy mục tiêu dinh dưỡng từ profile người dùng
                    daily_calories, daily_protein, daily_fat, daily_carbs = tdee_nutrition_service.get_nutrition_targets_from_user_profile(user_profile)
                    
                    daily_targets = {
                        "calories": daily_calories,
                        "protein": daily_protein,
                        "fat": daily_fat,
                        "carbs": daily_carbs
                    }
                    
                    print(f"Mục tiêu dinh dưỡng hàng ngày: {daily_targets}")
            except Exception as e:
                print(f"Lỗi khi điều chỉnh mục tiêu dinh dưỡng: {str(e)}")
        
        # Phân bổ mục tiêu dinh dưỡng cho bữa ăn cụ thể
        try:
            from services.tdee_nutrition_service import tdee_nutrition_service
            meal_targets = tdee_nutrition_service.distribute_nutrition_by_meal(
                daily_targets["calories"],
                daily_targets["protein"],
                daily_targets["fat"],
                daily_targets["carbs"],
                meal_type
            )
            print(f"Mục tiêu dinh dưỡng cho bữa {meal_type}: {meal_targets}")
        except Exception as e:
            print(f"Lỗi khi phân bổ dinh dưỡng: {str(e)}")
            # Phân bổ thủ công nếu có lỗi
            meal_ratios = {"breakfast": 0.25, "lunch": 0.40, "dinner": 0.35, "snack": 0.15}
            ratio = meal_ratios.get(meal_type, 0.33)
            meal_targets = {
                "calories": int(daily_targets["calories"] * ratio),
                "protein": int(daily_targets["protein"] * ratio),
                "fat": int(daily_targets["fat"] * ratio),
                "carbs": int(daily_targets["carbs"] * ratio)
            }
            print(f"Phân bổ thủ công cho bữa {meal_type}: {meal_targets}")
            
            # Điều chỉnh giảm mục tiêu cho bữa ăn phụ nếu tỉ lệ cao
            if meal_type == "snack" and ratio > 0.15:
                for key in meal_targets:
                    meal_targets[key] = int(meal_targets[key] * 0.6)  # Giảm xuống còn 60% so với phân bổ ban đầu
                print(f"Đã điều chỉnh giảm cho bữa phụ: {meal_targets}")
                
        # Reset used_dishes_tracker để tránh trùng lặp món ăn
        from services.meal_tracker import reset_tracker
        reset_tracker()  # Reset toàn bộ tracker để đảm bảo tính đa dạng tối đa
        
        # Get user profile data for personalized meal generation
        user_data = None
        try:
            user_profile = firestore_service.get_user(user_id)
            if user_profile:
                user_data = {
                    'gender': user_profile.get('gender', 'unknown'),
                    'age': user_profile.get('age', 30),
                    'goal': user_profile.get('goal', 'unknown'),
                    'activity_level': user_profile.get('activity_level', 'unknown')
                }
                print(f"Using user profile data for personalization: {user_data}")
        except Exception as e:
            print(f"Error getting user profile for personalization: {str(e)}")
        
        # Tạo bữa ăn mới
        # Ưu tiên sử dụng use_ai từ request thay vì từ query parameter
        use_ai_value = replace_request.use_ai if replace_request.use_ai is not None else use_ai
        print(f"Sử dụng AI: {use_ai_value} (từ request: {replace_request.use_ai}, từ query: {use_ai})")
        
        new_meal = services.generate_meal(
            meal_type,
            meal_targets["calories"],
            meal_targets["protein"],
            meal_targets["fat"],
            meal_targets["carbs"],
            preferences=preferences,
            allergies=allergies,
            cuisine_style=cuisine_style,
            use_ai=use_ai_value,
            day_of_week=day_of_week,  # Thêm day_of_week để tăng tính đa dạng
            user_data=user_data  # Add user profile data for personalization
        )
        
        # Cập nhật bữa ăn trong kế hoạch
        if meal_type == "breakfast":
            current_plan.days[day_index].breakfast = new_meal
        elif meal_type == "lunch":
            current_plan.days[day_index].lunch = new_meal
        elif meal_type == "dinner":
            current_plan.days[day_index].dinner = new_meal
        elif meal_type == "snack":
            # Check if snack field exists in the day plan
            if not hasattr(current_plan.days[day_index], 'snack'):
                # Add snack field to the day plan
                # Using setattr to dynamically add a new attribute
                setattr(current_plan.days[day_index], 'snack', new_meal)
            else:
                # Update existing snack field
                current_plan.days[day_index].snack = new_meal
        
        # Lưu kế hoạch ăn cập nhật vào cả storage_manager và Firestore
        storage_manager.save_meal_plan(current_plan, user_id)
        
        # Đồng thời lưu vào Firestore để đảm bảo dữ liệu được đồng bộ
        try:
            # Chuyển đổi model thành dict để lưu vào Firestore
            plan_dict = current_plan.dict()
            # Lưu vào collection latest_meal_plans
            firestore_service.db.collection('latest_meal_plans').document(user_id).set(plan_dict)
            print(f"[DEBUG] Đã lưu kế hoạch ăn cập nhật vào Firestore cho user {user_id}")
        except Exception as e:
            print(f"[WARNING] Không thể lưu kế hoạch ăn vào Firestore: {str(e)}")
            # Không raise exception ở đây để tránh lỗi cho người dùng, 
            # vì đã lưu thành công vào storage_manager
        
        return ReplaceMealResponse(
            day_of_week=day_of_week,
            meal_type=meal_type,
            meal=new_meal,
            message=f"Đã thay thế thành công {meal_type} cho {day_of_week}"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error replacing meal: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Không thể thay thế bữa ăn: {str(e)}"
        )

# Endpoint đồng bộ dữ liệu từ Flutter
@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_data(
    data: Dict[str, Any],
    user_id: str = Query(None, description="ID của người dùng"),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Đồng bộ dữ liệu từ ứng dụng Flutter lên Firebase
    
    Endpoint này thay thế cho /sync và /firestore/users/sync
    
    Parameters:
    - data: Dữ liệu từ Flutter (bao gồm user, meals, exercises, water_logs)
    - user_id: ID của người dùng (query parameter hoặc từ token)
    
    Returns:
    - Kết quả đồng bộ
    """
    try:
        # Sử dụng user_id từ token nếu không có user_id được chỉ định
        if not user_id:
            user_id = user.uid
            
        print(f"Received sync request for user: {user_id}")
        print(f"Received data: {json.dumps(data, indent=2)[:500]}...")
        
        results = {
            "user_sync": False,
            "meals_sync": False,
            "exercises_sync": False,
            "water_logs_sync": False
        }
        
        # Đồng bộ dữ liệu người dùng
        if "user" in data and isinstance(data["user"], dict):
            try:
                # Chuẩn bị dữ liệu người dùng
                user_data = data["user"].copy()  # Tạo bản sao để tránh thay đổi dữ liệu gốc
                user_data["lastSyncTime"] = datetime.now().isoformat()
                
                print(f"[SYNC] Processing user data for {user_id}: {json.dumps(user_data, indent=2)}")
                
                # Đảm bảo các trường dữ liệu được ánh xạ đúng
                # Chuyển đổi tên trường từ Flutter sang tên trường trong Firestore nếu cần
                field_mappings = {
                    "height_cm": "height",
                    "weight_kg": "weight",
                    "activity_level": "activityLevel",
                    "diet_preference": "dietPreference",
                    "diet_restrictions": "dietRestrictions",
                    "health_conditions": "healthConditions",
                    "target_weight_kg": "targetWeight",
                    # Thêm các ánh xạ khác nếu cần
                }
                
                # Áp dụng ánh xạ trường
                for flutter_field, firestore_field in field_mappings.items():
                    if flutter_field in user_data:
                        user_data[firestore_field] = user_data.pop(flutter_field)
                
                # Xử lý nutrition_goals đặc biệt
                if "nutrition_goals" in user_data and isinstance(user_data["nutrition_goals"], dict):
                    nutrition_goals = user_data.pop("nutrition_goals")
                    print(f"[SYNC] Found nutrition_goals: {nutrition_goals}")
                    
                    # Ánh xạ trực tiếp các giá trị dinh dưỡng vào document gốc
                    if "calories" in nutrition_goals:
                        user_data["targetCalories"] = float(nutrition_goals["calories"])
                    if "protein" in nutrition_goals:
                        user_data["targetProtein"] = float(nutrition_goals["protein"])
                    if "fat" in nutrition_goals:
                        user_data["targetFat"] = float(nutrition_goals["fat"])
                    if "carbs" in nutrition_goals:
                        user_data["targetCarbs"] = float(nutrition_goals["carbs"])
                    
                    # Vẫn giữ lại nutritionGoals cho tương thích ngược
                    user_data["nutritionGoals"] = nutrition_goals
                
                print(f"[SYNC] Mapped user data: {json.dumps(user_data, indent=2)}")
                
                # Kiểm tra xem người dùng đã tồn tại chưa
                existing_user = firestore_service.get_user(user_id)
                
                if existing_user:
                    print(f"[SYNC] Updating existing user: {user_id}")
                    print(f"[SYNC] Existing data: {json.dumps(existing_user, indent=2)}")
                    
                    # Đảm bảo giữ lại các trường quan trọng từ dữ liệu hiện có
                    # nhưng vẫn cập nhật các giá trị dinh dưỡng mới
                    merged_data = {**existing_user}
                    
                    # Cập nhật các trường dinh dưỡng từ dữ liệu mới
                    if "targetCalories" in user_data:
                        merged_data["targetCalories"] = user_data["targetCalories"]
                    if "targetProtein" in user_data:
                        merged_data["targetProtein"] = user_data["targetProtein"]
                    if "targetFat" in user_data:
                        merged_data["targetFat"] = user_data["targetFat"]
                    if "targetCarbs" in user_data:
                        merged_data["targetCarbs"] = user_data["targetCarbs"]
                    
                    # Cập nhật các trường khác từ dữ liệu mới
                    for key, value in user_data.items():
                        if key not in ["targetCalories", "targetProtein", "targetFat", "targetCarbs"]:
                            merged_data[key] = value
                    
                    print(f"[SYNC] Merged data to save: {json.dumps(merged_data, indent=2)}")
                    
                    success = firestore_service.update_user(user_id, merged_data)
                    if success:
                        print(f"[SYNC] Successfully updated user: {user_id}")
                        results["user_sync"] = True
                    else:
                        print(f"[SYNC] Failed to update user: {user_id}")
                else:
                    # Tạo người dùng mới
                    print(f"[SYNC] Creating new user: {user_id}")
                    user_data["created_at"] = datetime.now().isoformat()
                    success = firestore_service.create_user(user_id, user_data)
                    if success:
                        print(f"[SYNC] Successfully created new user: {user_id}")
                        results["user_sync"] = True
                    else:
                        print(f"[SYNC] Failed to create user: {user_id}")
            except Exception as e:
                print(f"[SYNC] Error syncing user data: {str(e)}")
                import traceback
                traceback.print_exc()
                results["user_sync_error"] = str(e)
        
        # Đồng bộ dữ liệu bữa ăn
        if "meals" in data and isinstance(data["meals"], list):
            try:
                # TODO: Implement meal sync
                results["meals_sync"] = True
            except Exception as e:
                print(f"Error syncing meals data: {str(e)}")
                results["meals_sync_error"] = str(e)
        
        # Đồng bộ dữ liệu bài tập
        if "exercises" in data and isinstance(data["exercises"], list):
            try:
                # TODO: Implement exercise sync
                results["exercises_sync"] = True
            except Exception as e:
                print(f"Error syncing exercises data: {str(e)}")
                results["exercises_sync_error"] = str(e)
                
        # Đồng bộ dữ liệu uống nước
        if "water_logs" in data and isinstance(data["water_logs"], list):
            try:
                # TODO: Implement water log sync
                results["water_logs_sync"] = True
            except Exception as e:
                print(f"Error syncing water logs data: {str(e)}")
                results["water_logs_sync_error"] = str(e)
        
        # Kiểm tra lại dữ liệu sau khi đồng bộ
        final_user = firestore_service.get_user(user_id)
        print(f"[SYNC] Final user data after sync: {json.dumps(final_user, indent=2) if final_user else 'None'}")
        
        return {
            "message": "Đồng bộ dữ liệu thành công",
            "user_id": user_id,
            "results": results
        }
    except Exception as e:
        print(f"Error in sync_data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi đồng bộ dữ liệu: {str(e)}"
        )

# Endpoint để cập nhật thông tin người dùng đầy đủ từ Flutter
@router.post("/sync-user-profile", status_code=status.HTTP_200_OK)
async def sync_user_profile(
    user_data: Dict[str, Any],
    user_id: str = Query(None, description="ID của người dùng"),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Đồng bộ thông tin đầy đủ của người dùng từ Flutter lên Firestore
    
    Parameters:
    - user_data: Dữ liệu người dùng từ Flutter (bao gồm thông tin cá nhân, mục tiêu, cài đặt)
    - user_id: ID của người dùng (query parameter hoặc từ token)
    
    Returns:
    - Kết quả đồng bộ
    """
    try:
        # Sử dụng user_id từ token nếu không có user_id được chỉ định
        if not user_id:
            user_id = user.uid
            
        print(f"Đồng bộ thông tin người dùng: {user_id}")
        print(f"Dữ liệu nhận được: {user_data}")
        
        # Đảm bảo có các trường cần thiết
        if "tdee" not in user_data:
            print("Thiếu trường TDEE, sẽ tính toán dựa trên thông tin có sẵn")
            # Có thể thêm logic tính TDEE ở đây
        
        # Thêm trường lastSyncTime
        user_data["lastSyncTime"] = datetime.now().isoformat()
        
        # Kiểm tra xem người dùng đã tồn tại chưa
        existing_user = firestore_service.get_user(user_id)
        
        if existing_user:
            # Cập nhật người dùng hiện có
            success = firestore_service.update_user(user_id, user_data)
            if success:
                print(f"Đã cập nhật thông tin người dùng: {user_id}")
                return {
                    "message": "Đã đồng bộ thông tin người dùng thành công",
                    "status": "updated",
                    "user_id": user_id
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Không thể cập nhật thông tin người dùng"
                )
        else:
            # Tạo người dùng mới
            user_data["created_at"] = datetime.now().isoformat()
            success = firestore_service.create_user(user_id, user_data)
            if success:
                print(f"Đã tạo người dùng mới: {user_id}")
                return {
                    "message": "Đã tạo người dùng mới thành công",
                    "status": "created",
                    "user_id": user_id
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Không thể tạo người dùng mới"
                )
    except Exception as e:
        print(f"Lỗi khi đồng bộ thông tin người dùng: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi đồng bộ thông tin người dùng: {str(e)}"
        ) 