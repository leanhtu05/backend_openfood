from fastapi import APIRouter, Request, Depends, HTTPException, Query, Form
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse, Response
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Optional, Any
import os
from datetime import datetime, timedelta
import json
import csv
import io
import secrets
import time
try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils.dataframe import dataframe_to_rows
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False

try:
    from docx import Document
    from docx.shared import Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    WORD_AVAILABLE = True
except ImportError:
    WORD_AVAILABLE = False

# Temporary tokens for download (in-memory storage)
download_tokens = {}

# Import services
from services.firestore_service import firestore_service
from middleware.auth import (
    authenticate_admin,
    create_admin_session,
    get_current_admin,
    delete_admin_session,
    require_admin_auth
)
from auth_utils import get_current_user, TokenPayload

router = APIRouter(prefix="/admin", tags=["Admin"])

# ==================== AUTHENTICATION ROUTES ====================

@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request, error: str = None, success: str = None):
    """Hiển thị trang đăng nhập admin"""
    # Nếu đã đăng nhập rồi thì redirect về dashboard
    if get_current_admin(request):
        return RedirectResponse(url="/admin/", status_code=302)

    templates = get_templates()
    return templates.TemplateResponse("admin/login.html", {
        "request": request,
        "error": error,
        "success": success
    })

@router.get("/fast-login", response_class=HTMLResponse)
async def admin_fast_login_page(
    request: Request,
    error: str = None,
    success: str = None,
    templates: Jinja2Templates = Depends(get_templates)
):
    """🚀 Trang đăng nhập admin tối ưu hóa"""
    # Nếu đã đăng nhập rồi thì redirect về fast dashboard
    if get_current_admin(request):
        return RedirectResponse(url="/admin/fast-dashboard", status_code=302)

    return templates.TemplateResponse("admin/fast_login.html", {
        "request": request,
        "error": error,
        "success": success
    })

@router.post("/login")
async def admin_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Xử lý đăng nhập admin"""
    try:
        print(f"[AUTH] Admin login attempt: {username}")

        if authenticate_admin(username, password):
            # Tạo session
            session_token = create_admin_session(username)
            print(f"[AUTH] Admin login successful: {username}")

            # 🚀 Redirect về fast dashboard với session cookie
            response = RedirectResponse(url="/admin/fast-dashboard", status_code=302)
            response.set_cookie(
                key="admin_session",
                value=session_token,
                max_age=86400,  # 24 hours
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite="lax"
            )
            return response
        else:
            print(f"[AUTH] Admin login failed: {username}")
            return RedirectResponse(
                url="/admin/fast-login?error=Tên đăng nhập hoặc mật khẩu không đúng",
                status_code=302
            )
    except Exception as e:
        print(f"[AUTH] Admin login error: {str(e)}")
        return RedirectResponse(
            url="/admin/fast-login?error=Có lỗi xảy ra khi đăng nhập",
            status_code=302
        )

@router.post("/fast-login")
async def admin_fast_login(request: Request, username: str = Form(...), password: str = Form(...)):
    """🚀 Xử lý đăng nhập admin tối ưu hóa"""
    try:
        print(f"[FAST-AUTH] Admin login attempt: {username}")

        if authenticate_admin(username, password):
            # Tạo session
            session_token = create_admin_session(username)
            print(f"[FAST-AUTH] Admin login successful: {username}")

            # Redirect về fast dashboard với session cookie
            response = RedirectResponse(url="/admin/fast-dashboard", status_code=302)
            response.set_cookie(
                key="admin_session",
                value=session_token,
                max_age=86400,  # 24 hours
                httponly=True,
                secure=False,  # Set to True in production with HTTPS
                samesite="lax"
            )
            return response
        else:
            print(f"[FAST-AUTH] Admin login failed: {username}")
            return RedirectResponse(
                url="/admin/fast-login?error=Tên đăng nhập hoặc mật khẩu không đúng",
                status_code=302
            )
    except Exception as e:
        print(f"[FAST-AUTH] Admin login error: {str(e)}")
        return RedirectResponse(
            url="/admin/fast-login?error=Có lỗi xảy ra khi đăng nhập",
            status_code=302
        )

@router.get("/logout")
async def admin_logout(request: Request):
    """Đăng xuất admin"""
    session_token = request.cookies.get("admin_session")
    if session_token:
        delete_admin_session(session_token)

    response = RedirectResponse(url="/admin/login?success=Đã đăng xuất thành công", status_code=302)
    response.delete_cookie("admin_session")
    return response

# ==================== ADMIN PAGES ====================

# Template instance
def get_templates():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# Import food_items from openfood_router (fallback)
try:
    from routers.openfood_router import food_items as fallback_food_items
except ImportError:
    fallback_food_items = []

def get_foods_data():
    """Lấy dữ liệu foods từ Firebase, fallback về dữ liệu mẫu nếu cần"""
    try:
        # Thử lấy từ Firebase trước
        foods = firestore_service.get_all_foods()
        if foods:
            return foods
        else:
            # Fallback về dữ liệu mẫu
            return fallback_food_items
    except Exception as e:
        print(f"Error getting foods from Firebase: {str(e)}")
        # Fallback về dữ liệu mẫu
        return fallback_food_items

def get_system_stats():
    """Lấy thống kê tổng quan của hệ thống"""
    try:
        # Thống kê món ăn từ Firebase
        foods_data = get_foods_data()
        total_foods = len(foods_data)
        
        # Thống kê người dùng (từ Firestore)
        try:
            users = firestore_service.get_all_users()
            active_users = len([u for u in users if u.get('last_login')])
        except:
            active_users = 0
        
        # Thống kê meal plans
        try:
            meal_plans = firestore_service.get_all_meal_plans()
            total_meal_plans = len(meal_plans)
        except:
            total_meal_plans = 0
        
        # API calls hôm nay (giả lập)
        api_calls_today = 150  # Có thể implement tracking thực tế
        
        return {
            "total_foods": total_foods,
            "active_users": active_users,
            "total_meal_plans": total_meal_plans,
            "api_calls_today": api_calls_today
        }
    except Exception as e:
        print(f"Error getting system stats: {str(e)}")
        return {
            "total_foods": 0,
            "active_users": 0,
            "total_meal_plans": 0,
            "api_calls_today": 0
        }

def get_recent_activities():
    """Lấy hoạt động gần đây từ Firebase"""
    try:
        activities = []

        # Lấy meal plans gần đây
        recent_meal_plans = firestore_service.get_all_meal_plans()
        for plan in recent_meal_plans[:3]:  # Lấy 3 meal plans gần nhất
            activities.append({
                "action": "Tạo meal plan",
                "description": f"Kế hoạch bữa ăn cho user {plan.get('user_id', 'Unknown')[:8]}...",
                "timestamp": plan.get('created_at', 'Không rõ')
            })

        # Lấy người dùng mới
        recent_users = firestore_service.get_all_users()
        for user in recent_users[:2]:  # Lấy 2 users gần nhất
            activities.append({
                "action": "Người dùng đăng ký",
                "description": f"Người dùng mới: {user.get('email', 'Unknown')}",
                "timestamp": user.get('created_at', 'Không rõ')
            })

        # Sắp xếp theo thời gian (nếu có)
        return activities[:5]  # Trả về 5 hoạt động gần nhất

    except Exception as e:
        print(f"Error getting recent activities: {str(e)}")
        # Fallback to mock data
        return [
            {
                "action": "Hệ thống khởi động",
                "description": "Server đã khởi động thành công",
                "timestamp": "Vừa xong"
            }
        ]

def get_recent_foods():
    """Lấy món ăn được tạo gần đây từ Firebase"""
    try:
        # Lấy dữ liệu foods từ Firebase
        foods_data = get_foods_data()

        # Sắp xếp theo thời gian tạo và lấy 5 món gần nhất
        sorted_foods = sorted(foods_data, key=lambda x: x.get('created_at', ''), reverse=True)

        # Format lại dữ liệu để hiển thị đẹp hơn
        formatted_foods = []
        for food in sorted_foods[:5]:
            formatted_foods.append({
                "id": food.get('id', ''),
                "name": food.get('name', 'Không rõ'),
                "nutrition": {
                    "calories": food.get('nutrition', {}).get('calories', 0)
                },
                "created_at": food.get('created_at', 'Không rõ')
            })

        return formatted_foods
    except Exception as e:
        print(f"Error getting recent foods: {str(e)}")
        return []

def get_chart_data():
    """Tạo dữ liệu cho biểu đồ"""
    # Dữ liệu hoạt động 7 ngày qua (giả lập)
    activity_labels = []
    activity_data = []
    
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        activity_labels.append(date.strftime("%d/%m"))
        activity_data.append(50 + i * 10 + (i % 3) * 20)  # Giả lập dữ liệu
    
    # Dữ liệu loại món ăn
    food_type_labels = ["Bữa sáng", "Bữa trưa", "Bữa tối", "Đồ uống", "Tráng miệng"]
    food_type_data = [25, 35, 30, 5, 5]  # Giả lập phần trăm
    
    return {
        "activity_labels": activity_labels,
        "activity_data": activity_data,
        "food_type_labels": food_type_labels,
        "food_type_data": food_type_data
    }

def get_system_status():
    """Kiểm tra trạng thái hệ thống"""
    try:
        # Kiểm tra AI service
        from groq_integration import groq_service
        ai_available = groq_service.available
        ai_type = "LLaMA 3 (Groq)" if ai_available else None
    except:
        ai_available = False
        ai_type = None
    
    # Kiểm tra Firebase
    try:
        firebase_connected = firestore_service.check_connection()
    except:
        firebase_connected = False
    
    return {
        "ai_available": ai_available,
        "ai_type": ai_type,
        "firebase_connected": firebase_connected
    }

@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates)
):
    """Trang dashboard admin"""
    # Kiểm tra xác thực admin
    admin_username = get_current_admin(request)
    if not admin_username:
        return RedirectResponse(url="/admin/login", status_code=302)
    try:
        # Lấy dữ liệu thống kê
        stats = get_system_stats()
        recent_activities = get_recent_activities()
        recent_foods = get_recent_foods()
        chart_data = get_chart_data()
        system_status = get_system_status()
        
        return templates.TemplateResponse("admin/dashboard.html", {
            "request": request,
            "stats": stats,
            "recent_activities": recent_activities,
            "recent_foods": recent_foods,
            "activity_chart_labels": chart_data["activity_labels"],
            "activity_chart_data": chart_data["activity_data"],
            "food_type_labels": chart_data["food_type_labels"],
            "food_type_data": chart_data["food_type_data"],
            "system_status": system_status
        })
    except Exception as e:
        print(f"Error in admin dashboard: {str(e)}")
        # Trả về trang với dữ liệu mặc định
        return templates.TemplateResponse("admin/dashboard.html", {
            "request": request,
            "stats": {"total_foods": 0, "active_users": 0, "total_meal_plans": 0, "api_calls_today": 0},
            "recent_activities": [],
            "recent_foods": [],
            "activity_chart_labels": [],
            "activity_chart_data": [],
            "food_type_labels": [],
            "food_type_data": [],
            "system_status": {"ai_available": False, "ai_type": None, "firebase_connected": False}
        })

@router.get("/fast-dashboard", response_class=HTMLResponse)
async def admin_fast_dashboard(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates)
):
    """🚀 Trang dashboard admin tối ưu hóa"""
    # Kiểm tra xác thực admin
    admin_username = get_current_admin(request)
    if not admin_username:
        return RedirectResponse(url="/admin/fast-login", status_code=302)

    try:
        # Lấy dữ liệu thống kê (optimized - ít data hơn)
        stats = get_system_stats()
        recent_activities = get_recent_activities()[:5]  # Chỉ lấy 5 activities gần nhất
        recent_foods = get_recent_foods()[:5]  # Chỉ lấy 5 foods gần nhất
        system_status = get_system_status()

        return templates.TemplateResponse("admin/fast_dashboard.html", {
            "request": request,
            "stats": stats,
            "recent_activities": recent_activities,
            "recent_foods": recent_foods,
            "system_status": system_status
        })
    except Exception as e:
        print(f"Error in fast admin dashboard: {str(e)}")
        # Trả về trang với dữ liệu mặc định
        return templates.TemplateResponse("admin/fast_dashboard.html", {
            "request": request,
            "stats": {"total_foods": 0, "active_users": 0, "total_meal_plans": 0, "api_calls_today": 0},
            "recent_activities": [],
            "recent_foods": [],
            "system_status": {"ai_available": False, "ai_type": None, "firebase_connected": False}
        })

@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    templates: Jinja2Templates = Depends(get_templates)
):
    """Trang quản lý người dùng"""
    # Kiểm tra xác thực admin
    admin_username = get_current_admin(request)
    if not admin_username:
        return RedirectResponse(url="/admin/login", status_code=302)
    try:
        print(f"[ADMIN] Getting all users from Firebase...")
        # Lấy danh sách người dùng từ Firestore
        users = firestore_service.get_all_users()
        print(f"[ADMIN] Retrieved {len(users)} users from Firebase")

        # Debug: In ra một vài user đầu tiên
        if users:
            print(f"[ADMIN] First user sample: {users[0] if users else 'None'}")
            print(f"[ADMIN] User type: {type(users[0]) if users else 'None'}")
        else:
            print(f"[ADMIN] No users found!")
        
        # Lọc theo từ khóa tìm kiếm
        if search:
            search = search.lower()
            users = [
                user for user in users 
                if search in user.get('email', '').lower() or 
                   search in user.get('display_name', '').lower()
            ]
        
        # Phân trang
        total_users = len(users)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        users_page = users[start_idx:end_idx]
        
        # Tính toán thông tin phân trang
        total_pages = (total_users + limit - 1) // limit
        has_prev = page > 1
        has_next = page < total_pages
        
        return templates.TemplateResponse("admin/users.html", {
            "request": request,
            "users": users_page,
            "current_page": page,
            "total_pages": total_pages,
            "total_users": total_users,
            "has_prev": has_prev,
            "has_next": has_next,
            "search": search or ""
        })
    except Exception as e:
        print(f"Error in admin users: {str(e)}")
        return templates.TemplateResponse("admin/users.html", {
            "request": request,
            "users": [],
            "current_page": 1,
            "total_pages": 1,
            "total_users": 0,
            "has_prev": False,
            "has_next": False,
            "search": search or "",
            "error": f"Lỗi khi tải dữ liệu người dùng: {str(e)}"
        })

@router.get("/meal-plans", response_class=HTMLResponse)
async def admin_meal_plans(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = None,
    templates: Jinja2Templates = Depends(get_templates)
):
    """Trang quản lý kế hoạch bữa ăn"""
    try:
        # Lấy danh sách meal plans
        if user_id:
            meal_plans = firestore_service.get_user_meal_plans(user_id)
        else:
            meal_plans = firestore_service.get_all_meal_plans()
        
        # Phân trang
        total_plans = len(meal_plans)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        plans_page = meal_plans[start_idx:end_idx]
        
        # Tính toán thông tin phân trang
        total_pages = (total_plans + limit - 1) // limit
        has_prev = page > 1
        has_next = page < total_pages
        
        return templates.TemplateResponse("admin/meal_plans.html", {
            "request": request,
            "meal_plans": plans_page,
            "current_page": page,
            "total_pages": total_pages,
            "total_plans": total_plans,
            "has_prev": has_prev,
            "has_next": has_next,
            "user_id": user_id or ""
        })
    except Exception as e:
        print(f"Error in admin meal plans: {str(e)}")
        return templates.TemplateResponse("admin/meal_plans.html", {
            "request": request,
            "meal_plans": [],
            "current_page": 1,
            "total_pages": 1,
            "total_plans": 0,
            "has_prev": False,
            "has_next": False,
            "user_id": user_id or "",
            "error": f"Lỗi khi tải dữ liệu kế hoạch bữa ăn: {str(e)}"
        })

@router.get("/foods", response_class=HTMLResponse)
async def admin_foods(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    templates: Jinja2Templates = Depends(get_templates)
):
    """Trang quản lý món ăn"""
    try:
        # Lấy danh sách foods từ Firebase
        foods_data = get_foods_data()

        # Lọc theo từ khóa tìm kiếm
        if search:
            search = search.lower()
            foods_data = [
                food for food in foods_data
                if search in food.get('name', '').lower() or
                   search in food.get('description', '').lower()
            ]

        # Phân trang
        total_foods = len(foods_data)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        foods_page = foods_data[start_idx:end_idx]

        # Tính toán thông tin phân trang
        total_pages = (total_foods + limit - 1) // limit
        has_prev = page > 1
        has_next = page < total_pages

        return templates.TemplateResponse("admin/foods.html", {
            "request": request,
            "foods": foods_page,
            "current_page": page,
            "total_pages": total_pages,
            "total_foods": total_foods,
            "has_prev": has_prev,
            "has_next": has_next,
            "search": search or ""
        })
    except Exception as e:
        print(f"Error in admin foods: {str(e)}")
        return templates.TemplateResponse("admin/foods.html", {
            "request": request,
            "foods": [],
            "current_page": 1,
            "total_pages": 1,
            "total_foods": 0,
            "has_prev": False,
            "has_next": False,
            "search": search or "",
            "error": f"Lỗi khi tải dữ liệu món ăn: {str(e)}"
        })

@router.get("/reports", response_class=HTMLResponse)
async def admin_reports(
    request: Request,
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    templates: Jinja2Templates = Depends(get_templates)
):
    """Trang báo cáo và thống kê"""
    try:
        # Thiết lập ngày mặc định nếu không có
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # Lấy dữ liệu metrics
        metrics = get_report_metrics(start_date, end_date)

        # Lấy dữ liệu biểu đồ
        chart_data = get_report_chart_data(start_date, end_date)

        # Lấy top users
        top_users = get_top_active_users()

        # Lấy lỗi gần đây
        recent_errors = get_recent_errors()

        return templates.TemplateResponse("admin/reports.html", {
            "request": request,
            "start_date": start_date,
            "end_date": end_date,
            "metrics": metrics,
            "activity_labels": chart_data["activity_labels"],
            "activity_data": chart_data["activity_data"],
            "api_calls_data": chart_data["api_calls_data"],
            "device_labels": chart_data["device_labels"],
            "device_data": chart_data["device_data"],
            "popular_foods_labels": chart_data["popular_foods_labels"],
            "popular_foods_data": chart_data["popular_foods_data"],
            "feature_labels": chart_data["feature_labels"],
            "feature_data": chart_data["feature_data"],
            "top_users": top_users,
            "recent_errors": recent_errors
        })
    except Exception as e:
        print(f"Error in admin reports: {str(e)}")
        # Trả về trang với dữ liệu mặc định
        return templates.TemplateResponse("admin/reports.html", {
            "request": request,
            "start_date": start_date or datetime.now().strftime("%Y-%m-%d"),
            "end_date": end_date or datetime.now().strftime("%Y-%m-%d"),
            "metrics": {},
            "activity_labels": [],
            "activity_data": [],
            "api_calls_data": [],
            "device_labels": [],
            "device_data": [],
            "popular_foods_labels": [],
            "popular_foods_data": [],
            "feature_labels": [],
            "feature_data": [],
            "top_users": [],
            "recent_errors": [],
            "error": f"Lỗi khi tải báo cáo: {str(e)}"
        })

def get_report_metrics(start_date: str, end_date: str):
    """Lấy các metrics cho báo cáo từ Firebase"""
    try:
        # Lấy dữ liệu thật từ Firebase
        users = firestore_service.get_all_users()
        meal_plans = firestore_service.get_all_meal_plans()

        # Tính toán metrics thật
        total_users = len(users)
        total_meal_plans = len(meal_plans)

        # Đếm users mới trong khoảng thời gian
        new_users = 0
        for user in users:
            created_at = user.get('created_at')
            if created_at:
                # Chuyển đổi created_at thành string nếu cần
                if hasattr(created_at, 'strftime'):
                    created_at_str = created_at.strftime('%Y-%m-%d')
                else:
                    created_at_str = str(created_at)[:10]  # Lấy phần YYYY-MM-DD

                if start_date <= created_at_str <= end_date:
                    new_users += 1

        # Đếm meal plans mới trong khoảng thời gian
        new_meal_plans = 0
        for plan in meal_plans:
            created_at = plan.get('created_at')
            if created_at:
                # Chuyển đổi created_at thành string nếu cần
                if hasattr(created_at, 'strftime'):
                    created_at_str = created_at.strftime('%Y-%m-%d')
                else:
                    created_at_str = str(created_at)[:10]  # Lấy phần YYYY-MM-DD

                if start_date <= created_at_str <= end_date:
                    new_meal_plans += 1

        # Tính toán tỷ lệ tăng trưởng (giả định)
        users_growth = (new_users / max(total_users - new_users, 1)) * 100 if total_users > 0 else 0
        meal_plans_growth = (new_meal_plans / max(total_meal_plans - new_meal_plans, 1)) * 100 if total_meal_plans > 0 else 0

        return {
            "total_api_calls": total_users * 50 + total_meal_plans * 20,  # Ước tính
            "api_calls_growth": min(users_growth + meal_plans_growth, 50),  # Giới hạn 50%
            "new_users": new_users,
            "new_users_growth": users_growth,
            "meal_plans_created": new_meal_plans,
            "meal_plans_growth": meal_plans_growth,
            "activity_rate": min((total_users * 0.7), 100),  # Giả định 70% users active
            "activity_rate_change": min(users_growth * 0.5, 10)  # Thay đổi activity dựa trên user growth
        }
    except Exception as e:
        print(f"Error getting report metrics: {str(e)}")
        return {
            "total_api_calls": 0,
            "api_calls_growth": 0,
            "new_users": 0,
            "new_users_growth": 0,
            "meal_plans_created": 0,
            "meal_plans_growth": 0,
            "activity_rate": 0,
            "activity_rate_change": 0
        }

def get_report_chart_data(start_date: str, end_date: str):
    """Lấy dữ liệu cho các biểu đồ từ Firebase"""
    try:
        # Lấy dữ liệu thật từ Firebase
        users = firestore_service.get_all_users()
        meal_plans = firestore_service.get_all_meal_plans()

        # Tạo dữ liệu cho biểu đồ hoạt động theo ngày
        days = []
        activity_data = []
        api_calls_data = []

        # Tạo dữ liệu cho 30 ngày gần đây
        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            days.append(date.strftime("%d/%m"))

            # Đếm hoạt động trong ngày (giả lập dựa trên dữ liệu thật)
            target_date = date.strftime("%Y-%m-%d")

            # Đếm users được tạo trong ngày
            day_users = 0
            for u in users:
                created_at = u.get('created_at')
                if created_at:
                    if hasattr(created_at, 'strftime'):
                        created_date = created_at.strftime('%Y-%m-%d')
                    else:
                        created_date = str(created_at)[:10]
                    if created_date == target_date:
                        day_users += 1

            # Đếm meal plans được tạo trong ngày
            day_plans = 0
            for p in meal_plans:
                created_at = p.get('created_at')
                if created_at:
                    if hasattr(created_at, 'strftime'):
                        created_date = created_at.strftime('%Y-%m-%d')
                    else:
                        created_date = str(created_at)[:10]
                    if created_date == target_date:
                        day_plans += 1

            day_activity = day_users * 5
            day_api_calls = day_plans * 10

            activity_data.append(max(day_activity, 10 + i % 20))  # Đảm bảo có dữ liệu hiển thị
            api_calls_data.append(max(day_api_calls, 50 + i % 30))

        # Thống kê món ăn phổ biến từ Firebase
        foods_data = get_foods_data()
        popular_foods = {}
        for food in foods_data[:20]:  # Lấy 20 món đầu tiên
            name = food.get('name', 'Unknown')
            # Giả lập popularity dựa trên calories (món có calories cao thường được quan tâm)
            calories = food.get('nutrition', {}).get('calories', 0)
            popularity = min(calories / 10, 50)  # Chuyển đổi calories thành popularity score
            popular_foods[name] = popularity

        # Sắp xếp và lấy top 5
        sorted_foods = sorted(popular_foods.items(), key=lambda x: x[1], reverse=True)[:5]
        popular_foods_labels = [item[0] for item in sorted_foods]
        popular_foods_data = [int(item[1]) for item in sorted_foods]

        return {
            "activity_labels": days,
            "activity_data": activity_data,
            "api_calls_data": api_calls_data,
            "device_labels": ["Mobile", "Desktop", "Tablet"],
            "device_data": [65, 25, 10],  # Giả lập device usage
            "popular_foods_labels": popular_foods_labels,
            "popular_foods_data": popular_foods_data,
            "feature_labels": ["Tạo meal plan", "Tìm kiếm thực phẩm", "Chat AI", "Theo dõi dinh dưỡng", "Báo cáo"],
            "feature_data": [len(meal_plans), len(foods_data)//10, len(users)//2, len(users)//3, len(users)//5]
        }
    except Exception as e:
        print(f"Error getting chart data: {str(e)}")
        return {
            "activity_labels": [],
            "activity_data": [],
            "api_calls_data": [],
            "device_labels": [],
            "device_data": [],
            "popular_foods_labels": [],
            "popular_foods_data": [],
            "feature_labels": [],
            "feature_data": []
        }

def get_top_active_users():
    """Lấy danh sách người dùng hoạt động nhất từ Firebase"""
    try:
        # Lấy dữ liệu thật từ Firebase
        users = firestore_service.get_all_users()
        meal_plans = firestore_service.get_all_meal_plans()

        # Tính toán activity cho mỗi user
        user_activities = {}

        # Đếm meal plans cho mỗi user
        for plan in meal_plans:
            user_id = plan.get('user_id', '')
            if user_id:
                if user_id not in user_activities:
                    user_activities[user_id] = {'meal_plans_count': 0, 'activity_count': 0}
                user_activities[user_id]['meal_plans_count'] += 1
                user_activities[user_id]['activity_count'] += 5  # Mỗi meal plan = 5 điểm activity

        # Tạo danh sách top users
        top_users = []
        for user in users[:10]:  # Lấy tối đa 10 users
            user_id = user.get('uid', user.get('id', ''))
            activity_data = user_activities.get(user_id, {'meal_plans_count': 0, 'activity_count': 0})

            # Tính thêm activity từ thông tin user
            if user.get('last_login'):
                activity_data['activity_count'] += 10
            if user.get('profile_completed'):
                activity_data['activity_count'] += 5

            top_users.append({
                "display_name": user.get('display_name', user.get('name', 'Người dùng ẩn danh')),
                "email": user.get('email', 'Không có email'),
                "photo_url": user.get('photo_url'),
                "activity_count": activity_data['activity_count'],
                "meal_plans_count": activity_data['meal_plans_count'],
                "last_activity": user.get('last_login', user.get('created_at', 'Không rõ'))
            })

        # Sắp xếp theo activity_count và lấy top 5
        top_users.sort(key=lambda x: x['activity_count'], reverse=True)
        return top_users[:5]

    except Exception as e:
        print(f"Error getting top users: {str(e)}")
        return [
            {
                "display_name": "Không có dữ liệu",
                "email": "system@openfood.com",
                "photo_url": None,
                "activity_count": 0,
                "meal_plans_count": 0,
                "last_activity": "Không rõ"
            }
        ]

def get_recent_errors():
    """Lấy danh sách lỗi gần đây"""
    try:
        # Giả lập dữ liệu lỗi
        return [
            {
                "type": "API Timeout",
                "message": "Groq API timeout khi tạo meal plan",
                "level": "warning",
                "count": 3
            },
            {
                "type": "Database Connection",
                "message": "Kết nối Firestore bị gián đoạn",
                "level": "error",
                "count": 1
            }
        ]
    except Exception as e:
        print(f"Error getting recent errors: {str(e)}")
        return []

@router.get("/settings", response_class=HTMLResponse)
async def admin_settings(
    request: Request,
    templates: Jinja2Templates = Depends(get_templates)
):
    """Trang cấu hình hệ thống"""
    try:
        # Lấy trạng thái hệ thống
        system_status = get_system_status()

        # Lấy cấu hình hiện tại
        settings = get_current_settings()

        return templates.TemplateResponse("admin/settings.html", {
            "request": request,
            "system_status": system_status,
            "settings": settings
        })
    except Exception as e:
        print(f"Error in admin settings: {str(e)}")
        return templates.TemplateResponse("admin/settings.html", {
            "request": request,
            "system_status": {
                "database_connected": False,
                "ai_service_available": False,
                "firebase_connected": False,
                "storage_available": False
            },
            "settings": {},
            "error": f"Lỗi khi tải cấu hình: {str(e)}"
        })

def get_current_settings():
    """Lấy cấu hình hiện tại của hệ thống"""
    try:
        import os

        # Lấy cấu hình từ biến môi trường và cấu hình mặc định
        settings = {
            # AI & API Settings
            "groq_api_key": "***" if os.getenv("GROQ_API_KEY") else "",
            "groq_model": "llama3-8b-8192",
            "groq_timeout": 30,
            "usda_api_key": "***" if os.getenv("USDA_API_KEY") else "",
            "usda_max_results": 10,
            "usda_cache_enabled": True,
            "rate_limit_per_minute": 60,
            "rate_limit_per_day": 1000,
            "cache_expiry_hours": 24,
            "cache_enabled": True,

            # Database Settings
            "firebase_project_id": os.getenv("FIREBASE_PROJECT_ID", ""),
            "firebase_storage_bucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
            "firebase_emulator_enabled": False,
            "connection_pool_size": 10,
            "query_timeout": 30,
            "enable_query_logging": False,

            # Security Settings
            "jwt_secret": "***" if os.getenv("JWT_SECRET") else "",
            "token_expiry_hours": 24,
            "require_email_verification": False,
            "allowed_origins": "*",
            "enable_cors": True,
            "force_https": False,

            # Performance Settings
            "max_workers": 4,
            "request_timeout": 30,
            "enable_gzip": True,
            "log_level": "INFO",
            "enable_metrics": True,
            "enable_health_check": True,

            # Notification Settings
            "smtp_host": "",
            "smtp_port": 587,
            "smtp_username": "",
            "smtp_password": "",
            "admin_email": "",
            "alert_on_errors": True,
            "alert_on_high_usage": True,
            "daily_reports": False
        }

        return settings
    except Exception as e:
        print(f"Error getting current settings: {str(e)}")
        return {}

# API endpoints for food records CRUD
@router.get("/api/foods/{food_id}")
async def get_food_api(food_id: str):
    """API để lấy thông tin một food record"""
    try:
        print(f"[API] Getting food record with ID: {food_id}")
        food = firestore_service.get_food_record(food_id)
        print(f"[API] Food record result: {food is not None}")
        if food:
            print(f"[API] Food record data keys: {list(food.keys()) if food else 'None'}")
            return {"success": True, "food": food}
        else:
            print(f"[API] Food record not found for ID: {food_id}")
            return {"success": False, "message": "Không tìm thấy food record"}
    except Exception as e:
        print(f"[API] Error getting food record: {str(e)}")
        return {"success": False, "message": f"Lỗi: {str(e)}"}

# API endpoints for meal plans CRUD
@router.get("/api/meal-plans/{plan_id}")
async def get_meal_plan_api(plan_id: str):
    """API để lấy thông tin một meal plan"""
    try:
        print(f"[API] Getting meal plan with ID: {plan_id}")
        meal_plan_dict = firestore_service.get_meal_plan_dict(plan_id)
        print(f"[API] Meal plan result: {meal_plan_dict is not None}")
        if meal_plan_dict:
            print(f"[API] Meal plan data keys: {list(meal_plan_dict.keys())}")
            return {"success": True, "meal_plan": meal_plan_dict}
        else:
            print(f"[API] Meal plan not found for ID: {plan_id}")
            return {"success": False, "message": "Không tìm thấy meal plan"}
    except Exception as e:
        print(f"[API] Error getting meal plan: {str(e)}")
        return {"success": False, "message": f"Lỗi: {str(e)}"}

@router.put("/api/meal-plans/{plan_id}")
async def update_meal_plan_api(plan_id: str, meal_plan_data: dict):
    """API để cập nhật meal plan"""
    try:
        print(f"[API] Updating meal plan with ID: {plan_id}")
        print(f"[API] Update data: {meal_plan_data}")

        # Cập nhật meal plan trong Firebase
        success = firestore_service.update_meal_plan(plan_id, meal_plan_data)

        if success:
            print(f"[API] Meal plan updated successfully")
            return {"success": True, "message": "Cập nhật meal plan thành công"}
        else:
            print(f"[API] Failed to update meal plan")
            return {"success": False, "message": "Không thể cập nhật meal plan"}
    except Exception as e:
        print(f"[API] Error updating meal plan: {str(e)}")
        return {"success": False, "message": f"Lỗi: {str(e)}"}

@router.delete("/api/meal-plans/{plan_id}")
async def delete_meal_plan_api(plan_id: str):
    """API để xóa meal plan"""
    try:
        print(f"[API] Deleting meal plan with ID: {plan_id}")

        # Xóa meal plan từ Firebase
        success = firestore_service.delete_meal_plan(plan_id)

        if success:
            print(f"[API] Meal plan deleted successfully")
            return {"success": True, "message": "Xóa meal plan thành công"}
        else:
            print(f"[API] Failed to delete meal plan")
            return {"success": False, "message": "Không thể xóa meal plan"}
    except Exception as e:
        print(f"[API] Error deleting meal plan: {str(e)}")
        return {"success": False, "message": f"Lỗi: {str(e)}"}

# API endpoints for users
@router.get("/api/users/{user_id}")
async def get_user_api(user_id: str):
    """API để lấy thông tin một user"""
    try:
        print(f"[API] Getting user with ID: {user_id}")
        user = firestore_service.get_user_by_id(user_id)
        print(f"[API] User result: {user is not None}")
        if user:
            print(f"[API] User data keys: {list(user.keys()) if isinstance(user, dict) else 'Not a dict'}")
            return {"success": True, "user": user}
        else:
            print(f"[API] User not found for ID: {user_id}")
            return {"success": False, "message": "Không tìm thấy người dùng"}
    except Exception as e:
        print(f"[API] Error getting user: {str(e)}")
        return {"success": False, "message": f"Lỗi: {str(e)}"}

@router.delete("/api/users/{user_id}")
async def delete_user_api(user_id: str, request: Request):
    """API để xóa user và tất cả dữ liệu liên quan"""
    try:
        # Kiểm tra xác thực admin
        admin_username = get_current_admin(request)
        if not admin_username:
            return {"success": False, "message": "Không có quyền truy cập"}

        print(f"[API] Admin {admin_username} deleting user: {user_id}")

        # Kiểm tra user có tồn tại không
        user = firestore_service.get_user_by_id(user_id)
        if not user:
            return {"success": False, "message": "Không tìm thấy người dùng"}

        # Xóa user và tất cả dữ liệu liên quan
        success = firestore_service.delete_user(user_id)

        if success:
            print(f"[API] Successfully deleted user: {user_id}")
            return {
                "success": True,
                "message": f"Đã xóa người dùng {user.get('name', user.get('email', user_id))} và tất cả dữ liệu liên quan"
            }
        else:
            print(f"[API] Failed to delete user: {user_id}")
            return {"success": False, "message": "Không thể xóa người dùng"}

    except Exception as e:
        print(f"[API] Error deleting user: {str(e)}")
        return {"success": False, "message": f"Lỗi: {str(e)}"}

@router.get("/api/foods/{food_id}/test")
async def test_food_api(food_id: str):
    """Test API để debug"""
    return {
        "success": True,
        "food_id": food_id,
        "message": "Test API hoạt động bình thường",
        "food": {
            "id": food_id,
            "name": "Test Food",
            "description": "Test Description",
            "mealType": "Test Meal",
            "nutrition": {
                "calories": 100,
                "protein": 10,
                "fat": 5,
                "carbs": 15
            }
        }
    }

@router.post("/api/foods")
async def create_food_api(food_data: dict):
    """API để tạo food record mới (chỉ cho demo - thực tế food_records được tạo từ app)"""
    try:
        return {"success": False, "message": "Tính năng tạo food record mới chưa được hỗ trợ. Food records được tạo từ ứng dụng mobile."}
    except Exception as e:
        return {"success": False, "message": f"Lỗi: {str(e)}"}

@router.put("/api/foods/{food_id}")
async def update_food_api(food_id: str, food_data: dict):
    """API để cập nhật food record"""
    try:
        success = firestore_service.update_food_record(food_id, food_data)
        if success:
            return {"success": True, "message": "Cập nhật food record thành công"}
        else:
            return {"success": False, "message": "Không thể cập nhật food record"}
    except Exception as e:
        return {"success": False, "message": f"Lỗi: {str(e)}"}

@router.delete("/api/foods/{food_id}")
async def delete_food_api(food_id: str):
    """API để xóa food record"""
    try:
        success = firestore_service.delete_food_record(food_id)
        if success:
            return {"success": True, "message": "Xóa food record thành công"}
        else:
            return {"success": False, "message": "Không thể xóa food record"}
    except Exception as e:
        return {"success": False, "message": f"Lỗi: {str(e)}"}

# 🚀 FAST API ENDPOINTS FOR OPTIMIZED ADMIN

@router.get("/api/quick-stats")
async def get_quick_stats(request: Request):
    """🚀 API lấy stats nhanh cho fast dashboard"""
    # Kiểm tra xác thực admin
    admin_username = get_current_admin(request)
    if not admin_username:
        return {"success": False, "message": "Unauthorized"}

    try:
        stats = get_system_stats()
        return {"success": True, "data": stats}
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@router.get("/api/quick-export")
async def quick_export(request: Request):
    """🚀 API xuất báo cáo nhanh (CSV đơn giản)"""
    # Kiểm tra xác thực admin
    admin_username = get_current_admin(request)
    if not admin_username:
        return {"success": False, "message": "Unauthorized"}

    try:
        # Tạo CSV đơn giản với dữ liệu cơ bản
        stats = get_system_stats()
        csv_content = f"""Metric,Value
Total Foods,{stats.get('total_foods', 0)}
Active Users,{stats.get('active_users', 0)}
Total Meal Plans,{stats.get('total_meal_plans', 0)}
API Calls Today,{stats.get('api_calls_today', 0)}
Export Time,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=quick_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@router.post("/api/fast-refresh")
async def fast_refresh_data(request: Request):
    """🚀 API làm mới dữ liệu nhanh"""
    # Kiểm tra xác thực admin
    admin_username = get_current_admin(request)
    if not admin_username:
        return {"success": False, "message": "Unauthorized"}

    try:
        # Clear cache nếu có
        # Lấy dữ liệu mới
        stats = get_system_stats()
        recent_activities = get_recent_activities()[:3]  # Chỉ lấy 3 activities

        return {
            "success": True,
            "data": {
                "stats": stats,
                "recent_activities": recent_activities,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

# API endpoint tạo download token
@router.post("/api/create-download-token")
async def create_download_token(request: Request):
    """Tạo token tạm thời để download báo cáo"""
    # Kiểm tra xác thực admin
    admin_username = get_current_admin(request)
    if not admin_username:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Tạo token ngẫu nhiên
    token = secrets.token_urlsafe(32)

    # Lưu token với thời gian hết hạn (5 phút)
    download_tokens[token] = {
        "admin": admin_username,
        "created_at": time.time(),
        "expires_at": time.time() + 300  # 5 phút
    }

    # Xóa các token đã hết hạn
    current_time = time.time()
    expired_tokens = [t for t, data in download_tokens.items() if data["expires_at"] < current_time]
    for expired_token in expired_tokens:
        del download_tokens[expired_token]

    return {"success": True, "token": token}

# API endpoint debug dependencies
@router.get("/api/debug/dependencies")
async def debug_dependencies(request: Request):
    """Debug endpoint để kiểm tra dependencies"""
    admin_username = get_current_admin(request)
    if not admin_username:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return {
        "excel_available": EXCEL_AVAILABLE,
        "word_available": WORD_AVAILABLE,
        "python_version": __import__('sys').version,
        "dependencies": {
            "openpyxl": "Available" if EXCEL_AVAILABLE else "Not installed",
            "python-docx": "Available" if WORD_AVAILABLE else "Not installed"
        }
    }

# API endpoint test download đơn giản
@router.get("/api/test-download")
async def test_download(request: Request):
    """Test download đơn giản"""
    admin_username = get_current_admin(request)
    if not admin_username:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Tạo file text đơn giản
    content = f"""ADMIN REPORT TEST
Admin: {admin_username}
Date: {datetime.now().isoformat()}
Status: Working!

This is a test download to verify the download functionality.
"""

    def generate_content():
        yield content

    return StreamingResponse(
        generate_content(),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"}
    )

# API endpoint test CSV
@router.get("/api/test-csv")
async def test_csv(request: Request):
    """Test CSV export đơn giản"""
    admin_username = get_current_admin(request)
    if not admin_username:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Tạo CSV đơn giản
    csv_content = f"""ADMIN REPORT TEST
Admin,{admin_username}
Date,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status,Working

Sample Data
Name,Email,Age
John Doe,john@example.com,25
Jane Smith,jane@example.com,30
Bob Johnson,bob@example.com,35
"""

    def generate_csv():
        yield csv_content

    return StreamingResponse(
        generate_csv(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=test_csv_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

# API endpoint xuất báo cáo
@router.get("/api/export/report")
async def export_report(
    request: Request,
    format: str = Query("csv", description="Format: csv, json, excel, word"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    token: Optional[str] = Query(None, description="Download token")
):
    """API để xuất báo cáo dữ liệu"""
    # Kiểm tra xác thực admin (session hoặc token)
    admin_username = get_current_admin(request)

    # Nếu không có session, kiểm tra token
    if not admin_username and token:
        if token in download_tokens:
            token_data = download_tokens[token]
            current_time = time.time()

            # Kiểm tra token còn hạn không
            if token_data["expires_at"] > current_time:
                admin_username = token_data["admin"]
                # Xóa token sau khi sử dụng (one-time use)
                del download_tokens[token]
            else:
                # Token đã hết hạn
                del download_tokens[token]
                raise HTTPException(status_code=401, detail="Token expired")
        else:
            raise HTTPException(status_code=401, detail="Invalid token")

    if not admin_username:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        # Thiết lập ngày mặc định
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        print(f"[EXPORT] Starting export for admin: {admin_username}, format: {format}")

        # Lấy dữ liệu từ Firebase với error handling
        try:
            users = firestore_service.get_all_users()
            print(f"[EXPORT] Got {len(users)} users")
        except Exception as e:
            print(f"[EXPORT] Error getting users: {e}")
            users = []

        try:
            food_records = firestore_service.get_all_food_records()
            print(f"[EXPORT] Got {len(food_records)} food records")
        except Exception as e:
            print(f"[EXPORT] Error getting food records: {e}")
            food_records = []

        try:
            meal_plans = firestore_service.get_all_meal_plans()
            print(f"[EXPORT] Got {len(meal_plans)} meal plans")
        except Exception as e:
            print(f"[EXPORT] Error getting meal plans: {e}")
            meal_plans = []

        # Tạo báo cáo tổng hợp đơn giản
        report_data = {
            "export_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "period": f"{start_date} to {end_date}",
            "admin": admin_username,
            "summary": {
                "total_users": len(users),
                "total_food_records": len(food_records),
                "total_meal_plans": len(meal_plans),
                "active_users": len([u for u in users if u.get('last_login_at')]) if users else 0,
            },
            "users": users[:10],  # Chỉ 10 users để test
            "recent_food_records": food_records[:10],  # 10 food records
            "recent_meal_plans": meal_plans[:5]  # 5 meal plans
        }

        if format.lower() == "json":
            # Xuất JSON
            json_str = json.dumps(report_data, indent=2, ensure_ascii=False, default=str)

            def generate_json():
                yield json_str

            return StreamingResponse(
                generate_json(),
                media_type="application/json",
                headers={"Content-Disposition": f"attachment; filename=admin_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
            )

        elif format.lower() == "excel" and EXCEL_AVAILABLE:
            # Xuất Excel
            wb = Workbook()

            # Xóa sheet mặc định
            wb.remove(wb.active)

            # Tạo sheet Summary
            summary_ws = wb.create_sheet("Summary")
            summary_ws.append(["ADMIN REPORT SUMMARY"])
            summary_ws.append([])
            summary_ws.append(["Export Date", report_data['export_date']])
            summary_ws.append(["Period", report_data['period']])
            summary_ws.append(["Admin", report_data['admin']])
            summary_ws.append([])

            # Thêm summary data
            summary_ws.append(["STATISTICS"])
            for key, value in report_data['summary'].items():
                summary_ws.append([key.replace('_', ' ').title(), value])

            # Format header
            for row in summary_ws.iter_rows(min_row=1, max_row=1):
                for cell in row:
                    cell.font = Font(bold=True, size=14)
                    cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                    cell.font = Font(bold=True, color="FFFFFF")

            # Tạo sheet Users
            if users:
                users_ws = wb.create_sheet("Users")
                user_headers = ['ID', 'Email', 'Name', 'Created At', 'Last Login', 'Age', 'Gender']
                users_ws.append(user_headers)

                for user in users[:100]:
                    row_data = [
                        user.get('id', ''),
                        user.get('email', ''),
                        user.get('name', ''),
                        str(user.get('created_at', '')),
                        str(user.get('last_login_at', '')),
                        user.get('age', ''),
                        user.get('gender', '')
                    ]
                    users_ws.append(row_data)

                # Format headers
                for cell in users_ws[1]:
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")

            # Tạo sheet Food Records
            if food_records:
                foods_ws = wb.create_sheet("Food Records")
                food_headers = ['ID', 'User ID', 'Description', 'Meal Type', 'Date', 'Created At']
                foods_ws.append(food_headers)

                for food in food_records[:50]:
                    row_data = [
                        food.get('id', ''),
                        food.get('user_id', ''),
                        food.get('description', ''),
                        food.get('mealType', ''),
                        str(food.get('date', '')),
                        str(food.get('created_at', ''))
                    ]
                    foods_ws.append(row_data)

                # Format headers
                for cell in foods_ws[1]:
                    cell.font = Font(bold=True)
                    cell.fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")

            # Lưu Excel file
            excel_buffer = io.BytesIO()
            wb.save(excel_buffer)
            excel_buffer.seek(0)

            def generate_excel():
                yield excel_buffer.getvalue()

            return StreamingResponse(
                generate_excel(),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment; filename=admin_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"}
            )

        elif format.lower() == "word" and WORD_AVAILABLE:
            # Xuất Word
            doc = Document()

            # Title
            title = doc.add_heading('ADMIN REPORT', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Report info
            doc.add_heading('Report Information', level=1)
            info_table = doc.add_table(rows=3, cols=2)
            info_table.style = 'Table Grid'

            info_table.cell(0, 0).text = 'Export Date'
            info_table.cell(0, 1).text = report_data['export_date']
            info_table.cell(1, 0).text = 'Period'
            info_table.cell(1, 1).text = report_data['period']
            info_table.cell(2, 0).text = 'Admin'
            info_table.cell(2, 1).text = report_data['admin']

            # Summary
            doc.add_heading('Summary Statistics', level=1)
            summary_table = doc.add_table(rows=len(report_data['summary']) + 1, cols=2)
            summary_table.style = 'Table Grid'

            # Headers
            summary_table.cell(0, 0).text = 'Metric'
            summary_table.cell(0, 1).text = 'Value'

            # Data
            for i, (key, value) in enumerate(report_data['summary'].items(), 1):
                summary_table.cell(i, 0).text = key.replace('_', ' ').title()
                summary_table.cell(i, 1).text = str(value)

            # Users section
            if users:
                doc.add_heading('Recent Users (Top 20)', level=1)
                users_table = doc.add_table(rows=min(21, len(users) + 1), cols=4)
                users_table.style = 'Table Grid'

                # Headers
                users_table.cell(0, 0).text = 'Email'
                users_table.cell(0, 1).text = 'Name'
                users_table.cell(0, 2).text = 'Created At'
                users_table.cell(0, 3).text = 'Gender'

                # Data (top 20)
                for i, user in enumerate(users[:20], 1):
                    users_table.cell(i, 0).text = user.get('email', '')[:30]  # Limit length
                    users_table.cell(i, 1).text = user.get('name', '')[:20]
                    users_table.cell(i, 2).text = str(user.get('created_at', ''))[:10]
                    users_table.cell(i, 3).text = user.get('gender', '')

            # Food records section
            if food_records:
                doc.add_heading('Recent Food Records (Top 15)', level=1)
                foods_table = doc.add_table(rows=min(16, len(food_records) + 1), cols=4)
                foods_table.style = 'Table Grid'

                # Headers
                foods_table.cell(0, 0).text = 'User ID'
                foods_table.cell(0, 1).text = 'Description'
                foods_table.cell(0, 2).text = 'Meal Type'
                foods_table.cell(0, 3).text = 'Date'

                # Data (top 15)
                for i, food in enumerate(food_records[:15], 1):
                    foods_table.cell(i, 0).text = food.get('user_id', '')[:15]
                    foods_table.cell(i, 1).text = food.get('description', '')[:30]
                    foods_table.cell(i, 2).text = food.get('mealType', '')
                    foods_table.cell(i, 3).text = str(food.get('date', ''))[:10]

            # Lưu Word file
            word_buffer = io.BytesIO()
            doc.save(word_buffer)
            word_buffer.seek(0)

            def generate_word():
                yield word_buffer.getvalue()

            return StreamingResponse(
                generate_word(),
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                headers={"Content-Disposition": f"attachment; filename=admin_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx"}
            )

        elif format.lower() == "excel":
            if not EXCEL_AVAILABLE:
                # Fallback to CSV if Excel not available
                format = "csv"

        elif format.lower() == "word":
            if not WORD_AVAILABLE:
                # Fallback to CSV if Word not available
                format = "csv"

        # Xuất CSV (fallback cho tất cả formats)
        output = io.StringIO()

        # Tạo CSV đơn giản
        output.write("ADMIN REPORT\n")
        output.write(f"Export Date: {report_data['export_date']}\n")
        output.write(f"Period: {report_data['period']}\n")
        output.write(f"Admin: {report_data['admin']}\n")
        output.write("\n")

        # Summary
        output.write("SUMMARY\n")
        for key, value in report_data['summary'].items():
            output.write(f"{key.replace('_', ' ').title()}: {value}\n")
        output.write("\n")

        # Users data (simplified)
        if users:
            output.write("USERS DATA (Top 10)\n")
            output.write("Email,Name,Created At,Gender\n")

            for user in users:
                try:
                    email = str(user.get('email', 'N/A')).replace(',', ';')[:50]
                    name = str(user.get('name', 'N/A')).replace(',', ';')[:30]
                    created = str(user.get('created_at', 'N/A'))[:19]
                    gender = str(user.get('gender', 'N/A'))[:10]
                    output.write(f'"{email}","{name}","{created}","{gender}"\n')
                except Exception as e:
                    print(f"[EXPORT] Error processing user: {e}")
                    output.write('"Error","Error","Error","Error"\n')
            output.write("\n")
        else:
            output.write("USERS DATA: No users found\n\n")

        # Food records (simplified)
        if food_records:
            output.write("FOOD RECORDS (Top 10)\n")
            output.write("User ID,Description,Meal Type,Date\n")

            for food in food_records:
                try:
                    user_id = str(food.get('user_id', 'N/A'))[:20]
                    desc = str(food.get('description', 'N/A')).replace(',', ';')[:40]
                    meal_type = str(food.get('mealType', 'N/A'))[:15]
                    date = str(food.get('date', 'N/A'))[:19]
                    output.write(f'"{user_id}","{desc}","{meal_type}","{date}"\n')
                except Exception as e:
                    print(f"[EXPORT] Error processing food record: {e}")
                    output.write('"Error","Error","Error","Error"\n')
        else:
            output.write("FOOD RECORDS: No records found\n")

        csv_content = output.getvalue()
        print(f"[EXPORT] CSV content generated, length: {len(csv_content)} characters")

        def generate_csv():
            yield csv_content

        print(f"[EXPORT] Returning StreamingResponse for CSV")
        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=admin_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
        )

    except Exception as e:
        print(f"Error exporting report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Lỗi xuất báo cáo: {str(e)}")
