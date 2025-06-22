# -*- coding: utf-8 -*-
"""
Test script để kiểm tra Vietnamese Dish Generator
Tạo 10 món ăn mẫu để xem chất lượng
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from services.vietnamese_dish_generator import vietnamese_dish_generator
    print("✅ Successfully imported vietnamese_dish_generator")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📁 Current directory:", os.getcwd())
    print("📁 Python path:", sys.path)
    sys.exit(1)

import json

def test_dish_generation():
    """Test tạo món ăn"""
    print("🔧 Testing Vietnamese Dish Generator...")
    print("=" * 60)
    
    # Tạo 10 món ăn mẫu
    sample_dishes = vietnamese_dish_generator.generate_multiple_dishes(10)
    
    for i, dish in enumerate(sample_dishes, 1):
        print(f"\n📋 MÓN {i}: {dish['name']}")
        print(f"🌍 Miền: {dish['region']}")
        print(f"🍽️ Bữa: {dish['meal_type']}")
        print(f"⏰ Thời gian: {dish['cooking_time']}")
        print(f"📊 Dinh dưỡng: {dish['nutrition']['calories']} kcal, "
              f"{dish['nutrition']['protein']}g protein, "
              f"{dish['nutrition']['fat']}g fat, "
              f"{dish['nutrition']['carbs']}g carbs")
        
        print("🥘 Nguyên liệu:")
        for ingredient in dish['ingredients']:
            print(f"  - {ingredient['name']}: {ingredient['amount']}g")
        
        print("👨‍🍳 Cách làm:")
        for step in dish['preparation']:
            print(f"  • {step}")
        
        print("-" * 60)
    
    return sample_dishes

def analyze_nutrition_accuracy(dishes):
    """Phân tích độ chính xác dinh dưỡng"""
    print("\n🔍 PHÂN TÍCH ĐỘ CHÍNH XÁC DINH DƯỠNG:")
    print("=" * 60)
    
    total_dishes = len(dishes)
    valid_nutrition = 0
    
    for dish in dishes:
        nutrition = dish['nutrition']
        calories = nutrition['calories']
        protein = nutrition['protein']
        fat = nutrition['fat']
        carbs = nutrition['carbs']
        
        # Kiểm tra tính hợp lý
        calculated_calories = (protein * 4) + (fat * 9) + (carbs * 4)
        calorie_diff = abs(calculated_calories - calories) / calories if calories > 0 else 1
        
        if calorie_diff < 0.3:  # Sai lệch < 30%
            valid_nutrition += 1
        else:
            print(f"⚠️ {dish['name']}: Sai lệch calories {calorie_diff:.1%}")
    
    accuracy = (valid_nutrition / total_dishes) * 100
    print(f"✅ Độ chính xác dinh dưỡng: {accuracy:.1f}% ({valid_nutrition}/{total_dishes})")
    
    return accuracy

def analyze_diversity(dishes):
    """Phân tích độ đa dạng"""
    print("\n🌈 PHÂN TÍCH ĐỘ ĐA DẠNG:")
    print("=" * 60)
    
    # Đếm theo miền
    regions = {}
    meal_types = {}
    proteins = {}
    
    for dish in dishes:
        region = dish['region']
        meal_type = dish['meal_type']
        
        regions[region] = regions.get(region, 0) + 1
        meal_types[meal_type] = meal_types.get(meal_type, 0) + 1
        
        # Đếm protein
        for ingredient in dish['ingredients']:
            name = ingredient['name']
            if any(keyword in name for keyword in ['thịt', 'cá', 'tôm', 'gà', 'bò', 'heo']):
                proteins[name] = proteins.get(name, 0) + 1
    
    print("🌍 Phân bố theo miền:")
    for region, count in regions.items():
        print(f"  {region}: {count} món")
    
    print("\n🍽️ Phân bố theo bữa:")
    for meal_type, count in meal_types.items():
        print(f"  {meal_type}: {count} món")
    
    print("\n🥩 Đa dạng protein:")
    for protein, count in sorted(proteins.items(), key=lambda x: x[1], reverse=True):
        print(f"  {protein}: {count} lần")
    
    diversity_score = len(set(dish['name'] for dish in dishes)) / len(dishes) * 100
    print(f"\n📊 Điểm đa dạng: {diversity_score:.1f}% (tên món không trùng)")
    
    return diversity_score

if __name__ == "__main__":
    # Test tạo món ăn
    dishes = test_dish_generation()
    
    # Phân tích
    nutrition_accuracy = analyze_nutrition_accuracy(dishes)
    diversity_score = analyze_diversity(dishes)
    
    print("\n" + "=" * 60)
    print("📊 KẾT QUẢ TỔNG QUAN:")
    print(f"✅ Độ chính xác dinh dưỡng: {nutrition_accuracy:.1f}%")
    print(f"🌈 Độ đa dạng món ăn: {diversity_score:.1f}%")
    
    if nutrition_accuracy > 80 and diversity_score > 80:
        print("🎉 CHẤT LƯỢNG TỐT - Có thể tạo 300+ món ăn!")
    elif nutrition_accuracy > 60 and diversity_score > 60:
        print("⚠️ CHẤT LƯỢNG TRUNG BÌNH - Cần cải thiện")
    else:
        print("❌ CHẤT LƯỢNG THẤP - Cần sửa đổi thuật toán")
