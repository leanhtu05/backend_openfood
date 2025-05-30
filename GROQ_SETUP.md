# Hướng dẫn thiết lập Groq API để sử dụng LLaMA 3

## Giới thiệu

Dự án này đã được cập nhật để sử dụng LLaMA 3 của Meta thông qua Groq API. Groq cung cấp một nền tảng suy luận siêu nhanh cho các mô hình LLM, bao gồm LLaMA 3. Ưu điểm của Groq so với Gemini là:

1. **Không hạn chế về địa lý** - Hoạt động toàn cầu
2. **Hiệu suất cao hơn** - Tốc độ phản hồi nhanh hơn
3. **API linh hoạt** - Tương thích với OpenAI API format
4. **Nhiều mô hình** - Hỗ trợ các mô hình khác nhau như LLaMA 3 và Mixtral

## Các bước thiết lập

### 1. Đăng ký tài khoản Groq

1. Truy cập [console.groq.com](https://console.groq.com) và đăng ký tài khoản mới
2. Xác nhận email của bạn và đăng nhập vào tài khoản

### 2. Tạo API Key

1. Trong console Groq, chọn "API Keys" từ menu bên trái
2. Nhấp vào "Create API Key"
3. Đặt tên cho API key (ví dụ: "DietAI Integration")
4. Sao chép API key được tạo - **LƯU Ý: API key sẽ chỉ hiển thị một lần**

### 3. Cài đặt thư viện Groq

Chạy lệnh sau để cài đặt thư viện Groq Python:

```bash
pip install groq
```

Hoặc nếu bạn đã clone dự án, chạy:

```bash
pip install -r requirements.txt
```

### 4. Cấu hình API Key

Có hai cách để cấu hình API key:

#### Cách 1: Sử dụng biến môi trường

**Windows:**
```bash
set GROQ_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export GROQ_API_KEY=your_api_key_here
```

#### Cách 2: Sử dụng tệp .env

1. Tạo file `.env` trong thư mục gốc của dự án
2. Thêm dòng sau vào file:
```
GROQ_API_KEY=your_api_key_here
```

### 5. Kiểm tra cài đặt

Để kiểm tra xem Groq API đã được cấu hình đúng chưa, chạy script kiểm tra:

```bash
python check_groq.py
```

hoặc

```bash
python check_ai_services.py
```

Nếu mọi thứ đều đúng, bạn sẽ thấy thông báo "Groq available: True" và thông tin về model được sử dụng.

## Các mô hình có sẵn

Groq cung cấp nhiều mô hình khác nhau, bao gồm:

1. **llama3-70b-8192** - LLaMA 3 70B (mạnh nhất, hiệu suất cao nhất)
2. **llama3-8b-8192** - LLaMA 3 8B (cân bằng tốt giữa tốc độ và hiệu suất)
3. **mixtral-8x7b-32768** - Mixtral (lựa chọn thay thế nếu LLaMA không khả dụng)

Dự án được cấu hình để tự động chọn mô hình tốt nhất có sẵn, ưu tiên theo thứ tự trên.

## Xử lý lỗi phổ biến

### API Key không hợp lệ
Nếu bạn nhận được lỗi "API key not valid", hãy đảm bảo bạn đã sao chép đúng API key từ console Groq.

### Không thể kết nối đến Groq API
Kiểm tra kết nối internet của bạn và đảm bảo không có tường lửa hoặc proxy chặn kết nối đến api.groq.com.

### Mô hình không được tìm thấy
Nếu bạn nhận được lỗi về mô hình không có sẵn, hãy kiểm tra danh sách mô hình hiện tại trên [trang tài liệu Groq](https://console.groq.com/docs/models). 