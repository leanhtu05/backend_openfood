# Hướng dẫn cập nhật thông tin người dùng từ Flutter lên Firestore qua FastAPI

Tài liệu này mô tả chi tiết luồng cập nhật thông tin người dùng từ Flutter thông qua FastAPI và lưu vào Firestore.

## Sơ đồ luồng dữ liệu

```
Flutter → FastAPI → Firestore
```

## 1. Từ phía Flutter

### Chuẩn bị dữ liệu

```dart
// Lấy thông tin người dùng từ form
final userId = FirebaseAuth.instance.currentUser!.uid;
final idToken = await FirebaseAuth.instance.currentUser!.getIdToken();

// Chuẩn bị dữ liệu cần cập nhật
final userData = {
  "name": "Nguyễn Văn A",
  "age": 25,
  "gender": "male",
  "height": 170,
  "weight": 65,
  "goal": "giảm cân",
  "activityLevel": "moderate",
  "dietType": "omnivore",
  "preferred_cuisines": ["Việt Nam", "Ý", "Nhật Bản"],
  "allergies": ["hải sản", "lạc"]
};
```

### Gửi request lên FastAPI

```dart
final response = await http.patch(
  Uri.parse('https://your-api.com/firestore/users/$userId'),
  headers: {
    'Authorization': 'Bearer $idToken',
    'Content-Type': 'application/json',
  },
  body: jsonEncode(userData),
);

if (response.statusCode == 200) {
  print('Cập nhật thông tin thành công');
} else {
  print('Lỗi: ${response.body}');
}
```

## 2. Từ phía FastAPI

### Endpoint xử lý cập nhật thông tin người dùng

FastAPI đã được cấu hình với endpoint `/firestore/users/{user_id}` với phương thức PATCH để xử lý cập nhật thông tin người dùng. Endpoint này:

1. Xác thực Firebase ID Token
2. Kiểm tra xem người dùng có quyền cập nhật thông tin không (user_id trong token phải khớp với user_id trong URL)
3. Cập nhật thông tin vào Firestore

### Mã nguồn endpoint

```python
@router.patch("/users/{user_id}")
async def update_user(
    user_id: str, 
    user_data: FlutterUserUpdate,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Cập nhật thông tin người dùng từ Flutter
    
    Args:
        user_id: ID của người dùng cần cập nhật
        user_data: Dữ liệu người dùng cần cập nhật
        current_user: Thông tin người dùng đã xác thực từ token
        
    Returns:
        Thông báo cập nhật thành công
    """
    # Kiểm tra token khớp với người dùng
    if user_id != current_user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Không có quyền sửa thông tin người dùng khác"
        )
    
    try:
        # Chuyển đổi dữ liệu từ model thành dict
        update_data = user_data.to_dict()
        
        # Thêm thời gian cập nhật
        update_data["updated_at"] = datetime.now().isoformat()
        
        # Cập nhật thông tin người dùng trong Firestore
        success = firestore_service.update_user(user_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Không thể cập nhật thông tin người dùng"
            )
            
        return {"message": "Cập nhật thông tin người dùng thành công"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Lỗi khi cập nhật thông tin người dùng: {str(e)}"
        )
```

### Model dữ liệu

```python
class FlutterUserUpdate(BaseModel):
    """Model cho dữ liệu cập nhật từ Flutter"""
    name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None
    goal: Optional[str] = None
    activityLevel: Optional[str] = None
    dietType: Optional[str] = None
    preferred_cuisines: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    tdeeValues: Optional[TDEEValues] = None
    heightCm: Optional[float] = None
    weightKg: Optional[float] = None
```

## 3. Từ phía Firestore

Dữ liệu người dùng được lưu trong collection `users` với document ID là Firebase UID của người dùng. Cấu trúc dữ liệu:

```json
{
  "name": "Nguyễn Văn A",
  "email": "example@gmail.com",
  "age": 25,
  "gender": "male",
  "height": 170,
  "weight": 65,
  "goal": "giảm cân",
  "activityLevel": "moderate",
  "dietType": "omnivore",
  "preferred_cuisines": ["Việt Nam", "Ý", "Nhật Bản"],
  "allergies": ["hải sản", "lạc"],
  "created_at": "2023-08-15T10:30:00.000Z",
  "updated_at": "2023-08-16T15:45:00.000Z",
  "tdeeValues": {
    "calories": 2000,
    "carbs": 250,
    "fat": 65,
    "protein": 150
  }
}
```

## 4. Xác thực và bảo mật

### Firebase Authentication

- Sử dụng Firebase Authentication để xác thực người dùng
- Mỗi request từ Flutter phải kèm theo Firebase ID Token trong header `Authorization`
- FastAPI xác thực token và chỉ cho phép người dùng cập nhật thông tin của chính họ

### Xử lý lỗi

FastAPI trả về các mã lỗi HTTP phù hợp:
- 401: Token không hợp lệ hoặc hết hạn
- 403: Không có quyền sửa thông tin người dùng khác
- 404: Không tìm thấy người dùng
- 500: Lỗi server khi cập nhật thông tin

## 5. Kiểm tra API

Bạn có thể sử dụng script `test_update_user.py` để kiểm tra API:

```bash
python test_update_user.py
```

Script này sẽ:
1. Tạo một user test trong Firebase nếu chưa có
2. Tạo custom token và yêu cầu bạn nhập ID token
3. Gửi request cập nhật thông tin người dùng
4. Hiển thị kết quả

## 6. Lưu ý khi triển khai

1. Đảm bảo đã cấu hình CORS cho FastAPI để cho phép request từ ứng dụng Flutter
2. Kiểm tra kỹ các quyền trong Firebase Security Rules để đảm bảo chỉ người dùng có quyền mới có thể cập nhật thông tin
3. Xử lý các trường hợp lỗi và hiển thị thông báo phù hợp cho người dùng
4. Cân nhắc thêm validation dữ liệu đầu vào để đảm bảo dữ liệu hợp lệ trước khi lưu vào Firestore 