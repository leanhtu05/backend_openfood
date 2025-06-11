from flask import Flask, request, jsonify
import os
import uuid
import time
from datetime import datetime, timezone, timedelta
from openai import OpenAI
from firebase_config import firebase_config

# Thiết lập timezone Việt Nam (UTC+7)
VIETNAM_TZ = timezone(timedelta(hours=7))

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
    
    def save_chat(self, user_id, user_message, ai_reply, augmented=False):
        """
        Lưu một cuộc hội thoại chat vào Firestore
        
        Args:
            user_id: ID của người dùng (có thể tự tạo nếu không có)
            user_message: Tin nhắn của người dùng
            ai_reply: Phản hồi của AI
            augmented: Đánh dấu nếu phản hồi đã được tăng cường bằng RAG
            
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
                "timestamp": datetime.now(VIETNAM_TZ).isoformat(),
                "model": "llama3-8b-8192",
                "augmented": augmented  # Đánh dấu nếu sử dụng RAG
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

# Hàm định dạng dữ liệu người dùng thành context
def format_user_context(user_profile, meal_plan, food_logs, exercise_history=None, water_intake=None, exercise_date=None, water_date=None):
    """
    Định dạng dữ liệu người dùng thành một đoạn văn bản context cho chatbot

    Args:
        user_profile: Dữ liệu hồ sơ người dùng
        meal_plan: Dữ liệu kế hoạch ăn uống
        food_logs: Danh sách các bản ghi thực phẩm đã ăn
        exercise_history: Lịch sử bài tập của người dùng
        water_intake: Lượng nước uống trong ngày
        exercise_date: Ngày của dữ liệu bài tập (nếu khác hôm nay)
        water_date: Ngày của dữ liệu nước uống (nếu khác hôm nay)

    Returns:
        Đoạn văn bản context đã định dạng
    """
    context_parts = []
    today_str = datetime.now(VIETNAM_TZ).strftime("%Y-%m-%d")
    
    # Thông tin hồ sơ
    if user_profile:
        goal = user_profile.get('goal', 'Không rõ')
        calories_target = user_profile.get('tdeeValues', {}).get('calories', 'Không rõ')
        allergies = ", ".join(user_profile.get('allergies', [])) or "không có"
        height = user_profile.get('height', 'Không rõ')
        weight = user_profile.get('weight', 'Không rõ')
        diet_restrictions = ", ".join(user_profile.get('dietRestrictions', [])) or "không có"
        
        context_parts.append(f"- Hồ sơ: Mục tiêu là '{goal}', mục tiêu calo hàng ngày là {calories_target} kcal. "
                           f"Chiều cao: {height}cm, cân nặng: {weight}kg. "
                           f"Dị ứng với: {allergies}. Hạn chế ăn uống: {diet_restrictions}.")

    # Thông tin kế hoạch bữa ăn hôm nay
    if meal_plan:
        today_day = datetime.now(VIETNAM_TZ).strftime("%A").lower()
        # Chuyển đổi tên ngày tiếng Anh sang tiếng Việt nếu cần
        days_translation = {
            "monday": "monday", "tuesday": "tuesday", "wednesday": "wednesday", 
            "thursday": "thursday", "friday": "friday", "saturday": "saturday", "sunday": "sunday"
        }
        today_day_key = days_translation.get(today_day, today_day)
        
        # Tìm dữ liệu ngày hiện tại trong kế hoạch
        today_plan = None
        if "days" in meal_plan:
            for day in meal_plan.get("days", []):
                if day.get("day_of_week", "").lower() == today_day_key:
                    today_plan = day
                    break
        
        if today_plan:
            breakfast = ", ".join([dish.get("name", "") for dish in today_plan.get("breakfast", [])])
            lunch = ", ".join([dish.get("name", "") for dish in today_plan.get("lunch", [])])
            dinner = ", ".join([dish.get("name", "") for dish in today_plan.get("dinner", [])])
            
            context_parts.append(f"- Kế hoạch hôm nay: "
                              f"Bữa sáng gồm {breakfast}. "
                              f"Bữa trưa gồm {lunch}. "
                              f"Bữa tối gồm {dinner}.")

    # Thông tin nhật ký đã ăn
    if food_logs:
        # Tính tổng calo từ nhiều nguồn khác nhau
        eaten_calories = 0
        for log in food_logs:
            # Cách 1: Từ total_nutrition (cấu trúc cũ)
            if log.get('total_nutrition', {}).get('calories'):
                eaten_calories += log.get('total_nutrition', {}).get('calories', 0)
            # Cách 2: Từ trường calories (cấu trúc mới)
            elif log.get('calories'):
                eaten_calories += log.get('calories', 0)
            # Cách 3: Từ items[].calories (cấu trúc mới)
            elif log.get('items'):
                for item in log.get('items', []):
                    eaten_calories += item.get('calories', 0)
        
        # Thu thập tên các món ăn
        eaten_dishes = []
        for log in food_logs:
            # Cách 1: Từ recognized_foods (cấu trúc cũ)
            if log.get('recognized_foods'):
                for food in log.get('recognized_foods', []):
                    if food.get('food_name'):
                        eaten_dishes.append(food.get('food_name'))
            
            # Cách 2: Từ items (cấu trúc mới)
            elif log.get('items'):
                for item in log.get('items', []):
                    if item.get('name'):
                        eaten_dishes.append(item.get('name'))
            
            # Cách 3: Từ description (cấu trúc mới)
            elif log.get('description'):
                eaten_dishes.append(log.get('description'))
        
        if eaten_dishes:
            context_parts.append(f"- Nhật ký đã ăn hôm nay: Đã ăn {len(food_logs)} bữa với các món: {', '.join(eaten_dishes)}. "
                              f"Tổng calo đã nạp: {eaten_calories} kcal.")
        else:
            context_parts.append(f"- Nhật ký đã ăn hôm nay: Đã ghi nhận {len(food_logs)} bữa ăn nhưng không có thông tin chi tiết.")
    else:
        context_parts.append("- Nhật ký đã ăn hôm nay: Chưa ghi nhận bữa nào.")
    
    # Thông tin bài tập
    if exercise_history:
        # Tính tổng calo đã đốt
        burned_calories = 0
        for exercise in exercise_history:
            # Cách 1: Từ calories_burned (cấu trúc cũ)
            if 'calories_burned' in exercise:
                burned_calories += exercise.get('calories_burned', 0)
            # Cách 2: Từ calories (cấu trúc mới)
            elif 'calories' in exercise:
                burned_calories += exercise.get('calories', 0)
        
        # Liệt kê các bài tập đã thực hiện
        exercise_list = []
        for exercise in exercise_history:
            # Cách 1: Từ cấu trúc cũ
            if exercise.get('exercise_name') and exercise.get('duration_minutes'):
                exercise_name = exercise.get('exercise_name')
                duration = exercise.get('duration_minutes')
                exercise_list.append(f"{exercise_name} ({duration} phút)")
            # Cách 2: Từ cấu trúc mới
            elif exercise.get('name') and exercise.get('minutes'):
                exercise_name = exercise.get('name')
                duration = exercise.get('minutes')
                exercise_list.append(f"{exercise_name} ({duration} phút)")
        
        if exercise_list:
            if exercise_date and exercise_date != today_str:
                # Dữ liệu từ ngày khác - hiển thị rõ ràng
                context_parts.append(f"- Bài tập hôm nay: Chưa ghi nhận bài tập nào. "
                                   f"(Gần nhất: {exercise_date} đã tập {len(exercise_history)} bài tập: {', '.join(exercise_list)}, đốt {burned_calories} kcal)")
            else:
                # Dữ liệu hôm nay
                context_parts.append(f"- Bài tập hôm nay: Đã tập {len(exercise_history)} bài tập: {', '.join(exercise_list)}. "
                                   f"Tổng calo đã đốt: {burned_calories} kcal.")
        else:
            if exercise_date and exercise_date != today_str:
                context_parts.append(f"- Bài tập hôm nay: Chưa ghi nhận bài tập nào. "
                                   f"(Gần nhất: {exercise_date} có {len(exercise_history)} hoạt động)")
            else:
                context_parts.append(f"- Bài tập hôm nay: Đã ghi nhận {len(exercise_history)} hoạt động nhưng không có thông tin chi tiết.")
    else:
        context_parts.append("- Bài tập hôm nay: Chưa ghi nhận bài tập nào.")
    
    # Thông tin nước uống
    if water_intake:
        # Tính tổng lượng nước đã uống
        total_water_ml = 0
        for intake in water_intake:
            # Cách 1: Từ amount_ml (cấu trúc cũ)
            if 'amount_ml' in intake:
                total_water_ml += intake.get('amount_ml', 0)
            # Cách 2: Từ amount (cấu trúc mới)
            elif 'amount' in intake:
                total_water_ml += intake.get('amount', 0)
        
        # Chuyển đổi sang lít
        total_water_liter = total_water_ml / 1000
        
        # Kiểm tra có đạt mục tiêu không
        water_target = 2000  # Mặc định 2 lít (2000ml)
        
        # Cố gắng lấy mục tiêu từ user_profile
        if user_profile:
            if user_profile.get('waterTarget', {}).get('amount_ml'):
                water_target = user_profile.get('waterTarget', {}).get('amount_ml')
            elif user_profile.get('water_target'):
                water_target = user_profile.get('water_target')
        
        water_target_liter = water_target / 1000
        percentage = (total_water_liter / water_target_liter) * 100 if water_target_liter > 0 else 0
        
        if water_date and water_date != today_str:
            # Dữ liệu từ ngày khác - hiển thị rõ ràng
            context_parts.append(f"- Nước uống hôm nay: Chưa ghi nhận lượng nước uống nào. "
                              f"(Gần nhất: {water_date} đã uống {total_water_liter:.1f} lít - {percentage:.0f}% mục tiêu)")
        else:
            # Dữ liệu hôm nay
            context_parts.append(f"- Nước uống hôm nay: Đã uống {total_water_liter:.1f} lít nước "
                              f"({percentage:.0f}% mục tiêu {water_target_liter:.1f} lít).")
    else:
        context_parts.append("- Nước uống hôm nay: Chưa ghi nhận lượng nước uống nào.")
        
    return "\n".join(context_parts)

# Khởi tạo đối tượng quản lý lịch sử chat
chat_history = ChatHistoryManager()

@app.route('/chat', methods=['POST'])
def chat():
    """
    Endpoint nhận tin nhắn từ người dùng, xử lý qua Groq API và trả về phản hồi
    Sử dụng kỹ thuật RAG (Retrieval-Augmented Generation) để cá nhân hóa phản hồi
    
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
        
        # Áp dụng RAG: Truy xuất dữ liệu người dùng từ Firestore
        use_rag = True  # Có thể điều chỉnh thành tham số trong request
        augmented_prompt = user_message
        
        try:
            if use_rag and user_id != 'anonymous':
                print(f"Chat request for user: {user_id}")
                # Import module firestore_service
                from services.firestore_service import firestore_service
                
                # 1. Lấy hồ sơ người dùng
                user_profile = firestore_service.get_user(user_id) or {}
                
                # 2. Lấy kế hoạch ăn mới nhất
                meal_plan_data = firestore_service.get_latest_meal_plan(user_id)
                meal_plan_dict = meal_plan_data.dict() if meal_plan_data else {}
                
                # 3. Lấy nhật ký ăn uống hôm nay
                vietnam_now = datetime.now(VIETNAM_TZ)
                today_str = vietnam_now.strftime("%Y-%m-%d")
                print(f"[DEBUG] ⏰ Thời gian hiện tại (VN): {vietnam_now.isoformat()}")
                print(f"[DEBUG] 📅 Đang truy vấn dữ liệu cho ngày: {today_str}")
                print(f"[DEBUG] 🌏 Timezone: {VIETNAM_TZ}")
                food_logs_today = firestore_service.get_food_logs_by_date(user_id, today_str) or []

                # 4. Lấy thông tin bài tập hôm nay - với fallback logic
                print(f"[DEBUG] Đang truy vấn dữ liệu bài tập cho user {user_id} với ngày {today_str}...")
                exercise_history = firestore_service.get_exercise_history(user_id, start_date=today_str, end_date=today_str) or []
                print(f"[DEBUG] Tìm thấy {len(exercise_history)} bài tập cho ngày {today_str}")
                if exercise_history:
                    for ex in exercise_history:
                        print(f"[DEBUG] Bài tập: {ex.get('exercise_name', 'N/A')} - {ex.get('date', 'N/A')}")

                # Nếu không có dữ liệu hôm nay, thử tìm dữ liệu gần nhất (trong 7 ngày qua)
                exercise_date = today_str  # Mặc định là hôm nay
                if not exercise_history:
                    for days_back in range(1, 8):  # Tìm trong 7 ngày qua
                        past_date = (datetime.now(VIETNAM_TZ) - timedelta(days=days_back)).strftime("%Y-%m-%d")
                        exercise_history = firestore_service.get_exercise_history(user_id, start_date=past_date, end_date=past_date) or []
                        if exercise_history:
                            exercise_date = past_date
                            print(f"[DEBUG] Tìm thấy dữ liệu bài tập gần nhất vào ngày: {past_date}")
                            break

                # 5. Lấy thông tin nước uống hôm nay - với fallback logic
                print(f"[DEBUG] Đang truy vấn dữ liệu nước uống cho user {user_id} với ngày {today_str}...")
                water_intake = firestore_service.get_water_intake_by_date(user_id, today_str) or []
                print(f"[DEBUG] Tìm thấy {len(water_intake)} lượt uống nước cho ngày {today_str}")
                if water_intake:
                    for water in water_intake:
                        print(f"[DEBUG] Nước uống: {water.get('amount_ml', 'N/A')}ml - {water.get('date', 'N/A')}")

                # Nếu không có dữ liệu hôm nay, thử tìm dữ liệu gần nhất (trong 7 ngày qua)
                water_date = today_str  # Mặc định là hôm nay
                if not water_intake:
                    for days_back in range(1, 8):  # Tìm trong 7 ngày qua
                        past_date = (datetime.now(VIETNAM_TZ) - timedelta(days=days_back)).strftime("%Y-%m-%d")
                        water_intake = firestore_service.get_water_intake_by_date(user_id, past_date) or []
                        if water_intake:
                            water_date = past_date
                            print(f"[DEBUG] Tìm thấy dữ liệu nước uống gần nhất vào ngày: {past_date}")
                            break
                
                # Kiểm tra các collection Firebase đang sử dụng
                print(f"[DEBUG] Kiểm tra collections Firebase: users, exercises, exercise_histories, water_entries, water_intake")
                
                # Tạo context từ dữ liệu đã truy xuất
                context_data = format_user_context(
                    user_profile,
                    meal_plan_dict,
                    food_logs_today,
                    exercise_history,
                    water_intake,
                    exercise_date,
                    water_date
                )
                
                # Xây dựng prompt thông minh
                augmented_prompt = f"""Bạn là một trợ lý dinh dưỡng ảo tên là DietAI. Nhiệm vụ của bạn là trả lời câu hỏi của người dùng dựa trên thông tin cá nhân và hoạt động hàng ngày của họ.

--- DỮ LIỆU CÁ NHÂN CỦA NGƯỜI DÙNG ---
{context_data}
--- KẾT THÚC DỮ LIỆU ---

Dựa vào các thông tin trên, hãy trả lời câu hỏi sau của người dùng một cách thân thiện và chính xác bằng tiếng Việt:

Câu hỏi: "{user_message}"
"""
                print(f"DEBUG: Using RAG with augmented prompt")
        except Exception as e:
            print(f"Lỗi khi áp dụng RAG: {str(e)}")
            print(f"Tiếp tục với prompt thông thường")
            use_rag = False
            import traceback
            traceback.print_exc()
        
        # Chờ thêm một chút trước khi gọi API để đảm bảo tất cả dữ liệu đã được xử lý
        time.sleep(0.5)
        
        # Gọi Groq API với system prompt và user message
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system", 
                    "content": "Bạn là trợ lý dinh dưỡng ảo tên là DietAI. Trả lời dựa trên dữ liệu người dùng." 
                    if use_rag else 
                    "Bạn là trợ lý ẩm thực thông minh, chuyên tư vấn món ăn theo nhu cầu người dùng"
                },
                {
                    "role": "user", 
                    "content": augmented_prompt
                }
            ],
            temperature=0.7,
        )
        
        # Trích xuất phản hồi từ AI
        ai_reply = completion.choices[0].message.content
        
        # Lưu lịch sử chat vào Firebase
        chat_id = chat_history.save_chat(user_id, user_message, ai_reply, augmented=use_rag)
        
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