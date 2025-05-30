# Hướng dẫn triển khai DietAI API lên Render

## Chuẩn bị
1. Đăng ký tài khoản [Render](https://render.com/) nếu chưa có.
2. Đảm bảo mã nguồn đã được đẩy lên GitHub.

## Các bước triển khai

### Phương pháp 1: Bằng cách sử dụng Dashboard của Render

1. Đăng nhập vào tài khoản Render của bạn.
2. Nhấp vào nút "New+" ở góc trên bên phải và chọn "Web Service".
3. Kết nối repository GitHub của bạn hoặc nhập URL của nó.
4. Cấu hình như sau:
   - **Name**: Đặt tên cho service (ví dụ: dietai-api)
   - **Environment**: Python
   - **Region**: Chọn region gần vị trí của bạn nhất
   - **Branch**: main (hoặc nhánh bạn muốn triển khai)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Cấu hình môi trường (Environment Variables) nếu cần:
   - Đảm bảo thêm bất kỳ biến môi trường nào mà ứng dụng của bạn sử dụng
   - Đặc biệt là các khóa API như Firebase hoặc Gemini nếu có sử dụng
6. Nhấp vào "Create Web Service" để bắt đầu quá trình triển khai.

### Phương pháp 2: Bằng cách sử dụng render.yaml

1. Đảm bảo đã thêm tệp `render.yaml` vào thư mục gốc của dự án.
2. Đăng nhập vào Render.
3. Nhấp vào "New+" và chọn "Blueprint".
4. Kết nối repository GitHub chứa tệp render.yaml của bạn.
5. Render sẽ tự động phát hiện tệp cấu hình và tạo các dịch vụ được chỉ định.
6. Xem lại cấu hình và nhấp vào "Apply" để triển khai.

## Sau khi triển khai

1. Truy cập API thông qua URL mà Render cung cấp (thường có dạng `https://[service-name].onrender.com`).
2. Truy cập `/docs` để xem trang Swagger UI của FastAPI và kiểm tra tài liệu API.

## Lưu ý quan trọng

1. Render cung cấp một tầng miễn phí nhưng có một số hạn chế:
   - Dịch vụ miễn phí sẽ "ngủ" sau 15 phút không hoạt động, và mất một chút thời gian để khởi động lại khi có yêu cầu mới.
   - Có giới hạn về số giờ sử dụng mỗi tháng.

2. Đối với môi trường sản xuất, hãy cân nhắc nâng cấp lên gói trả phí của Render để có hiệu suất tốt hơn và thời gian hoạt động liên tục.

3. Nếu bạn sử dụng các dịch vụ Firebase, hãy đảm bảo tệp xác thực Firebase (`firebase-credentials.json`) đã được thêm vào Render dưới dạng biến môi trường hoặc tệp cấu hình bí mật. 