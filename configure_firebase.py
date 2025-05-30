"""
Script để cấu hình Firebase Storage Bucket
"""
import os
import json

def configure_firebase_storage():
    """Cấu hình Firebase Storage Bucket"""
    
    print("\n=== FIREBASE STORAGE BUCKET CONFIGURATION ===")
    
    # Kiểm tra config.py
    config_file = "config.py"
    if not os.path.exists(config_file):
        print(f"Creating new config.py file...")
        with open(config_file, "w") as f:
            f.write('"""\nConfig file for application settings\n"""\n\n')
            f.write('# Firebase settings\n')
            f.write('FIREBASE_STORAGE_BUCKET = ""\n')
    
    # Đọc cấu hình hiện tại
    current_bucket = ""
    try:
        with open(config_file, "r") as f:
            config_content = f.read()
            # Tìm giá trị hiện tại
            import re
            bucket_match = re.search(r'FIREBASE_STORAGE_BUCKET\s*=\s*["\']([^"\']*)["\']', config_content)
            if bucket_match:
                current_bucket = bucket_match.group(1)
    except Exception as e:
        print(f"Error reading config file: {str(e)}")
    
    print(f"Current Storage Bucket: '{current_bucket}'")
    
    # Kiểm tra file firebase-credentials.json
    credentials_file = "firebase-credentials.json"
    if os.path.exists(credentials_file):
        print(f"Found Firebase credentials file: {credentials_file}")
        try:
            with open(credentials_file, "r") as f:
                creds = json.load(f)
                project_id = creds.get("project_id", "")
                if project_id:
                    print(f"Detected project ID: {project_id}")
                    suggested_bucket = f"{project_id}.appspot.com"
                    print(f"Suggested bucket name: {suggested_bucket}")
                else:
                    print("No project ID found in credentials file")
                    suggested_bucket = ""
        except Exception as e:
            print(f"Error reading credentials file: {str(e)}")
            suggested_bucket = ""
    else:
        print(f"Firebase credentials file not found: {credentials_file}")
        suggested_bucket = ""
    
    # Nhận bucket mới từ người dùng
    new_bucket = input(f"Enter new Storage Bucket name (or press Enter to use '{suggested_bucket if suggested_bucket else current_bucket}'): ").strip()
    
    if not new_bucket and suggested_bucket:
        new_bucket = suggested_bucket
    elif not new_bucket:
        new_bucket = current_bucket
    
    if new_bucket:
        # Cập nhật config.py
        try:
            if current_bucket:
                # Thay thế giá trị hiện có
                with open(config_file, "r") as f:
                    content = f.read()
                
                updated_content = re.sub(
                    r'FIREBASE_STORAGE_BUCKET\s*=\s*["\']([^"\']*)["\']', 
                    f'FIREBASE_STORAGE_BUCKET = "{new_bucket}"', 
                    content
                )
                
                with open(config_file, "w") as f:
                    f.write(updated_content)
            else:
                # Thêm dòng mới nếu không tìm thấy
                with open(config_file, "a", encoding="utf-8") as f:
                    f.write(f'\nFIREBASE_STORAGE_BUCKET = "{new_bucket}"\n')
            
            print(f"Successfully updated Storage Bucket to: {new_bucket}")
        except Exception as e:
            print(f"Error updating config file: {str(e)}")
    else:
        print("No Storage Bucket specified. Configuration unchanged.")
    
    print("\nTo apply changes, restart your server.")
    print("=== CONFIGURATION COMPLETE ===")

if __name__ == "__main__":
    configure_firebase_storage() 