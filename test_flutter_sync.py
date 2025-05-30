import requests
import json
from datetime import datetime
import uuid

# URL của API
BASE_URL = "http://localhost:8000"

# Tạo ID người dùng ngẫu nhiên cho việc kiểm tra
user_id = f"flutter_test_{int(datetime.now().timestamp())}"
print(f"Kiểm tra đồng bộ dữ liệu cho user_id: {user_id}")

# Dữ liệu mẫu từ Flutter (đầy đủ các trường)
user_data = {
    "name": "Người dùng kiểm tra",
    "email": "leanhtu16032003@gmail.com",
    "gender": "Nam",
    "age": 28,
    "height_cm": 159.0,
    "weight_kg": 65.0,
    "activity_level": "Ít vận động",
    "goal": "Giảm cân",
    "pace": 0.75,
    "target_weight_kg": 60.0,
    "event": "Sinh nhật",
    "event_date": {
        "day": 16,
        "month": 3,
        "year": 2024
    },
    "diet_restrictions": [
        "vegetarian"
    ],
    "diet_preference": "low-carb",
    "health_conditions": [
        "hypertension"
    ],
    "nutrition_goals": {
        "calories": 1800,
        "protein": 120,
        "carbs": 150,
        "fat": 60
    },
    "settings": {
        "notifications_enabled": True,
        "theme": "dark",
        "language": "vi"
    }
}

# 1. Tạo người dùng mới
print("\n1. Tạo người dùng mới")
create_response = requests.post(
    f"{BASE_URL}/firestore/users/{user_id}",
    json={"name": user_data["name"], "email": user_data["email"]}
)
print(f"Kết quả tạo người dùng: {create_response.status_code}")
print(create_response.json())

# 2. Kiểm tra người dùng đã được tạo
print("\n2. Kiểm tra người dùng đã được tạo")
get_response = requests.get(f"{BASE_URL}/firestore/users/{user_id}")
print(f"Kết quả lấy thông tin người dùng: {get_response.status_code}")
print(json.dumps(get_response.json(), indent=2, ensure_ascii=False))

# 3. Đồng bộ dữ liệu đầy đủ từ Flutter
print("\n3. Đồng bộ dữ liệu đầy đủ từ Flutter")
sync_data = {
    "user": user_data,
    "meals": [],
    "exercises": [],
    "water_logs": []
}

sync_response = requests.post(
    f"{BASE_URL}/api/sync?user_id={user_id}",
    json=sync_data
)
print(f"Kết quả đồng bộ dữ liệu: {sync_response.status_code}")
print(json.dumps(sync_response.json(), indent=2, ensure_ascii=False))

# 4. Kiểm tra dữ liệu sau khi đồng bộ
print("\n4. Kiểm tra dữ liệu sau khi đồng bộ")
get_response = requests.get(f"{BASE_URL}/firestore/users/{user_id}")
print(f"Kết quả lấy thông tin người dùng sau đồng bộ: {get_response.status_code}")
print(json.dumps(get_response.json(), indent=2, ensure_ascii=False))

print("\nKiểm tra hoàn tất!") 