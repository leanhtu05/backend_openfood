"""
Script để chạy tất cả các test theo trình tự
"""
import os
import sys
import subprocess
import time

def run_command(command, description):
    """Chạy một lệnh và trả về kết quả"""
    print(f"\n\n{'='*50}")
    print(f"=== {description} ===")
    print(f"{'='*50}")
    print(f"Command: {command}")
    print(f"{'-'*50}\n")
    
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"\n{'-'*50}")
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{'-'*50}")
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False

def run_tests():
    """Chạy tất cả các test theo trình tự"""
    
    print("\n=== RUNNING ALL TESTS ===\n")
    
    # 1. Kiểm tra cấu hình Firebase Storage Bucket
    run_command("python configure_firebase.py", "Configure Firebase Storage Bucket")
    
    # 2. Kiểm tra kết nối với Groq và thử nhiều temperature
    run_command("python test_groq_direct_output.py", "Test Groq API with different temperatures")
    
    # 3. Kiểm tra cấu trúc meal plan từ Firebase
    run_command("python test_firebase_meal_plan.py", "Test Firebase meal plan structure")
    
    # 4. Chạy server debug (không chạy cái này, chỉ hiển thị hướng dẫn)
    print(f"\n\n{'='*50}")
    print(f"=== RUNNING THE SERVER (MANUAL STEP) ===")
    print(f"{'='*50}")
    print("To run the server in debug mode, open a new terminal and execute:")
    print("python run_debug_server.py")
    print("\nAfter the server is running, open another terminal and run:")
    print("python test_flutter_groq_firebase.py")
    print(f"{'='*50}\n")
    
    # Hỏi người dùng có muốn chạy test_flutter_groq_firebase.py không
    run_full_test = input("Do you want to run the full test (test_flutter_groq_firebase.py)? (y/n): ").strip().lower()
    
    if run_full_test == 'y':
        # Kiểm tra xem server có đang chạy không
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_running = False
        try:
            # Kết nối đến port 8000
            sock.connect(('localhost', 8000))
            server_running = True
        except:
            server_running = False
        finally:
            sock.close()
        
        if server_running:
            # Chạy test full quy trình
            run_command("python test_flutter_groq_firebase.py", "Test full data flow: Flutter → Groq → Firebase")
        else:
            print("\n❌ Server is not running. Please start the server first.")
            print("Run 'python run_debug_server.py' in a separate terminal, then try again.")
    
    print("\n=== ALL TESTS COMPLETED ===")

if __name__ == "__main__":
    run_tests() 