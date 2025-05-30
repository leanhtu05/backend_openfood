"""
Script chạy server FastAPI thống nhất (tích hợp cả chat API)
"""
import os
import subprocess
import sys

# Nhập uvicorn
import uvicorn

def setup_and_run():
    """Thiết lập biến môi trường và chạy FastAPI server"""
    print("=== KHỞI ĐỘNG SERVER THỐNG NHẤT ===")
    
    # Kiểm tra GROQ_API_KEY
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        print("\nGROQ_API_KEY chưa được thiết lập.")
        setup_key = input("Bạn có muốn thiết lập GROQ_API_KEY ngay bây giờ? (y/n): ")
        
        if setup_key.lower() == "y":
            api_key = input("Nhập GROQ_API_KEY của bạn: ")
            os.environ["GROQ_API_KEY"] = api_key
            print("Đã thiết lập GROQ_API_KEY.")
        else:
            print("\nLưu ý: Chat API sẽ không hoạt động nếu không có GROQ_API_KEY!")
            print("Bạn vẫn có thể sử dụng các API dinh dưỡng khác.")
    else:
        print(f"GROQ_API_KEY đã được thiết lập: {groq_api_key[:4]}...{groq_api_key[-4:]}")
    
    # Hiển thị thông tin
    print("\n=== THÔNG TIN SERVER ===")
    print("• Server sẽ chạy tại: http://localhost:8000")
    print("• Tài liệu API: http://localhost:8000/docs")
    print("• Tất cả API (kể cả chat) đều có trên cùng một cổng.")
    print("• Nhấn Ctrl+C để dừng server.")
    
    print("\n=== KHỞI ĐỘNG SERVER ===")
    
    # Chạy server FastAPI
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n\n=== SERVER ĐÃ DỪNG ===")
    except Exception as e:
        print(f"\nLỗi khi chạy server: {str(e)}")
        
if __name__ == "__main__":
    setup_and_run() 