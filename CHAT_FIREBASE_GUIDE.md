# Hướng dẫn sử dụng tính năng lưu lịch sử chat với Firebase

Tài liệu này hướng dẫn cách sử dụng API lưu trữ lịch sử chat trên Firebase đã được triển khai trong hệ thống.

## Cài đặt

1. Đảm bảo đã cài đặt các thư viện cần thiết:
   ```bash
   pip install -r requirements.txt
   ```

2. Cấu hình Firebase:
   - Tạo file `firebase-credentials.json` trong thư mục `backend/`
   - Hoặc thiết lập biến môi trường `FIREBASE_CREDENTIALS_JSON` với nội dung của file credentials

## API Endpoints

### 1. Gửi tin nhắn chat

**Endpoint:** `/chat`
**Method:** POST
**Content-Type:** application/json

**Request Body:**
```json
{
  "message": "Món ăn nào tốt cho người bị tiểu đường?",
  "user_id": "user_123"  // Tùy chọn, mặc định là "anonymous"
}
```

**Response:**
```json
{
  "reply": "Người bị tiểu đường nên ăn các thực phẩm có chỉ số đường huyết thấp như rau xanh, ngũ cốc nguyên hạt, đậu, cá, và thịt nạc...",
  "chat_id": "abcd1234-efgh-5678-ijkl-90mnopqrstuv"
}
```

### 2. Lấy lịch sử chat

**Endpoint:** `/chat/history`
**Method:** GET

**Query Parameters:**
- `user_id`: ID của người dùng (mặc định là "anonymous")
- `limit`: Số lượng tin nhắn tối đa cần lấy (mặc định là 10)

**Ví dụ:** `/chat/history?user_id=user_123&limit=5`

**Response:**
```json
{
  "history": [
    {
      "id": "abcd1234-efgh-5678-ijkl-90mnopqrstuv",
      "user_id": "user_123",
      "user_message": "Món ăn nào tốt cho người bị tiểu đường?",
      "ai_reply": "Người bị tiểu đường nên ăn các thực phẩm có chỉ số đường huyết thấp như rau xanh...",
      "timestamp": "2023-09-15T08:30:45.123456",
      "model": "llama3-8b-8192"
    },
    // Các tin nhắn khác...
  ],
  "count": 1
}
```

## Cấu trúc dữ liệu trong Firebase

Lịch sử chat được lưu trong collection `chat_history` với cấu trúc như sau:

- **Document ID:** UUID tự động tạo cho mỗi cuộc hội thoại
- **Fields:**
  - `user_id`: ID của người dùng
  - `user_message`: Tin nhắn của người dùng
  - `ai_reply`: Phản hồi của AI
  - `timestamp`: Thời gian gửi tin nhắn (ISO format)
  - `model`: Mô hình AI được sử dụng

## Kiểm tra

Để kiểm tra tính năng lưu trữ lịch sử chat, chạy lệnh:
```bash
python test_chat_history.py
```

## Tích hợp với Flutter

Khi gọi API từ ứng dụng Flutter, sử dụng các endpoint và format JSON như đã mô tả ở trên.

### Ví dụ code Dart:

```dart
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<String> sendChatMessage(String message, String userId) async {
  final response = await http.post(
    Uri.parse('http://your-api-host:5000/chat'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'message': message,
      'user_id': userId,
    }),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['reply'];
  } else {
    throw Exception('Không thể gửi tin nhắn');
  }
}

Future<List<dynamic>> getChatHistory(String userId, {int limit = 10}) async {
  final response = await http.get(
    Uri.parse('http://your-api-host:5000/chat/history?user_id=$userId&limit=$limit'),
  );

  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['history'];
  } else {
    throw Exception('Không thể lấy lịch sử chat');
  }
}
``` 