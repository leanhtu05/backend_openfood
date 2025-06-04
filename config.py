import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Load biến môi trường từ file .env
load_dotenv()

class Config:
    """Lớp cấu hình cho ứng dụng DietAI API"""
    
    # API keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    NUTRITIONIX_APP_ID: str = os.getenv("NUTRITIONIX_APP_ID")
    NUTRITIONIX_API_KEY: str = os.getenv("NUTRITIONIX_API_KEY")
    USDA_API_KEY: str = os.getenv("USDA_API_KEY")
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
    USE_FIREBASE: bool = os.getenv("USE_FIREBASE", "False").lower() in ('true', 'yes', '1')
    FIREBASE_PROJECT_ID: Optional[str] = os.getenv("FIREBASE_PROJECT_ID", "food-ai-96ef6")
    FIREBASE_STORAGE_BUCKET: Optional[str] = os.getenv("FIREBASE_STORAGE_BUCKET", "food-ai-96ef6.appspot.com")
    
    # Storage
    DATA_DIR: str = os.getenv("DATA_DIR", "data")
    MEAL_PLANS_DIR: str = os.path.join(DATA_DIR, "meal_plans")
    CACHE_DIR: str = os.path.join(DATA_DIR, "cache")
    NUTRITION_CACHE_FILE: str = os.path.join(CACHE_DIR, "nutrition_cache.json")
    USDA_CACHE_FILE: str = os.path.join(CACHE_DIR, "usda_cache.json")
    
    # Nutritionix optimization
    USE_NUTRITIONIX_CACHE: bool = os.getenv("USE_NUTRITIONIX_CACHE", "True").lower() in ('true', 'yes', '1')
    USE_NUTRITIONIX_BATCH: bool = os.getenv("USE_NUTRITIONIX_BATCH", "True").lower() in ('true', 'yes', '1')
    
    # USDA API Settings
    USE_USDA_CACHE: bool = os.getenv("USE_USDA_CACHE", "True").lower() in ('true', 'yes', '1')
    USDA_CACHE_TTL_DAYS: int = int(os.getenv("USDA_CACHE_TTL_DAYS", "30"))
    
    # Cache settings
    CACHE_TTL_DAYS: int = int(os.getenv("CACHE_TTL_DAYS", "30"))
    
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Cors
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """Lấy tất cả cấu hình dưới dạng dictionary"""
        return {
            key: value for key, value in cls.__dict__.items()
            if not key.startswith('__') and not callable(value)
        }
    
    @classmethod
    def create_dirs(cls) -> None:
        """Tạo các thư mục cần thiết cho ứng dụng"""
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        os.makedirs(cls.MEAL_PLANS_DIR, exist_ok=True)
        os.makedirs(cls.CACHE_DIR, exist_ok=True)
        
    @classmethod
    def get_firebase_config(cls) -> Dict[str, Any]:
        """Lấy cấu hình Firebase dưới dạng dictionary"""
        return {
            "projectId": cls.FIREBASE_PROJECT_ID,
            "storageBucket": cls.FIREBASE_STORAGE_BUCKET
        }

# Tạo các thư mục cần thiết
Config.create_dirs()

# Export singleton
config = Config() 

# Export constants for easy access
FIREBASE_STORAGE_BUCKET = config.FIREBASE_STORAGE_BUCKET
FIREBASE_PROJECT_ID = config.FIREBASE_PROJECT_ID
