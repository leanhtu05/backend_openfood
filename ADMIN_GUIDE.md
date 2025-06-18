# OpenFood Admin Management System

Hệ thống quản lý admin cho ứng dụng OpenFood với giao diện web hiện đại và đầy đủ tính năng.

## 🚀 Tính năng chính

### 1. Dashboard Tổng quan
- **Thống kê real-time**: Số lượng món ăn, người dùng hoạt động, kế hoạch bữa ăn
- **Biểu đồ trực quan**: Hoạt động hệ thống, phân bố loại món ăn
- **Trạng thái hệ thống**: Kiểm tra kết nối Database, AI Service, Firebase
- **Hoạt động gần đây**: Theo dõi các hành động mới nhất trong hệ thống

### 2. Quản lý Người dùng
- **Danh sách người dùng**: Xem tất cả người dùng với phân trang
- **Tìm kiếm**: Tìm kiếm theo email hoặc tên hiển thị
- **Chi tiết người dùng**: Xem thông tin chi tiết và thống kê hoạt động
- **Quản lý quyền**: Khóa/mở khóa tài khoản người dùng

### 3. Quản lý Kế hoạch Bữa ăn
- **Danh sách meal plans**: Xem tất cả kế hoạch bữa ăn
- **Lọc theo người dùng**: Xem kế hoạch của người dùng cụ thể
- **Chi tiết kế hoạch**: Xem chi tiết từng ngày và món ăn
- **Chỉnh sửa/Xóa**: Quản lý kế hoạch bữa ăn

### 4. Báo cáo & Thống kê
- **Metrics tổng quan**: API calls, người dùng mới, tỷ lệ hoạt động
- **Biểu đồ chi tiết**: Hoạt động theo thời gian, thiết bị, tính năng
- **Top người dùng**: Danh sách người dùng hoạt động nhất
- **Lỗi hệ thống**: Theo dõi lỗi và cảnh báo

### 5. Cấu hình Hệ thống
- **AI & API**: Cấu hình Groq API, USDA API, rate limiting
- **Database**: Cấu hình Firebase, performance settings
- **Bảo mật**: JWT, CORS, authentication settings
- **Hiệu suất**: Server performance, logging, monitoring
- **Thông báo**: Email alerts, notification settings

## 🎨 Giao diện & UX

### Responsive Design
- **Mobile-first**: Tối ưu cho điện thoại và tablet
- **Sidebar collapse**: Sidebar thu gọn trên màn hình nhỏ
- **Touch-friendly**: Các nút và controls dễ sử dụng trên touch screen

### Dark Mode Support
- **Auto-detect**: Tự động phát hiện theme preference của hệ thống
- **Manual toggle**: Chuyển đổi theme thủ công
- **Persistent**: Lưu lựa chọn theme trong localStorage

### Accessibility
- **Keyboard navigation**: Hỗ trợ điều hướng bằng bàn phím
- **Screen reader**: Tương thích với screen reader
- **Focus indicators**: Hiển thị rõ ràng focus state
- **Color contrast**: Đảm bảo độ tương phản màu sắc

## 🛠 Cài đặt và Sử dụng

### Yêu cầu hệ thống
- Python 3.8+
- FastAPI
- Firebase Admin SDK
- Bootstrap 5.3+
- Chart.js

### Cài đặt
1. **Clone repository**:
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Cài đặt dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Cấu hình Firebase**:
   - Đặt file `firebase-credentials.json` trong thư mục root
   - Hoặc set biến môi trường `FIREBASE_SERVICE_ACCOUNT_JSON`

4. **Cấu hình API Keys**:
   ```bash
   export GROQ_API_KEY="your-groq-api-key"
   export USDA_API_KEY="your-usda-api-key"
   ```

5. **Chạy server**:
   ```bash
   python main.py
   ```

### Truy cập Admin Panel
- **URL**: `http://localhost:8000/admin`
- **Dashboard**: `http://localhost:8000/admin/dashboard`
- **Users**: `http://localhost:8000/admin/users`
- **Reports**: `http://localhost:8000/admin/reports`
- **Settings**: `http://localhost:8000/admin/settings`

## 📊 API Endpoints

### Admin Routes
```
GET  /admin                 - Dashboard tổng quan
GET  /admin/dashboard       - Dashboard (alias)
GET  /admin/users           - Quản lý người dùng
GET  /admin/meal-plans      - Quản lý kế hoạch bữa ăn
GET  /admin/reports         - Báo cáo & thống kê
GET  /admin/settings        - Cấu hình hệ thống
```

### Food Management Routes
```
GET  /                      - Trang chủ
GET  /food                  - Danh sách món ăn
GET  /food/create           - Tạo món ăn mới
GET  /food/{id}             - Chi tiết món ăn
GET  /food/edit/{id}        - Chỉnh sửa món ăn
POST /api/generate-meal     - Tạo món ăn với AI
```

## 🔧 Cấu hình

### Environment Variables
```bash
# Firebase
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# API Keys
GROQ_API_KEY=your-groq-api-key
USDA_API_KEY=your-usda-api-key

# Security
JWT_SECRET=your-jwt-secret

# Performance
MAX_WORKERS=4
REQUEST_TIMEOUT=30
```

### Firebase Collections
- `users` - Thông tin người dùng
- `meal_plans` - Kế hoạch bữa ăn
- `latest_meal_plans` - Kế hoạch bữa ăn mới nhất
- `exercises` - Bài tập
- `water_entries` - Lượng nước uống
- `chat_history` - Lịch sử chat với AI

## 🎯 Tính năng nâng cao

### Real-time Updates
- **Auto-refresh**: Tự động cập nhật dữ liệu mỗi 30 giây
- **Status monitoring**: Theo dõi trạng thái hệ thống real-time
- **Notification system**: Thông báo in-app và browser notifications

### Export & Import
- **CSV Export**: Xuất dữ liệu người dùng, món ăn ra CSV
- **JSON Export**: Xuất cấu hình và dữ liệu ra JSON
- **Backup**: Sao lưu dữ liệu định kỳ

### Security Features
- **Rate limiting**: Giới hạn số request per minute/day
- **CORS protection**: Bảo vệ cross-origin requests
- **Input validation**: Kiểm tra và làm sạch dữ liệu đầu vào
- **Error handling**: Xử lý lỗi an toàn và thông báo phù hợp

## 🐛 Troubleshooting

### Lỗi thường gặp

1. **Firebase connection failed**:
   - Kiểm tra file credentials
   - Verify project ID
   - Check network connectivity

2. **AI API timeout**:
   - Kiểm tra API key
   - Tăng timeout setting
   - Check rate limits

3. **Charts not loading**:
   - Verify Chart.js is loaded
   - Check console for JavaScript errors
   - Ensure data format is correct

### Debug Mode
```bash
# Bật debug logging
export LOG_LEVEL=DEBUG
python main.py
```

## 📝 Changelog

### Version 1.0.0
- ✅ Dashboard tổng quan với thống kê real-time
- ✅ Quản lý người dùng với tìm kiếm và phân trang
- ✅ Quản lý kế hoạch bữa ăn
- ✅ Báo cáo và thống kê với biểu đồ
- ✅ Cấu hình hệ thống toàn diện
- ✅ Responsive design và dark mode
- ✅ Export/import functionality
- ✅ Real-time notifications

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

Nếu bạn gặp vấn đề hoặc cần hỗ trợ:
- Tạo issue trên GitHub
- Email: support@openfood.com
- Documentation: `/docs` endpoint
