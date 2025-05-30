"""
Compatibility router to handle requests from the Flutter app in both formats.
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Body, status, Security
from typing import Dict, Optional, List, Any

from models import (
    NutritionTarget, 
    ReplaceDayRequest, 
    WeeklyMealPlan, 
    DayMealPlan,
    TokenPayload, 
    ReplaceDayResponse
)
import services
from auth_utils import get_current_user
from storage_manager import storage_manager
from models.flutter_user_profile import FlutterUserProfile
from firebase_admin import auth, firestore
from datetime import datetime

# Create compatibility router (no prefix to match original paths)
router = APIRouter(tags=["Compatibility"])

# LƯU Ý: Endpoint /replace-day đã bị loại bỏ
# Vui lòng sử dụng /api/replace-day thay thế
# Điều này giúp cải thiện tính nhất quán của API và tránh trùng lặp

# Endpoint để xử lý đồng bộ dữ liệu từ Flutter
@router.post("/sync")
async def sync_flutter_data(
    data: Dict[str, Any],
    user_id: str = Query("default", description="ID của người dùng")
):
    """
    Đồng bộ dữ liệu từ ứng dụng Flutter lên Firebase
    
    LƯU Ý: Endpoint này sẽ bị loại bỏ trong tương lai.
    Vui lòng sử dụng /api/sync thay thế.
    
    Parameters:
    - data: Dữ liệu từ Flutter (bao gồm user, meals, exercises, water_logs)
    - user_id: ID của người dùng (query parameter)
    
    Returns:
    - Kết quả đồng bộ
    """
    try:
        print(f"Received sync request for user: {user_id}")
        print(f"CẢNH BÁO: Endpoint /sync đã lỗi thời. Vui lòng sử dụng /api/sync trong tương lai.")
        
        # Kiểm tra xem user_id có hợp lệ không
        if user_id == "default" or not user_id:
            # Thử lấy user_id từ dữ liệu người dùng
            if "user" in data and isinstance(data["user"], dict) and "uid" in data["user"]:
                user_id = data["user"]["uid"]
                print(f"Using user ID from data: {user_id}")
            else:
                return {"error": "Không tìm thấy user_id hợp lệ"}
        
        results = {
            "user_sync": False,
            "meals_sync": False,
            "exercises_sync": False,
            "water_logs_sync": False
        }
        
        # Đồng bộ dữ liệu người dùng
        if "user" in data and isinstance(data["user"], dict):
            try:
                # Lấy Firestore client
                db = firestore.client()
                
                # Chuẩn bị dữ liệu người dùng
                user_data = data["user"]
                user_data["lastSyncTime"] = datetime.now().isoformat()
                
                # Kiểm tra xem người dùng đã tồn tại chưa
                user_doc = db.collection("users").document(user_id).get()
                
                if user_doc.exists:
                    # Cập nhật dữ liệu người dùng hiện có
                    db.collection("users").document(user_id).update(user_data)
                    print(f"Updated existing user: {user_id}")
                else:
                    # Tạo người dùng mới
                    user_data["createdAt"] = datetime.now().isoformat()
                    db.collection("users").document(user_id).set(user_data)
                    print(f"Created new user: {user_id}")
                
                results["user_sync"] = True
            except Exception as e:
                print(f"Error syncing user data: {str(e)}")
                results["user_sync_error"] = str(e)
        
        # TODO: Implement sync for meals, exercises, and water_logs
        
        return {
            "message": "Đồng bộ dữ liệu thành công",
            "user_id": user_id,
            "results": results
        }
    except Exception as e:
        print(f"Error in sync_flutter_data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi đồng bộ dữ liệu: {str(e)}"
        )

# Các endpoint tương thích khác sẽ được thêm vào đây trong tương lai