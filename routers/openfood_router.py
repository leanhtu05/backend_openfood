from fastapi import APIRouter, Request, Depends, Form, HTTPException, Body
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Optional, Any
import os
import uuid
from datetime import datetime
import json

# Import GroqService để tạo món ăn tự động
from groq_integration import groq_service

router = APIRouter()

# Danh sách món ăn tạm thời (trong thực tế bạn sẽ dùng database)
food_items = []

# Template instance sẽ được inject qua dependency
def get_templates():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return Jinja2Templates(directory=os.path.join(base_dir, "templates"))

# Helper function để đảm bảo giá trị dinh dưỡng là số
def ensure_numeric(value, default=0):
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    """Trang chủ OpenFood"""
    # Lấy 3 món ăn ngẫu nhiên cho phần gợi ý
    suggested_foods = food_items[:3] if len(food_items) >= 3 else food_items
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "suggested_foods": suggested_foods
    })

@router.get("/food", response_class=HTMLResponse)
async def list_foods(
    request: Request, 
    search: Optional[str] = None,
    meal_type: Optional[str] = None,
    sort: Optional[str] = "name",
    templates: Jinja2Templates = Depends(get_templates)
):
    """Liệt kê danh sách món ăn với tính năng tìm kiếm và sắp xếp"""
    filtered_foods = food_items
    
    # Lọc theo từ khóa tìm kiếm
    if search:
        search = search.lower()
        filtered_foods = [
            food for food in filtered_foods 
            if search in food["name"].lower() or 
               (food.get("description") and search in food["description"].lower())
        ]
    
    # Lọc theo loại bữa ăn
    if meal_type:
        filtered_foods = [
            food for food in filtered_foods
            if food.get("meal_type") == meal_type
        ]
    
    # Sắp xếp kết quả
    if sort == "calories":
        filtered_foods = sorted(filtered_foods, key=lambda x: x["nutrition"]["calories"])
    elif sort == "protein":
        filtered_foods = sorted(filtered_foods, key=lambda x: x["nutrition"]["protein"])
    else:  # Default: sort by name
        filtered_foods = sorted(filtered_foods, key=lambda x: x["name"])
    
    return templates.TemplateResponse("food/list.html", {
        "request": request,
        "foods": filtered_foods
    })

@router.get("/food/create", response_class=HTMLResponse)
async def create_food_form(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    """Hiển thị form tạo món ăn mới"""
    return templates.TemplateResponse("food/create.html", {"request": request})

@router.post("/food/create")
async def create_food(request: Request):
    """Xử lý tạo món ăn mới từ form"""
    form_data = await request.form()
    
    # Extract the basic information
    food_id = str(uuid.uuid4())
    name = form_data.get("name")
    description = form_data.get("description", "")
    preparation_time = form_data.get("preparation_time", "")
    health_benefits = form_data.get("health_benefits", "")
    
    # Extract nutrition values
    nutrition = {
        "calories": ensure_numeric(form_data.get("calories"), 0),
        "protein": ensure_numeric(form_data.get("protein"), 0),
        "fat": ensure_numeric(form_data.get("fat"), 0),
        "carbs": ensure_numeric(form_data.get("carbs"), 0),
    }
    
    # Extract ingredients
    ingredients = []
    for key in form_data.keys():
        if key.startswith("ingredient_name_"):
            index = key.split("_")[-1]
            ingredient_name = form_data.get(f"ingredient_name_{index}")
            ingredient_amount = form_data.get(f"ingredient_amount_{index}", "")
            
            if ingredient_name:
                ingredients.append({
                    "name": ingredient_name,
                    "amount": ingredient_amount
                })
    
    # Extract preparation steps
    preparation = []
    for key in form_data.keys():
        if key.startswith("preparation_step_"):
            index = key.split("_")[-1]
            step = form_data.get(f"preparation_step_{index}")
            
            if step:
                preparation.append(step)
    
    # Create the food item
    food_item = {
        "id": food_id,
        "name": name,
        "description": description,
        "preparation_time": preparation_time,
        "health_benefits": health_benefits,
        "ingredients": ingredients,
        "preparation": preparation,
        "nutrition": nutrition,
        "created_at": datetime.now().isoformat()
    }
    
    food_items.append(food_item)
    
    return RedirectResponse(url=f"/food/{food_id}", status_code=303)

@router.get("/food/{food_id}", response_class=HTMLResponse)
async def food_detail(
    food_id: str, 
    request: Request, 
    templates: Jinja2Templates = Depends(get_templates)
):
    """Hiển thị chi tiết món ăn"""
    # Tìm món ăn theo ID
    food = next((item for item in food_items if item["id"] == food_id), None)
    if not food:
        raise HTTPException(status_code=404, detail="Món ăn không tồn tại")
        
    return templates.TemplateResponse("food/detail.html", {
        "request": request, 
        "food": food
    })

@router.get("/food/edit/{food_id}", response_class=HTMLResponse)
async def edit_food_form(
    food_id: str, 
    request: Request, 
    templates: Jinja2Templates = Depends(get_templates)
):
    """Hiển thị form chỉnh sửa món ăn"""
    # Tìm món ăn theo ID
    food = next((item for item in food_items if item["id"] == food_id), None)
    if not food:
        raise HTTPException(status_code=404, detail="Món ăn không tồn tại")
        
    return templates.TemplateResponse("food/edit.html", {
        "request": request, 
        "food": food
    })

@router.post("/food/edit/{food_id}")
async def edit_food(food_id: str, request: Request):
    """Xử lý cập nhật thông tin món ăn"""
    # Tìm món ăn theo ID
    food_index = next((i for i, item in enumerate(food_items) if item["id"] == food_id), None)
    if food_index is None:
        raise HTTPException(status_code=404, detail="Món ăn không tồn tại")
    
    form_data = await request.form()
    
    # Extract the basic information
    name = form_data.get("name")
    description = form_data.get("description", "")
    preparation_time = form_data.get("preparation_time", "")
    health_benefits = form_data.get("health_benefits", "")
    
    # Extract nutrition values
    nutrition = {
        "calories": ensure_numeric(form_data.get("calories"), 0),
        "protein": ensure_numeric(form_data.get("protein"), 0),
        "fat": ensure_numeric(form_data.get("fat"), 0),
        "carbs": ensure_numeric(form_data.get("carbs"), 0),
    }
    
    # Extract ingredients
    ingredients = []
    for key in form_data.keys():
        if key.startswith("ingredient_name_"):
            index = key.split("_")[-1]
            ingredient_name = form_data.get(f"ingredient_name_{index}")
            ingredient_amount = form_data.get(f"ingredient_amount_{index}", "")
            
            if ingredient_name:
                ingredients.append({
                    "name": ingredient_name,
                    "amount": ingredient_amount
                })
    
    # Extract preparation steps
    preparation = []
    for key in form_data.keys():
        if key.startswith("preparation_step_"):
            index = key.split("_")[-1]
            step = form_data.get(f"preparation_step_{index}")
            
            if step:
                preparation.append(step)
    
    # Update the food item
    food_items[food_index].update({
        "name": name,
        "description": description,
        "preparation_time": preparation_time,
        "health_benefits": health_benefits,
        "ingredients": ingredients,
        "preparation": preparation,
        "nutrition": nutrition,
        "updated_at": datetime.now().isoformat()
    })
    
    return RedirectResponse(url=f"/food/{food_id}", status_code=303)

@router.delete("/api/food/{food_id}")
async def delete_food(food_id: str):
    """API endpoint để xóa món ăn"""
    global food_items
    initial_length = len(food_items)
    food_items = [item for item in food_items if item["id"] != food_id]
    
    if len(food_items) == initial_length:
        raise HTTPException(status_code=404, detail="Món ăn không tồn tại")
    
    return {"message": "Đã xóa món ăn thành công"}

@router.get("/food/generate", response_class=HTMLResponse)
async def generate_food_form(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    """Hiển thị form tạo món ăn với AI"""
    return templates.TemplateResponse("food/create.html", {
        "request": request,
        "use_ai": True
    })

@router.post("/api/generate-meal")
async def generate_meal(
    meal_data: Dict[str, Any] = Body(...)
):
    """API endpoint để tạo món ăn với Groq AI"""
    try:
        # Lấy thông tin từ request body
        meal_type = meal_data.get("meal_type", "lunch")
        calories = int(meal_data.get("calories", 400))
        protein = int(meal_data.get("protein", 25))
        fat = int(meal_data.get("fat", 15))
        carbs = int(meal_data.get("carbs", 40))
        preferences = meal_data.get("preferences", [])
        allergies = meal_data.get("allergies", [])
        cuisine_style = meal_data.get("cuisine_style", "vietnamese")
        
        # Sử dụng groq_service đã import
        
        # Gọi API để tạo món ăn
        meal_suggestions = groq_service.generate_meal_suggestions(
            calories_target=calories,
            protein_target=protein,
            fat_target=fat,
            carbs_target=carbs,
            meal_type=meal_type,
            preferences=preferences,
            allergies=allergies,
            cuisine_style=cuisine_style
        )
        
        # Trả về kết quả dưới dạng JSON
        return meal_suggestions
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi tạo món ăn: {str(e)}")

# Load món ăn ban đầu từ file JSON nếu có
def load_initial_foods():
    """Tải dữ liệu món ăn ban đầu từ file nếu có"""
    try:
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "foods.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                global food_items
                food_items = json.load(f)
                print(f"Đã tải {len(food_items)} món ăn từ file")
    except Exception as e:
        print(f"Lỗi khi tải dữ liệu món ăn: {str(e)}")

# Lưu dữ liệu món ăn vào file
def save_foods_to_file():
    """Lưu dữ liệu món ăn vào file"""
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        os.makedirs(data_dir, exist_ok=True)
        
        file_path = os.path.join(data_dir, "foods.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(food_items, f, ensure_ascii=False, indent=2)
            print(f"Đã lưu {len(food_items)} món ăn vào file")
    except Exception as e:
        print(f"Lỗi khi lưu dữ liệu món ăn: {str(e)}")

# Initialize data on startup
load_initial_foods() 