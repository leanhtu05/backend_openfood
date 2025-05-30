# Hướng dẫn thiết lập Firebase cho DietAI API

Tài liệu này hướng dẫn cách thiết lập Firebase để sử dụng với DietAI API.

## 1. Tạo dự án Firebase

1. Truy cập [Firebase Console](https://console.firebase.google.com/)
2. Nhấn "Add project" để tạo dự án mới
3. Đặt tên dự án (ví dụ: "dietai-api")
4. Chọn "Continue" và làm theo các bước còn lại để hoàn tất tạo dự án

## 2. Thiết lập Firestore Database

1. Từ sidebar của Firebase Console, chọn "Firestore Database"
2. Nhấn "Create database"
3. Chọn "Start in production mode" và chọn region phù hợp với vị trí người dùng của bạn
4. Tạo các collection sau:
   - `meal_plans`: lưu trữ các kế hoạch thực đơn
   - `latest_meal_plans`: lưu trữ kế hoạch thực đơn mới nhất của mỗi người dùng
   - `nutrition_cache`: lưu trữ cache thông tin dinh dưỡng

## 3. Tạo Service Account và tải Credentials

1. Từ sidebar, chọn Project settings (biểu tượng bánh răng)
2. Chọn tab "Service accounts"
3. Nhấn "Generate new private key" để tạo và tải về file credentials
4. Đổi tên file credentials thành `firebase-credentials.json` và lưu vào thư mục gốc của dự án

## 4. Cấu hình Storage (tùy chọn, nếu bạn muốn lưu trữ file)

1. Từ sidebar, chọn "Storage"
2. Nhấn "Get started" và làm theo hướng dẫn
3. Chọn region phù hợp với vị trí người dùng của bạn

## 5. Cập nhật file .env

Tạo file `.env` từ file `.env.example` và cập nhật các biến môi trường:

```
USE_FIREBASE=True
FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
```

Thay `your-project-id` bằng ID dự án Firebase của bạn.

## 6. Cài đặt thư viện

Đảm bảo bạn đã cài đặt thư viện firebase-admin:

```
pip install firebase-admin
```

## 7. Kiểm tra kết nối

Khởi động ứng dụng và kiểm tra xem Firebase đã được kết nối thành công hay chưa:

```
python -m uvicorn main:app --reload
```

Nếu không có lỗi liên quan đến Firebase, tức là kết nối đã thành công.

## Cấu trúc dữ liệu

### Collection: meal_plans
```json
{
  "days": [...],
  "user_id": "user123",
  "timestamp": "2023-05-25T14:30:00"
}
```

### Collection: latest_meal_plans
Document ID là user_id:
```json
{
  "days": [...],
  "user_id": "user123",
  "timestamp": "2023-05-25T14:30:00"
}
```

### Collection: nutrition_cache
Document ID là key cache:
```json
{
  "value": {
    "calories": 200,
    "protein": 15,
    "fat": 10,
    "carbs": 25
  },
  "expiry": 1717890000
}
``` 