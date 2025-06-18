"""
Chat API Endpoint for DietAI
Provides intelligent chat functionality with RAG (Retrieval-Augmented Generation)
"""

import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from openai import OpenAI

from auth_utils import get_current_user
from models import TokenPayload

# Initialize router
router = APIRouter(prefix="/chat", tags=["Chat API"])

# Initialize Groq client for chat API
groq_api_key = os.environ.get("GROQ_API_KEY", "")
try:
    chat_client = OpenAI(
        api_key=groq_api_key,
        base_url="https://api.groq.com/openai/v1"
    )
    chat_available = bool(groq_api_key)
except:
    chat_client = None
    chat_available = False

# Chat API models
class ChatMessage(BaseModel):
    message: str
    user_id: str = "anonymous"

class ChatResponse(BaseModel):
    reply: str
    chat_id: str = ""

def format_user_context(user_profile: dict, meal_plan: dict, food_logs: list, exercise_history: list = None, water_intake: list = None, user_id: str = None) -> str:
    """
    Định dạng dữ liệu người dùng thành một đoạn văn bản context cho chatbot
    
    Args:
        user_profile: Dữ liệu hồ sơ người dùng
        meal_plan: Dữ liệu kế hoạch ăn uống
        food_logs: Danh sách các bản ghi thực phẩm đã ăn
        exercise_history: Lịch sử tập luyện (tùy chọn)
        water_intake: Lượng nước uống (tùy chọn)
        user_id: ID người dùng (tùy chọn)
        
    Returns:
        str: Context được định dạng cho chatbot
    """
    context_parts = []
    
    # Thông tin hồ sơ người dùng
    if user_profile:
        context_parts.append("=== THÔNG TIN NGƯỜI DÙNG ===")
        if 'name' in user_profile:
            context_parts.append(f"- Tên: {user_profile['name']}")
        if 'age' in user_profile:
            context_parts.append(f"- Tuổi: {user_profile['age']}")
        if 'weight' in user_profile:
            context_parts.append(f"- Cân nặng: {user_profile['weight']} kg")
        if 'height' in user_profile:
            context_parts.append(f"- Chiều cao: {user_profile['height']} cm")
        if 'activity_level' in user_profile:
            context_parts.append(f"- Mức độ hoạt động: {user_profile['activity_level']}")
        if 'health_conditions' in user_profile:
            context_parts.append(f"- Tình trạng sức khỏe: {user_profile['health_conditions']}")
        if 'dietary_preferences' in user_profile:
            context_parts.append(f"- Sở thích ăn uống: {user_profile['dietary_preferences']}")
    
    # Kế hoạch ăn uống hiện tại
    if meal_plan:
        context_parts.append("\n=== KẾ HOẠCH ĂN UỐNG HIỆN TẠI ===")
        if 'nutrition_targets' in meal_plan:
            targets = meal_plan['nutrition_targets']
            context_parts.append(f"- Mục tiêu calories: {targets.get('calories', 'N/A')} kcal")
            context_parts.append(f"- Mục tiêu protein: {targets.get('protein', 'N/A')} g")
            context_parts.append(f"- Mục tiêu carbs: {targets.get('carbs', 'N/A')} g")
            context_parts.append(f"- Mục tiêu fat: {targets.get('fat', 'N/A')} g")
        
        if 'weekly_plan' in meal_plan:
            context_parts.append("- Có kế hoạch ăn uống cho tuần này")
    
    # Lịch sử thực phẩm gần đây
    if food_logs:
        context_parts.append("\n=== THỰC PHẨM ĐÃ ĂN GÂN ĐÂY ===")
        recent_foods = food_logs[:5]  # Chỉ lấy 5 bản ghi gần nhất
        for food_log in recent_foods:
            if 'recognized_foods' in food_log:
                for food in food_log['recognized_foods']:
                    food_name = food.get('food_name', 'Unknown')
                    context_parts.append(f"- {food_name}")
    
    # Lịch sử tập luyện (nếu có)
    if exercise_history:
        context_parts.append("\n=== LỊCH SỬ TẬP LUYỆN ===")
        recent_exercises = exercise_history[:3]  # Chỉ lấy 3 bản ghi gần nhất
        for exercise in recent_exercises:
            exercise_name = exercise.get('exercise_name', 'Unknown')
            duration = exercise.get('duration', 'N/A')
            context_parts.append(f"- {exercise_name}: {duration} phút")
    
    # Lượng nước uống (nếu có)
    if water_intake:
        context_parts.append("\n=== LƯỢNG NƯỚC UỐNG HÔM NAY ===")
        total_water = sum([entry.get('amount', 0) for entry in water_intake])
        context_parts.append(f"- Tổng lượng nước: {total_water} ml")
    else:
        context_parts.append("\n=== LƯỢNG NƯỚC UỐNG HÔM NAY ===")
        context_parts.append("- Nước uống hôm nay: Chưa ghi nhận lượng nước uống nào.")
    
    return "\n".join(context_parts)

@router.post("", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    user: TokenPayload = Depends(get_current_user)
):
    """
    Endpoint nhận tin nhắn từ người dùng, xử lý qua Groq API và trả về phản hồi
    Sử dụng kỹ thuật RAG (Retrieval-Augmented Generation) để cá nhân hóa phản hồi
    
    Args:
    - message: Tin nhắn từ người dùng
    - user: Thông tin người dùng đã xác thực
    
    Returns:
    - Phản hồi từ AI
    """
    try:
        if not chat_client or not chat_available:
            raise HTTPException(
                status_code=503,
                detail="Groq API không khả dụng. Vui lòng cấu hình GROQ_API_KEY trong biến môi trường."
            )
        
        # Lấy user_id từ token xác thực
        user_id = user.uid
        print(f"Chat request for user: {user_id}")
        
        # Truy xuất dữ liệu người dùng từ Firestore
        try:
            from services.firestore_service import firestore_service
            
            # Lấy hồ sơ người dùng
            user_profile = firestore_service.get_user_profile(user_id)
            print(f"User profile retrieved: {bool(user_profile)}")
            
            # Lấy kế hoạch ăn uống hiện tại
            meal_plan = firestore_service.get_latest_meal_plan(user_id)
            print(f"Meal plan retrieved: {bool(meal_plan)}")
            
            # Lấy lịch sử thực phẩm gần đây (7 ngày)
            food_logs = firestore_service.get_recent_food_logs(user_id, days=7)
            print(f"Food logs retrieved: {len(food_logs) if food_logs else 0} entries")
            
            # Lấy lịch sử tập luyện (tùy chọn)
            exercise_history = firestore_service.get_recent_exercise_logs(user_id, days=7)
            print(f"Exercise history retrieved: {len(exercise_history) if exercise_history else 0} entries")
            
            # Lấy lượng nước uống hôm nay
            water_intake = firestore_service.get_today_water_intake(user_id)
            print(f"Water intake retrieved: {len(water_intake) if water_intake else 0} entries")
            
            # Tạo context từ dữ liệu người dùng
            user_context = format_user_context(
                user_profile=user_profile,
                meal_plan=meal_plan,
                food_logs=food_logs,
                exercise_history=exercise_history,
                water_intake=water_intake,
                user_id=user_id
            )
            
            # Tạo prompt được tăng cường với dữ liệu người dùng
            augmented_prompt = f"""
Dựa trên thông tin sau về người dùng:

{user_context}

Hãy trả lời câu hỏi sau một cách cá nhân hóa và hữu ích:
{message.message}

Lưu ý: Hãy đưa ra lời khuyên cụ thể dựa trên dữ liệu thực tế của người dùng.
"""
            print(f"Augmented prompt created with {len(user_context)} characters of context")
            
        except Exception as retrieval_error:
            print(f"Lỗi khi truy xuất dữ liệu người dùng: {str(retrieval_error)}")
            print(f"Tiếp tục với prompt thông thường")
            # Fallback to regular prompt if retrieval fails
            augmented_prompt = message.message
            
        # Gọi Groq API với prompt đã được bổ sung dữ liệu
        completion = chat_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là trợ lý dinh dưỡng ảo tên là DietAI. Trả lời dựa trên dữ liệu người dùng."
                },
                {"role": "user", "content": augmented_prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
            timeout=60  # Tăng timeout lên 60 giây
        )
        
        ai_reply = completion.choices[0].message.content
        print(f"AI reply generated: {len(ai_reply)} characters")
        
        # Lưu tin nhắn vào Firebase
        try:
            from firebase_admin import firestore
            db = firestore.client()
            
            # Tạo dữ liệu chat
            chat_data = {
                "user_id": user_id,
                "user_message": message.message,
                "ai_reply": ai_reply,
                "timestamp": datetime.now().isoformat(),
                "model": "llama3-8b-8192",
                "augmented": True
            }
            
            # Tạo ID cho chat
            chat_id = str(uuid.uuid4())
            
            # Lưu vào Firestore
            db.collection("chat_history").document(chat_id).set(chat_data)
            print(f"Đã lưu chat với ID: {chat_id}")
            
            # Trả về kết quả dạng JSON với chat_id
            return {"reply": ai_reply, "chat_id": chat_id}
            
        except Exception as firebase_error:
            print(f"Lỗi khi lưu chat vào Firebase: {str(firebase_error)}")
            # Vẫn trả về phản hồi ngay cả khi lưu vào Firebase thất bại
            return ChatResponse(reply=ai_reply)
        
    except Exception as e:
        print(f"Lỗi khi xử lý chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi: {str(e)}")

@router.get("/history")
async def get_chat_history(
    user_id: str = Query(..., description="ID của người dùng"),
    limit: int = Query(10, description="Số lượng tin nhắn tối đa trả về")
):
    """
    Lấy lịch sử chat của một người dùng
    
    Parameters:
    - user_id: ID của người dùng
    - limit: Số lượng tin nhắn tối đa trả về
    
    Returns:
    - Danh sách lịch sử chat
    """
    try:
        from firebase_admin import firestore
        db = firestore.client()
        
        # Truy vấn Firestore
        chats = (db.collection("chat_history")
                .where("user_id", "==", user_id)
                .limit(limit)
                .get())
        
        # Chuyển đổi kết quả thành danh sách
        chat_list = []
        for chat in chats:
            chat_data = chat.to_dict()
            chat_data["id"] = chat.id
            chat_list.append(chat_data)
        
        return {"history": chat_list, "count": len(chat_list)}
        
    except Exception as e:
        print(f"Lỗi khi lấy lịch sử chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Đã xảy ra lỗi khi lấy lịch sử chat: {str(e)}")

@router.get("/health")
async def chat_health_check():
    """
    Health check endpoint cho Chat API
    """
    return {
        "status": "healthy" if chat_available else "unhealthy",
        "service": "Chat API",
        "groq_available": chat_available,
        "model": "llama3-8b-8192" if chat_available else None
    }
