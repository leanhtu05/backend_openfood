from flask import Flask, request, jsonify
import os
import uuid
from datetime import datetime
from openai import OpenAI
from firebase_config import firebase_config

app = Flask(__name__)

# Khởi tạo Groq client với API key từ biến môi trường
groq_api_key = os.environ.get("GROQ_API_KEY", "")
if not groq_api_key:
    print("CẢNH BÁO: GROQ_API_KEY không được thiết lập")

client = OpenAI(
    api_key=groq_api_key,
    base_url="https://api.groq.com/openai/v1"
)

class ChatHistoryManager:
    """Lớp quản lý lịch sử chat với Firebase"""
    
    def __init__(self):
        """Khởi tạo kết nối đến Firestore"""
        self.db = firebase_config.get_db()
        self.collection_name = "chat_history"
    
    def save_chat(self, user_id, user_message, ai_reply):
        """
        Lưu một cuộc hội thoại chat vào Firestore
        
        Args:
            user_id: ID của người dùng (có thể tự tạo nếu không có)
            user_message: Tin nhắn của người dùng
            ai_reply: Phản hồi của AI
            
        Returns:
            chat_id: ID của cuộc hội thoại đã lưu
        """
        try:
            # Tạo ID duy nhất cho cuộc hội thoại
            chat_id = str(uuid.uuid4())
            
            # Tạo document với dữ liệu hội thoại
            chat_data = {
                "user_id": user_id,
                "user_message": user_message,
                "ai_reply": ai_reply,
                "timestamp": datetime.now().isoformat(),
                "model": "llama3-8b-8192"
            }
            
            # Lưu vào Firestore
            self.db.collection(self.collection_name).document(chat_id).set(chat_data)
            print(f"Đã lưu chat với ID: {chat_id}")
            
            return chat_id
        except Exception as e:
            print(f"Lỗi khi lưu lịch sử chat: {str(e)}")
            return None
    
    def get_user_chat_history(self, user_id, limit=10):
        """
        Lấy lịch sử chat của một người dùng
        
        Args:
            user_id: ID của người dùng
            limit: Số lượng cuộc hội thoại tối đa trả về
            
        Returns:
            list: Danh sách các cuộc hội thoại
        """
        try:
            # Truy vấn Firestore
            chats = (self.db.collection(self.collection_name)
                    .where("user_id", "==", user_id)
                    .limit(limit)
                    .get())
            
            # Chuyển đổi kết quả thành danh sách
            chat_list = []
            for chat in chats:
                chat_data = chat.to_dict()
                chat_data["id"] = chat.id
                chat_list.append(chat_data)
            
            return chat_list
        except Exception as e:
            print(f"Lỗi khi lấy lịch sử chat: {str(e)}")
            return []

# Khởi tạo đối tượng quản lý lịch sử chat
chat_history = ChatHistoryManager()

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint nhận tin nhắn từ người dùng, xử lý qua Groq API và trả về phản hồi
    Ví dụ request: {"message": "Món ăn nào tốt cho người bị tiểu đường?", "user_id": "user123"}
    Ví dụ response: {"reply": "Có nhiều món ăn phù hợp cho người tiểu đường...", "chat_id": "abc123"}
    """
    try:
        # Nhận message từ request
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Vui lòng cung cấp tin nhắn trong trường 'message'"}), 400
            
        user_message = data['message']
        # Lấy user_id từ request, nếu không có thì dùng "anonymous"
        user_id = data.get('user_id', 'anonymous')
        
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
        
        # Lưu lịch sử chat vào Firebase
        chat_id = chat_history.save_chat(user_id, user_message, ai_reply)
        
        # Trả về kết quả dạng JSON
        return jsonify({
            "reply": ai_reply, 
            "chat_id": chat_id
        })
        
    except Exception as e:
        print(f"Lỗi khi xử lý chat: {str(e)}")
        return jsonify({"error": f"Đã xảy ra lỗi: {str(e)}"}), 500

@app.route('/chat/history', methods=['GET'])
def get_chat_history():
    """
    Endpoint trả về lịch sử chat của một người dùng
    Ví dụ request: GET /chat/history?user_id=user123&limit=5
    """
    try:
        # Lấy user_id từ query parameters
        user_id = request.args.get('user_id', 'anonymous')
        limit = int(request.args.get('limit', 10))
        
        # Lấy lịch sử chat
        history = chat_history.get_user_chat_history(user_id, limit)
        
        # Trả về kết quả dạng JSON
        return jsonify({
            "history": history,
            "count": len(history)
        })
        
    except Exception as e:
        print(f"Lỗi khi lấy lịch sử chat: {str(e)}")
        return jsonify({"error": f"Đã xảy ra lỗi: {str(e)}"}), 500

if __name__ == "__main__":
    # Chạy server Flask ở cổng 5000
    app.run(debug=True, host="0.0.0.0", port=5000) 