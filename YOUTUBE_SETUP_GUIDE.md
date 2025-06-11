# Hướng dẫn cấu hình YouTube API cho tự động tìm kiếm video

## Tổng quan
Tính năng này sẽ tự động tìm kiếm video hướng dẫn nấu ăn trên YouTube cho mỗi món ăn mà AI tạo ra, giúp người dùng có thể xem video ngay lập tức mà không cần tìm kiếm thủ công.

## Bước 1: Tạo YouTube Data API Key

### 1.1. Truy cập Google Cloud Console
- Vào https://console.cloud.google.com/
- Đăng nhập bằng tài khoản Google của bạn

### 1.2. Tạo hoặc chọn Project
- Nếu chưa có project, tạo project mới
- Nếu đã có project (như project Firebase hiện tại), chọn project đó

### 1.3. Bật YouTube Data API v3
- Vào **APIs & Services** > **Library**
- Tìm kiếm "YouTube Data API v3"
- Click vào kết quả và nhấn **Enable**

### 1.4. Tạo API Key
- Vào **APIs & Services** > **Credentials**
- Click **Create Credentials** > **API Key**
- Copy API Key được tạo ra

### 1.5. Hạn chế API Key (Khuyến nghị)
- Click vào API Key vừa tạo để chỉnh sửa
- Trong **Application restrictions**, chọn **HTTP referrers** hoặc **IP addresses** tùy theo môi trường
- Trong **API restrictions**, chọn **Restrict key** và chỉ chọn **YouTube Data API v3**
- Click **Save**

## Bước 2: Cấu hình Backend

### 2.1. Thêm API Key vào Environment Variables

#### Trên Windows (Development):
```bash
set YOUTUBE_API_KEY=your_youtube_api_key_here
```

#### Trên Linux/Mac (Development):
```bash
export YOUTUBE_API_KEY=your_youtube_api_key_here
```

#### Trong file .env (Production):
```env
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### 2.2. Khởi động lại Backend
Sau khi cấu hình API Key, khởi động lại backend để áp dụng thay đổi:

```bash
cd backend
python main.py
```

## Bước 3: Kiểm tra hoạt động

### 3.1. Kiểm tra trạng thái YouTube API
```bash
curl http://localhost:8000/youtube/status
```

Kết quả mong đợi:
```json
{
  "youtube_available": true,
  "api_key_configured": true,
  "message": "YouTube API sẵn sàng"
}
```

### 3.2. Test tìm kiếm video
```bash
curl "http://localhost:8000/youtube/search?dish_name=phở bò" \
  -H "Authorization: Bearer YOUR_FIREBASE_TOKEN"
```

Kết quả mong đợi:
```json
{
  "success": true,
  "message": "Tìm thấy video cho món 'phở bò'",
  "dish_name": "phở bò",
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "video_info": {
    "title": "Cách nấu phở bò ngon...",
    "channel_title": "Kênh nấu ăn ABC",
    "view_count": "123456"
  }
}
```

## Bước 4: Tích hợp với App Flutter

Sau khi backend hoạt động, video URL sẽ tự động được thêm vào mỗi món ăn khi:

1. **Tạo kế hoạch ăn mới**: AI tạo món ăn → Tự động tìm video → Lưu vào Firestore
2. **Xem chi tiết món ăn**: App hiển thị video player với URL đã có sẵn
3. **Không cần thao tác thủ công**: Toàn bộ quá trình tự động

## Cấu trúc dữ liệu mới

### Dish Model (đã cập nhật):
```json
{
  "name": "Phở bò",
  "ingredients": [...],
  "preparation": [...],
  "nutrition": {...},
  "video_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

## Lưu ý quan trọng

### Quota và Rate Limiting
- YouTube Data API có giới hạn 10,000 units/ngày (miễn phí)
- Mỗi lần search tiêu tốn ~100 units
- Có thể tìm kiếm ~100 món ăn/ngày với tài khoản miễn phí

### Tối ưu hóa
- Hệ thống chỉ tìm video cho món ăn mới (chưa có video_url)
- Sử dụng cache để tránh tìm kiếm trùng lặp
- Xử lý song song để tăng tốc độ

### Fallback
- Nếu không tìm thấy video, món ăn vẫn được tạo bình thường
- Nếu YouTube API không khả dụng, hệ thống vẫn hoạt động

## Troubleshooting

### Lỗi "YouTube API không khả dụng"
- Kiểm tra API Key đã được cấu hình chưa
- Kiểm tra API Key có đúng không
- Kiểm tra YouTube Data API v3 đã được bật chưa

### Lỗi "Quota exceeded"
- Đã sử dụng hết quota ngày
- Chờ đến ngày hôm sau hoặc nâng cấp quota

### Không tìm thấy video phù hợp
- Tên món ăn quá đặc biệt hoặc hiếm
- Hệ thống sẽ thử nhiều từ khóa khác nhau
- Món ăn vẫn được tạo, chỉ thiếu video

## Kết quả mong đợi

Sau khi hoàn thành setup:

1. ✅ Người dùng tạo kế hoạch ăn → AI tạo món ăn → Tự động có video
2. ✅ Người dùng xem chi tiết món ăn → Video hiển thị ngay lập tức
3. ✅ Không cần tìm kiếm video thủ công
4. ✅ Trải nghiệm mượt mà, chuyên nghiệp

Đây chính là giải pháp tự động hóa hoàn toàn mà bạn đã yêu cầu! 🎯
