# DietAI Backend API

Backend API cho ứng dụng DietAI - quản lý và đề xuất kế hoạch dinh dưỡng cá nhân.

## Yêu cầu hệ thống

- Python 3.9+
- pip (trình quản lý gói của Python)

## Cài đặt

1. Clone repository hoặc tải xuống mã nguồn

2. Tạo và kích hoạt môi trường ảo (khuyến nghị):

```bash
# Windows

python -m venv venv
venv\Scripts\activate
venv\Scripts\activate
# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Cài đặt các gói phụ thuộc:

```bash
pip install -r requirements.txt
```

4. Cấu hình Nutritionix API (tùy chọn):

Đăng ký tài khoản tại [Nutritionix](https://www.nutritionix.com/business/api) để lấy API key và App ID. Sau đó, cập nhật các biến môi trường sau trong tệp `.env` hoặc trực tiếp trong tệp `nutritionix.py`:

```
NUTRITIONIX_APP_ID=your_app_id
NUTRITIONIX_API_KEY=your_api_key
```

## Chạy ứng dụng

Chạy server phát triển:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

```

API sẽ chạy tại: http://localhost:8000

Tài liệu API tự động được tạo ra tại: http://localhost:8000/docs

## API Endpoints

### 1. POST /generate-weekly-meal

Tạo kế hoạch thực đơn cho cả tuần dựa trên mục tiêu dinh dưỡng.

**Request:**

```json
{
  "calories_target": 2000,
  "protein_target": 150,
  "fat_target": 70,
  "carbs_target": 200
}
```

**Query Parameters:**
- `user_id` (tùy chọn): ID người dùng để lưu kế hoạch (mặc định: "default")

**Response:** Kế hoạch thực đơn chi tiết cho 7 ngày.

### 2. POST /replace-day

Thay thế kế hoạch thực đơn cho một ngày cụ thể.

**Request:**

```json
{
  "day_of_week": "Thứ 2",
  "calories_target": 1800,
  "protein_target": 140,
  "fat_target": 60,
  "carbs_target": 180
}
```

**Query Parameters:**
- `user_id` (tùy chọn): ID người dùng (mặc định: "default")

**Response:** Kế hoạch thực đơn mới cho ngày được chỉ định.

### 3. POST /replace-week

Tạo lại kế hoạch thực đơn cho cả tuần.

**Request:** Giống với `/generate-weekly-meal`.

**Query Parameters:**
- `user_id` (tùy chọn): ID người dùng (mặc định: "default")

### 4. GET /meal-plan-history

Lấy lịch sử kế hoạch thực đơn của người dùng.

**Query Parameters:**
- `user_id` (tùy chọn): ID người dùng (mặc định: "default")
- `limit` (tùy chọn): Số lượng kế hoạch tối đa trả về (mặc định: 10)

**Response:** Danh sách các kế hoạch thực đơn đã tạo trước đây.

### 5. DELETE /meal-plan/{filename}

Xóa một kế hoạch thực đơn cụ thể.

**Path Parameters:**
- `filename`: Tên file cần xóa

**Response:** Thông báo kết quả xóa.

## Ví dụ sử dụng API

### Sử dụng cURL

```bash
# Tạo kế hoạch thực đơn hàng tuần
curl -X POST "http://localhost:8000/generate-weekly-meal?user_id=user123" \
  -H "Content-Type: application/json" \
  -d '{"calories_target": 2000, "protein_target": 150, "fat_target": 70, "carbs_target": 200}'

# Thay thế kế hoạch thực đơn cho một ngày
curl -X POST "http://localhost:8000/replace-day?user_id=user123" \
  -H "Content-Type: application/json" \
  -d '{"day_of_week": "Thứ 2", "calories_target": 1800, "protein_target": 140, "fat_target": 60, "carbs_target": 180}'

# Lấy lịch sử kế hoạch thực đơn
curl -X GET "http://localhost:8000/meal-plan-history?user_id=user123&limit=5"

# Xóa một kế hoạch thực đơn
curl -X DELETE "http://localhost:8000/meal-plan/user123_20230815_123456.json"
```

### Sử dụng Postman

1. Tạo một yêu cầu POST mới đến `http://localhost:8000/generate-weekly-meal?user_id=user123`
2. Đặt header `Content-Type: application/json`
3. Thêm body JSON:
```json
{
  "calories_target": 2000,
  "protein_target": 150,
  "fat_target": 70,
  "carbs_target": 200
}
```
4. Gửi yêu cầu và xem kết quả

## Cấu trúc dự án

```
backend/
├── main.py           # Khởi tạo FastAPI và các route
├── models.py         # Định nghĩa Pydantic schemas
├── nutritionix.py    # Tích hợp Nutritionix API
├── services.py       # Logic sinh meal plan
├── storage.py        # Xử lý lưu trữ dữ liệu file-based
├── utils.py          # Hàm tiện ích
├── requirements.txt  # Danh sách các gói phụ thuộc
├── README.md         # Tài liệu
└── data/             # Thư mục lưu trữ dữ liệu
    └── meal_plans/   # Kế hoạch thực đơn được lưu dưới dạng JSON
```

## Hệ thống lưu trữ dữ liệu

API sử dụng hệ thống lưu trữ dữ liệu dựa trên file JSON:

- Mỗi kế hoạch thực đơn được lưu thành một file JSON riêng trong thư mục `data/meal_plans/`
- Tên file được tạo theo format: `user_id_timestamp.json` (ví dụ: `user123_20230815_123456.json`)
- Ngoài ra, kế hoạch thực đơn mới nhất của mỗi người dùng luôn được lưu với tên `user_id_latest.json`
- Hệ thống hỗ trợ nhiều người dùng qua tham số `user_id` trong API
- Các kế hoạch thực đơn cũ vẫn được giữ lại để xem lịch sử

Ưu điểm của hệ thống lưu trữ file:
- Dễ triển khai, không cần cài đặt cơ sở dữ liệu
- Dữ liệu được lưu trữ lâu dài và không bị mất khi khởi động lại server
- Hỗ trợ lưu trữ lịch sử kế hoạch thực đơn
- Dễ dàng mở rộng để hỗ trợ nhiều người dùng

## Lưu ý

- Trong môi trường sản xuất với số lượng người dùng lớn, nên cân nhắc sử dụng cơ sở dữ liệu như MongoDB hoặc PostgreSQL thay vì lưu trữ file.
- Dữ liệu công thức và dinh dưỡng hiện là dữ liệu mẫu. Trong ứng dụng thực tế, bạn sẽ sử dụng dữ liệu từ Nutritionix API hoặc cơ sở dữ liệu của riêng bạn.

# Tích hợp USDA FoodData Central API (Tìm kiếm bằng tiếng Việt)

API hỗ trợ tìm kiếm thông tin dinh dưỡng của thực phẩm từ cơ sở dữ liệu USDA FoodData Central, với khả năng tìm kiếm bằng tiếng Việt.

## Đăng ký USDA API Key

1. Truy cập trang đăng ký API key: https://fdc.nal.usda.gov/api-key-signup.html
2. Điền thông tin và gửi đơn đăng ký
3. Bạn sẽ nhận được API key qua email
4. Thêm API key vào file `.env`:

```
USDA_API_KEY=your_api_key_here
```

## Các endpoint USDA API

### 1. Tìm kiếm thực phẩm

```
GET /usda/search?query={query}&vietnamese={vietnamese}&max_results={max_results}
```

**Tham số**:
- `query`: Từ khóa tìm kiếm (tiếng Việt hoặc tiếng Anh)
- `vietnamese`: `true` nếu truy vấn là tiếng Việt, `false` nếu là tiếng Anh (mặc định: `true`)
- `max_results`: Số kết quả tối đa trả về (mặc định: 10)

**Ví dụ**:
```
GET /usda/search?query=cơm tấm&vietnamese=true&max_results=5
```

### 2. Lấy thông tin chi tiết về thực phẩm

```
GET /usda/food/{food_id}
```

**Tham số**:
- `food_id`: ID của thực phẩm trong USDA FoodData Central

**Ví dụ**:
```
GET /usda/food/1750340
```

### 3. Lấy thông tin dinh dưỡng

```
GET /usda/nutrition?query={query}&amount={amount}&vietnamese={vietnamese}
```

**Tham số**:
- `query`: Tên thực phẩm cần tìm (tiếng Việt hoặc tiếng Anh)
- `amount`: Số lượng (ví dụ: '100g', '1 cup') (tùy chọn)
- `vietnamese`: `true` nếu truy vấn là tiếng Việt, `false` nếu là tiếng Anh (mặc định: `true`)

**Ví dụ**:
```
GET /usda/nutrition?query=100g gạo&vietnamese=true
```

### 4. Dịch tên thực phẩm từ tiếng Việt sang tiếng Anh

```
GET /usda/translate?vietnamese_query={vietnamese_query}
```

**Tham số**:
- `vietnamese_query`: Tên thực phẩm bằng tiếng Việt

**Ví dụ**:
```
GET /usda/translate?vietnamese_query=thịt bò xào rau muống
```

### 5. Xóa cache USDA API

```
POST /usda/clear-cache
```

## Cấu hình USDA API

Các tùy chọn cấu hình cho USDA API được đặt trong file `config.py`:

```python
# USDA API Settings
USE_USDA_CACHE: bool = os.getenv("USE_USDA_CACHE", "True").lower() in ('true', 'yes', '1')
USDA_CACHE_TTL_DAYS: int = int(os.getenv("USDA_CACHE_TTL_DAYS", "30"))
```

Bạn có thể thiết lập các giá trị này trong file `.env`:

```
# USDA API Settings
USE_USDA_CACHE=True
USDA_CACHE_TTL_DAYS=30
```

# Chat API với Groq (Tích hợp)

API tương tác với Groq LLM, sử dụng mô hình llama3-8b-8192 để trả lời các câu hỏi về ẩm thực, được tích hợp trực tiếp vào server FastAPI chính.

## Yêu cầu

- Python 3.7+
- FastAPI
- OpenAI SDK (cập nhật)
- Groq API key

## Cài đặt

1. Thiết lập Groq API key:
```bash
export GROQ_API_KEY="your-api-key-here"  # Trên Linux/Mac
set GROQ_API_KEY=your-api-key-here       # Trên Windows
```

## Chạy Server Thống Nhất

Sử dụng script chạy server thống nhất để khởi động tất cả các API (bao gồm cả Chat API) trên cùng một cổng:

```bash
python run_unified_server.py
```

Server sẽ chạy tại `http://localhost:8000` và tất cả các API đều có sẵn trên cổng này.

## Kiểm tra API

Bạn có thể kiểm tra tất cả các API (bao gồm cả Chat API) bằng script test:
```bash
python integration_test.py
```

Hoặc sử dụng curl:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Gợi ý một số món ăn lành mạnh cho bữa tối"}'
```

## Sử dụng API

### Endpoint: POST /chat

**Request:**
```json
{
  "message": "Món ăn nào tốt cho người bị tiểu đường?"
}
```

**Response:**
```json
{
  "reply": "Có nhiều món ăn phù hợp cho người tiểu đường..."
}
```

## Tích hợp với ứng dụng

Bạn có thể tích hợp Chat API vào ứng dụng bằng cách gửi yêu cầu HTTP POST tới endpoint `/chat` với dữ liệu JSON có trường `message`. 