from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Optional
import hashlib
import os
from datetime import datetime, timedelta

# Admin credentials (trong thực tế nên lưu trong database hoặc environment variables)
ADMIN_CREDENTIALS = {
    "admin": "admin123",  # username: password
    "foodai_admin": "foodai2024",
    "manager": "manager123"
}

# Session storage (trong thực tế nên dùng Redis hoặc database)
admin_sessions = {}

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def create_admin_session(username: str) -> str:
    """Create admin session and return session token"""
    import secrets
    session_token = secrets.token_urlsafe(32)
    admin_sessions[session_token] = {
        "username": username,
        "created_at": datetime.now(),
        "last_activity": datetime.now()
    }
    return session_token

def get_admin_session(session_token: str) -> Optional[dict]:
    """Get admin session by token"""
    if session_token in admin_sessions:
        session = admin_sessions[session_token]
        # Check if session is expired (24 hours)
        if datetime.now() - session["created_at"] > timedelta(hours=24):
            del admin_sessions[session_token]
            return None
        
        # Update last activity
        session["last_activity"] = datetime.now()
        return session
    return None

def delete_admin_session(session_token: str):
    """Delete admin session"""
    if session_token in admin_sessions:
        del admin_sessions[session_token]

def authenticate_admin(username: str, password: str) -> bool:
    """Authenticate admin credentials"""
    if username in ADMIN_CREDENTIALS:
        return ADMIN_CREDENTIALS[username] == password
    return False

def get_current_admin(request: Request) -> Optional[str]:
    """Get current admin username from session"""
    session_token = request.cookies.get("admin_session")
    if session_token:
        session = get_admin_session(session_token)
        if session:
            return session["username"]
    return None

def require_admin_auth(request: Request) -> str:
    """Require admin authentication, raise exception if not authenticated"""
    admin_username = get_current_admin(request)
    if not admin_username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required"
        )
    return admin_username

def admin_login_required(func):
    """Decorator to require admin login for routes"""
    def wrapper(*args, **kwargs):
        request = None
        # Find request object in arguments
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        
        if not request:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Request object not found"
            )
        
        # Check if admin is authenticated
        admin_username = get_current_admin(request)
        if not admin_username:
            # Redirect to login page
            return RedirectResponse(url="/admin/login", status_code=302)
        
        return func(*args, **kwargs)
    return wrapper

class AdminAuthMiddleware:
    """Middleware to check admin authentication for admin routes"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            path = request.url.path
            
            # Skip authentication for login page and static files
            if (path.startswith("/admin/login") or 
                path.startswith("/static/") or 
                path.startswith("/favicon.ico") or
                not path.startswith("/admin/")):
                await self.app(scope, receive, send)
                return
            
            # Check admin authentication for admin routes
            admin_username = get_current_admin(request)
            if not admin_username:
                # Redirect to login page
                response = RedirectResponse(url="/admin/login", status_code=302)
                await response(scope, receive, send)
                return
        
        await self.app(scope, receive, send)
