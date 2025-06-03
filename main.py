from fastapi import FastAPI, HTTPException, Depends, Query, Body, Path, Header, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional, List, Any
import time
import os
import json
from datetime import datetime

"""
LƯU Ý VỀ CÁC ENDPOINT ĐÃ LOẠI BỎ:

Các endpoint sau đã được loại bỏ do trùng lặp chức năng:
1. /generate-weekly-meal -> thay thế bằng /api/meal-plan/generate
2. /generate-weekly-meal-demo -> thay thế bằng /api/meal-plan/generate
3. /replace-week -> thay thế bằng /api/replace-day
4. /sync -> thay thế bằng /api/sync
5. /firestore/users/sync -> thay thế bằng /api/sync

Việc loại bỏ các endpoint trùng lặp giúp API dễ bảo trì hơn và tránh nhầm lẫn cho người dùng.
"""

from models import (
    NutritionTarget, ReplaceDayRequest, WeeklyMealPlan, DayMealPlan,
    GenerateWeeklyMealRequest, GenerateWeeklyMealResponse, ReplaceDayResponse, ReplaceWeekResponse,
    TokenPayload, AuthRequest, UserResponse, AuthResponse
)
import services
from storage_manager import storage_manager
from auth_utils import get_current_user, security, ensure_user_in_firestore

# Import generate_random_data
from generate_random_data import generate_weekly_plan

# Import USDA API integration
from usda_integration import usda_api

# Import routers
from routers import firestore_router, api_router, compat_router, meal_plan_router

# Thêm import cho chat API
from pydantic import BaseModel
from openai import OpenAI

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK
# Đảm bảo các import cần thiết đã có ở đầu file:
# import firebase_admin
# from firebase_admin import credentials
# import os
# import json
# from config import config # Đảm bảo config được import

try:
    firebase_app = firebase_admin.get_app()
    print("Firebase Admin SDK đã được khởi tạo trước đó.")
except ValueError:  # Nghĩa là chưa có app nào được khởi tạo
    print("Đang khởi tạo Firebase Admin SDK...")
    cred = None
    initialized_method = ""

    # 1. Ưu tiên biến môi trường FIREBASE_SERVICE_ACCOUNT_JSON
    firebase_service_account_json_str = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
    if firebase_service_account_json_str:
        try:
            service_account_info = json.loads(firebase_service_account_json_str)
            cred = credentials.Certificate(service_account_info)
            initialized_method = "FIREBASE_SERVICE_ACCOUNT_JSON environment variable"
        except Exception as e:
            print(f"Lỗi khi parse FIREBASE_SERVICE_ACCOUNT_JSON: {e}")

    # 2. Nếu không có biến môi trường, thử tải từ FIREBASE_CREDENTIALS_PATH trong config
    if cred is None and hasattr(config, 'FIREBASE_CREDENTIALS_PATH') and config.FIREBASE_CREDENTIALS_PATH and os.path.exists(config.FIREBASE_CREDENTIALS_PATH):
        try:
            cred = credentials.Certificate(config.FIREBASE_CREDENTIALS_PATH)
            initialized_method = f"file: {config.FIREBASE_CREDENTIALS_PATH}"
        except Exception as e:
            print(f"Lỗi khi tải credentials từ {config.FIREBASE_CREDENTIALS_PATH}: {e}")
    
    # 3. Nếu vẫn không có, thử các đường dẫn mặc định (giữ lại logic cũ của bạn một phần)
    if cred is None:
        default_paths = [
            "firebase-credentials.json",
            "firebase-service-account.json",
            os.path.join(os.path.dirname(__file__), "firebase-credentials.json"),
        ]
        for path in default_paths:
            if os.path.exists(path):
                try:
                    cred = credentials.Certificate(path)
                    initialized_method = f"default file path: {path}"
                    break
                except Exception as e:
                    print(f"Lỗi khi tải credentials từ {path}: {e}")

    # 4. Cuối cùng, nếu không có file nào, thử Application Default Credentials
    if cred is None:
        try:
            cred = credentials.ApplicationDefault()
            initialized_method = "Application Default Credentials"
        except Exception as e:
            print(f"Không thể lấy Application Default Credentials: {e}")
            # raise ValueError("Không thể khởi tạo Firebase: Không tìm thấy credentials hợp lệ.") # Bỏ comment nếu muốn dừng hẳn

    if cred:
        try:
            firebase_admin.initialize_app(cred, {
                'projectId': config.FIREBASE_PROJECT_ID, 
                'storageBucket': config.FIREBASE_STORAGE_BUCKET
            })
            print(f"Firebase Admin SDK initialized successfully using {initialized_method}.")
            print(f"Project ID: {firebase_admin.get_app().project_id}, Storage Bucket: {config.FIREBASE_STORAGE_BUCKET}")
        except Exception as e:
            print(f"Lỗi khi gọi firebase_admin.initialize_app: {e}")
            # raise e # Bỏ comment nếu muốn dừng hẳn
    else:
        print("Không thể khởi tạo Firebase Admin SDK: Không tìm thấy credentials hợp lệ.")
        # raise ValueError("Không thể khởi tạo Firebase: Không tìm thấy credentials hợp lệ.") # Bỏ comment nếu muốn dừng hẳn

# Create FastAPI app
app = FastAPI(
    title="DietAI API",
    description="API for generating and managing personalized nutrition plans",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "X-Requested-With"],
    expose_headers=["Content-Length", "Content-Range", "Content-Disposition"],
)

# Middleware để ghi log các request
@app.middleware("http")
async def log_requests(request, call_next):
    path = request.url.path
    method = request.method
    
    # Log chi tiết cho endpoint /sync
    if path == "/sync" or path.endswith("/sync"):
        print(f"\n===== REQUEST {method} {path} =====")
        print(f"Query params: {request.query_params}")
        try:
            body = await request.body()
            if body:
                print(f"Request body length: {len(body)} bytes")
                if len(body) < 1000:  # Chỉ in nếu body không quá dài
                    try:
                        body_json = json.loads(body)
                        print(f"Request body (JSON): {json.dumps(body_json, indent=2)[:500]}...")
                    except:
                        print(f"Request body: {body[:200]}...")
        except Exception as e:
            print(f"Error reading request body: {str(e)}")
    
    response = await call_next(request)
    
    # Log chi tiết cho endpoint /sync
    if path == "/sync" or path.endswith("/sync"):
        print(f"===== RESPONSE {response.status_code} =====\n")
    
    return response

# Khởi tạo Groq client cho chat API
groq_api_key = os.environ.get("GROQ_API_KEY", "")
try:
    chat_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    chat_available = bool(groq_api_key)
except:
    chat_client = None
    chat_available = False

# Chat API models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "anonymous"

class ChatResponse(BaseModel):
    reply: str
    chat_id: str = ""

# Thêm các router vào ứng dụng
app.include_router(firestore_router)
app.include_router(api_router)
app.include_router(compat_router)
app.include_router(meal_plan_router)

# Đã chuyển hàm get_current_user sang file auth_utils.py

# Dependency to get the current meal plan from storage
async def get_current_meal_plan(
    user_id: str = "default",
    user: Optional[TokenPayload] = Depends(get_current_user)
) -> Optional[WeeklyMealPlan]:
    """
    Đọc kế hoạch thực đơn hiện tại từ bộ nhớ (Firebase hoặc file)
    
    Args:
        user_id: ID của người dùng
        user: Thông tin người dùng đã xác thực
        
    Returns:
        Đối tượng WeeklyMealPlan hiện tại hoặc None
    """
    # Nếu user_id không phải "default" và khác với uid trong token,
    # chỉ cho phép nếu là dữ liệu public hoặc người dùng là admin
    if user_id != "default" and user_id != user.uid:
        # Kiểm tra quyền admin hoặc dữ liệu public ở đây nếu cần
        pass
    
    return storage_manager.load_meal_plan(user_id)

# Thiết lập router cho xác thực
from fastapi import APIRouter

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

@auth_router.post("/login", response_model=AuthResponse)
async def login(auth_request: AuthRequest):
    """
    Đăng nhập bằng Firebase ID Token
    
    Args:
        auth_request: Yêu cầu đăng nhập với Firebase ID Token
        
    Returns:
        AuthResponse: Thông tin người dùng đã xác thực
    """
    try:
        # Verify token
        decoded_token = auth.verify_id_token(auth_request.id_token, check_revoked=False, clock_skew_seconds=60)
        
        # Lấy thông tin người dùng từ Firebase
        user_record = auth.get_user(decoded_token["uid"])
        
        # Đảm bảo người dùng tồn tại trong Firestore
        user_id = user_record.uid
        ensure_user_in_firestore(user_id)
        
        # Tạo phản hồi
        user_response = UserResponse(
            uid=user_record.uid,
            email=user_record.email,
            display_name=user_record.display_name,
            photo_url=user_record.photo_url,
            email_verified=user_record.email_verified,
            created_at=datetime.fromtimestamp(user_record.user_metadata.creation_timestamp / 1000).isoformat() if user_record.user_metadata.creation_timestamp else None,
            last_login=datetime.fromtimestamp(user_record.user_metadata.last_sign_in_timestamp / 1000).isoformat() if user_record.user_metadata.last_sign_in_timestamp else None,
            is_anonymous=user_record.provider_id == "anonymous"
        )
        
        return AuthResponse(user=user_response)
    except Exception as e:
        print(f"Lỗi đăng nhập: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=401, detail=f"Đăng nhập thất bại: {str(e)}")

# Thêm router auth vào app
app.include_router(auth_router)

@app.get("/")
async def root():
    """Root endpoint to check if API is running"""
    return {"message": "Welcome to DietAI API. Visit /docs for API documentation."}

# Endpoint /replace-day đã được xử lý trong api_router và compat_router

@app.get("/meal-plan-history", response_model=List[Dict])
async def get_meal_plan_history(
    user_id: str = Query("default", description="ID của người dùng"),
    limit: int = Query(10, description="Số lượng kế hoạch tối đa"),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Lấy lịch sử kế hoạch thực đơn của người dùng
    
    Parameters:
    - user_id: ID của người dùng (query parameter)
    - limit: Số lượng kế hoạch tối đa trả về (query parameter)
    
    Returns:
    - Danh sách các kế hoạch thực đơn trước đây
    """
    # Sử dụng user_id từ token nếu không có user_id được chỉ định
    if user_id == "default":
        user_id = user.uid
        
    try:
        history = storage_manager.get_meal_plan_history(user_id, limit)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting meal plan history: {str(e)}")

@app.delete("/meal-plan/{filename}")
async def delete_meal_plan(
    filename: str,
    user: TokenPayload = Depends(get_current_user)
):
    """
    Xóa một kế hoạch thực đơn
    
    Parameters:
    - filename: Tên file hoặc ID document cần xóa
    
    Returns:
    - Thông báo kết quả
    """
    # Kiểm tra quyền xóa (có thể thêm logic để chỉ cho phép xóa file của người dùng hiện tại)
    
    if storage_manager.delete_meal_plan(filename):
        return {"message": f"Deleted meal plan: {filename}"}
    else:
        raise HTTPException(status_code=404, detail=f"Meal plan not found: {filename}")

@app.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user: TokenPayload = Depends(get_current_user)
):
    """
    Lấy thông tin người dùng hiện tại
    
    Returns:
        UserResponse: Thông tin người dùng hiện tại
    """
    try:
        # Lấy thông tin chi tiết từ Firebase
        user_record = auth.get_user(user.uid)
        
        # Tạo UserResponse
        return UserResponse(
            uid=user_record.uid,
            email=user_record.email,
            display_name=user_record.display_name,
            photo_url=user_record.photo_url,
            email_verified=user_record.email_verified,
            created_at=datetime.fromtimestamp(user_record.user_metadata.creation_timestamp / 1000).isoformat() if user_record.user_metadata.creation_timestamp else None,
            last_login=datetime.fromtimestamp(user_record.user_metadata.last_sign_in_timestamp / 1000).isoformat() if user_record.user_metadata.last_sign_in_timestamp else None,
            is_anonymous=user_record.provider_id == "anonymous"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user info: {str(e)}")

# Endpoint kiểm tra token
@app.get("/validate-token")
async def validate_token(
    user: TokenPayload = Depends(get_current_user)
):
    """
    Kiểm tra tính hợp lệ của token
    
    Returns:
        Dict: Kết quả kiểm tra token
    """
    return {
        "valid": True,
        "uid": user.uid,
        "email": user.email
    }

@app.get("/check-ai-availability")
async def check_ai_availability():
    """
    Kiểm tra xem tính năng AI có khả dụng không
    
    Returns:
    - Thông tin về tính khả dụng của AI
    """
    try:
        # Kiểm tra Groq LLaMA 3
        try:
            from groq_integration_direct import groq_service  # Fixed version
            if groq_service.available:
                return {
                    "ai_available": True,
                    "ai_type": "LLaMA 3 (Groq)",
                    "model": getattr(groq_service, "model", "unknown"),
                    "message": "LLaMA 3 via Groq API is available and ready to use"
                }
        except ImportError:
            pass
            
        # Không có AI nào khả dụng
        return {
            "ai_available": False,
            "message": "No AI service is available. Install Groq client and set API key to enable AI features."
        }
    except Exception as e:
        return {
            "ai_available": False,
            "message": f"Error checking AI availability: {str(e)}"
        }

@app.get("/cache-info")
async def get_cache_info():
    """
    Hiển thị thông tin về cache và rate limiting của Groq
    
    Returns:
    - Thông tin về cache và rate limiting
    """
    try:
        from groq_integration_direct import groq_service  # Fixed version
        cache_info = groq_service.get_cache_info()
        
        rate_limiter_info = {
            "requests_per_minute": groq_service.rate_limiter.requests_per_minute,
            "requests_per_day": groq_service.rate_limiter.requests_per_day,
            "minute_requests_used": groq_service.rate_limiter.minute_requests,
            "day_requests_used": groq_service.rate_limiter.day_requests,
            "minute_reset_in_seconds": max(0, int(groq_service.rate_limiter.minute_reset_time - time.time())),
            "day_reset_in_seconds": max(0, int(groq_service.rate_limiter.day_reset_time - time.time()))
        }
        
        return {
            "cache": cache_info,
            "rate_limiter": rate_limiter_info,
            "ai_available": groq_service.available
        }
    except Exception as e:
        return {
            "error": f"Error getting cache info: {str(e)}"
        }

@app.get("/api-status")
async def get_api_status():
    """
    Kiểm tra trạng thái API, bao gồm thông tin quota của AI và rate limit
    
    Returns:
    - Thông tin trạng thái API, quota và rate limit
    """
    try:
        import time
        import datetime
        
        # Kiểm tra Groq LLaMA 3
        try:
            from groq_integration_direct import groq_service  # Fixed version
            if groq_service.available:
                current_time = time.time()
                quota_status = {
                    "exceeded": groq_service.quota_exceeded,
                    "reset_time": None,
                    "remaining_seconds": None,
                    "estimated_reset_time_utc": None,
                }
                
                if groq_service.quota_reset_time:
                    quota_status["reset_time"] = groq_service.quota_reset_time
                    remaining = max(0, int(groq_service.quota_reset_time - current_time))
                    quota_status["remaining_seconds"] = remaining
                    reset_time_utc = datetime.datetime.utcfromtimestamp(groq_service.quota_reset_time).isoformat()
                    quota_status["estimated_reset_time_utc"] = reset_time_utc
                
                rate_limit_status = {
                    "minute_limit": groq_service.rate_limiter.requests_per_minute,
                    "day_limit": groq_service.rate_limiter.requests_per_day,
                    "minute_used": groq_service.rate_limiter.minute_requests,
                    "day_used": groq_service.rate_limiter.day_requests,
                    "minute_reset_in": max(0, int(groq_service.rate_limiter.minute_reset_time - current_time)),
                    "day_reset_in": max(0, int(groq_service.rate_limiter.day_reset_time - current_time)),
                }
                
                return {
                    "ai_available": True,
                    "ai_type": "LLaMA 3 (Groq)",
                    "ai_model": getattr(groq_service, "model", "unknown"),
                    "use_fallback_data": groq_service.quota_exceeded or not groq_service.available,
                    "quota_status": quota_status,
                    "rate_limits": rate_limit_status,
                    "server_time_utc": datetime.datetime.utcnow().isoformat()
                }
        except ImportError:
            pass
        
        # Không có AI nào khả dụng
        return {
            "ai_available": False,
            "ai_type": "None",
            "use_fallback_data": True,
            "server_time_utc": datetime.datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "ai_available": False,
            "use_fallback_data": True,
            "error": f"Error checking API status: {str(e)}"
        }

@app.post("/clear-cache")
async def clear_cache():
    """
    Xóa cache để buộc tạo mới dữ liệu
    
    Returns:
    - Thông báo kết quả
    """
    try:
        result = {"message": "Cache cleared successfully", "details": []}
        
        # Xóa cache của Groq
        try:
            from groq_integration_direct import groq_service  # Fixed version
            groq_service.clear_cache()
            result["details"].append("Groq cache cleared")
        except ImportError:
            pass
        except Exception as e:
            result["details"].append(f"Error clearing Groq cache: {str(e)}")
            
        return result
    except Exception as e:
        return {"error": f"Error clearing cache: {str(e)}"}

# USDA Food Database Endpoints
@app.get("/usda/search", tags=["USDA Food Database"])
async def search_usda_foods(
    query: str = Query(..., description="Từ khóa tìm kiếm thực phẩm (tiếng Việt hoặc tiếng Anh)"),
    vietnamese: bool = Query(True, description="Có phải truy vấn tiếng Việt không"),
    max_results: int = Query(10, description="Số kết quả tối đa trả về")
):
    """
    Tìm kiếm thực phẩm trong cơ sở dữ liệu USDA FoodData Central.
    
    Nếu query là tiếng Việt, hệ thống sẽ dịch sang tiếng Anh trước khi tìm kiếm.
    
    Parameters:
    - query: Từ khóa tìm kiếm thực phẩm
    - vietnamese: Có phải truy vấn tiếng Việt không
    - max_results: Số kết quả tối đa trả về
    
    Returns:
    - Danh sách các thực phẩm phù hợp với từ khóa tìm kiếm
    """
    try:
        if not usda_api.available:
            raise HTTPException(
                status_code=503, 
                detail="USDA API không khả dụng. Vui lòng cấu hình USDA_API_KEY trong biến môi trường."
            )
        
        results = usda_api.search_foods(query, vietnamese=vietnamese, max_results=max_results)
        
        return {
            "query": query,
            "translated_query": usda_api._translate_vi_to_en(query) if vietnamese else query,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tìm kiếm thực phẩm: {str(e)}")

@app.get("/usda/food/{food_id}", tags=["USDA Food Database"])
async def get_usda_food(
    food_id: int = Path(..., description="ID của thực phẩm trong USDA FoodData Central")
):
    """
    Lấy thông tin chi tiết về một loại thực phẩm trong USDA FoodData Central.
    
    Parameters:
    - food_id: ID của thực phẩm
    
    Returns:
    - Thông tin chi tiết về thực phẩm
    """
    try:
        if not usda_api.available:
            raise HTTPException(
                status_code=503, 
                detail="USDA API không khả dụng. Vui lòng cấu hình USDA_API_KEY trong biến môi trường."
            )
        
        food_detail = usda_api.get_food_detail(food_id)
        
        if not food_detail:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thực phẩm có ID: {food_id}")
        
        return food_detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy thông tin thực phẩm: {str(e)}")

@app.get("/usda/nutrition", tags=["USDA Food Database"])
async def get_nutrition_info(
    query: str = Query(..., description="Tên thực phẩm cần tìm (tiếng Việt hoặc tiếng Anh)"),
    amount: Optional[str] = Query(None, description="Số lượng (ví dụ: '100g', '1 cup')"),
    vietnamese: bool = Query(True, description="Có phải truy vấn tiếng Việt không")
):
    """
    Lấy thông tin dinh dưỡng cho một loại thực phẩm với số lượng cụ thể.
    
    Parameters:
    - query: Tên thực phẩm cần tìm
    - amount: Số lượng (ví dụ: "100g", "1 cup")
    - vietnamese: Có phải truy vấn tiếng Việt không
    
    Returns:
    - Thông tin dinh dưỡng của thực phẩm với số lượng đã chỉ định
    """
    try:
        if not usda_api.available:
            raise HTTPException(
                status_code=503, 
                detail="USDA API không khả dụng. Vui lòng cấu hình USDA_API_KEY trong biến môi trường."
            )
        
        nutrition_info = usda_api.get_nutrition_info(query, amount, vietnamese=vietnamese)
        
        if not nutrition_info:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy thông tin dinh dưỡng cho: {query}")
        
        return {
            "query": query,
            "translated_query": usda_api._translate_vi_to_en(query) if vietnamese else query,
            "nutrition": nutrition_info
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy thông tin dinh dưỡng: {str(e)}")

@app.get("/usda/translate", tags=["USDA Food Database"])
async def translate_food_name(
    vietnamese_query: str = Query(..., description="Tên thực phẩm bằng tiếng Việt")
):
    """
    Dịch tên thực phẩm từ tiếng Việt sang tiếng Anh.
    
    Parameters:
    - vietnamese_query: Tên thực phẩm bằng tiếng Việt
    
    Returns:
    - Tên thực phẩm đã được dịch sang tiếng Anh
    """
    try:
        english_query = usda_api._translate_vi_to_en(vietnamese_query)
        
        return {
            "vietnamese": vietnamese_query,
            "english": english_query
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi dịch tên thực phẩm: {str(e)}")

@app.post("/usda/clear-cache", tags=["USDA Food Database"])
async def clear_usda_cache():
    """
    Xóa cache của USDA API.
    
    Returns:
    - Thông báo kết quả
    """
    try:
        usda_api.clear_cache()
        return {"success": True, "message": "Đã xóa cache USDA API"}
    except Exception as e:
        return {"success": False, "error": f"Lỗi khi xóa cache USDA API: {str(e)}"}

# Thêm endpoint /chat vào FastAPI
@app.post("/chat", response_model=ChatResponse, tags=["Chat API"])
async def chat(message: ChatMessage):
    """
    Endpoint nhận tin nhắn từ người dùng, xử lý qua Groq API và trả về phản hồi
    
    Parameters:
    - message: Nội dung tin nhắn từ người dùng
    
    Returns:
    - Phản hồi từ AI
    """
    try:
        if not chat_client or not chat_available:
            raise HTTPException(
                status_code=503,
                detail="Groq API không khả dụng. Vui lòng cấu hình GROQ_API_KEY trong biến môi trường."
            )
            
        # Gọi Groq API với system prompt và user message
        completion = chat_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system", 
                    "content": "Bạn là trợ lý ẩm thực thông minh, chuyên tư vấn món ăn theo nhu cầu người dùng. Hãy trả lời bằng tiếng Việt."
                },
                {
                    "role": "user", 
                    "content": message.message
                }
            ],
            temperature=0.7,
        )
        
        # Trích xuất phản hồi từ AI
        ai_reply = completion.choices[0].message.content
        
        # Lưu tin nhắn vào Firebase
        try:
            from firebase_admin import firestore
            db = firestore.client()
            
            # Tạo dữ liệu chat
            chat_data = {
                "user_id": message.user_id if hasattr(message, 'user_id') else "anonymous",
                "user_message": message.message,
                "ai_reply": ai_reply,
                "timestamp": datetime.now().isoformat(),
                "model": "llama3-8b-8192"
            }
            
            # Tạo ID cho chat
            import uuid
            chat_id = str(uuid.uuid4())
            
            # Lưu vào Firestore
            db.collection("chat_history").document(chat_id).set(chat_data)
            print(f"Đã lưu chat với ID: {chat_id}")
            
            # Trả về kết quả dạng JSON với chat_id
            return {"reply": ai_reply, "chat_id": chat_id}
            
        except Exception as firebase_error:
            print(f"Lỗi khi lưu chat vào Firebase: {str(firebase_error)}")
            # Vẫn trả về phản hồi ngay cả khi lưu vào Firebase thất bại
            return ChatResponse(reply=ai_reply)
        
    except Exception as e:
        print(f"Lỗi khi xử lý chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi: {str(e)}")

# Thêm endpoint lấy lịch sử chat
@app.get("/chat/history", tags=["Chat API"])
async def get_chat_history(
    user_id: str = Query(..., description="ID của người dùng"),
    limit: int = Query(10, description="Số lượng tin nhắn tối đa trả về")
):
    """
    Lấy lịch sử chat của một người dùng
    
    Parameters:
    - user_id: ID của người dùng
    - limit: Số lượng tin nhắn tối đa trả về
    
    Returns:
    - Danh sách các cuộc hội thoại
    """
    try:
        from firebase_admin import firestore
        db = firestore.client()
        
        # Truy vấn Firestore
        chats = (db.collection("chat_history")
                .where("user_id", "==", user_id)
                .limit(limit)
                .get())
        
        # Chuyển đổi kết quả thành danh sách
        chat_list = []
        for chat in chats:
            chat_data = chat.to_dict()
            chat_data["id"] = chat.id
            chat_list.append(chat_data)
        
        return {"history": chat_list, "count": len(chat_list)}
        
    except Exception as e:
        print(f"Lỗi khi lấy lịch sử chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi khi lấy lịch sử chat: {str(e)}")

# Endpoint /meal-plan/{user_id} đã được xử lý trong api_router

# Thêm route chuyển hướng cho /api/firestore/users/sync
@app.post("/api/firestore/users/sync")
async def redirect_to_api_sync(
    data: Dict[str, Any],
    user_id: str = Query(None, description="ID của người dùng")
):
    """
    Chuyển hướng từ /api/firestore/users/sync sang /api/sync
    
    Endpoint này được giữ lại để tương thích với các phiên bản cũ của ứng dụng Flutter
    """
    from fastapi.responses import RedirectResponse
    redirect_url = f"/api/sync?user_id={user_id}" if user_id else "/api/sync"
    print(f"Chuyển hướng từ /api/firestore/users/sync sang {redirect_url}")
    print(f"Dữ liệu nhận được: {json.dumps(data, indent=2)[:500]}...")
    # Sử dụng status_code=307 để đảm bảo phương thức POST và body được giữ nguyên khi chuyển hướng
    return RedirectResponse(url=redirect_url, status_code=307)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
