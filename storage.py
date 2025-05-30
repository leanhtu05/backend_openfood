import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from models import WeeklyMealPlan, DayMealPlan

# Thư mục lưu trữ dữ liệu
DATA_DIR = "data"
MEAL_PLANS_DIR = os.path.join(DATA_DIR, "meal_plans")

# Đảm bảo các thư mục tồn tại
def ensure_dirs_exist():
    """Tạo các thư mục cần thiết nếu chưa tồn tại"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MEAL_PLANS_DIR, exist_ok=True)

# Hàm chuyển đổi Pydantic model sang dict tương thích với cả phiên bản 1.x và 2.x
def model_to_dict(model):
    """Chuyển đổi Pydantic model sang dict tương thích với cả phiên bản 1.x và 2.x"""
    try:
        # Thử phương thức model_dump() (Pydantic 2.x)
        return model.model_dump()
    except AttributeError:
        try:
            # Thử phương thức dict() (Pydantic 1.x)
            return model.dict()
        except AttributeError:
            raise ValueError("Model không hỗ trợ model_dump() hoặc dict()")

# Lưu meal plan vào file
def save_meal_plan(meal_plan: WeeklyMealPlan, user_id: str = "default") -> str:
    """
    Lưu kế hoạch thực đơn vào file JSON
    
    Args:
        meal_plan: Đối tượng WeeklyMealPlan cần lưu
        user_id: ID của người dùng (mặc định là "default")
        
    Returns:
        Đường dẫn đến file đã lưu
    """
    ensure_dirs_exist()
    
    # Tạo tên file dựa trên user_id và timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}.json"
    filepath = os.path.join(MEAL_PLANS_DIR, filename)
    
    # Cũng lưu một file "latest" cho người dùng này
    latest_filepath = os.path.join(MEAL_PLANS_DIR, f"{user_id}_latest.json")
    
    # Chuyển đổi Pydantic model thành JSON
    meal_plan_dict = model_to_dict(meal_plan)
    meal_plan_json = json.dumps(meal_plan_dict, ensure_ascii=False)
    
    # Lưu vào file
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(meal_plan_json)
    
    # Lưu phiên bản mới nhất
    with open(latest_filepath, "w", encoding="utf-8") as f:
        f.write(meal_plan_json)
    
    return filepath

# Đọc meal plan từ file
def load_meal_plan(user_id: str = "default") -> Optional[WeeklyMealPlan]:
    """
    Đọc kế hoạch thực đơn mới nhất từ file JSON
    
    Args:
        user_id: ID của người dùng (mặc định là "default")
        
    Returns:
        Đối tượng WeeklyMealPlan hoặc None nếu không tìm thấy
    """
    ensure_dirs_exist()
    
    # Đường dẫn đến file mới nhất của người dùng
    latest_filepath = os.path.join(MEAL_PLANS_DIR, f"{user_id}_latest.json")
    
    # Kiểm tra xem file có tồn tại không
    if not os.path.exists(latest_filepath):
        return None
    
    try:
        # Đọc từ file JSON
        with open(latest_filepath, "r", encoding="utf-8") as f:
            meal_plan_json = f.read()
        
        # Chuyển đổi JSON thành Pydantic model
        meal_plan = WeeklyMealPlan.parse_raw(meal_plan_json)
        return meal_plan
    except Exception as e:
        print(f"Lỗi khi đọc meal plan: {e}")
        return None

# Lấy lịch sử meal plan
def get_meal_plan_history(user_id: str = "default", limit: int = 10) -> List[Dict]:
    """
    Lấy lịch sử kế hoạch thực đơn của người dùng
    
    Args:
        user_id: ID của người dùng (mặc định là "default")
        limit: Số lượng kế hoạch tối đa trả về
        
    Returns:
        Danh sách các kế hoạch thực đơn, mỗi kế hoạch bao gồm filepath và timestamp
    """
    ensure_dirs_exist()
    
    # Lấy tất cả các file của người dùng
    user_files = [f for f in os.listdir(MEAL_PLANS_DIR) 
                 if f.startswith(user_id) and not f.endswith("_latest.json")]
    
    # Sắp xếp theo thời gian (mới nhất trước)
    user_files.sort(reverse=True)
    
    # Giới hạn số lượng
    user_files = user_files[:limit]
    
    history = []
    for filename in user_files:
        # Trích xuất timestamp từ tên file
        try:
            # Format: user_id_YYYYMMDD_HHMMSS.json
            timestamp_str = filename.replace(f"{user_id}_", "").replace(".json", "")
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            
            history.append({
                "filepath": os.path.join(MEAL_PLANS_DIR, filename),
                "timestamp": timestamp.isoformat(),
                "filename": filename
            })
        except Exception:
            # Bỏ qua các file không đúng định dạng
            continue
    
    return history

# Xóa meal plan
def delete_meal_plan(filename: str) -> bool:
    """
    Xóa một kế hoạch thực đơn
    
    Args:
        filename: Tên file cần xóa
        
    Returns:
        True nếu xóa thành công, False nếu không
    """
    filepath = os.path.join(MEAL_PLANS_DIR, filename)
    
    if not os.path.exists(filepath):
        return False
    
    try:
        os.remove(filepath)
        return True
    except Exception:
        return False 