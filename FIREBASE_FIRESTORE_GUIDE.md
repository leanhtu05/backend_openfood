# Hướng dẫn sử dụng Firebase Firestore API

## Giới thiệu

API này cung cấp các endpoints để tương tác với Firebase Firestore, cho phép lưu trữ và truy xuất:
- Dữ liệu người dùng (hồ sơ cá nhân, sức khỏe)
- Nhật ký hàng ngày về thực phẩm đã tiêu thụ
- Thực đơn đã chọn hoặc được gợi ý
- Kết quả gợi ý từ AI

## Cài đặt

1. Đảm bảo bạn đã cài đặt Firebase và cấu hình credentials:
   ```bash
   pip install firebase-admin
   ```

2. Tạo file `firebase-credentials.json` từ Firebase Console và đặt trong thư mục gốc của dự án.

3. Hoặc đặt biến môi trường:
   ```
   FIREBASE_CREDENTIALS_JSON="{...json credentials here...}"
   ```

## Cấu trúc dữ liệu

### 1. Thông tin người dùng

Collection `users` chứa thông tin của từng người dùng:

```json
{
  "name": "Nguyễn Văn A",
  "email": "user@example.com",
  "age": 25,
  "weight": 65,
  "height": 170,
  "targetCalories": 2000
}
```

Subcollection `daily_logs` chứa log hàng ngày của người dùng:

```
users/
  └── userId123/
        └── daily_logs/
              └── 2025-05-19/
                    - caloriesIntake: 1900
                    - meals: ["Phở", "Trứng luộc"]
```

### 2. Thực đơn

Collection `meal_plans` chứa các kế hoạch bữa ăn:

```json
{
  "userId": "userId123",
  "date": "2025-05-19",
  "meals": [
    {
      "name": "Cơm gà",
      "calories": 520,
      "type": "lunch"
    },
    {
      "name": "Trái cây",
      "calories": 200,
      "type": "snack"
    }
  ]
}
```

### 3. Gợi ý từ AI

Collection `ai_suggestions` chứa các gợi ý từ AI:

```json
{
  "userId": "userId123",
  "input": "Tôi muốn ăn ít carb",
  "suggestedMeals": [
    {
      "name": "Salad ức gà",
      "calories": 300
    },
    {
      "name": "Súp rau củ",
      "calories": 150
    }
  ],
  "timestamp": "2025-05-19T10:30:00Z"
}
```

## API Endpoints

Tất cả các endpoints đều có tiền tố `/firestore`

### Quản lý người dùng

- **Tạo người dùng mới**
  ```
  POST /firestore/users/{user_id}
  ```
  Body:
  ```json
  {
    "name": "Nguyễn Văn A",
    "email": "user@example.com",
    "age": 25,
    "weight": 65,
    "height": 170,
    "targetCalories": 2000
  }
  ```

- **Lấy thông tin người dùng**
  ```
  GET /firestore/users/{user_id}
  ```

- **Cập nhật thông tin người dùng**
  ```
  PATCH /firestore/users/{user_id}
  ```
  Body:
  ```json
  {
    "weight": 64,
    "targetCalories": 1800
  }
  ```

- **Xóa người dùng**
  ```
  DELETE /firestore/users/{user_id}
  ```

### Quản lý nhật ký hàng ngày

- **Thêm nhật ký mới**
  ```
  POST /firestore/users/{user_id}/daily-logs
  ```
  Body:
  ```json
  {
    "date": "2025-05-19",
    "caloriesIntake": 1900,
    "meals": ["Phở", "Trứng luộc"]
  }
  ```

- **Lấy nhật ký theo ngày**
  ```
  GET /firestore/users/{user_id}/daily-logs/{date}
  ```

- **Lấy danh sách nhật ký**
  ```
  GET /firestore/users/{user_id}/daily-logs?limit=7
  ```

- **Cập nhật nhật ký**
  ```
  PATCH /firestore/users/{user_id}/daily-logs/{date}
  ```
  Body:
  ```json
  {
    "caloriesIntake": 2050,
    "meals": ["Phở", "Trứng luộc", "Sữa chua"]
  }
  ```

### Quản lý kế hoạch bữa ăn

- **Tạo kế hoạch bữa ăn mới**
  ```
  POST /firestore/meal-plans
  ```
  Body:
  ```json
  {
    "userId": "userId123",
    "date": "2025-05-19",
    "meals": [
      {
        "name": "Cơm gà",
        "calories": 520,
        "type": "lunch"
      },
      {
        "name": "Trái cây",
        "calories": 200,
        "type": "snack"
      }
    ]
  }
  ```

- **Lấy kế hoạch bữa ăn theo ID**
  ```
  GET /firestore/meal-plans/{plan_id}
  ```

- **Lấy kế hoạch bữa ăn theo ngày và người dùng**
  ```
  GET /firestore/users/{user_id}/meal-plans/date/{date}
  ```

- **Xóa kế hoạch bữa ăn**
  ```
  DELETE /firestore/meal-plans/{plan_id}
  ```

### Quản lý gợi ý từ AI

- **Lưu gợi ý**
  ```
  POST /firestore/ai-suggestions
  ```
  Body:
  ```json
  {
    "userId": "userId123",
    "input": "Tôi muốn ăn ít carb",
    "suggestedMeals": [
      {
        "name": "Salad ức gà",
        "calories": 300
      },
      {
        "name": "Súp rau củ",
        "calories": 150
      }
    ]
  }
  ```

- **Lấy danh sách gợi ý**
  ```
  GET /firestore/users/{user_id}/ai-suggestions?limit=10
  ```

## Ví dụ sử dụng

### Truy vấn thông tin người dùng và nhật ký hôm nay

```python
import requests

API_URL = "http://localhost:8000"
USER_ID = "user123"

# Lấy thông tin người dùng
user_response = requests.get(f"{API_URL}/firestore/users/{USER_ID}")
user = user_response.json()
print(f"Xin chào {user['name']}, mục tiêu calories của bạn: {user['targetCalories']}")

# Lấy nhật ký hôm nay
today = "2025-05-19"  # datetime.now().strftime("%Y-%m-%d")
log_response = requests.get(f"{API_URL}/firestore/users/{USER_ID}/daily-logs/{today}")

if log_response.status_code == 200:
    log = log_response.json()
    print(f"Hôm nay bạn đã tiêu thụ {log['caloriesIntake']} calories")
    print(f"Các bữa ăn: {', '.join(log['meals'])}")
else:
    print("Bạn chưa có dữ liệu cho hôm nay")
```

### Tạo kế hoạch bữa ăn mới

```python
import requests

API_URL = "http://localhost:8000"
USER_ID = "user123"

# Tạo kế hoạch bữa ăn mới
meal_plan = {
    "userId": USER_ID,
    "date": "2025-05-20",
    "meals": [
        {
            "name": "Bún chả",
            "calories": 450,
            "type": "lunch"
        },
        {
            "name": "Sinh tố",
            "calories": 180,
            "type": "breakfast"
        }
    ]
}

response = requests.post(f"{API_URL}/firestore/meal-plans", json=meal_plan)
if response.status_code == 201:
    result = response.json()
    print(f"Kế hoạch bữa ăn đã được tạo với ID: {result['plan_id']}")
else:
    print(f"Lỗi: {response.status_code} - {response.text}")
```

## Xử lý lỗi

API trả về các mã lỗi HTTP tiêu chuẩn:

- 400: Bad Request - Yêu cầu không hợp lệ
- 404: Not Found - Không tìm thấy tài nguyên
- 500: Internal Server Error - Lỗi server

Mỗi phản hồi lỗi đều chứa thông tin chi tiết trong trường `detail`:

```json
{
  "detail": "User with ID user456 not found"
}
``` 