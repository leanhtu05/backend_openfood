from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from typing import Dict, Optional, List, Any
from pydantic import BaseModel
import logging
import services
from auth_utils import get_current_user, TokenPayload

# Thiết lập logger
logger = logging.getLogger(__name__)

# Tạo router
router = APIRouter(prefix="/api/meal-plan", tags=["Meal Plan"])

# Model cho request tạo kế hoạch ăn
class MealPlanRequest(BaseModel):
    user_id: str
    calories_target: float = 1500.0  # Giảm mặc định xuống 1500 kcal
    protein_target: float = 90.0     # Điều chỉnh protein
    fat_target: float = 50.0         # Điều chỉnh fat
    carbs_target: float = 187.5      # Điều chỉnh carbs
    preferences: Optional[str] = None
    allergies: Optional[str] = None
    cuisine_style: Optional[str] = None
    use_ai: bool = True
    ensure_diversity: bool = False  # Tham số mới để đảm bảo đa dạng món ăn
    use_tdee: bool = True           # Tham số mới để sử dụng TDEE

# Endpoint tạo kế hoạch ăn mới
@router.post("/generate")
async def generate_meal_plan_endpoint(
    request: MealPlanRequest,
    user: TokenPayload = Depends(get_current_user)
):
    """
    Tạo kế hoạch ăn uống hàng tuần mới cho người dùng.
    
    Args:
        request: Thông tin yêu cầu tạo kế hoạch ăn
        user: Thông tin người dùng đã xác thực
        
    Returns:
        Dict: Kết quả tạo kế hoạch ăn
    """
    try:
        # Kiểm tra quyền truy cập
        if request.user_id != user.uid:
            # Cho phép admin tạo kế hoạch cho người dùng khác
            if not user.is_admin:
                raise HTTPException(
                    status_code=403,
                    detail="Không có quyền tạo kế hoạch ăn cho người dùng khác"
                )
        
        # Gọi service để tạo kế hoạch ăn uống
        meal_plan = services.generate_meal_plan(
            user_id=request.user_id,
            calories_target=request.calories_target,
            protein_target=request.protein_target,
            fat_target=request.fat_target,
            carbs_target=request.carbs_target,
            preferences=request.preferences,
            allergies=request.allergies,
            cuisine_style=request.cuisine_style,
            use_ai=request.use_ai,
            ensure_diversity=request.ensure_diversity,  # Truyền tham số mới
            use_tdee=request.use_tdee                   # Truyền tham số mới
        )
        
        return {
            "status": "success",
            "message": "Đã tạo kế hoạch ăn uống thành công",
            "data": meal_plan
        }
    except Exception as e:
        logger.error(f"Error generating meal plan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Không thể tạo kế hoạch ăn uống: {str(e)}"
        )

# Endpoint lấy kế hoạch ăn hiện tại
@router.get("/{user_id}")
async def get_meal_plan_endpoint(
    user_id: str = Path(..., description="ID của người dùng"),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Lấy kế hoạch ăn uống hiện tại của người dùng.
    
    Args:
        user_id: ID của người dùng
        user: Thông tin người dùng đã xác thực
        
    Returns:
        Dict: Kế hoạch ăn uống hiện tại
    """
    try:
        # Kiểm tra quyền truy cập
        if user_id != user.uid and not user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Không có quyền xem kế hoạch ăn của người dùng khác"
            )
        
        # Gọi service để lấy kế hoạch ăn uống
        meal_plan = services.get_meal_plan(user_id)
        
        if not meal_plan:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy kế hoạch ăn uống cho người dùng này"
            )
        
        return {
            "status": "success",
            "data": meal_plan
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting meal plan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Không thể lấy kế hoạch ăn uống: {str(e)}"
        )

# Endpoint thay thế một bữa ăn cụ thể
@router.post("/replace-meal")
async def replace_meal_endpoint(
    request: Dict[str, Any] = Body(...),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Thay thế một bữa ăn cụ thể trong kế hoạch ăn uống.
    
    Args:
        request: Thông tin yêu cầu thay thế bữa ăn
        user: Thông tin người dùng đã xác thực
        
    Returns:
        Dict: Kết quả thay thế bữa ăn
    """
    try:
        user_id = request.get("user_id")
        
        # Kiểm tra quyền truy cập
        if user_id != user.uid and not user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Không có quyền thay đổi kế hoạch ăn của người dùng khác"
            )
        
        # Xác định loại bữa ăn cần thay đổi
        meal_type = request.get("meal_type", "").lower()
        
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
            "tối": "dinner"
        }
        
        # Nếu meal_type là tiếng Việt, chuyển đổi sang tiếng Anh
        if meal_type in meal_type_mapping:
            meal_type = meal_type_mapping[meal_type]
            
        # Reset used_dishes_tracker để tránh trùng lặp khi thay thế món ăn
        from services import used_dishes_tracker
        # Chỉ reset loại bữa ăn cần thay thế
        if meal_type in ["breakfast", "lunch", "dinner"]:
            used_dishes_tracker[meal_type] = set()
        
        # Điều chỉnh calories nếu quá cao
        if request.get("calories_target", 0) > 1500:
            request["calories_target"] = 1500
        
        # Gọi service để thay thế bữa ăn
        result = services.replace_meal(request)
        
        return {
            "status": "success",
            "message": "Đã thay thế bữa ăn thành công",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error replacing meal: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Không thể thay thế bữa ăn: {str(e)}"
        ) 