"""
Kiểm tra tính năng lưu trữ lịch sử chat trên Firebase

Tập tin này chứa các thủ tục kiểm tra chức năng lưu trữ và truy xuất
lịch sử chat từ Firebase thông qua lớp ChatHistoryManager trong chat_endpoint.py
"""

import os
import sys
import json
import unittest
from datetime import datetime
from chat_endpoint import ChatHistoryManager

class TestChatHistory(unittest.TestCase):
    """Test cho chức năng lưu trữ lịch sử chat"""
    
    def setUp(self):
        """Thiết lập trước mỗi bài kiểm tra"""
        self.chat_manager = ChatHistoryManager()
        self.test_user_id = "test_user_" + datetime.now().strftime("%Y%m%d%H%M%S")
    
    def test_save_and_retrieve_chat(self):
        """Kiểm tra lưu trữ và truy xuất lịch sử chat"""
        print(f"\nKiểm tra lưu và lấy lịch sử chat cho người dùng: {self.test_user_id}")
        
        # Tạo tin nhắn kiểm tra
        user_message = "Món ăn nào tốt cho người bị tiểu đường?"
        ai_reply = "Người bị tiểu đường nên ăn các thực phẩm có chỉ số đường huyết thấp như rau xanh, ngũ cốc nguyên hạt, đậu, cá, và thịt nạc. Bạn nên hạn chế thực phẩm giàu carbs đơn giản và đường tinh luyện."
        
        # Lưu chat
        chat_id = self.chat_manager.save_chat(self.test_user_id, user_message, ai_reply)
        
        # Kiểm tra xem chat_id có được trả về không
        self.assertIsNotNone(chat_id, "Không thể lưu chat vào Firebase")
        print(f"Đã lưu chat với ID: {chat_id}")
        
        # Lấy lịch sử chat
        history = self.chat_manager.get_user_chat_history(self.test_user_id, limit=5)
        
        # Kiểm tra kết quả
        self.assertTrue(len(history) > 0, "Không thể lấy lịch sử chat từ Firebase")
        print(f"Đã tìm thấy {len(history)} cuộc hội thoại")
        
        # Kiểm tra nội dung chat
        found_chat = False
        for chat in history:
            if chat.get("user_message") == user_message and chat.get("ai_reply") == ai_reply:
                found_chat = True
                print(f"Đã tìm thấy chat đã lưu trong lịch sử: {chat.get('id')}")
                break
        
        self.assertTrue(found_chat, "Không tìm thấy chat đã lưu trong lịch sử")
    
    def test_multiple_chats(self):
        """Kiểm tra lưu nhiều cuộc hội thoại cho cùng một người dùng"""
        print(f"\nKiểm tra lưu nhiều cuộc hội thoại cho người dùng: {self.test_user_id}")
        
        # Lưu 3 cuộc hội thoại
        chat_ids = []
        for i in range(3):
            user_message = f"Câu hỏi thử nghiệm {i+1}"
            ai_reply = f"Trả lời thử nghiệm {i+1}"
            
            chat_id = self.chat_manager.save_chat(self.test_user_id, user_message, ai_reply)
            self.assertIsNotNone(chat_id, f"Không thể lưu chat {i+1}")
            chat_ids.append(chat_id)
            print(f"Đã lưu chat {i+1} với ID: {chat_id}")
        
        # Lấy lịch sử chat
        history = self.chat_manager.get_user_chat_history(self.test_user_id, limit=5)
        
        # Kiểm tra số lượng chat
        self.assertTrue(len(history) >= 3, f"Không tìm thấy đủ lịch sử chat. Tìm thấy {len(history)}, cần ít nhất 3")
        print(f"Đã tìm thấy {len(history)} cuộc hội thoại")

if __name__ == "__main__":
    print("Bắt đầu kiểm tra lưu trữ lịch sử chat Firebase...")
    unittest.main() 