import os
import sys

# Thêm thông tin header
print("===== KIỂM TRA TÍCH HỢP AI =====")

# Kiểm tra biến môi trường
print("\n--- KIỂM TRA BIẾN MÔI TRƯỜNG ---")
has_groq = os.getenv("GROQ_API_KEY") is not None
print(f"GROQ_API_KEY: {'Đã thiết lập' if has_groq else 'Chưa thiết lập'}")

# Kiểm tra thư viện
print("\n--- KIỂM TRA THƯ VIỆN ---")
has_groq_lib = False

try:
    import groq
    has_groq_lib = True
    print(f"Thư viện Groq: Đã cài đặt (phiên bản {groq.__version__})")
except ImportError:
    print("Thư viện Groq: Chưa cài đặt")

# Kiểm tra dịch vụ
print("\n--- KIỂM TRA DỊCH VỤ ---")
groq_available = False

try:
    from groq_integration_direct import groq_service  # Fixed version
    groq_available = groq_service.available
    print(f"Dịch vụ Groq (LLaMA 3): {'Khả dụng' if groq_available else 'Không khả dụng'}")
    if groq_available:
        print(f"  - Model: {getattr(groq_service, 'model', 'unknown')}")
        print(f"  - API Key: ***{groq_service.api_key[-4:] if groq_service.api_key else 'None'}")
except Exception as e:
    print(f"Lỗi khi kiểm tra Groq: {str(e)}")

# Kiểm tra services.py
print("\n--- KIỂM TRA MODULE SERVICES ---")
try:
    # Import trực tiếp từ module services.py (tệp tin) thay vì package services (thư mục)
    import services as services_module
    AI_SERVICE = getattr(services_module, 'AI_SERVICE', None)
    AI_AVAILABLE = getattr(services_module, 'AI_AVAILABLE', False)
    print(f"AI Service: {AI_SERVICE.__class__.__name__ if AI_SERVICE else 'None'}")
    print(f"AI Available: {AI_AVAILABLE}")
except Exception as e:
    print(f"Lỗi khi kiểm tra services.py: {str(e)}")

# Kết luận
print("\n--- KẾT LUẬN ---")
if groq_available:
    print("LLaMA 3 qua Groq đã sẵn sàng để sử dụng")
elif has_groq and not groq_available:
    print("Cần kiểm tra API key Groq (có thể không hợp lệ)")
else:
    print("Không có dịch vụ AI nào sẵn sàng")
    print("Hướng dẫn:")
    print("1. Cài đặt thư viện Groq: pip install groq")
    print("2. Thiết lập biến môi trường GROQ_API_KEY với API key của bạn")
    print("   - Windows: set GROQ_API_KEY=your_key_here")
    print("   - Linux/Mac: export GROQ_API_KEY=your_key_here")
    print("3. Hoặc tạo file .env với nội dung: GROQ_API_KEY=your_key_here") 