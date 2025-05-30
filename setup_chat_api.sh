#!/bin/bash

echo "=== Cài đặt Chat API với Groq ==="

# Cài đặt các thư viện cần thiết
echo "Đang cài đặt các thư viện cần thiết..."
pip install flask openai requests

# Nhắc nhở về API key
echo ""
echo "=== QUAN TRỌNG ==="
echo "Bạn cần thiết lập Groq API key trước khi chạy API:"
echo ""
echo "Trên Linux/Mac:"
echo "  export GROQ_API_KEY=\"your-api-key-here\""
echo ""
echo "Trên Windows:"
echo "  set GROQ_API_KEY=your-api-key-here"
echo ""

# Hướng dẫn chạy API
echo "=== Hướng dẫn chạy API ==="
echo "1. Thiết lập API key như hướng dẫn trên"
echo "2. Chạy: python chat_endpoint.py"
echo "3. Server sẽ khởi động tại http://localhost:5000"
echo "4. Kiểm tra API với: python test_chat_endpoint.py"
echo ""
echo "Cài đặt hoàn tất!" 