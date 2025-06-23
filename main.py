from fastapi import FastAPI, HTTPException, Depends, Query, Body, Path, Header, Security, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from typing import Dict, Optional, List, Any
import time
import os
import json
from datetime import datetime
import logging
from fastapi.responses import JSONResponse
from datetime import timedelta as Duration
import auth_utils as auth_service

# Import config từ module config
from config import config

# Import get_optional_current_user từ auth_utils
from auth_utils import get_current_user, security, ensure_user_in_firestore, get_optional_current_user

# Import DAYS_OF_WEEK từ utils
from utils import DAYS_OF_WEEK

# Thiết lập logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)

# Thêm các import còn thiếu
try:
    # Import groq_service từ groq_integration_direct
    from groq_integration import groq_service  # Enhanced version
except ImportError:
    logger.warning("Không thể import groq_service từ groq_integration_direct. Tạo một dịch vụ giả lập.")
    # Tạo một dịch vụ giả lập nếu không thể import
    class DummyGroqService:
        def chat(self, *args, **kwargs):
            return {"choices": [{"message": {"content": "Dịch vụ AI không khả dụng"}}]}
    groq_service = DummyGroqService()

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
    TokenPayload, AuthRequest, UserResponse, AuthResponse, FoodRecognitionResponse
)
import services
from storage_manager import storage_manager
from auth_utils import get_current_user, security, ensure_user_in_firestore

# Import generate_random_data
from generate_random_data import generate_weekly_plan

# Import USDA API integration
from usda_integration import usda_api

# Import routers
from routers import firestore_router, api_router, compat_router, meal_plan_router, openfood_router, admin_router, youtube_router

# Thêm import cho chat API
from pydantic import BaseModel, Field, validator
from openai import OpenAI

# Firebase Admin SDK
import firebase_admin
from firebase_admin import credentials, auth

# Import Food Recognition
from food_recognition_service import food_recognition_service

# Import Firebase Storage
from firebase_storage_service import firebase_storage_service

# YouTube services removed

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
            # Lấy cấu hình Firebase từ config
            firebase_config = config.get_firebase_config()
            firebase_admin.initialize_app(cred, firebase_config)
            
            print(f"Firebase Admin SDK initialized successfully using {initialized_method}.")
            print(f"Project ID: {firebase_admin.get_app().project_id}, Storage Bucket: {firebase_config['storageBucket']}")
            
            # Kiểm tra kết nối với Storage
            print("Testing Firebase Storage connection...")
            if firebase_storage_service.check_connection():
                print("Successfully connected to Firebase Storage!")
            else:
                print("WARNING: Could not connect to Firebase Storage!")
                
                # Nếu không thể kết nối, kiểm tra và cố gắng sửa cấu hình storageBucket
                if not firebase_config.get('storageBucket'):
                    # Thử thiết lập storageBucket mặc định nếu chưa có
                    default_bucket = "food-ai-96ef6.appspot.com"
                    print(f"Attempting to set default storage bucket: {default_bucket}")
                    
                    try:
                        # Tạo cấu hình mới với storageBucket
                        updated_config = firebase_config.copy()
                        updated_config['storageBucket'] = default_bucket
                        
                        # Khởi tạo lại app với cấu hình mới
                        firebase_admin.delete_app(firebase_admin.get_app())
                        firebase_admin.initialize_app(cred, updated_config)
                        print(f"Reinitialized Firebase with storage bucket: {default_bucket}")
                        
                        # Kiểm tra lại kết nối
                        if firebase_storage_service.check_connection():
                            print("Successfully connected to Firebase Storage after reconfiguration!")
                        else:
                            print("Still unable to connect to Firebase Storage after reconfiguration.")
                    except Exception as storage_error:
                        print(f"Error setting default storage bucket: {storage_error}")
        except Exception as e:
            print(f"Lỗi khi gọi firebase_admin.initialize_app: {e}")
            # raise e # Bỏ comment nếu muốn dừng hẳn
    else:
        print("Không thể khởi tạo Firebase Admin SDK: Không tìm thấy credentials hợp lệ.")

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
app.include_router(firestore_router, prefix="/firestore", tags=["Firestore"])
app.include_router(api_router, prefix="/api", tags=["API"])
app.include_router(compat_router, tags=["Compatibility"])
app.include_router(meal_plan_router, prefix="/api/meal-plan", tags=["Meal Plan"])

# Mount OpenFood router
app.include_router(openfood_router.router, tags=["OpenFood Management"])

# Mount Admin router
app.include_router(admin_router.router, tags=["Admin Management"])

# Mount YouTube router
app.include_router(youtube_router.router, tags=["YouTube Proxy"])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Đã chuyển hàm get_current_user sang file auth_utils.py

# Dependency to get the current meal plan from storage
async def get_current_meal_plan(
    user_id: str = "default",
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
) -> Optional[WeeklyMealPlan]:
    """
    Đọc kế hoạch thực đơn hiện tại từ bộ nhớ (Firebase hoặc file)
    
    Args:
        user_id: ID của người dùng
        user: Thông tin người dùng đã xác thực (có thể là None)
        
    Returns:
        Đối tượng WeeklyMealPlan hiện tại hoặc None
    """
    # Kiểm tra xác thực chỉ khi user tồn tại
    if user is not None:
        # Nếu user_id không phải "default" và khác với uid trong token,
        # chỉ cho phép nếu là dữ liệu public hoặc người dùng là admin
        if user_id != "default" and user_id != user.uid:
            # Kiểm tra quyền admin hoặc dữ liệu public ở đây nếu cần
            pass
    
    print(f"[DEBUG] Getting meal plan for user_id: {user_id}")
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

@app.get("/debug/groq")
async def debug_groq():
    """Debug endpoint to check Groq integration on Render"""
    import sys

    debug_info = {
        "groq_api_key_set": bool(os.getenv("GROQ_API_KEY")),
        "groq_api_key_length": len(os.getenv("GROQ_API_KEY", "")),
        "python_version": sys.version,
        "environment": "render" if os.getenv("RENDER") else "local",
        "timestamp": datetime.now().isoformat()
    }

    # Test Groq import
    try:
        import groq
        debug_info["groq_import"] = "success"
        debug_info["groq_version"] = getattr(groq, "__version__", "unknown")

        # Test Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            try:
                client = groq.Groq(api_key=api_key)
                debug_info["groq_client"] = "success"

                # Test simple API call
                completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=10,
                    temperature=0.0,
                    timeout=30
                )
                debug_info["groq_api_call"] = "success"
                debug_info["groq_response"] = completion.choices[0].message.content

            except Exception as e:
                debug_info["groq_client"] = f"failed: {str(e)}"
        else:
            debug_info["groq_client"] = "no_api_key"

    except ImportError as e:
        debug_info["groq_import"] = f"failed: {str(e)}"

    # Test GroqService integration
    try:
        from groq_integration import GroqService  # Enhanced version  # Fixed version
        debug_info["groq_service_import"] = "success"

        service = GroqService()
        debug_info["groq_service_available"] = service.available

        if service.available:
            # Test meal generation
            meals = service.generate_meal_suggestions(
                calories_target=300,
                protein_target=20,
                fat_target=10,
                carbs_target=40,
                meal_type="bữa sáng",
                use_ai=True
            )
            debug_info["groq_service_test"] = "success" if meals else "no_meals_generated"
            debug_info["generated_meals_count"] = len(meals) if meals else 0
        else:
            debug_info["groq_service_test"] = "service_not_available"

    except Exception as e:
        debug_info["groq_service_import"] = f"failed: {str(e)}"

    return debug_info

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
            from groq_integration import groq_service  # Enhanced version  # Fixed version
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
        from groq_integration import groq_service  # Enhanced version  # Fixed version
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
            from groq_integration import groq_service  # Enhanced version  # Fixed version
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
            from groq_integration import groq_service  # Enhanced version  # Fixed version
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

# Thêm hàm format_user_context trước định nghĩa endpoint /chat
def format_user_context(user_profile: dict, meal_plan: dict, food_logs: list, exercise_history: list = None, water_intake: list = None, user_id: str = None) -> str:
    """
    Định dạng dữ liệu người dùng thành một đoạn văn bản context cho chatbot

    Args:
        user_profile: Dữ liệu hồ sơ người dùng
        meal_plan: Dữ liệu kế hoạch ăn uống
        food_logs: Danh sách các bản ghi thực phẩm đã ăn
        exercise_history: Lịch sử bài tập của người dùng
        water_intake: Lượng nước uống trong ngày
        user_id: ID của người dùng

    Returns:
        Đoạn văn bản context đã định dạng
    """
    context_parts = []

    # Thông tin hồ sơ
    if user_profile:
        # Hỗ trợ các cấu trúc dữ liệu khác nhau
        goal = user_profile.get('goal', user_profile.get('dietGoal', 'Không rõ'))

        # Lấy mục tiêu calo từ tdee_calories hoặc nutrition_goals.calories
        calories_target = (
            user_profile.get('tdee_calories') or
            user_profile.get('nutrition_goals', {}).get('calories') or
            user_profile.get('targetCalories', 'Không rõ')
        )

        # Dị ứng có thể lưu ở trường allergies hoặc diet_restrictions
        allergies = ", ".join(user_profile.get('allergies', [])) or "không có"

        # Chế độ ăn đặc biệt từ diet_restrictions
        diet_restrictions = ", ".join(user_profile.get('diet_restrictions', [])) or "không có"

        # Chiều cao từ height_cm
        height = user_profile.get('height_cm', user_profile.get('height', 'Không rõ'))

        # Cân nặng từ weight_kg
        weight = user_profile.get('weight_kg', user_profile.get('weight', 'Không rõ'))

        # Độ tuổi từ age
        age = user_profile.get('age', 'Không rõ')

        # Giới tính từ gender
        gender = user_profile.get('gender', 'Không rõ')

        # Mức độ hoạt động
        activity = user_profile.get('activity_level', 'Không rõ')

        # In dữ liệu hồ sơ để debug
        print(f"[DEBUG] User profile data: {user_profile}")

        context_parts.append(f"- Hồ sơ: Người dùng {age} tuổi, giới tính {gender}. Mục tiêu là '{goal}', mức hoạt động '{activity}'. "
                          f"Mục tiêu calo hàng ngày là {calories_target} kcal. "
                          f"Chiều cao: {height}cm, cân nặng: {weight}kg. "
                          f"Dị ứng với: {allergies}. Chế độ ăn: {diet_restrictions}.")

    # Thông tin kế hoạch bữa ăn hôm nay
    if meal_plan:
        today_day = datetime.now().strftime("%A").lower()
        # Chuyển đổi tên ngày tiếng Anh sang tiếng Việt nếu cần
        days_translation = {
            "monday": "monday", "tuesday": "tuesday", "wednesday": "wednesday",
            "thursday": "thursday", "friday": "friday", "saturday": "saturday", "sunday": "sunday"
        }
        today_day_key = days_translation.get(today_day, today_day)

        # Tìm dữ liệu ngày hiện tại trong kế hoạch
        today_plan = None
        if "days" in meal_plan:
            for day in meal_plan.get("days", []):
                if day.get("day_of_week", "").lower() == today_day_key:
                    today_plan = day
                    break

        if today_plan:
            breakfast = ", ".join([dish.get("name", "") for dish in today_plan.get("breakfast", [])])
            lunch = ", ".join([dish.get("name", "") for dish in today_plan.get("lunch", [])])
            dinner = ", ".join([dish.get("name", "") for dish in today_plan.get("dinner", [])])

            context_parts.append(f"- Kế hoạch hôm nay: "
                              f"Bữa sáng gồm {breakfast}. "
                              f"Bữa trưa gồm {lunch}. "
                              f"Bữa tối gồm {dinner}.")

    # Thông tin nhật ký đã ăn
    if food_logs:
        # 🔧 FIX: Tính tổng calo CHÍNH XÁC - tránh tính 2 lần
        eaten_calories = 0
        for log in food_logs:
            log_calories = 0  # Calories cho log này

            # Ưu tiên 1: Từ total_nutrition.calories (đã tính tổng)
            if log.get('total_nutrition', {}).get('calories'):
                log_calories = log.get('total_nutrition', {}).get('calories', 0)
                print(f"[DEBUG] Log calories from total_nutrition: {log_calories}")

            # Ưu tiên 2: Từ trường calories trực tiếp
            elif log.get('calories'):
                log_calories = log.get('calories', 0)
                print(f"[DEBUG] Log calories from calories field: {log_calories}")

            # Ưu tiên 3: Tính từ items (nếu không có calories tổng)
            elif log.get('items'):
                for item in log.get('items', []):
                    item_calories = item.get('calories', 0)
                    log_calories += item_calories
                    print(f"[DEBUG] Item calories: {item_calories}, total so far: {log_calories}")

            eaten_calories += log_calories
            print(f"[DEBUG] Added {log_calories} calories from this log, total eaten: {eaten_calories}")

        # Thu thập tên các món ăn
        eaten_dishes = []
        for log in food_logs:
            # Cách 1: Từ recognized_foods (cấu trúc cũ)
            if log.get('recognized_foods'):
                for food in log.get('recognized_foods', []):
                    if food.get('food_name'):
                        eaten_dishes.append(food.get('food_name'))

            # Cách 2: Từ items (cấu trúc mới)
            elif log.get('items'):
                for item in log.get('items', []):
                    if item.get('name'):
                        eaten_dishes.append(item.get('name'))

            # Cách 3: Từ description (cấu trúc mới)
            elif log.get('description'):
                eaten_dishes.append(log.get('description'))

        if eaten_dishes:
            context_parts.append(f"- Nhật ký đã ăn hôm nay: Đã ăn {len(food_logs)} bữa với các món: {', '.join(eaten_dishes)}. "
                             f"Tổng calo đã nạp: {eaten_calories} kcal.")
        else:
            context_parts.append(f"- Nhật ký đã ăn hôm nay: Đã ghi nhận {len(food_logs)} bữa ăn nhưng không có thông tin chi tiết.")
    else:
        context_parts.append("- Nhật ký đã ăn hôm nay: Chưa ghi nhận bữa nào.")

    # Thông tin bài tập
    if exercise_history:
        # Tính tổng calo đã đốt
        burned_calories = 0
        for exercise in exercise_history:
            # Cách 1: Từ calories_burned (cấu trúc cũ)
            if 'calories_burned' in exercise:
                burned_calories += exercise.get('calories_burned', 0)
            # Cách 2: Từ calories (cấu trúc mới)
            elif 'calories' in exercise:
                burned_calories += exercise.get('calories', 0)

        # Liệt kê các bài tập đã thực hiện
        exercise_list = []
        for exercise in exercise_history:
            # Cách 1: Từ cấu trúc cũ
            if exercise.get('exercise_name') and exercise.get('duration_minutes'):
                exercise_name = exercise.get('exercise_name')
                duration = exercise.get('duration_minutes')
                exercise_list.append(f"{exercise_name} ({duration} phút)")
            # Cách 2: Từ cấu trúc mới
            elif exercise.get('name') and exercise.get('minutes'):
                exercise_name = exercise.get('name')
                duration = exercise.get('minutes')
                exercise_list.append(f"{exercise_name} ({duration} phút)")

        if exercise_list:
            context_parts.append(f"- Bài tập hôm nay: Đã tập {len(exercise_history)} bài tập: {', '.join(exercise_list)}. "
                               f"Tổng calo đã đốt: {burned_calories} kcal.")
        else:
            context_parts.append(f"- Bài tập hôm nay: Đã ghi nhận {len(exercise_history)} hoạt động nhưng không có thông tin chi tiết.")
    else:
        if user_id:
            print(f"[DEBUG] Không tìm thấy dữ liệu bài tập cho user_id={user_id}. Kiểm tra collection và index")
        context_parts.append("- Bài tập hôm nay: Chưa ghi nhận bài tập nào.")

    # Thông tin nước uống
    if water_intake:
        # Tính tổng lượng nước đã uống
        total_water_ml = 0
        for intake in water_intake:
            # Cách 1: Từ amount_ml (cấu trúc cũ)
            if 'amount_ml' in intake:
                total_water_ml += intake.get('amount_ml', 0)
            # Cách 2: Từ amount (cấu trúc mới)
            elif 'amount' in intake:
                total_water_ml += intake.get('amount', 0)

        # Chuyển đổi sang lít
        total_water_liter = total_water_ml / 1000

        # Kiểm tra có đạt mục tiêu không
        water_target = 2000  # Mặc định 2 lít (2000ml)

        # Cố gắng lấy mục tiêu từ user_profile
        if user_profile:
            if user_profile.get('waterTarget', {}).get('amount_ml'):
                water_target = user_profile.get('waterTarget', {}).get('amount_ml')
            elif user_profile.get('water_target'):
                water_target = user_profile.get('water_target')
            elif user_profile.get('nutrition_goals', {}).get('water'):
                water_target = user_profile.get('nutrition_goals', {}).get('water')

        water_target_liter = water_target / 1000
        percentage = (total_water_liter / water_target_liter) * 100 if water_target_liter > 0 else 0

        context_parts.append(f"- Nước uống hôm nay: Đã uống {total_water_liter:.1f} lít nước "
                          f"({percentage:.0f}% mục tiêu {water_target_liter:.1f} lít).")
    else:
        if user_id:
            print(f"[DEBUG] Không tìm thấy dữ liệu nước uống cho user_id={user_id}. Kiểm tra collection và index")
        context_parts.append("- Nước uống hôm nay: Chưa ghi nhận lượng nước uống nào.")

    return "\n".join(context_parts)

# 🔧 FIX: Đã xóa endpoint /chat duplicate thứ nhất
# Endpoint chính được giữ lại ở dòng 1270 với logic tính calories đã được sửa

# 🔧 FIX: Đã xóa function duplicate format_user_context thứ 2
# Function chính đã được định nghĩa ở dòng 832 và đã được sửa lỗi tính calories

# Cập nhật endpoint /chat để sử dụng xác thực và RAG
@app.post("/chat", response_model=ChatResponse, tags=["Chat API"])
async def chat(
    message: ChatMessage,
    user: TokenPayload = Depends(get_current_user)  # Thêm xác thực người dùng
):
    """
    Endpoint nhận tin nhắn từ người dùng, xử lý qua Groq API và trả về phản hồi
    Sử dụng kỹ thuật RAG (Retrieval-Augmented Generation) để cá nhân hóa phản hồi
    
    Parameters:
    - message: Nội dung tin nhắn từ người dùng
    - user: Thông tin người dùng đã xác thực
    
    Returns:
    - Phản hồi từ AI
    """
    try:
        if not chat_client or not chat_available:
            raise HTTPException(
                status_code=503,
                detail="Groq API không khả dụng. Vui lòng cấu hình GROQ_API_KEY trong biến môi trường."
            )
        
        # Lấy user_id từ token xác thực
        user_id = user.uid
        print(f"Chat request for user: {user_id}")
        
        # Truy xuất dữ liệu người dùng từ Firestore
        try:
            from services.firestore_service import firestore_service
            
            # 1. Lấy hồ sơ người dùng
            user_profile = firestore_service.get_user(user_id) or {}
            print(f"[DEBUG] User profile retrieved from Firestore: {user_profile}")
            
            # Nếu không tìm thấy dữ liệu từ get_user, thử phương thức get_user_profile
            if not user_profile or len(user_profile) == 0:
                print(f"[DEBUG] No user data found with get_user, trying get_user_profile")
                profile_obj = firestore_service.get_user_profile(user_id)
                if profile_obj:
                    # Chuyển đổi từ UserProfile thành dict nếu cần
                    if hasattr(profile_obj, 'to_dict'):
                        user_profile = profile_obj.to_dict()
                    elif hasattr(profile_obj, '__dict__'):
                        user_profile = profile_obj.__dict__
                print(f"[DEBUG] User profile from get_user_profile: {user_profile}")
            
            # 2. Lấy kế hoạch ăn mới nhất
            try:
                meal_plan_data = firestore_service.get_latest_meal_plan(user_id) or {}
                if hasattr(meal_plan_data, 'dict'):
                    meal_plan_dict = meal_plan_data.dict()
                else:
                    meal_plan_dict = meal_plan_data
            except Exception as e:
                print(f"[DEBUG] Error getting meal plan: {str(e)}")
                meal_plan_dict = {}
            
            # 3. Lấy nhật ký ăn uống hôm nay
            today_str = datetime.now().strftime("%Y-%m-%d")
            try:
                food_logs_today = firestore_service.get_food_logs_by_date(user_id, today_str) or []
            except Exception as e:
                print(f"[DEBUG] Error getting food logs: {str(e)}")
                food_logs_today = []
            
            # 4. Lấy thông tin bài tập hôm nay
            exercise_history = []
            try:
                print(f"[DEBUG] Đang tìm bài tập với userId={user_id} trong collection exercises")
                exercise_history = firestore_service.get_exercise_history(user_id, start_date=today_str, end_date=today_str) or []
            except Exception as e:
                print(f"Error getting exercise history: {str(e)}")
                
                # Hướng dẫn tạo index nếu cần
                if "requires an index" in str(e):
                    index_url = str(e).split("create it here: ")[1] if "create it here: " in str(e) else ""
                    if index_url:
                        print(f"[INDEX NEEDED] Please create the required Firestore index at: {index_url}")
            
            # 5. Lấy thông tin nước uống hôm nay
            water_intake = []
            try:
                print(f"[DEBUG] Đang tìm nước uống với userId={user_id} trong collection water_entries")
                water_intake = firestore_service.get_water_intake_by_date(user_id, today_str) or []
            except Exception as e:
                print(f"Error getting water intake by date: {str(e)}")
                
                # Hướng dẫn tạo index nếu cần
                if "requires an index" in str(e):
                    index_url = str(e).split("create it here: ")[1] if "create it here: " in str(e) else ""
                    if index_url:
                        print(f"[INDEX NEEDED] Please create the required Firestore index at: {index_url}")
            
            # Tạo context từ dữ liệu đã truy xuất
            context_data = format_user_context(
                user_profile, 
                meal_plan_dict, 
                food_logs_today,
                exercise_history,
                water_intake,
                user_id
            )
            
            # Xây dựng prompt thông minh
            augmented_prompt = f"""Bạn là một trợ lý dinh dưỡng ảo tên là DietAI. Nhiệm vụ của bạn là trả lời câu hỏi của người dùng dựa trên thông tin cá nhân và hoạt động hàng ngày của họ.

--- DỮ LIỆU CÁ NHÂN CỦA NGƯỜI DÙNG ---
{context_data}
--- KẾT THÚC DỮ LIỆU ---

Dựa vào các thông tin trên, hãy trả lời câu hỏi sau của người dùng một cách thân thiện và chính xác bằng tiếng Việt:

Câu hỏi: "{message.message}"
"""
            print(f"DEBUG: Augmented Prompt:\n{augmented_prompt[:500]}...")  # In ra 500 ký tự đầu để kiểm tra
            
        except Exception as e:
            print(f"Lỗi khi truy xuất dữ liệu người dùng: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"Tiếp tục với prompt thông thường")
            # Fallback to regular prompt if retrieval fails
            augmented_prompt = message.message
            
        # Gọi Groq API với prompt đã được bổ sung dữ liệu
        completion = chat_client.chat.completions.create(
            model="llama3-8b-8192",  # Có thể nâng cấp lên model lớn hơn nếu cần
            messages=[
                {
                    "role": "system", 
                    "content": "Bạn là trợ lý dinh dưỡng ảo tên là DietAI. Trả lời dựa trên dữ liệu người dùng."
                },
                {
                    "role": "user", 
                    "content": augmented_prompt
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
                "user_id": user_id,
                "user_message": message.message,
                "ai_reply": ai_reply,
                "timestamp": datetime.now().isoformat(),
                "model": "llama3-8b-8192",
                "augmented": True  # Đánh dấu đây là câu trả lời đã được tăng cường
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

# Food Recognition API models
class FoodRecognitionRequest(BaseModel):
    meal_type: str = Field("snack", description="Loại bữa ăn (breakfast, lunch, dinner, snack)")
    save_to_firebase: bool = Field(True, description="Lưu kết quả vào Firebase")

@app.post("/api/food/recognize", response_model=FoodRecognitionResponse, tags=["Food Recognition"])
async def recognize_food(
    meal_type: str = Form("snack", description="Loại bữa ăn (breakfast, lunch, dinner, snack)"),
    save_to_firebase: bool = Form(True, description="Lưu kết quả vào Firebase"),
    image: UploadFile = File(..., description="Ảnh thực phẩm cần nhận diện"),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Nhận diện thực phẩm từ ảnh sử dụng Gemini Vision Pro
    
    Parameters:
    - meal_type: Loại bữa ăn (breakfast, lunch, dinner, snack)
    - save_to_firebase: Lưu kết quả vào Firebase
    - image: File ảnh cần nhận diện
    
    Returns:
    - Kết quả nhận diện thực phẩm
    """
    try:
        # Kiểm tra Gemini Vision service có khả dụng không
        if not food_recognition_service.available:
            raise HTTPException(
                status_code=503,
                detail="Dịch vụ nhận diện thực phẩm không khả dụng. Hãy đảm bảo GEMINI_API_KEY đã được cấu hình."
            )
        
        # Kiểm tra nếu file không phải ảnh
        if not image.content_type.startswith("image/"):
            raise HTTPException(
                status_code=400,
                detail=f"File tải lên phải là ảnh, không phải {image.content_type}"
            )
        
        # Đọc dữ liệu ảnh
        image_data = await image.read()
        
        # Gọi service để nhận diện thực phẩm
        result = await food_recognition_service.recognize_food_from_image(
            image_data=image_data,
            user_id=user.uid,
            meal_type=meal_type,
            save_to_firebase=save_to_firebase
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error recognizing food: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi nhận diện thực phẩm: {str(e)}")

@app.get("/api/food/logs", tags=["Food Recognition"])
async def get_food_logs(
    limit: int = Query(20, description="Số lượng bản ghi tối đa"),
    user_id: str = Query("default", description="ID của người dùng"),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Lấy danh sách các bản ghi nhận diện thực phẩm của người dùng
    
    Parameters:
    - limit: Số lượng bản ghi tối đa trả về
    - user_id: ID của người dùng
    
    Returns:
    - Danh sách các bản ghi nhận diện thực phẩm
    """
    try:
        # Sử dụng user_id từ token nếu không có user_id được chỉ định
        if user_id == "default":
            user_id = user.uid
            
        # Kiểm tra quyền truy cập
        if user_id != user.uid and not user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Không có quyền xem bản ghi của người dùng khác"
            )
        
        # Lấy danh sách bản ghi
        from services.firestore_service import firestore_service
        logs = firestore_service.get_food_logs(user_id, limit)
        
        return {
            "user_id": user_id,
            "count": len(logs),
            "logs": logs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy bản ghi thực phẩm: {str(e)}")

@app.get("/api/food/logs/{date}", tags=["Food Recognition"])
async def get_food_logs_by_date(
    date: str = Path(..., description="Ngày theo định dạng YYYY-MM-DD"),
    user_id: str = Query("default", description="ID của người dùng"),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Lấy danh sách các bản ghi nhận diện thực phẩm của người dùng theo ngày
    
    Parameters:
    - date: Ngày theo định dạng YYYY-MM-DD
    - user_id: ID của người dùng
    
    Returns:
    - Danh sách các bản ghi nhận diện thực phẩm cho ngày đó
    """
    try:
        # Sử dụng user_id từ token nếu không có user_id được chỉ định
        if user_id == "default":
            user_id = user.uid
            
        # Kiểm tra quyền truy cập
        if user_id != user.uid and not user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Không có quyền xem bản ghi của người dùng khác"
            )
            
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail="Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD."
            )
        
        # Lấy danh sách bản ghi theo ngày
        from services.firestore_service import firestore_service
        logs = firestore_service.get_food_logs_by_date(user_id, date)
        
        return {
            "user_id": user_id,
            "date": date,
            "count": len(logs),
            "logs": logs
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi lấy bản ghi thực phẩm: {str(e)}")

@app.delete("/api/food/logs/{log_id}", tags=["Food Recognition"])
async def delete_food_log(
    log_id: str = Path(..., description="ID của bản ghi cần xóa"),
    user_id: str = Query("default", description="ID của người dùng"),
    user: TokenPayload = Depends(get_current_user)
):
    """
    Xóa một bản ghi nhận diện thực phẩm
    
    Parameters:
    - log_id: ID của bản ghi cần xóa
    - user_id: ID của người dùng
    
    Returns:
    - Thông báo kết quả
    """
    try:
        # Sử dụng user_id từ token nếu không có user_id được chỉ định
        if user_id == "default":
            user_id = user.uid
            
        # Kiểm tra quyền truy cập
        if user_id != user.uid and not user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Không có quyền xóa bản ghi của người dùng khác"
            )
        
        # Xóa bản ghi
        from services.firestore_service import firestore_service
        success = firestore_service.delete_food_log(user_id, log_id)
        
        if success:
            return {"message": f"Đã xóa bản ghi {log_id} thành công"}
        else:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy bản ghi {log_id}")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi xóa bản ghi thực phẩm: {str(e)}")

@app.get("/api/food/check-availability", tags=["Food Recognition"])
async def check_food_recognition_availability():
    """
    Kiểm tra trạng thái khả dụng của dịch vụ nhận diện thực phẩm
    
    Returns:
    - Thông tin về trạng thái khả dụng của dịch vụ
    """
    try:
        return {
            "gemini_vision_available": food_recognition_service.gemini_available,
            "firebase_storage_available": food_recognition_service.firebase_storage_available,
            "firestore_available": food_recognition_service.firestore_available,
            "service_available": food_recognition_service.available,
            "status": "available" if food_recognition_service.available else "unavailable"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# Thêm endpoint test Firebase Storage
@app.get("/api/storage/test", tags=["Firebase Storage"])
async def test_firebase_storage():
    """
    Kiểm tra kết nối đến Firebase Storage
    
    Returns:
        Dict: Thông tin về kết nối Firebase Storage
    """
    bucket_name = firebase_storage_service.bucket_name if firebase_storage_service.available else None
    connection_ok = firebase_storage_service.check_connection()
    
    # Lấy danh sách files
    files = firebase_storage_service.list_files(max_results=5) if connection_ok else []
    
    return {
        "service_available": firebase_storage_service.available,
        "connection_ok": connection_ok,
        "bucket_name": bucket_name,
        "sample_files": files[:5] if files else [],
        "status": "ok" if connection_ok else "error"
    }

# Cập nhật model cho yêu cầu tạo kế hoạch ăn
class MealPlanRequest(BaseModel):
    user_id: str = "default"
    calories_target: int = 2000
    protein_target: int = 120
    fat_target: int = 65
    carbs_target: int = 250
    use_ai: bool = True
    preferences: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    cuisine_style: Optional[str] = None
    diet_restrictions: Optional[List[str]] = None
    diet_preference: Optional[str] = None
    health_conditions: Optional[List[str]] = None
    fiber_target: Optional[int] = None
    sugar_target: Optional[int] = None
    sodium_target: Optional[int] = None
    day_of_week: Optional[str] = None  # Thêm trường ngày trong tuần
    meal_type: Optional[str] = None    # Thêm trường loại bữa ăn

@app.post("/api/meal-plan/generate", tags=["Meal Plan"])
async def generate_meal_plan(
    meal_plan_request: MealPlanRequest,
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    try:
        # Extract request data
        user_id = meal_plan_request.user_id
        calories_target = meal_plan_request.calories_target
        protein_target = meal_plan_request.protein_target
        fat_target = meal_plan_request.fat_target
        carbs_target = meal_plan_request.carbs_target
        use_ai = meal_plan_request.use_ai
        preferences = meal_plan_request.preferences or []
        allergies = meal_plan_request.allergies or []
        cuisine_style = meal_plan_request.cuisine_style
        diet_restrictions = meal_plan_request.diet_restrictions or []
        diet_preference = meal_plan_request.diet_preference
        health_conditions = meal_plan_request.health_conditions or []
        fiber_target = meal_plan_request.fiber_target
        sugar_target = meal_plan_request.sugar_target
        sodium_target = meal_plan_request.sodium_target
        
        # Create user_data dictionary with all relevant health information
        user_data = {
            "allergies": allergies,
            "diet_restrictions": diet_restrictions,
            "diet_preference": diet_preference,
            "health_conditions": health_conditions,
            "fiber_target": fiber_target,
            "sugar_target": sugar_target,
            "sodium_target": sodium_target
        }
        
        # Log received data for debugging
        logger.info(f"Generating meal plan for user {user_id}")
        logger.info(f"Nutrition targets: {calories_target}cal, {protein_target}g protein, {fat_target}g fat, {carbs_target}g carbs")
        logger.info(f"Health info: allergies={allergies}, health_conditions={health_conditions}, diet_restrictions={diet_restrictions}")
        
        # Generate weekly meal plan
        weekly_plan = {}
        for day in DAYS_OF_WEEK:
            breakfast_meals = groq_service.generate_meal_suggestions(
                calories_target=int(calories_target * 0.25),  # 25% of calories for breakfast
                protein_target=int(protein_target * 0.25),
                fat_target=int(fat_target * 0.25),
                carbs_target=int(carbs_target * 0.25),
                meal_type="breakfast",
                preferences=preferences,
                allergies=allergies,
                cuisine_style=cuisine_style,
                use_ai=use_ai,
                user_data=user_data  # Pass all health-related data
            )
            
            lunch_meals = groq_service.generate_meal_suggestions(
                calories_target=int(calories_target * 0.35),  # 35% of calories for lunch
                protein_target=int(protein_target * 0.35),
                fat_target=int(fat_target * 0.35),
                carbs_target=int(carbs_target * 0.35),
                meal_type="lunch",
                preferences=preferences,
                allergies=allergies,
                cuisine_style=cuisine_style,
                use_ai=use_ai,
                user_data=user_data  # Pass all health-related data
            )
            
            dinner_meals = groq_service.generate_meal_suggestions(
                calories_target=int(calories_target * 0.40),  # 40% of calories for dinner
                protein_target=int(protein_target * 0.40),
                fat_target=int(fat_target * 0.40),
                carbs_target=int(carbs_target * 0.40),
                meal_type="dinner",
                preferences=preferences,
                allergies=allergies,
                cuisine_style=cuisine_style,
                use_ai=use_ai,
                user_data=user_data  # Pass all health-related data
            )
            
            # Continue with the rest of your code...
        
        # Return a placeholder response for now
        return {"message": "Meal plan generation is in progress"}
        
    except Exception as e:
        # Handle exceptions
        raise HTTPException(
            status_code=500,
            detail=f"Error generating meal plan: {str(e)}"
        )

# Cập nhật endpoint thay thế một ngày
@app.post("/api/replace-day", tags=["Meal Plan"])
async def replace_day(
    meal_plan_request: MealPlanRequest,
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    try:
        # Extract data from request
        user_id = meal_plan_request.user_id
        day_of_week = meal_plan_request.day_of_week
        calories_target = meal_plan_request.calories_target
        protein_target = meal_plan_request.protein_target
        fat_target = meal_plan_request.fat_target
        carbs_target = meal_plan_request.carbs_target
        use_ai = meal_plan_request.use_ai
        preferences = meal_plan_request.preferences or []
        allergies = meal_plan_request.allergies or []
        cuisine_style = meal_plan_request.cuisine_style
        diet_restrictions = meal_plan_request.diet_restrictions or []
        diet_preference = meal_plan_request.diet_preference
        health_conditions = meal_plan_request.health_conditions or []
        fiber_target = meal_plan_request.fiber_target
        sugar_target = meal_plan_request.sugar_target
        sodium_target = meal_plan_request.sodium_target
        
        # Kiểm tra day_of_week
        if not day_of_week:
            raise HTTPException(status_code=400, detail="day_of_week là trường bắt buộc")
            
        # Create user_data dictionary with all relevant health information
        user_data = {
            "allergies": allergies,
            "diet_restrictions": diet_restrictions,
            "diet_preference": diet_preference,
            "health_conditions": health_conditions,
            "fiber_target": fiber_target,
            "sugar_target": sugar_target,
            "sodium_target": sodium_target
        }
        
        # Lấy kế hoạch hiện tại của người dùng
        current_plan = await get_current_meal_plan(user_id, user)
        if not current_plan:
            raise HTTPException(
                status_code=404, 
                detail=f"Không tìm thấy kế hoạch bữa ăn cho người dùng {user_id}"
            )
        
        # Tạo đối tượng ReplaceDayRequest
        from models import ReplaceDayRequest
        replace_request = ReplaceDayRequest(
            day_of_week=day_of_week,
            meal_type="all",  # Thay thế cả ngày nên meal_type là "all"
            calories_target=calories_target,
            protein_target=protein_target,
            fat_target=fat_target,
            carbs_target=carbs_target
        )
        
        # Gọi service để thay thế kế hoạch cả ngày
        import services
        try:
            new_day_plan = services.replace_day_meal_plan(
                current_weekly_plan=current_plan,
                replace_request=replace_request,
                preferences=preferences,
                allergies=allergies,
                cuisine_style=cuisine_style,
                use_ai=use_ai,
                user_data=user_data
            )
        except Exception as service_error:
            print(f"❌ Error in services.replace_day_meal_plan: {str(service_error)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Lỗi khi thay thế kế hoạch ngày: {str(service_error)}"
            )
        
        # Kiểm tra xem ngày cần thay thế có tồn tại trong kế hoạch không
        day_found = False
        for i, day in enumerate(current_plan.days):
            if day.day_of_week == day_of_week:
                current_plan.days[i] = new_day_plan
                day_found = True
                break
                
        if not day_found:
            raise HTTPException(
                status_code=400, 
                detail=f"Ngày '{day_of_week}' không có trong kế hoạch"
            )
        
        # Cập nhật kế hoạch trong Firebase
        from services.firestore_service import firestore_service
        try:
            # Chuyển đổi sang dict để gửi đến Firestore
            plan_dict = current_plan.dict()
            # Đảm bảo preparation luôn là list trước khi lưu
            result = firestore_service.save_meal_plan(user_id, plan_dict)
        
            if not result:
                raise HTTPException(
                    status_code=500, 
                    detail="Không thể lưu kế hoạch vào Firestore"
                )
        except Exception as firestore_error:
            print(f"❌ Error saving to Firestore: {str(firestore_error)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Lỗi khi lưu vào Firestore: {str(firestore_error)}"
            )
            
        # Trả về kết quả thành công
        return {
            "message": f"Đã thay thế kế hoạch cho ngày {day_of_week} thành công",
            "day_meal_plan": new_day_plan.dict()  # Chuyển đổi Pydantic model thành dict để tránh lỗi định dạng
        }
    
    except Exception as e:
        # Hiển thị chi tiết lỗi trong log để debug
        import traceback
        print(f"❌ Error in replace_day: {str(e)}")
        traceback.print_exc()
        
        # Handle exceptions
        raise HTTPException(
            status_code=500,
            detail=f"Error replacing day: {str(e)}"
        )

# Test endpoint để kiểm tra authentication
@app.post("/api/test-auth", tags=["Test"])
async def test_auth(
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    """Test endpoint để kiểm tra authentication"""
    try:
        print(f"🔍 Test auth - User: {user.uid if user else 'Anonymous'}")
        return {
            "authenticated": user is not None,
            "user_id": user.uid if user else None,
            "message": "Authentication test successful"
        }
    except Exception as e:
        print(f"❌ Error in test_auth: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test auth error: {str(e)}")

# Cập nhật endpoint thay thế một bữa ăn cụ thể
@app.post("/api/meal-plan/replace-meal", tags=["Meal Plan"])
async def replace_meal(
    meal_plan_request: MealPlanRequest,
    user: Optional[TokenPayload] = Depends(get_optional_current_user)
):
    try:
        print(f"🔄 Replace meal request received")
        print(f"📋 User: {user.uid if user else 'Anonymous'}")
        print(f"📋 Request data: {meal_plan_request.model_dump()}")
        # Extract data from request
        user_id = meal_plan_request.user_id
        day_of_week = meal_plan_request.day_of_week
        meal_type = meal_plan_request.meal_type
        calories_target = meal_plan_request.calories_target
        protein_target = meal_plan_request.protein_target
        fat_target = meal_plan_request.fat_target
        carbs_target = meal_plan_request.carbs_target
        use_ai = meal_plan_request.use_ai
        preferences = meal_plan_request.preferences or []
        allergies = meal_plan_request.allergies or []
        cuisine_style = meal_plan_request.cuisine_style
        diet_restrictions = meal_plan_request.diet_restrictions or []
        diet_preference = meal_plan_request.diet_preference
        health_conditions = meal_plan_request.health_conditions or []
        fiber_target = meal_plan_request.fiber_target
        sugar_target = meal_plan_request.sugar_target
        sodium_target = meal_plan_request.sodium_target
        
        # Create user_data dictionary with all relevant health information
        user_data = {
            "allergies": allergies,
            "diet_restrictions": diet_restrictions,
            "diet_preference": diet_preference,
            "health_conditions": health_conditions,
            "fiber_target": fiber_target,
            "sugar_target": sugar_target,
            "sodium_target": sodium_target
        }
        
        # Generate new meal
        new_meals = groq_service.generate_meal_suggestions(
            calories_target=calories_target,
            protein_target=protein_target,
            fat_target=fat_target,
            carbs_target=carbs_target,
            meal_type=meal_type,
            preferences=preferences,
            allergies=allergies,
            cuisine_style=cuisine_style,
            use_ai=use_ai,
            user_data=user_data
        )

        print(f"✅ Generated {len(new_meals) if new_meals else 0} new meals")

        # 🔥 QUAN TRỌNG: Lưu meal plan vào Firestore để Flutter có thể lấy được
        try:
            from services.firestore_service import firestore_service

            print(f"🔄 Đang lưu meal plan vào Firestore cho user {user_id}...")

            # Lấy meal plan hiện tại từ Firestore
            from storage_manager import storage_manager
            meal_plan = storage_manager.load_meal_plan(user_id)

            if meal_plan:
                print(f"✅ Tìm thấy meal plan, đang cập nhật {meal_type} cho {day_of_week}")

                # Tìm ngày cần thay đổi và cập nhật
                for i, day in enumerate(meal_plan.days):
                    if day.day_of_week == day_of_week:
                        # Tạo meal object từ new_meals
                        if new_meals and len(new_meals) > 0:
                            from models import Meal, Dish

                            # Convert new_meals thành Meal object
                            dishes = []
                            for meal_data in new_meals:
                                dish = Dish(
                                    name=meal_data.get('name', ''),
                                    description=meal_data.get('description', ''),
                                    ingredients=meal_data.get('ingredients', []),
                                    preparation=meal_data.get('preparation', []),
                                    nutrition=meal_data.get('nutrition', {}),
                                    preparation_time=meal_data.get('preparation_time', ''),
                                    health_benefits=meal_data.get('health_benefits', '')
                                )
                                dishes.append(dish)

                            # Tính toán nutrition cho meal
                            from utils import calculate_meal_nutrition
                            meal_nutrition = calculate_meal_nutrition(dishes)

                            new_meal = Meal(dishes=dishes, nutrition=meal_nutrition)

                            # Cập nhật bữa ăn
                            if meal_type.lower() == "breakfast" or meal_type.lower() == "bữa sáng":
                                meal_plan.days[i].breakfast = new_meal
                            elif meal_type.lower() == "lunch" or meal_type.lower() == "bữa trưa":
                                meal_plan.days[i].lunch = new_meal
                            elif meal_type.lower() == "dinner" or meal_type.lower() == "bữa tối":
                                meal_plan.days[i].dinner = new_meal

                            # Cập nhật tổng dinh dưỡng của ngày
                            from utils import calculate_day_nutrition
                            meal_plan.days[i].nutrition = calculate_day_nutrition(
                                meal_plan.days[i].breakfast,
                                meal_plan.days[i].lunch,
                                meal_plan.days[i].dinner
                            )

                            print(f"✅ Đã cập nhật {meal_type} cho {day_of_week}")
                        break

                # Lưu vào local storage
                storage_manager.save_meal_plan(meal_plan, user_id)
                print(f"✅ Đã lưu meal plan vào local storage")

                # Convert meal_plan thành dict để lưu vào Firestore
                def convert_to_dict(obj):
                    """Recursively convert Pydantic models to dict"""
                    if hasattr(obj, 'model_dump'):
                        # Pydantic v2
                        return obj.model_dump()
                    elif hasattr(obj, 'dict'):
                        # Pydantic v1
                        return obj.dict()
                    elif hasattr(obj, '__dict__'):
                        # Regular object
                        result = {}
                        for key, value in obj.__dict__.items():
                            if isinstance(value, list):
                                result[key] = [convert_to_dict(item) for item in value]
                            elif hasattr(value, '__dict__') or hasattr(value, 'model_dump') or hasattr(value, 'dict'):
                                result[key] = convert_to_dict(value)
                            else:
                                result[key] = value
                        return result
                    else:
                        return obj

                meal_plan_dict = convert_to_dict(meal_plan)
                print(f"✅ Đã convert meal plan thành dict")

                # Lưu vào Firestore
                success = firestore_service.save_meal_plan(user_id, meal_plan_dict)
                if success:
                    print(f"✅ Đã lưu meal plan vào Firestore cho user {user_id}")
                else:
                    print(f"❌ Lỗi lưu meal plan vào Firestore cho user {user_id}")
            else:
                print(f"⚠️ Không tìm thấy meal plan cho user {user_id}")

        except Exception as e:
            print(f"❌ Exception khi lưu meal plan: {e}")
            import traceback
            traceback.print_exc()

        # Return the generated meals
        return {
            "message": f"Successfully replaced {meal_type} on {day_of_week}",
            "user_id": user_id,
            "day_of_week": day_of_week,
            "meal_type": meal_type,
            "new_meals": new_meals,
            "success": True
        }
    
    except HTTPException as he:
        # Re-raise HTTP exceptions (like 403, 401, etc.)
        print(f"❌ HTTP Exception in replace_meal: {he.status_code} - {he.detail}")
        raise he
    except Exception as e:
        # Handle other exceptions
        print(f"❌ Unexpected error in replace_meal: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error replacing meal: {str(e)}"
        )

# Thêm xử lý cho OTP hết hạn trong endpoint verify_phone_number (nếu có)
@app.post("/verify-phone-number", tags=["Authentication"])
async def verify_phone_number(
    phone_number: str = Body(..., embed=True),
    resend: bool = Body(False, embed=True)
):
    try:
        # Gọi dịch vụ xác thực số điện thoại
        # Tăng thời gian chờ timeout
        await auth_service.verify_phone_number(
            phone_number,
            timeout=Duration(seconds=120),  # Tăng timeout lên 120 giây
            resend=resend
        )
        
        return {"success": True, "message": "Mã xác thực đã được gửi"}
    except Exception as e:
        if "expired" in str(e).lower():
            # Xử lý trường hợp OTP hết hạn
            return JSONResponse(
                status_code=410,  # Gone - Mã đã hết hạn
                content={
                    "success": False,
                    "error_code": "otp_expired",
                    "message": "Mã xác thực đã hết hạn. Vui lòng gửi lại mã mới.",
                    "should_resend": True
                }
            )
        
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi gửi mã xác thực: {str(e)}"
        )

# YouTube functionality removed

# YouTube enhance dishes functionality removed

# Video cache functionality removed

# All video cache endpoints removed

# 🔧 FIX: Register chat endpoint từ chat_endpoint.py để sử dụng logic tối ưu hóa
try:
    import chat_endpoint
    # Register routes từ chat_endpoint
    app.mount("/chat-optimized", chat_endpoint.app)
    print("✅ Đã mount chat_endpoint tại /chat-optimized - sử dụng logic tối ưu hóa")
    print("💡 Sử dụng /chat-optimized thay vì /chat để có logic sửa lỗi")
except ImportError as e:
    print(f"⚠️ Không thể import chat_endpoint: {e}")
    print("💡 Sử dụng chat endpoint trong main.py")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)