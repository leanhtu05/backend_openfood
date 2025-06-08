"""
Script kiểm tra cài đặt cấu hình USE_ENHANCED_DISH_INFO
"""
import os
from config import config

# Kiểm tra giá trị hiện tại
print(f"USE_ENHANCED_DISH_INFO hiện tại: {config.USE_ENHANCED_DISH_INFO}")
print(f"Giá trị từ biến môi trường: {os.environ.get('USE_ENHANCED_DISH_INFO', 'không đặt')}")

# Đặt giá trị thành True
os.environ['USE_ENHANCED_DISH_INFO'] = "1"

# Tải lại cấu hình (để áp dụng giá trị mới)
from importlib import reload
import config as config_module
reload(config_module)
from config import config as new_config

# Kiểm tra lại
print(f"USE_ENHANCED_DISH_INFO sau khi đặt: {new_config.USE_ENHANCED_DISH_INFO}") 