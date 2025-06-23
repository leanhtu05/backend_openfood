from flask import Flask, request, jsonify
import os
import uuid
import time
import re
from datetime import datetime, timezone, timedelta
from openai import OpenAI
from firebase_config import firebase_config

# Thiết lập timezone Việt Nam (UTC+7)
VIETNAM_TZ = timezone(timedelta(hours=7))

def get_enhanced_nutrition_system_prompt(use_rag: bool = False) -> str:
    """
    Tạo system prompt nâng cao cho chatbot dinh dưỡng thông minh
    """
    base_prompt = """Bạn là DietAI - Chuyên gia dinh dưỡng AI hàng đầu Việt Nam với chuyên môn sâu về:

🎯 CHUYÊN MÔN CORE:
• Khoa học dinh dưỡng hiện đại (macro/micro nutrients, bioavailability)
• Tính toán TDEE, BMR, body composition chính xác
• Phân tích glycemic index, insulin response, metabolic pathways
• Dinh dưỡng lâm sàng cho các bệnh lý (tiểu đường, cao huyết áp, béo phì)
• Dinh dưỡng thể thao và tối ưu hóa hiệu suất

🧬 KIẾN THỨC CHUYÊN SÂU:
• Tương tác thực phẩm-thuốc, absorption, metabolism
• Nutrient timing, meal frequency optimization
• Gut microbiome và prebiotics/probiotics
• Anti-inflammatory foods, antioxidants, phytonutrients
• Sustainable nutrition và environmental impact

🇻🇳 CHUYÊN GIA ẨM THỰC VIỆT:
• 500+ món ăn truyền thống với phân tích dinh dưỡng chi tiết
• Adaptation món Việt cho các mục tiêu sức khỏe
• Seasonal ingredients, local superfoods
• Cooking methods ảnh hưởng đến nutrition retention

📊 PHƯƠNG PHÁP TƯ VẤN:
• Evidence-based recommendations với citations
• Personalized advice dựa trên biomarkers, lifestyle
• Progressive goal setting với measurable outcomes
• Risk assessment và contraindications
• Cultural sensitivity trong dietary advice

💡 COMMUNICATION STYLE:
• Giải thích khoa học phức tạp một cách dễ hiểu
• Practical, actionable advice với specific portions
• Empathetic, non-judgmental approach
• Encourage sustainable lifestyle changes
• Provide alternatives cho mọi dietary restriction"""

    if use_rag:
        rag_addition = """

🔍 DỮ LIỆU NGƯỜI DÙNG AVAILABLE:
Bạn có quyền truy cập vào:
• Hồ sơ sức khỏe chi tiết (BMI, mục tiêu, bệnh lý)
• Lịch sử ăn uống và meal plans
• Food records với nutrition tracking
• Exercise data và activity levels
• Preferences, allergies, dietary restrictions

📋 RESPONSE GUIDELINES:
• Luôn reference specific user data khi relevant
• Provide personalized recommendations
• Compare current intake với recommended values
• Suggest specific adjustments dựa trên user goals
• Mention progress tracking và next steps"""

        return base_prompt + rag_addition

    return base_prompt + """

📋 GENERAL GUIDELINES:
• Provide evidence-based nutrition advice
• Suggest specific Vietnamese dishes when appropriate
• Include portion sizes và preparation tips
• Recommend gradual, sustainable changes
• Always consider individual health conditions"""

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
def format_user_context(user_profile, meal_plan, food_logs, exercise_history=None, water_intake=None, exercise_date=None, water_date=None, target_date=None, context_type='today'):
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
        target_date: Ngày được yêu cầu (YYYY-MM-DD)
        context_type: Loại ngữ cảnh thời gian ('today', 'yesterday', 'specific_date', 'relative')

    Returns:
        Đoạn văn bản context đã định dạng
    """
    context_parts = []
    today_str = datetime.now(VIETNAM_TZ).strftime("%Y-%m-%d")

    # Xác định nhãn thời gian dựa trên context_type
    if context_type == 'yesterday':
        time_label = "hôm qua"
        target_date_display = target_date if target_date else (datetime.now(VIETNAM_TZ) - timedelta(days=1)).strftime("%Y-%m-%d")
    elif context_type == 'today':
        time_label = "hôm nay"
        target_date_display = target_date if target_date else today_str
    elif context_type == 'specific_date':
        time_label = f"ngày {target_date}"
        target_date_display = target_date
    elif context_type == 'relative':
        time_label = f"ngày {target_date}"
        target_date_display = target_date
    else:
        time_label = "hôm nay"
        target_date_display = today_str
    
    # Thông tin hồ sơ
    if user_profile:
        goal = user_profile.get('goal', 'Không rõ')

        # 🔧 FIX: Lấy mục tiêu calories thực tế thay vì TDEE
        calories_target = 'Không rõ'

        # Ưu tiên lấy từ caloriesGoal (mục tiêu thực tế)
        if user_profile.get('caloriesGoal'):
            calories_target = user_profile.get('caloriesGoal')
        # Fallback về dailyCaloriesGoal
        elif user_profile.get('dailyCaloriesGoal'):
            calories_target = user_profile.get('dailyCaloriesGoal')
        # Fallback về goalCalories
        elif user_profile.get('goalCalories'):
            calories_target = user_profile.get('goalCalories')
        # Cuối cùng mới lấy TDEE (không nên dùng làm mục tiêu)
        elif user_profile.get('tdeeValues', {}).get('calories'):
            calories_target = user_profile.get('tdeeValues', {}).get('calories')
            print(f"⚠️ WARNING: Đang dùng TDEE làm mục tiêu calories cho user {user_profile.get('email', 'unknown')}")

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

        # 🔧 FIX: Đếm số bữa ăn thực tế và debug thông tin chi tiết
        print(f"[DEBUG] 🍽️ Phân tích {len(food_logs)} food logs:")
        for i, log in enumerate(food_logs):
            print(f"[DEBUG] 📝 Log #{i+1}: meal_type={log.get('meal_type', 'N/A')}, description={log.get('description', 'N/A')}")
            print(f"[DEBUG] 📝 Log #{i+1}: items={len(log.get('items', []))}, recognized_foods={len(log.get('recognized_foods', []))}")

        # Đếm tổng số món ăn từ tất cả các nguồn
        total_dishes = len(eaten_dishes)

        # 🔧 FIX: Phân tích meal_type để đếm số bữa ăn khác nhau - sửa lỗi đếm sai
        unique_meals = set()
        meal_details = {}  # Lưu chi tiết từng bữa ăn

        for log in food_logs:
            meal_type = log.get('meal_type', 'unknown')
            # 🔧 FIX: Kiểm tra meal_type chặt chẽ hơn
            if meal_type and meal_type != 'unknown' and meal_type.strip():
                unique_meals.add(meal_type)
                if meal_type not in meal_details:
                    meal_details[meal_type] = []

                # Thu thập món ăn cho từng bữa
                if log.get('recognized_foods'):
                    for food in log.get('recognized_foods', []):
                        if food.get('food_name'):
                            meal_details[meal_type].append(food.get('food_name'))
                elif log.get('items'):
                    for item in log.get('items', []):
                        if item.get('name'):
                            meal_details[meal_type].append(item.get('name'))
                elif log.get('description'):
                    meal_details[meal_type].append(log.get('description'))

        print(f"[DEBUG] 🍽️ Unique meals found: {unique_meals}")
        print(f"[DEBUG] 🍽️ Meal details: {meal_details}")
        print(f"[DEBUG] 🔢 Meal count logic: unique_meals={len(unique_meals)}, total_logs={len(food_logs)}")

        # 🔧 FIX: Tạo thông tin chi tiết với logic chính xác hơn
        if eaten_dishes:
            if unique_meals:
                # Có thông tin meal_type - hiển thị chi tiết từng bữa
                meal_summary = []
                for meal_type in sorted(unique_meals):
                    dishes_in_meal = meal_details.get(meal_type, [])
                    # Loại bỏ trùng lặp trong cùng một bữa ăn
                    unique_dishes_in_meal = list(set(dishes_in_meal))
                    if unique_dishes_in_meal:
                        meal_summary.append(f"{meal_type}: {', '.join(unique_dishes_in_meal)}")
                    else:
                        meal_summary.append(f"{meal_type}: không rõ món ăn")

                # 🔧 FIX: Đếm số bữa ăn thực tế (unique meal types) - sửa lỗi đếm sai
                actual_meal_count = len(unique_meals)
                print(f"[DEBUG] ✅ Đếm theo unique meal_types: {actual_meal_count} bữa")
                context_parts.append(f"- Nhật ký đã ăn {time_label}: Đã ăn {actual_meal_count} bữa ({'; '.join(meal_summary)}). "
                                  f"Tổng calo đã nạp: {eaten_calories} kcal.")
            else:
                # 🔧 FIX: Không có meal_type - đếm theo số records (mỗi record = 1 bữa)
                actual_meal_count = len(food_logs)
                print(f"[DEBUG] ⚠️ Không có meal_type hợp lệ, đếm theo số records: {actual_meal_count} bữa")
                if len(food_logs) == 1:
                    context_parts.append(f"- Nhật ký đã ăn {time_label}: Đã ăn 1 bữa với {total_dishes} món: {', '.join(eaten_dishes)}. "
                                      f"Tổng calo đã nạp: {eaten_calories} kcal.")
                else:
                    context_parts.append(f"- Nhật ký đã ăn {time_label}: Đã ăn {len(food_logs)} bữa với {total_dishes} món: {', '.join(eaten_dishes)}. "
                                      f"Tổng calo đã nạp: {eaten_calories} kcal.")
        else:
            # Không có thông tin món ăn chi tiết
            if unique_meals:
                context_parts.append(f"- Nhật ký đã ăn {time_label}: Đã ghi nhận {len(unique_meals)} bữa ăn nhưng không có thông tin chi tiết.")
            else:
                if len(food_logs) == 1:
                    context_parts.append(f"- Nhật ký đã ăn {time_label}: Đã ghi nhận 1 lần ăn nhưng không có thông tin chi tiết.")
                else:
                    context_parts.append(f"- Nhật ký đã ăn {time_label}: Đã ghi nhận {len(food_logs)} lần ghi nhận thực phẩm nhưng không có thông tin chi tiết.")
    else:
        context_parts.append(f"- Nhật ký đã ăn {time_label}: Chưa ghi nhận bữa nào.")
    
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
            if exercise_date and exercise_date != target_date_display:
                # Dữ liệu từ ngày khác - hiển thị rõ ràng
                context_parts.append(f"- Bài tập {time_label}: Chưa ghi nhận bài tập nào. "
                                   f"(Gần nhất: {exercise_date} đã tập {len(exercise_history)} bài tập: {', '.join(exercise_list)}, đốt {burned_calories} kcal)")
            else:
                # Dữ liệu đúng ngày được yêu cầu
                context_parts.append(f"- Bài tập {time_label}: Đã tập {len(exercise_history)} bài tập: {', '.join(exercise_list)}. "
                                   f"Tổng calo đã đốt: {burned_calories} kcal.")
        else:
            if exercise_date and exercise_date != target_date_display:
                context_parts.append(f"- Bài tập {time_label}: Chưa ghi nhận bài tập nào. "
                                   f"(Gần nhất: {exercise_date} có {len(exercise_history)} hoạt động)")
            else:
                context_parts.append(f"- Bài tập {time_label}: Đã ghi nhận {len(exercise_history)} hoạt động nhưng không có thông tin chi tiết.")
    else:
        context_parts.append(f"- Bài tập {time_label}: Chưa ghi nhận bài tập nào.")
    
    # Thông tin nước uống
    if water_intake:
        # Tính tổng lượng nước đã uống
        total_water_ml = 0
        for intake in water_intake:
            # Cách 1: Từ amount (cấu trúc mới từ Flutter)
            if 'amount' in intake:
                total_water_ml += intake.get('amount', 0)
            # Cách 2: Từ amount_ml (cấu trúc cũ)
            elif 'amount_ml' in intake:
                total_water_ml += intake.get('amount_ml', 0)
        
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
        
        if water_date and water_date != target_date_display:
            # Dữ liệu từ ngày khác - hiển thị rõ ràng
            context_parts.append(f"- Nước uống {time_label}: Chưa ghi nhận lượng nước uống nào. "
                              f"(Gần nhất: {water_date} đã uống {total_water_liter:.1f} lít - {percentage:.0f}% mục tiêu)")
        else:
            # Dữ liệu đúng ngày được yêu cầu
            context_parts.append(f"- Nước uống {time_label}: Đã uống {total_water_liter:.1f} lít nước "
                              f"({percentage:.0f}% mục tiêu {water_target_liter:.1f} lít).")
    else:
        context_parts.append(f"- Nước uống {time_label}: Chưa ghi nhận lượng nước uống nào.")
        
    return "\n".join(context_parts)

def analyze_user_nutrition(user_profile, food_logs, meal_plan):
    """
    Phân tích dinh dưỡng nâng cao cho người dùng
    """
    analysis_parts = []

    if not food_logs:
        return "Chưa có dữ liệu thực phẩm để phân tích."

    # Tính tổng macro nutrients
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0

    for log in food_logs:
        if log.get('total_nutrition'):
            total_calories += log.get('total_nutrition', {}).get('calories', 0)
            total_protein += log.get('total_nutrition', {}).get('protein', 0)
            total_carbs += log.get('total_nutrition', {}).get('carbs', 0)
            total_fat += log.get('total_nutrition', {}).get('fat', 0)
        elif log.get('items'):
            for item in log.get('items', []):
                total_calories += item.get('calories', 0)
                total_protein += item.get('protein', 0)
                total_carbs += item.get('carbs', 0)
                total_fat += item.get('fat', 0)

    # 🔧 FIX: Lấy mục tiêu calories thực tế thay vì TDEE - sửa lỗi lấy sai chỉ số
    target_calories = 2000  # Default
    if user_profile:
        print(f"[DEBUG] 🎯 Tìm mục tiêu calories trong user_profile keys: {list(user_profile.keys())}")

        # Ưu tiên lấy từ caloriesGoal (mục tiêu thực tế)
        if user_profile.get('caloriesGoal'):
            target_calories = user_profile.get('caloriesGoal')
            print(f"[DEBUG] ✅ Lấy từ caloriesGoal: {target_calories}")
        # Fallback về dailyCaloriesGoal
        elif user_profile.get('dailyCaloriesGoal'):
            target_calories = user_profile.get('dailyCaloriesGoal')
            print(f"[DEBUG] ✅ Lấy từ dailyCaloriesGoal: {target_calories}")
        # Fallback về goalCalories
        elif user_profile.get('goalCalories'):
            target_calories = user_profile.get('goalCalories')
            print(f"[DEBUG] ✅ Lấy từ goalCalories: {target_calories}")
        # Fallback về calorie_goal
        elif user_profile.get('calorie_goal'):
            target_calories = user_profile.get('calorie_goal')
            print(f"[DEBUG] ✅ Lấy từ calorie_goal: {target_calories}")
        # Fallback về nutrition_goals.calories
        elif user_profile.get('nutrition_goals', {}).get('calories'):
            target_calories = user_profile.get('nutrition_goals', {}).get('calories')
            print(f"[DEBUG] ✅ Lấy từ nutrition_goals.calories: {target_calories}")
        # KHÔNG lấy TDEE làm mục tiêu - đây là lỗi chính
        else:
            print(f"[DEBUG] ⚠️ Không tìm thấy mục tiêu calories, dùng default: {target_calories}")
            # Không lấy TDEE vì đó là tổng năng lượng tiêu hao, không phải mục tiêu ăn uống

    # Tính phần trăm macro
    if total_calories > 0:
        protein_percent = (total_protein * 4 / total_calories) * 100
        carbs_percent = (total_carbs * 4 / total_calories) * 100
        fat_percent = (total_fat * 9 / total_calories) * 100

        analysis_parts.append(f"• Tổng calo: {total_calories:.0f}/{target_calories:.0f} kcal ({(total_calories/target_calories)*100:.0f}%)")
        analysis_parts.append(f"• Protein: {total_protein:.1f}g ({protein_percent:.0f}% calo) - {'✅ Đạt' if 15 <= protein_percent <= 30 else '⚠️ Cần điều chỉnh'}")
        analysis_parts.append(f"• Carbs: {total_carbs:.1f}g ({carbs_percent:.0f}% calo) - {'✅ Đạt' if 45 <= carbs_percent <= 65 else '⚠️ Cần điều chỉnh'}")
        analysis_parts.append(f"• Fat: {total_fat:.1f}g ({fat_percent:.0f}% calo) - {'✅ Đạt' if 20 <= fat_percent <= 35 else '⚠️ Cần điều chỉnh'}")

        # Đánh giá tổng thể
        if total_calories < target_calories * 0.8:
            analysis_parts.append("⚠️ Calo thấp hơn mục tiêu - có thể cần tăng khẩu phần")
        elif total_calories > target_calories * 1.2:
            analysis_parts.append("⚠️ Calo cao hơn mục tiêu - có thể cần giảm khẩu phần")
        else:
            analysis_parts.append("✅ Calo trong tầm kiểm soát")

    return "\n".join(analysis_parts) if analysis_parts else "Không đủ dữ liệu để phân tích chi tiết."

def get_usda_nutrition_data(food_name):
    """
    Lấy dữ liệu dinh dưỡng từ USDA API (sync version)
    """
    try:
        import requests

        api_key = os.getenv("USDA_API_KEY", "GJRAy2mRHxo2FiejluDsPDBhzPvUL3J8xhihsKh2")
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"

        params = {
            "query": food_name,
            "pageSize": 3,
            "api_key": api_key,
            "dataType": ["Foundation", "SR Legacy"]
        }

        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            foods = data.get("foods", [])

            if foods:
                food = foods[0]  # Take first result
                nutrients = food.get("foodNutrients", [])

                # Extract key nutrients
                nutrition_info = {
                    "name": food.get("description", "Unknown food"),
                    "fdc_id": food.get("fdcId"),
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "fiber": 0,
                    "sodium": 0
                }

                nutrient_map = {
                    "Energy": "calories",
                    "Protein": "protein",
                    "Total lipid (fat)": "fat",
                    "Carbohydrate, by difference": "carbs",
                    "Fiber, total dietary": "fiber",
                    "Sodium, Na": "sodium"
                }

                for nutrient in nutrients:
                    name = nutrient.get("nutrient", {}).get("name", "")
                    amount = nutrient.get("amount", 0)

                    for usda_name, key in nutrient_map.items():
                        if usda_name in name:
                            nutrition_info[key] = amount
                            break

                return nutrition_info

    except Exception as e:
        print(f"Error getting USDA data for {food_name}: {e}")

    return None

def get_intelligent_food_recommendations_sync(user_message, user_profile, food_logs):
    """
    Tạo gợi ý thực phẩm thông minh dựa trên professional nutrition data
    """
    recommendations = []

    # Phân tích từ khóa trong tin nhắn
    message_lower = user_message.lower()

    # Tìm kiếm thực phẩm cụ thể trong tin nhắn để lấy dữ liệu USDA
    food_keywords = ['gạo', 'rice', 'thịt bò', 'beef', 'cá', 'fish', 'trứng', 'egg', 'sữa', 'milk']
    found_food = None

    for keyword in food_keywords:
        if keyword in message_lower:
            found_food = keyword
            break

    # Nếu tìm thấy thực phẩm, lấy dữ liệu USDA
    if found_food:
        usda_data = get_usda_nutrition_data(found_food)
        if usda_data:
            recommendations.append(f"📊 USDA DATA - {usda_data['name']}:")
            recommendations.append(f"• Calories: {usda_data['calories']:.1f} kcal/100g")
            recommendations.append(f"• Protein: {usda_data['protein']:.1f}g")
            recommendations.append(f"• Carbs: {usda_data['carbs']:.1f}g")
            recommendations.append(f"• Fat: {usda_data['fat']:.1f}g")
            recommendations.append(f"• Nguồn: USDA FoodData Central (FDC ID: {usda_data['fdc_id']})")

    # Gợi ý dựa trên health conditions
    if any(keyword in message_lower for keyword in ['tiểu đường', 'diabetes', 'đường huyết']):
        recommendations.append("\n🩺 CHO NGƯỜI TIỂU ĐƯỜNG:")
        recommendations.append("• Món phù hợp: Bún bò Huế (GI thấp), Gỏi cuốn (ít carbs)")
        recommendations.append("• Tránh: Cơm trắng, bánh ngọt, nước ngọt")
        recommendations.append("• Nguồn: Hiệp hội Tiểu đường Việt Nam")

    elif any(keyword in message_lower for keyword in ['cao huyết áp', 'huyết áp', 'hypertension']):
        recommendations.append("\n💓 CHO NGƯỜI CAO HUYẾT ÁP:")
        recommendations.append("• Món phù hợp: Gỏi cuốn (ít sodium), Phở không MSG")
        recommendations.append("• Tránh: Đồ ăn mặn, thực phẩm chế biến sẵn")
        recommendations.append("• Nguồn: Bộ Y tế Việt Nam - DASH Diet")

    elif any(keyword in message_lower for keyword in ['giảm cân', 'weight loss', 'béo phì']):
        recommendations.append("\n⚖️ CHO NGƯỜI GIẢM CÂN:")
        recommendations.append("• Món phù hợp: Gỏi cuốn (96 kcal/cuốn), Phở gà (ít calo hơn phở bò)")
        recommendations.append("• Tăng: Rau xanh, protein lean, chất xơ")
        recommendations.append("• Nguồn: Viện Dinh dưỡng Quốc gia")

    elif any(keyword in message_lower for keyword in ['protein', 'tăng cân', 'muscle']):
        recommendations.append("\n💪 CHO NGƯỜI TĂNG CÂN/CƠ BẮP:")
        recommendations.append("• Món giàu protein: Cơm tấm (22.5g protein), Phở bò (15.2g protein)")
        recommendations.append("• Thêm: Trứng, đậu phụ, cá hồi")
        recommendations.append("• Nguồn: USDA FoodData Central")

    # Gợi ý dựa trên thiếu hụt dinh dưỡng (từ food logs)
    if food_logs:
        total_iron = sum(log.get('total_nutrition', {}).get('iron', 0) for log in food_logs)
        if total_iron < 10:  # Thiếu sắt
            recommendations.append("\n🩸 THIẾU SẮT:")
            recommendations.append("• Thêm: Thịt đỏ, gan, rau bina vào phở")
            recommendations.append("• Tăng hấp thu: Ăn kèm vitamin C (cam, ổi)")

    # Gợi ý món Việt theo mùa
    current_month = datetime.now().month
    if current_month in [12, 1, 2]:  # Mùa đông
        recommendations.append("\n❄️ MÙA ĐÔNG:")
        recommendations.append("• Bún bò Huế (ấm bụng), Phở bò (bổ dưỡng)")
    elif current_month in [6, 7, 8]:  # Mùa hè
        recommendations.append("\n☀️ MÙA HÈ:")
        recommendations.append("• Gỏi cuốn (mát, ít calo), Chè (giải nhiệt)")

    return "\n".join(recommendations) if recommendations else "Không có gợi ý cụ thể cho câu hỏi này."

def parse_date_context(user_message):
    """
    Phân tích tin nhắn người dùng để xác định ngày được hỏi

    Args:
        user_message: Tin nhắn của người dùng

    Returns:
        tuple: (target_date_str, context_type)
        - target_date_str: Ngày được yêu cầu (YYYY-MM-DD)
        - context_type: Loại ngữ cảnh ('today', 'yesterday', 'specific_date', 'relative')
    """
    vietnam_now = datetime.now(VIETNAM_TZ)
    today_str = vietnam_now.strftime("%Y-%m-%d")
    yesterday_str = (vietnam_now - timedelta(days=1)).strftime("%Y-%m-%d")

    # Chuyển tin nhắn về chữ thường để dễ phân tích
    message_lower = user_message.lower().strip()

    # Các từ khóa chỉ thời gian
    yesterday_keywords = ['hôm qua', 'ngày hôm qua', 'qua', 'yesterday']
    today_keywords = ['hôm nay', 'ngày hôm nay', 'today', 'hiện tại']

    # Kiểm tra từ khóa "hôm qua"
    for keyword in yesterday_keywords:
        if keyword in message_lower:
            return yesterday_str, 'yesterday'

    # Kiểm tra từ khóa "hôm nay"
    for keyword in today_keywords:
        if keyword in message_lower:
            return today_str, 'today'

    # Kiểm tra các ngày tương đối khác
    relative_patterns = [
        (r'(\d+)\s*ngày\s*trước', lambda x: (vietnam_now - timedelta(days=int(x))).strftime("%Y-%m-%d")),
        (r'(\d+)\s*ngày\s*qua', lambda x: (vietnam_now - timedelta(days=int(x))).strftime("%Y-%m-%d")),
        (r'tuần\s*trước', lambda _: (vietnam_now - timedelta(days=7)).strftime("%Y-%m-%d")),
        (r'tuần\s*qua', lambda _: (vietnam_now - timedelta(days=7)).strftime("%Y-%m-%d"))
    ]

    for pattern, date_func in relative_patterns:
        match = re.search(pattern, message_lower)
        if match:
            try:
                if pattern.startswith(r'(\d+)'):
                    days = match.group(1)
                    return date_func(days), 'relative'
                else:
                    return date_func(None), 'relative'
            except:
                continue

    # Kiểm tra định dạng ngày cụ thể (DD/MM/YYYY, DD-MM-YYYY)
    date_patterns = [
        r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})',  # DD/MM/YYYY hoặc DD-MM-YYYY
        r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})'   # YYYY/MM/DD hoặc YYYY-MM-DD
    ]

    for pattern in date_patterns:
        match = re.search(pattern, message_lower)
        if match:
            try:
                if pattern.startswith(r'(\d{1,2})'):  # DD/MM/YYYY
                    day, month, year = match.groups()
                    target_date = datetime(int(year), int(month), int(day))
                else:  # YYYY/MM/DD
                    year, month, day = match.groups()
                    target_date = datetime(int(year), int(month), int(day))

                return target_date.strftime("%Y-%m-%d"), 'specific_date'
            except:
                continue

    # Mặc định trả về hôm nay
    return today_str, 'today'

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
                # Import module firestore_service và professional nutrition APIs
                from services.firestore_service import firestore_service
                from services.nutrition_api_service import nutrition_api

                # 0. Phân tích ngữ cảnh thời gian từ tin nhắn người dùng
                target_date, context_type = parse_date_context(user_message)
                print(f"[DEBUG] 🕐 Phân tích ngữ cảnh: target_date={target_date}, context_type={context_type}")

                # 1. Lấy hồ sơ người dùng
                user_profile = firestore_service.get_user(user_id) or {}

                # 2. Lấy kế hoạch ăn mới nhất
                meal_plan_data = firestore_service.get_latest_meal_plan(user_id)
                meal_plan_dict = meal_plan_data.dict() if meal_plan_data else {}

                # 3. Lấy nhật ký ăn uống theo ngày được yêu cầu
                vietnam_now = datetime.now(VIETNAM_TZ)
                today_str = vietnam_now.strftime("%Y-%m-%d")
                print(f"[DEBUG] ⏰ Thời gian hiện tại (VN): {vietnam_now.isoformat()}")
                print(f"[DEBUG] 📅 Đang truy vấn dữ liệu cho ngày: {target_date} (context: {context_type})")
                print(f"[DEBUG] 🌏 Timezone: {VIETNAM_TZ}")
                food_logs_target = firestore_service.get_food_logs_by_date(user_id, target_date) or []
                print(f"[DEBUG] 🍽️ Tìm thấy {len(food_logs_target)} food logs cho ngày {target_date}")

                # Debug chi tiết từng food log
                for i, log in enumerate(food_logs_target):
                    print(f"[DEBUG] 📝 Food Log #{i+1}:")
                    print(f"[DEBUG]   - ID: {log.get('id', 'N/A')}")
                    print(f"[DEBUG]   - Date: {log.get('date', 'N/A')}")
                    print(f"[DEBUG]   - Meal Type: {log.get('meal_type', 'N/A')}")
                    print(f"[DEBUG]   - Description: {log.get('description', 'N/A')}")
                    print(f"[DEBUG]   - Items count: {len(log.get('items', []))}")
                    print(f"[DEBUG]   - Recognized foods count: {len(log.get('recognized_foods', []))}")
                    print(f"[DEBUG]   - Timestamp: {log.get('timestamp', 'N/A')}")
                    print(f"[DEBUG]   - Created at: {log.get('created_at', 'N/A')}")

                # 4. Lấy thông tin bài tập theo ngày được yêu cầu - với fallback logic
                print(f"[DEBUG] Đang truy vấn dữ liệu bài tập cho user {user_id} với ngày {target_date}...")
                exercise_history = firestore_service.get_exercise_history(user_id, start_date=target_date, end_date=target_date) or []
                print(f"[DEBUG] Tìm thấy {len(exercise_history)} bài tập cho ngày {target_date}")
                if exercise_history:
                    for ex in exercise_history:
                        print(f"[DEBUG] Bài tập: {ex.get('exercise_name', 'N/A')} - {ex.get('date', 'N/A')}")

                # Nếu không có dữ liệu cho ngày được yêu cầu, thử tìm dữ liệu gần nhất (trong 7 ngày qua)
                exercise_date = target_date  # Mặc định là ngày được yêu cầu
                if not exercise_history and context_type in ['today', 'yesterday']:
                    # Chỉ fallback khi hỏi về hôm nay/hôm qua
                    for days_back in range(1, 8):  # Tìm trong 7 ngày qua
                        past_date = (datetime.now(VIETNAM_TZ) - timedelta(days=days_back)).strftime("%Y-%m-%d")
                        exercise_history = firestore_service.get_exercise_history(user_id, start_date=past_date, end_date=past_date) or []
                        if exercise_history:
                            exercise_date = past_date
                            print(f"[DEBUG] Tìm thấy dữ liệu bài tập gần nhất vào ngày: {past_date}")
                            break

                # 5. Lấy thông tin nước uống theo ngày được yêu cầu - với fallback logic
                print(f"[DEBUG] Đang truy vấn dữ liệu nước uống cho user {user_id} với ngày {target_date}...")
                water_intake = firestore_service.get_water_intake_by_date(user_id, target_date) or []
                print(f"[DEBUG] Tìm thấy {len(water_intake)} lượt uống nước cho ngày {target_date}")
                if water_intake:
                    for water in water_intake:
                        print(f"[DEBUG] Nước uống: {water.get('amount_ml', 'N/A')}ml - {water.get('date', 'N/A')}")

                # Nếu không có dữ liệu cho ngày được yêu cầu, thử tìm dữ liệu gần nhất (trong 7 ngày qua)
                water_date = target_date  # Mặc định là ngày được yêu cầu
                if not water_intake and context_type in ['today', 'yesterday']:
                    # Chỉ fallback khi hỏi về hôm nay/hôm qua
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
                    food_logs_target,
                    exercise_history,
                    water_intake,
                    exercise_date,
                    water_date,
                    target_date,
                    context_type
                )

                # Thêm nutrition analysis nâng cao với professional data
                nutrition_analysis = analyze_user_nutrition(user_profile, food_logs_target, meal_plan_dict)
                if nutrition_analysis:
                    context_data += f"\n\n🔬 PHÂN TÍCH DINH DƯỠNG NÂNG CAO:\n{nutrition_analysis}"

                # Thêm intelligent food recommendations (sync version)
                food_recommendations = get_intelligent_food_recommendations_sync(user_message, user_profile, food_logs_target)
                if food_recommendations:
                    context_data += f"\n\n🎯 GỢI Ý THỰC PHẨM THÔNG MINH:\n{food_recommendations}"
                
                # Xây dựng prompt thông minh với ngữ cảnh thời gian
                time_context_note = ""
                if context_type == 'yesterday':
                    time_context_note = f"\n⚠️ LƯU Ý QUAN TRỌNG: Người dùng đang hỏi về HÔM QUA ({target_date}), KHÔNG PHẢI hôm nay. Hãy trả lời chính xác về dữ liệu hôm qua."
                elif context_type == 'specific_date':
                    time_context_note = f"\n⚠️ LƯU Ý QUAN TRỌNG: Người dùng đang hỏi về ngày {target_date}, KHÔNG PHẢI hôm nay. Hãy trả lời chính xác về dữ liệu ngày đó."
                elif context_type == 'relative':
                    time_context_note = f"\n⚠️ LƯU Ý QUAN TRỌNG: Người dùng đang hỏi về ngày {target_date}, KHÔNG PHẢI hôm nay. Hãy trả lời chính xác về dữ liệu ngày đó."

                augmented_prompt = f"""Bạn là một trợ lý dinh dưỡng ảo tên là DietAI. Nhiệm vụ của bạn là trả lời câu hỏi của người dùng dựa trên thông tin cá nhân và hoạt động hàng ngày của họ.{time_context_note}

--- DỮ LIỆU CÁ NHÂN CỦA NGƯỜI DÙNG ---
{context_data}
--- KẾT THÚC DỮ LIỆU ---

HƯỚNG DẪN TRẢI LỜI:
1. Đọc kỹ dữ liệu trên và chú ý đến ngày cụ thể được đề cập
2. Trả lời chính xác theo ngày mà người dùng hỏi (hôm nay, hôm qua, hay ngày cụ thể)
3. Nếu không có dữ liệu cho ngày được hỏi, hãy nói rõ "không có dữ liệu" thay vì dùng dữ liệu từ ngày khác
4. Sử dụng ngôn ngữ thân thiện và chính xác bằng tiếng Việt

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
                    "content": get_enhanced_nutrition_system_prompt(use_rag)
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