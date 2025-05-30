import requests
import json
from datetime import datetime

# URL của API
BASE_URL = "http://localhost:8000"

# ID người dùng cần kiểm tra
user_id = "49DhdmJHFAY40eEgaPNEJqGdDQK2"
print(f"Kiểm tra đồng bộ dữ liệu cho user_id: {user_id}")

# Dữ liệu mẫu từ Flutter
user_data = {
    "name": "Người dùng kiểm tra",
    "gender": "male",
    "age": 30,
    "height_cm": 170.0,
    "weight_kg": 65.0,
    "activity_level": "Hoạt động vừa phải",
    "goal": "lose_weight",
    "pace": 0.5,
    "target_weight_kg": 60.0,
    "diet_restrictions": [],
    "diet_preference": "",
    "health_conditions": [],
    "nutrition_goals": {
        "calories": 2000,
        "protein": 150,
        "fat": 70,
        "carbs": 200
    }
}

# 1. Kiểm tra thông tin người dùng hiện tại
print("\n1. Kiểm tra thông tin người dùng hiện tại")
get_response = requests.get(f"{BASE_URL}/firestore/users/{user_id}")
print(f"Kết quả lấy thông tin người dùng: {get_response.status_code}")
print(json.dumps(get_response.json(), indent=2, ensure_ascii=False))

# 2. Đồng bộ dữ liệu với log chi tiết
print("\n2. Đồng bộ dữ liệu với log chi tiết")
sync_data = user_data.copy()

sync_response = requests.post(
    f"{BASE_URL}/api/sync?user_id={user_id}",
    json={"user": sync_data}
)
print(f"Kết quả đồng bộ dữ liệu: {sync_response.status_code}")
print(json.dumps(sync_response.json(), indent=2, ensure_ascii=False))

# 3. Kiểm tra thông tin người dùng sau khi đồng bộ
print("\n3. Kiểm tra thông tin người dùng sau khi đồng bộ")
get_response = requests.get(f"{BASE_URL}/firestore/users/{user_id}")
print(f"Kết quả lấy thông tin người dùng sau đồng bộ: {get_response.status_code}")
print(json.dumps(get_response.json(), indent=2, ensure_ascii=False))

# 4. Thử cập nhật trực tiếp
print("\n4. Thử cập nhật trực tiếp")
update_data = {
    "targetCalories": 2000,
    "targetProtein": 150,
    "targetFat": 70,
    "targetCarbs": 200,
    "updated_at": datetime.now().isoformat()
}

update_response = requests.put(
    f"{BASE_URL}/firestore/users/{user_id}",
    json=update_data
)
print(f"Kết quả cập nhật trực tiếp: {update_response.status_code}")
if update_response.status_code == 200:
    print(json.dumps(update_response.json(), indent=2, ensure_ascii=False))
else:
    print(f"Lỗi: {update_response.text}")

# 5. Kiểm tra thông tin người dùng sau khi cập nhật trực tiếp
print("\n5. Kiểm tra thông tin người dùng sau khi cập nhật trực tiếp")
get_response = requests.get(f"{BASE_URL}/firestore/users/{user_id}")
print(f"Kết quả lấy thông tin người dùng sau cập nhật: {get_response.status_code}")
print(json.dumps(get_response.json(), indent=2, ensure_ascii=False))

print("\nKiểm tra hoàn tất!") 