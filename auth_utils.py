from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import firebase_admin
from firebase_admin import auth
from models import TokenPayload
from datetime import datetime

# Security scheme
security = HTTPBearer()

# Hàm tiện ích để tự động tạo người dùng trong Firestore nếu chưa tồn tại
def ensure_user_in_firestore(user_id: str, user_info: TokenPayload = None) -> bool:
    """
    Kiểm tra và tự động tạo người dùng trong Firestore nếu chưa tồn tại
    
    Args:
        user_id: ID của người dùng
        user_info: Thông tin người dùng từ token (tùy chọn)
        
    Returns:
        bool: True nếu người dùng đã tồn tại hoặc được tạo thành công
    """
    try:
        # Import ở đây để tránh circular import
        from services.firestore_service import firestore_service
        
        # Kiểm tra xem người dùng đã tồn tại chưa
        existing_user = firestore_service.get_user(user_id)
        
        if existing_user:
            # Người dùng đã tồn tại, cập nhật thời gian đồng bộ
            firestore_service.update_user(user_id, {"lastSyncTime": datetime.now().isoformat()})
            return True
        
        # Người dùng chưa tồn tại, tạo mới
        from models.firestore_models import UserProfile
        
        # Lấy thông tin từ Firebase Auth nếu không có thông tin từ token
        if not user_info:
            try:
                user_record = auth.get_user(user_id)
                user_data = UserProfile(
                    name=user_record.display_name or "",
                    email=user_record.email or "",
                    lastSyncTime=datetime.now().isoformat()
                )
            except Exception as e:
                print(f"Không thể lấy thông tin người dùng từ Firebase Auth: {str(e)}")
                # Tạo với thông tin tối thiểu
                user_data = UserProfile(
                    name="",
                    email="",
                    lastSyncTime=datetime.now().isoformat()
                )
        else:
            # Sử dụng thông tin từ token
            user_data = UserProfile(
                name=user_info.name or "",
                email=user_info.email or "",
                lastSyncTime=datetime.now().isoformat()
            )
        
        # Lưu vào Firestore
        success = firestore_service.create_user(user_id, user_data)
        return success
    
    except Exception as e:
        print(f"Lỗi khi tạo người dùng trong Firestore: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Dependency để xác thực người dùng từ token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> TokenPayload:
    """
    Verify Firebase ID Token và trả về thông tin người dùng
    
    Args:
        credentials: HTTP Authorization header với Bearer token
        
    Returns:
        TokenPayload: Thông tin người dùng từ token
        
    Raises:
        HTTPException: Nếu token không hợp lệ hoặc hết hạn
    """
    token = credentials.credentials
    try:
        # Verify the token using Firebase Admin SDK
        decoded_token = auth.verify_id_token(token, check_revoked=False, clock_skew_seconds=60)
        
        # Tạo TokenPayload từ thông tin đã decode
        user_payload = TokenPayload(
            uid=decoded_token["uid"],
            email=decoded_token.get("email"),
            name=decoded_token.get("name"),
            email_verified=decoded_token.get("email_verified", False),
            picture=decoded_token.get("picture"),
            auth_time=decoded_token.get("auth_time"),
            exp=decoded_token.get("exp"),
            iat=decoded_token.get("iat"),
            role=decoded_token.get("role", "user")  # Mặc định là "user" nếu không có role
        )
        
        # Tự động đảm bảo người dùng tồn tại trong Firestore
        ensure_user_in_firestore(user_payload.uid, user_payload)
        
        return user_payload
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"}
        ) 