#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra tính sáng tạo của AI trong việc tạo món ăn mới
"""

import os
import sys
from groq_integration import GroqService

def test_creative_meal_generation():
    """Test khả năng tạo món ăn sáng tạo của AI"""
    
    print("🎨 TESTING AI CREATIVITY IN MEAL GENERATION")
    print("=" * 60)
    
    # Khởi tạo Groq service
    groq_service = GroqService()
    
    if not groq_service.available:
        print("❌ Groq service not available")
        return
    
    # Test cases cho các bữa ăn khác nhau
    test_cases = [
        {
            "meal_type": "bữa sáng",
            "calories": 350,
            "protein": 20,
            "fat": 15,
            "carbs": 45,
            "preferences": ["healthy", "innovative"],
            "description": "Creative breakfast with fusion elements"
        },
        {
            "meal_type": "bữa trưa", 
            "calories": 550,
            "protein": 35,
            "fat": 20,
            "carbs": 65,
            "preferences": ["high-protein", "fusion"],
            "description": "Innovative lunch combining traditional and modern"
        },
        {
            "meal_type": "bữa tối",
            "calories": 450,
            "protein": 25,
            "fat": 18,
            "carbs": 55,
            "preferences": ["light", "creative"],
            "description": "Creative dinner with unique presentation"
        }
    ]
    
    creative_dishes = []
    traditional_dishes = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"Meal Type: {test_case['meal_type']}")
        print(f"Targets: {test_case['calories']}cal, {test_case['protein']}g protein")
        
        try:
            # Generate meal suggestions
            results = groq_service.generate_meal_suggestions(
                calories_target=test_case['calories'],
                protein_target=test_case['protein'],
                fat_target=test_case['fat'],
                carbs_target=test_case['carbs'],
                meal_type=test_case['meal_type'],
                preferences=test_case['preferences'],
                use_ai=True
            )
            
            if results and len(results) > 0:
                for dish in results:
                    dish_name = dish.get('name', 'Unknown')
                    description = dish.get('description', 'No description')
                    
                    print(f"✅ Generated: {dish_name}")
                    print(f"   Description: {description}")
                    
                    # Analyze creativity
                    creativity_score = analyze_creativity(dish_name, description)
                    print(f"   Creativity Score: {creativity_score}/10")
                    
                    if creativity_score >= 7:
                        creative_dishes.append({
                            'name': dish_name,
                            'description': description,
                            'score': creativity_score,
                            'meal_type': test_case['meal_type']
                        })
                    else:
                        traditional_dishes.append({
                            'name': dish_name,
                            'description': description,
                            'score': creativity_score,
                            'meal_type': test_case['meal_type']
                        })
            else:
                print("❌ No dishes generated")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Summary report
    print("\n" + "=" * 60)
    print("📊 CREATIVITY ANALYSIS REPORT")
    print("=" * 60)
    
    print(f"\n🎨 CREATIVE DISHES ({len(creative_dishes)} dishes):")
    for dish in creative_dishes:
        print(f"   ⭐ {dish['name']} (Score: {dish['score']}/10)")
        print(f"      {dish['description'][:100]}...")
        print(f"      Meal: {dish['meal_type']}")
    
    print(f"\n📚 TRADITIONAL DISHES ({len(traditional_dishes)} dishes):")
    for dish in traditional_dishes:
        print(f"   📖 {dish['name']} (Score: {dish['score']}/10)")
        print(f"      {dish['description'][:100]}...")
        print(f"      Meal: {dish['meal_type']}")
    
    # Calculate overall creativity percentage
    total_dishes = len(creative_dishes) + len(traditional_dishes)
    if total_dishes > 0:
        creativity_percentage = (len(creative_dishes) / total_dishes) * 100
        print(f"\n🎯 OVERALL CREATIVITY: {creativity_percentage:.1f}%")
        
        if creativity_percentage >= 70:
            print("🎉 EXCELLENT! AI is generating highly creative dishes")
        elif creativity_percentage >= 50:
            print("👍 GOOD! AI shows good creativity")
        elif creativity_percentage >= 30:
            print("⚠️ MODERATE! AI needs more creativity prompting")
        else:
            print("❌ LOW! AI is generating mostly traditional dishes")
    else:
        print("❌ No dishes generated for analysis")

def analyze_creativity(dish_name: str, description: str) -> int:
    """
    Phân tích tính sáng tạo của món ăn
    
    Returns:
        int: Điểm sáng tạo từ 1-10
    """
    score = 0
    
    # Check for traditional names (negative points)
    traditional_names = [
        'phở gà', 'phở bò', 'cơm tấm', 'bánh mì', 'xôi mặn', 
        'cháo gà', 'bún bò', 'cơm chiên', 'bánh xèo', 'nem rán'
    ]
    
    name_lower = dish_name.lower()
    
    # Penalty for traditional names
    for traditional in traditional_names:
        if traditional in name_lower:
            score -= 3
            break
    
    # Bonus for creative elements
    creative_keywords = [
        'fusion', 'nướng mật ong', 'cuốn lá', 'sốt đặc biệt', 'truffle',
        'nấu dừa', 'bbq', 'grilled', 'crispy', 'caramelized', 'glazed',
        'herb-crusted', 'pan-seared', 'slow-cooked', 'smoked'
    ]
    
    for keyword in creative_keywords:
        if keyword in name_lower or keyword in description.lower():
            score += 2
    
    # Bonus for unique combinations
    if 'với' in name_lower or 'kết hợp' in description.lower():
        score += 1
    
    # Bonus for fusion elements
    if any(word in name_lower for word in ['fusion', 'style', 'kiểu']):
        score += 2
    
    # Bonus for detailed descriptions
    if len(description) > 100:
        score += 1
    
    # Bonus for innovative cooking methods
    innovative_methods = [
        'nướng than', 'áp chảo', 'hấp lá chuối', 'nấu chậm', 
        'ướp đặc biệt', 'tẩm bột', 'chiên giòn'
    ]
    
    for method in innovative_methods:
        if method in description.lower():
            score += 1
    
    # Base score
    score += 5
    
    # Ensure score is between 1-10
    return max(1, min(10, score))

if __name__ == "__main__":
    test_creative_meal_generation()
