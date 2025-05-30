from flask import Flask, request, jsonify
import os
from openai import OpenAI

app = Flask(__name__)

# Khởi tạo Groq client với API key từ biến môi trường
groq_api_key = os.environ.get("GROQ_API_KEY", "")
if not groq_api_key:
    print("CẢNH BÁO: GROQ_API_KEY không được thiết lập")

client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint nhận tin nhắn từ người dùng, xử lý qua Groq API và trả về phản hồi
    Ví dụ request: {"message": "Món ăn nào tốt cho người bị tiểu đường?"}
    Ví dụ response: {"reply": "Có nhiều món ăn phù hợp cho người tiểu đường..."}
    """
    try:
        # Nhận message từ request
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Vui lòng cung cấp tin nhắn trong trường 'message'"}), 400
            
        user_message = data['message']
        
        # Gọi Groq API với system prompt và user message
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system", 
                    "content": "Bạn là trợ lý ẩm thực thông minh, chuyên tư vấn món ăn theo nhu cầu người dùng"
                },
                {
                    "role": "user", 
                    "content": user_message
                }
            ],
            temperature=0.7,
        )
        
        # Trích xuất phản hồi từ AI
        ai_reply = completion.choices[0].message.content
        
        # Trả về kết quả dạng JSON
        return jsonify({"reply": ai_reply})
        
    except Exception as e:
        print(f"Lỗi khi xử lý chat: {str(e)}")
        return jsonify({"error": f"Đã xảy ra lỗi: {str(e)}"}), 500

if __name__ == "__main__":
    # Chạy server Flask ở cổng 5000
    app.run(debug=True, host="0.0.0.0", port=5000) 