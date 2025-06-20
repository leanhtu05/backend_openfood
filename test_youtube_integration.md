# Test YouTube Integration

## Tính năng đã tích hợp:

### 1. **YouTube Cooking Demo Screen** (`lib/screens/youtube_cooking_demo_screen.dart`)
- Hiển thị danh sách món ăn mẫu
- Mỗi món ăn có thể nhấn để xem chi tiết và video hướng dẫn

### 2. **Recipe Detail Screen** (`lib/screens/recipe_detail_screen.dart`)
- Đã cập nhật để tích hợp YouTube search
- Khi nhấn vào phần video, sẽ mở YouTube với từ khóa tìm kiếm tự động
- Fallback dialog nếu không thể mở YouTube

### 3. **Settings Integration**
- Thêm section "Tính năng Demo" trong Settings
- Button "YouTube Hướng Dẫn Nấu Ăn" để truy cập demo

## Cách sử dụng:

### Từ Settings:
1. Mở app → Settings
2. Cuộn xuống phần "Tính năng Demo"
3. Nhấn "YouTube Hướng Dẫn Nấu Ăn"

### Từ Recipe Detail:
1. Chọn một món ăn bất kỳ
2. Trong màn hình chi tiết, nhấn vào phần "Video hướng dẫn"
3. App sẽ mở YouTube với từ khóa tìm kiếm: "[Tên món ăn] hướng dẫn nấu ăn"

## Tính năng:

### ✅ Đã hoàn thành:
- [x] Tích hợp YouTube search trực tiếp trong Flutter
- [x] Giao diện đẹp với animation và gradient
- [x] Tự động tạo từ khóa tìm kiếm dựa trên tên món ăn
- [x] Fallback dialog khi không thể mở YouTube
- [x] Route navigation đã được thiết lập
- [x] Demo screen với danh sách món ăn mẫu

### 🔧 Cách hoạt động:
1. **Tự động tạo query**: Lấy tên món ăn + "hướng dẫn nấu ăn"
2. **Mở YouTube**: Sử dụng `url_launcher` để mở YouTube app hoặc browser
3. **Fallback**: Nếu không mở được, hiển thị dialog với từ khóa tìm kiếm

### 📱 Packages sử dụng:
- `url_launcher`: Để mở YouTube
- `youtube_player_flutter`: Đã có sẵn (có thể dùng cho tương lai)
- `video_player`: Đã có sẵn (có thể dùng cho tương lai)

## Ưu điểm của cách tiếp cận này:

1. **Không cần backend**: Tất cả logic ở Flutter
2. **Linh hoạt**: Có thể tùy chỉnh từ khóa tìm kiếm
3. **User-friendly**: Mở trực tiếp YouTube app nếu có
4. **Fallback tốt**: Hiển thị thông tin tìm kiếm nếu không mở được
5. **Performance**: Không cần load video trong app, giảm tải

## Test Cases:

### Test 1: Mở từ Settings
- Vào Settings → Demo → YouTube Hướng Dẫn Nấu Ăn
- Chọn một món ăn → Nhấn vào món ăn
- Nhấn vào phần video → Kiểm tra có mở YouTube không

### Test 2: Từ khóa tìm kiếm
- Kiểm tra từ khóa được tạo đúng format: "[Tên món] hướng dẫn nấu ăn"
- VD: "Phở Bò hướng dẫn nấu ăn"

### Test 3: Fallback
- Test trên thiết bị không có YouTube app
- Kiểm tra dialog fallback hiển thị đúng

## Mở rộng trong tương lai:

1. **Embed video**: Sử dụng `youtube_player_flutter` để phát video trong app
2. **Video cache**: Cache video để xem offline
3. **Playlist**: Tạo playlist các video hướng dẫn
4. **Rating**: Cho phép user đánh giá video
5. **Favorites**: Lưu video yêu thích
