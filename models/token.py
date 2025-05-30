from pydantic import BaseModel
from typing import Optional

class TokenPayload(BaseModel):
    """
    Mô hình dữ liệu chứa thông tin xác thực từ Firebase JWT token
    """
    uid: str
    email: Optional[str] = None
    name: Optional[str] = None
    email_verified: Optional[bool] = False
    picture: Optional[str] = None
    auth_time: Optional[int] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    role: Optional[str] = None 