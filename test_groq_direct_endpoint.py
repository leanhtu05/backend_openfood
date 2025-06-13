#!/usr/bin/env python3
"""
Test trực tiếp hệ thống Groq cải tiến thông qua meal suggestions
"""

import sys
import os
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from groq_integration import GroqService

def print_separator(title):
    """In separator với title"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_subsection(title):
    """In subsection header"""
    print(f"\n--- {title} ---")

def test_day_replacement_simulation():
    """Simulate việc thay thế một ngày hoàn chỉnh"""
    print_separator("🧪 TESTING DAY REPLACEMENT SIMULATION")
    
    # Khởi tạo service
    groq_service = GroqService()
    
    # Simulate thay thế Thứ 2 - Giảm cân
    test_case = {
        "name": "Thay thế Thứ 2 - Giảm cân",
        "day": "Thứ 2",
        "total_calories": 1200,
        "total_protein": 80,
        "total_fat": 40,
        "total_carbs": 120,
        "preferences": ["healthy", "low-calorie", "vietnamese"],
        "allergies": [],
        "cuisine_style": "Vietnamese"
    }
    
    print_subsection(f"Test Case: {test_case['name']}")
    print(f"📋 Target for the day:")
    print(f"   Day: {test_case['day']}")
    print(f"   Total Calories: {test_case['total_calories']}kcal")
    print(f"   Total Protein: {test_case['total_protein']}g")
    print(f"   Total Fat: {test_case['total_fat']}g")
    print(f"   Total Carbs: {test_case['total_carbs']}g")
    
    # Phân chia dinh dưỡng cho 3 bữa chính
    meals = [
        {
            "name": "Bữa sáng",
            "calories": int(test_case['total_calories'] * 0.25),  # 25%
            "protein": int(test_case['total_protein'] * 0.25),
            "fat": int(test_case['total_fat'] * 0.25),
            "carbs": int(test_case['total_carbs'] * 0.25)
        },
        {
            "name": "Bữa trưa", 
            "calories": int(test_case['total_calories'] * 0.4),   # 40%
            "protein": int(test_case['total_protein'] * 0.4),
            "fat": int(test_case['total_fat'] * 0.4),
            "carbs": int(test_case['total_carbs'] * 0.4)
        },
        {
            "name": "Bữa tối",
            "calories": int(test_case['total_calories'] * 0.35),  # 35%
            "protein": int(test_case['total_protein'] * 0.35),
            "fat": int(test_case['total_fat'] * 0.35),
            "carbs": int(test_case['total_carbs'] * 0.35)
        }
    ]
    
    day_results = []
    total_generated_calories = 0
    total_generated_protein = 0
    total_generated_fat = 0
    total_generated_carbs = 0
    
    for meal in meals:
        print_subsection(f"Generating {meal['name']}")
        print(f"Target: {meal['calories']}kcal, {meal['protein']}g protein, {meal['fat']}g fat, {meal['carbs']}g carbs")
        
        try:
            # Gọi Groq service
            meal_suggestions = groq_service.generate_meal_suggestions(
                meal_type=meal['name'].lower(),
                calories_target=meal['calories'],
                protein_target=meal['protein'],
                fat_target=meal['fat'],
                carbs_target=meal['carbs'],
                preferences=test_case['preferences'],
                allergies=test_case['allergies'],
                cuisine_style=test_case['cuisine_style']
            )
            
            if meal_suggestions:
                print(f"✅ SUCCESS: Generated {len(meal_suggestions)} dishes")
                
                meal_result = {
                    "meal_type": meal['name'],
                    "target": meal,
                    "dishes": meal_suggestions,
                    "status": "SUCCESS"
                }
                
                # Tính tổng dinh dưỡng thực tế
                actual_calories = sum(dish.get('nutrition', {}).get('calories', 0) for dish in meal_suggestions)
                actual_protein = sum(dish.get('nutrition', {}).get('protein', 0) for dish in meal_suggestions)
                actual_fat = sum(dish.get('nutrition', {}).get('fat', 0) for dish in meal_suggestions)
                actual_carbs = sum(dish.get('nutrition', {}).get('carbs', 0) for dish in meal_suggestions)
                
                meal_result["actual"] = {
                    "calories": actual_calories,
                    "protein": actual_protein,
                    "fat": actual_fat,
                    "carbs": actual_carbs
                }
                
                total_generated_calories += actual_calories
                total_generated_protein += actual_protein
                total_generated_fat += actual_fat
                total_generated_carbs += actual_carbs
                
                print(f"📊 Generated nutrition: {actual_calories}kcal, {actual_protein}g protein, {actual_fat}g fat, {actual_carbs}g carbs")
                
                # In chi tiết dishes
                for i, dish in enumerate(meal_suggestions, 1):
                    print(f"   🍽️ Dish {i}: {dish.get('name', 'Unknown')}")
                    nutrition = dish.get('nutrition', {})
                    print(f"      Nutrition: {nutrition.get('calories', 0)}kcal, {nutrition.get('protein', 0)}g protein")
                    print(f"      Ingredients: {len(dish.get('ingredients', []))} items")
                    print(f"      Prep time: {dish.get('preparation_time', 'N/A')}")
                
            else:
                print(f"❌ FAILED: No meal suggestions generated")
                meal_result = {
                    "meal_type": meal['name'],
                    "target": meal,
                    "dishes": [],
                    "status": "FAILED"
                }
            
            day_results.append(meal_result)
            
        except Exception as e:
            print(f"💥 ERROR: {str(e)}")
            meal_result = {
                "meal_type": meal['name'],
                "target": meal,
                "dishes": [],
                "status": "ERROR",
                "error": str(e)
            }
            day_results.append(meal_result)
    
    # Tóm tắt kết quả ngày
    print_separator("📊 DAY SUMMARY")
    
    successful_meals = len([r for r in day_results if r["status"] == "SUCCESS"])
    total_dishes = sum(len(r["dishes"]) for r in day_results)
    
    print(f"Day: {test_case['day']}")
    print(f"✅ Successful meals: {successful_meals}/3")
    print(f"🍽️ Total dishes generated: {total_dishes}")
    
    print(f"\n📊 Nutrition Comparison:")
    print(f"Target vs Actual:")
    print(f"   Calories: {test_case['total_calories']} → {total_generated_calories} ({total_generated_calories/test_case['total_calories']*100:.1f}%)")
    print(f"   Protein:  {test_case['total_protein']}g → {total_generated_protein}g ({total_generated_protein/test_case['total_protein']*100:.1f}%)")
    print(f"   Fat:      {test_case['total_fat']}g → {total_generated_fat}g ({total_generated_fat/test_case['total_fat']*100:.1f}%)")
    print(f"   Carbs:    {test_case['total_carbs']}g → {total_generated_carbs}g ({total_generated_carbs/test_case['total_carbs']*100:.1f}%)")
    
    # Đánh giá chất lượng
    print(f"\n🎯 Quality Assessment:")
    if successful_meals == 3:
        print("🎉 EXCELLENT: All meals generated successfully!")
    elif successful_meals >= 2:
        print("✅ GOOD: Most meals generated successfully")
    elif successful_meals >= 1:
        print("⚠️ PARTIAL: Some meals generated")
    else:
        print("❌ POOR: No meals generated successfully")
    
    # Đánh giá độ chính xác dinh dưỡng
    nutrition_accuracy = (
        abs(total_generated_calories - test_case['total_calories']) / test_case['total_calories'] * 100
    )
    
    if nutrition_accuracy <= 10:
        print("🎯 EXCELLENT: Nutrition targets very accurate (±10%)")
    elif nutrition_accuracy <= 20:
        print("✅ GOOD: Nutrition targets reasonably accurate (±20%)")
    elif nutrition_accuracy <= 30:
        print("⚠️ FAIR: Nutrition targets somewhat accurate (±30%)")
    else:
        print("❌ POOR: Nutrition targets not accurate (>30% deviation)")
    
    return day_results

def main():
    """Main function"""
    print("🚀 Starting Day Replacement Simulation Test")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run test
        results = test_day_replacement_simulation()
        
        print(f"\n⏰ Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("🎯 Day replacement simulation finished!")
        
        # Save results
        import json
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"day_replacement_test_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Results saved to: {filename}")
        
    except Exception as e:
        print(f"\n💥 Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
