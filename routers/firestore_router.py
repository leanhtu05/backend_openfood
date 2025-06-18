from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import RedirectResponse
from datetime import datetime

from services.firestore_service import firestore_service
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
from models.flutter_user_profile import FlutterUserProfile, FlutterUserUpdate
from auth_utils import get_current_user
from models.token import TokenPayload

router = APIRouter(tags=["firestore"])

# ===== USER ROUTES =====

@router.get("/users")
async def get_all_users():
    """Lấy danh sách tất cả người dùng (cho admin)"""
    try:
        users = firestore_service.get_all_users()
        return {"users": users, "total": len(users)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

@router.post("/users/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_user(user_id: str, user_data: UserProfile):
    """Tạo người dùng mới"""
    try:
        print(f"Attempting to create user with ID: {user_id}")
        print(f"User data: {user_data.dict()}")
        
        # Đảm bảo các trường bắt buộc có giá trị
        if not user_data.name:
            user_data.name = "Default Name"
        if not user_data.email:
            user_data.email = f"{user_id}@example.com"
            
        # Chuyển đổi thành dict và loại bỏ các giá trị None
        user_dict = user_data.to_dict()
        
        # Thêm trường thời gian tạo
        from datetime import datetime
        user_dict["created_at"] = datetime.now().isoformat()
        
        # Gọi trực tiếp đến Firebase thay vì qua service
        from firebase_integration import firebase
        try:
            firebase.db.collection('users').document(user_id).set(user_dict)
            print(f"Successfully created user {user_id}")
            return {"message": "User created successfully", "user_id": user_id}
        except Exception as firebase_error:
            print(f"Firebase error: {str(firebase_error)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Firebase error: {str(firebase_error)}"
            )
    except Exception as e:
        print(f"Detailed error creating user {user_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error creating user: {str(e)}"
        )

@router.patch("/users/{user_id}")
async def update_user(
    user_id: str, 
    user_data: FlutterUserUpdate,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Cập nhật thông tin người dùng từ Flutter
    
    Args:
        user_id: ID của người dùng cần cập nhật
        user_data: Dữ liệu người dùng cần cập nhật
        current_user: Thông tin người dùng đã xác thực từ token
        
    Returns:
        Thông báo cập nhật thành công
    """
    # Kiểm tra token khớp với người dùng
    if user_id != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Không có quyền sửa thông tin người dùng khác"
        )
    
    try:
        print(f"[API] Cập nhật thông tin người dùng {user_id}")
        print(f"[API] Dữ liệu cập nhật: {user_data}")
        
        # Chuyển đổi dữ liệu từ model thành dict
        update_data = user_data.to_dict()
        
        # Thêm thời gian cập nhật
        update_data["updated_at"] = datetime.now().isoformat()
        
        # Cập nhật thông tin người dùng trong Firestore
        success = firestore_service.update_user(user_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Không thể cập nhật thông tin người dùng"
            )
            
        return {"message": "Cập nhật thông tin người dùng thành công"}
    except Exception as e:
        print(f"[API] Lỗi khi cập nhật thông tin người dùng: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi khi cập nhật thông tin người dùng: {str(e)}"
        )

@router.post("/api/firestore/users/sync", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_to_api_sync(
    data: Dict[str, Any],
    user_id: str = Query(None, description="ID của người dùng")
):
    """
    Chuyển hướng từ /api/firestore/users/sync sang /api/sync
    
    Endpoint này được giữ lại để tương thích với các phiên bản cũ của ứng dụng Flutter
    """
    redirect_url = f"/api/sync?user_id={user_id}" if user_id else "/api/sync"
    print(f"Chuyển hướng từ /api/firestore/users/sync sang {redirect_url}")
    return RedirectResponse(url=redirect_url)

@router.get("/users/{user_id}", response_model=UserProfile)
async def get_user(user_id: str):
    """Lấy thông tin người dùng"""
    user = firestore_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with ID {user_id} not found"
        )
    return user

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Xóa người dùng"""
    # Đảm bảo user tồn tại
    user = firestore_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with ID {user_id} not found"
        )
        
    success = firestore_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete user"
        )
    return {"message": "User deleted successfully"}

# ===== DAILY LOG ROUTES =====

@router.post("/users/{user_id}/daily-logs")
async def add_daily_log(user_id: str, daily_log: DailyLog):
    """Thêm log hàng ngày cho người dùng"""
    # Đảm bảo user tồn tại
    user = firestore_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with ID {user_id} not found"
        )
        
    success = firestore_service.add_daily_log(user_id, daily_log)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to add daily log"
        )
    return {"message": "Daily log added successfully"}

@router.get("/users/{user_id}/daily-logs/{date}", response_model=DailyLog)
async def get_daily_log(user_id: str, date: str):
    """Lấy log hàng ngày của người dùng"""
    # Đảm bảo user tồn tại
    user = firestore_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with ID {user_id} not found"
        )
        
    log = firestore_service.get_daily_log(user_id, date)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Daily log for user {user_id} on {date} not found"
        )
    return log

@router.get("/users/{user_id}/daily-logs", response_model=List[DailyLog])
async def get_daily_logs(user_id: str, limit: int = 7):
    """Lấy danh sách log hàng ngày của người dùng"""
    # Đảm bảo user tồn tại
    user = firestore_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with ID {user_id} not found"
        )
        
    logs = firestore_service.get_daily_logs(user_id, limit)
    return logs

@router.patch("/users/{user_id}/daily-logs/{date}")
async def update_daily_log(user_id: str, date: str, data: Dict[str, Any]):
    """Cập nhật log hàng ngày"""
    # Đảm bảo user tồn tại
    user = firestore_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with ID {user_id} not found"
        )
        
    # Đảm bảo log tồn tại
    log = firestore_service.get_daily_log(user_id, date)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Daily log for user {user_id} on {date} not found"
        )
        
    success = firestore_service.update_daily_log(user_id, date, data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to update daily log"
        )
    return {"message": "Daily log updated successfully"}

# ===== MEAL PLAN ROUTES =====

@router.get("/meal-plans")
async def get_all_meal_plans():
    """Lấy danh sách tất cả meal plans (cho admin)"""
    try:
        meal_plans = firestore_service.get_all_meal_plans()
        return {"meal_plans": meal_plans, "total": len(meal_plans)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching meal plans: {str(e)}"
        )

@router.get("/foods")
async def get_all_foods():
    """Lấy danh sách tất cả foods (cho admin)"""
    try:
        foods = firestore_service.get_all_foods()
        return {"foods": foods, "total": len(foods)}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching foods: {str(e)}"
        )

@router.post("/meal-plans", status_code=status.HTTP_201_CREATED)
async def create_meal_plan(meal_plan: MealPlan):
    """Tạo kế hoạch bữa ăn mới"""
    plan_id = firestore_service.create_meal_plan(meal_plan)
    if not plan_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to create meal plan"
        )
    return {"message": "Meal plan created successfully", "plan_id": plan_id}

@router.get("/meal-plans/{plan_id}", response_model=MealPlan)
async def get_meal_plan(plan_id: str):
    """Lấy kế hoạch bữa ăn theo ID"""
    plan = firestore_service.get_meal_plan(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Meal plan with ID {plan_id} not found"
        )
    return plan

@router.get("/users/{user_id}/meal-plans/date/{date}", response_model=List[MealPlan])
async def get_meal_plans_by_user_date(user_id: str, date: str):
    """Lấy các kế hoạch bữa ăn của người dùng theo ngày"""
    plans = firestore_service.get_meal_plans_by_user_date(user_id, date)
    return plans

@router.delete("/meal-plans/{plan_id}")
async def delete_meal_plan(plan_id: str):
    """Xóa kế hoạch bữa ăn"""
    # Đảm bảo plan tồn tại
    plan = firestore_service.get_meal_plan(plan_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Meal plan with ID {plan_id} not found"
        )
        
    success = firestore_service.delete_meal_plan(plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to delete meal plan"
        )
    return {"message": "Meal plan deleted successfully"}

@router.get("/meal-plans/user/{user_id}", response_model=List[Dict])
async def get_meal_plans_by_user(user_id: str):
    """Lấy tất cả kế hoạch bữa ăn của một người dùng cụ thể"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    try:
        # Sử dụng hàm trong firebase integration để truy vấn
        plans = firestore_service.get_meal_plan_history(user_id, limit=10)
        return plans
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching meal plans: {str(e)}"
        )

@router.get("/latest-meal-plan/{user_id}")
async def get_latest_meal_plan(user_id: str):
    """Lấy kế hoạch bữa ăn mới nhất của một người dùng"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    try:
        # Sử dụng hàm trong firebase integration để truy vấn
        meal_plan = firestore_service.get_latest_meal_plan(user_id)
        
        if meal_plan:
            # Trả về meal plan đầy đủ thay vì chỉ metadata
            return meal_plan
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No meal plan found for user {user_id}"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching latest meal plan: {str(e)}"
        )

# ===== AI SUGGESTION ROUTES =====

@router.post("/ai-suggestions", status_code=status.HTTP_201_CREATED)
async def save_ai_suggestion(suggestion: AISuggestion):
    """Lưu gợi ý từ AI"""
    suggestion_id = firestore_service.save_ai_suggestion(suggestion)
    if not suggestion_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to save AI suggestion"
        )
    return {"message": "AI suggestion saved successfully", "suggestion_id": suggestion_id}

@router.get("/users/{user_id}/ai-suggestions", response_model=List[AISuggestion])
async def get_ai_suggestions(user_id: str, limit: int = 10):
    """Lấy danh sách gợi ý của người dùng"""
    suggestions = firestore_service.get_ai_suggestions(user_id, limit)
    return suggestions 

# ===== USER SETTINGS AND PREFERENCES ROUTES =====

@router.patch("/users/{user_id}/settings")
async def update_user_settings(user_id: str, settings: Dict[str, Any]):
    """
    Cập nhật cài đặt người dùng
    
    Args:
        user_id: ID của người dùng
        settings: Cài đặt cần cập nhật
        
    Returns:
        Thông báo cập nhật thành công
    """
    # Đảm bảo user tồn tại
    user = firestore_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with ID {user_id} not found"
        )
        
    success = firestore_service.update_user_settings(user_id, settings)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to update user settings"
        )
    return {"message": "User settings updated successfully"}

@router.patch("/users/{user_id}/preferences")
async def update_user_preferences(user_id: str, preferences: Dict[str, Any]):
    """
    Cập nhật sở thích thực phẩm của người dùng
    
    Args:
        user_id: ID của người dùng
        preferences: Sở thích cần cập nhật
        
    Returns:
        Thông báo cập nhật thành công
    """
    # Đảm bảo user tồn tại
    user = firestore_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with ID {user_id} not found"
        )
        
    success = firestore_service.update_user_preferences(user_id, preferences)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to update user preferences"
        )
    return {"message": "User preferences updated successfully"}

@router.post("/users/{user_id}/convert-anonymous")
async def convert_anonymous_account(
    user_id: str, 
    email: str,
    display_name: Optional[str] = None
):
    """
    Chuyển đổi tài khoản ẩn danh thành tài khoản chính thức
    
    Args:
        user_id: ID của người dùng
        email: Email người dùng
        display_name: Tên hiển thị (tùy chọn)
        
    Returns:
        Thông báo chuyển đổi thành công
    """
    # Đảm bảo user tồn tại
    user = firestore_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"User with ID {user_id} not found"
        )
        
    success = firestore_service.convert_anonymous_account(user_id, email, display_name)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Failed to convert anonymous account"
        )
    return {"message": "Anonymous account converted successfully"}

# ===== EXERCISE ENDPOINTS =====

@router.post("/exercises", status_code=status.HTTP_201_CREATED)
async def create_exercise(exercise: Exercise):
    """Tạo mới bài tập"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    exercise_id = firestore_service.create_exercise(exercise)
    if not exercise_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create exercise"
        )
    
    return {"id": exercise_id, "message": "Exercise created successfully"}

@router.get("/exercises/{exercise_id}", response_model=Exercise)
async def get_exercise(exercise_id: str):
    """Lấy thông tin chi tiết bài tập"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    exercise = firestore_service.get_exercise(exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise {exercise_id} not found"
        )
    
    return exercise

@router.patch("/exercises/{exercise_id}")
async def update_exercise(exercise_id: str, exercise_data: Dict[str, Any]):
    """Cập nhật thông tin bài tập"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    success = firestore_service.update_exercise(exercise_id, exercise_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise {exercise_id} not found or update failed"
        )
    
    return {"message": "Exercise updated successfully"}

@router.delete("/exercises/{exercise_id}")
async def delete_exercise(exercise_id: str):
    """Xóa bài tập"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    success = firestore_service.delete_exercise(exercise_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exercise {exercise_id} not found or delete failed"
        )
    
    return {"message": "Exercise deleted successfully"}

@router.get("/users/{user_id}/exercises", response_model=List[Exercise])
async def get_user_exercises(user_id: str, limit: int = 50):
    """Lấy danh sách bài tập của người dùng"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    exercises = firestore_service.get_user_exercises(user_id, limit)
    return exercises

@router.post("/users/{user_id}/exercise-history", status_code=status.HTTP_201_CREATED)
async def add_exercise_history(user_id: str, exercise_history: ExerciseHistory):
    """Lưu lịch sử bài tập của người dùng"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    # Đảm bảo userId khớp với đường dẫn
    if exercise_history.userId != user_id:
        exercise_history.userId = user_id
    
    history_id = firestore_service.add_exercise_history(exercise_history)
    if not history_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add exercise history"
        )
    
    return {"id": history_id, "message": "Exercise history added successfully"}

@router.get("/users/{user_id}/exercise-history", response_model=List[ExerciseHistory])
async def get_exercise_history(
    user_id: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None, 
    limit: int = 50
):
    """Lấy lịch sử bài tập của người dùng"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    try:
        # Lấy dữ liệu từ firestore_service
        history_data = firestore_service.get_exercise_history(user_id, start_date, end_date, limit)
        
        # Kiểm tra và làm sạch dữ liệu
        for item in history_data:
            # Xóa trường original_data nếu có (không cần thiết cho response model)
            if 'original_data' in item:
                del item['original_data']
            
            # Đảm bảo các trường bắt buộc tồn tại
            if 'userId' not in item or not item['userId']:
                item['userId'] = user_id
            
            if 'exerciseId' not in item or not item['exerciseId']:
                # Tạo exerciseId từ id nếu có
                item['exerciseId'] = item.get('id', f"exercise_{int(datetime.now().timestamp()*1000)}")
            
            if 'exercise_name' not in item or not item['exercise_name']:
                item['exercise_name'] = item.get('name', 'Unknown exercise')
            
            if 'duration_minutes' not in item or not item['duration_minutes']:
                item['duration_minutes'] = item.get('minutes', 0)
        
        return history_data
    except Exception as e:
        print(f"Error processing exercise history: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing exercise history: {str(e)}"
        )

# ===== BEVERAGE ENDPOINTS =====

@router.post("/beverages", status_code=status.HTTP_201_CREATED)
async def create_beverage(beverage: Beverage):
    """Tạo mới loại nước uống"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    beverage_id = firestore_service.create_beverage(beverage)
    if not beverage_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create beverage"
        )
    
    return {"id": beverage_id, "message": "Beverage created successfully"}

@router.get("/beverages/{beverage_id}", response_model=Beverage)
async def get_beverage(beverage_id: str):
    """Lấy thông tin chi tiết nước uống"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    beverage = firestore_service.get_beverage(beverage_id)
    if not beverage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Beverage {beverage_id} not found"
        )
    
    return beverage

@router.patch("/beverages/{beverage_id}")
async def update_beverage(beverage_id: str, beverage_data: Dict[str, Any]):
    """Cập nhật thông tin nước uống"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    success = firestore_service.update_beverage(beverage_id, beverage_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Beverage {beverage_id} not found or update failed"
        )
    
    return {"message": "Beverage updated successfully"}

@router.delete("/beverages/{beverage_id}")
async def delete_beverage(beverage_id: str):
    """Xóa nước uống"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    success = firestore_service.delete_beverage(beverage_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Beverage {beverage_id} not found or delete failed"
        )
    
    return {"message": "Beverage deleted successfully"}

@router.post("/users/{user_id}/water-intake", status_code=status.HTTP_201_CREATED)
async def add_water_intake(user_id: str, water_intake: WaterIntake):
    """Ghi nhận lượng nước uống hàng ngày"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    # Đảm bảo userId khớp với đường dẫn
    if water_intake.userId != user_id:
        water_intake.userId = user_id
    
    intake_id = firestore_service.add_water_intake(water_intake)
    if not intake_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add water intake"
        )
    
    return {"id": intake_id, "message": "Water intake added successfully"}

@router.get("/users/{user_id}/water-intake/{date}", response_model=List[WaterIntake])
async def get_water_intake_by_date(user_id: str, date: str):
    """Lấy thông tin nước uống theo ngày"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    intakes = firestore_service.get_water_intake_by_date(user_id, date)
    return intakes

@router.get("/users/{user_id}/water-intake/history")
async def get_water_intake_history(
    user_id: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None, 
    limit: int = 30
):
    """Lấy lịch sử uống nước của người dùng"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    history = firestore_service.get_water_intake_history(user_id, start_date, end_date, limit)
    return history

# ===== FOOD ITEM ENDPOINTS =====

@router.post("/foods", status_code=status.HTTP_201_CREATED)
async def create_food(food: FoodItem):
    """Tạo mới món ăn"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    food_id = firestore_service.create_food(food)
    if not food_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create food"
        )
    
    return {"id": food_id, "message": "Food created successfully"}

@router.get("/foods/{food_id}", response_model=FoodItem)
async def get_food(food_id: str):
    """Lấy thông tin chi tiết món ăn"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    food = firestore_service.get_food(food_id)
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food {food_id} not found"
        )
    
    return food

@router.patch("/foods/{food_id}")
async def update_food(food_id: str, food_data: Dict[str, Any]):
    """Cập nhật thông tin món ăn"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    success = firestore_service.update_food(food_id, food_data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food {food_id} not found or update failed"
        )
    
    return {"message": "Food updated successfully"}

@router.delete("/foods/{food_id}")
async def delete_food(food_id: str):
    """Xóa món ăn"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    success = firestore_service.delete_food(food_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food {food_id} not found or delete failed"
        )
    
    return {"message": "Food deleted successfully"}

@router.get("/users/{user_id}/favorite-foods", response_model=List[FoodItem])
async def get_favorite_foods(user_id: str, limit: int = 50):
    """Lấy danh sách món ăn yêu thích"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    foods = firestore_service.get_favorite_foods(user_id, limit)
    return foods

@router.post("/users/{user_id}/favorite-foods")
async def add_favorite_food(user_id: str, food_id: str):
    """Thêm món ăn vào danh sách yêu thích"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    success = firestore_service.add_favorite_food(user_id, food_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add favorite food"
        )
    
    return {"message": "Food added to favorites successfully"}

@router.delete("/users/{user_id}/favorite-foods/{food_id}")
async def remove_favorite_food(user_id: str, food_id: str):
    """Xóa món ăn khỏi danh sách yêu thích"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    success = firestore_service.remove_favorite_food(user_id, food_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Food {food_id} not found in favorites or remove failed"
        )
    
    return {"message": "Food removed from favorites successfully"}

@router.post("/users/{user_id}/food-intake", status_code=status.HTTP_201_CREATED)
async def add_food_intake(user_id: str, food_intake: FoodIntake):
    """Ghi nhận việc ăn một món ăn"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    # Đảm bảo userId khớp với đường dẫn
    if food_intake.userId != user_id:
        food_intake.userId = user_id
    
    intake_id = firestore_service.add_food_intake(food_intake)
    if not intake_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add food intake"
        )
    
    return {"id": intake_id, "message": "Food intake added successfully"}

@router.get("/users/{user_id}/food-intake/{date}", response_model=List[FoodIntake])
async def get_food_intake_by_date(user_id: str, date: str):
    """Lấy thông tin thức ăn theo ngày"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    intakes = firestore_service.get_food_intake_by_date(user_id, date)
    return intakes

@router.get("/users/{user_id}/food-intake/history", response_model=List[FoodIntake])
async def get_food_intake_history(
    user_id: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None, 
    limit: int = 50
):
    """Lấy lịch sử ăn uống của người dùng"""
    if not firestore_service.initialized:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Firestore service is not initialized"
        )
    
    history = firestore_service.get_food_intake_history(user_id, start_date, end_date, limit)
    return history 

@router.post("/users/flutter-structure", status_code=201)
async def create_flutter_user(user: FlutterUserProfile):
    try:
        from firebase_integration import firebase
        # Sử dụng phương thức to_dict đã được thêm vào
        user_dict = user.to_dict()
        user_id = user.uid or user.email or "flutter_user"  # Ưu tiên uid, nếu không có thì email
        
        print(f"Creating Flutter user with ID: {user_id}")
        print(f"User data: {user_dict}")
        
        # Thêm trường thời gian tạo nếu chưa có
        if "createdAt" not in user_dict:
            from datetime import datetime
            user_dict["createdAt"] = datetime.now().isoformat()
            
        # Thêm trường name từ displayName nếu có
        if user.displayName and "name" not in user_dict:
            user_dict["name"] = user.displayName
            
        # Ánh xạ các trường từ Flutter sang định dạng backend
        if user.heightCm:
            user_dict["height"] = user.heightCm
        if user.weightKg:
            user_dict["weight"] = user.weightKg
            
        # Lưu dữ liệu vào Firestore
        firebase.db.collection('users').document(user_id).set(user_dict)
        return {"message": "User created from Flutter structure", "user_id": user_id}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e)) 

# Thêm endpoint chuyển hướng cho food-entries
@router.get("/api/firestore/food-entries/{user_id}/date/{date}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_food_entries(
    user_id: str,
    date: str
):
    """
    Chuyển hướng từ /api/firestore/food-entries/{user_id}/date/{date} sang /firestore/users/{user_id}/food-intake/history
    """
    redirect_url = f"/firestore/users/{user_id}/food-intake/history?start_date={date}&end_date={date}"
    print(f"Chuyển hướng từ /api/firestore/food-entries sang {redirect_url}")
    return RedirectResponse(url=redirect_url)

# Thêm endpoint chuyển hướng cho water-entries
@router.get("/api/firestore/water-entries/{user_id}/date/{date}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_water_entries(
    user_id: str,
    date: str
):
    """
    Chuyển hướng từ /api/firestore/water-entries/{user_id}/date/{date} sang /firestore/users/{user_id}/water-intake/{date}
    """
    redirect_url = f"/firestore/users/{user_id}/water-intake/{date}"
    print(f"Chuyển hướng từ /api/firestore/water-entries sang {redirect_url}")
    return RedirectResponse(url=redirect_url)

# Thêm endpoint chuyển hướng cho exercises
@router.get("/api/firestore/exercises/{user_id}/date/{date}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_exercises(
    user_id: str,
    date: str
):
    """
    Chuyển hướng từ /api/firestore/exercises/{user_id}/date/{date} sang /firestore/users/{user_id}/exercise-history
    """
    redirect_url = f"/firestore/users/{user_id}/exercise-history?start_date={date}&end_date={date}"
    print(f"Chuyển hướng từ /api/firestore/exercises sang {redirect_url}")
    return RedirectResponse(url=redirect_url)

# Thêm endpoint chuyển hướng cho api/water-log
@router.get("/api/water-log/{user_id}/date/{date}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_water_log(
    user_id: str,
    date: str
):
    """
    Chuyển hướng từ /api/water-log/{user_id}/date/{date} sang /firestore/users/{user_id}/water-intake/{date}
    """
    redirect_url = f"/firestore/users/{user_id}/water-intake/{date}"
    print(f"Chuyển hướng từ /api/water-log sang {redirect_url}")
    return RedirectResponse(url=redirect_url)

# Thêm endpoint chuyển hướng cho api/food-log
@router.get("/api/food-log/{user_id}/{date}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_food_log(
    user_id: str,
    date: str
):
    """
    Chuyển hướng từ /api/food-log/{user_id}/{date} sang /firestore/users/{user_id}/food-intake/history
    """
    redirect_url = f"/firestore/users/{user_id}/food-intake/history?start_date={date}&end_date={date}"
    print(f"Chuyển hướng từ /api/food-log sang {redirect_url}")
    return RedirectResponse(url=redirect_url)

# Thêm endpoint chuyển hướng cho api/exercise
@router.get("/api/exercise/{user_id}/date/{date}", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect_exercise_log(
    user_id: str,
    date: str
):
    """
    Chuyển hướng từ /api/exercise/{user_id}/date/{date} sang /firestore/users/{user_id}/exercise-history
    """
    redirect_url = f"/firestore/users/{user_id}/exercise-history?start_date={date}&end_date={date}"
    print(f"Chuyển hướng từ /api/exercise sang {redirect_url}")
    return RedirectResponse(url=redirect_url) 