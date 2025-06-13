#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script để kiểm tra 2 cải tiến mới:
1. Health benefits chi tiết hơn
2. Tự động gen thêm món để đủ calories target
"""

import os
import sys
from groq_integration import GroqService

def test_health_benefits_improvement():
    """Test health benefits chi tiết"""
    print("🔍 TESTING DETAILED HEALTH BENEFITS")
    print("=" * 50)
    
    groq_service = GroqService()
    
    # Test với món có ít calories
    print("\n📋 Test 1: Low calorie breakfast (250 cal)")
    results = groq_service.generate_meal_suggestions(
        calories_target=250,
        protein_target=15,
        fat_target=8,
        carbs_target=35,
        meal_type="bữa sáng",
        preferences=["healthy"],
        use_ai=True
    )
    
    if results:
        for meal in results:
            print(f"✅ Dish: {meal.get('name', 'Unknown')}")
            print(f"   Health Benefits: {meal.get('health_benefits', 'None')}")
            print(f"   Length: {len(meal.get('health_benefits', ''))} characters")
    
    print("\n" + "=" * 50)

def test_calories_adequacy():
    """Test tự động bổ sung calories"""
    print("🔍 TESTING CALORIES ADEQUACY")
    print("=" * 50)
    
    groq_service = GroqService()
    
    # Test với target calories cao để xem có gen thêm món không
    print("\n📋 Test 1: High calorie lunch (600 cal)")
    results = groq_service.generate_meal_suggestions(
        calories_target=600,
        protein_target=40,
        fat_target=25,
        carbs_target=70,
        meal_type="bữa trưa",
        preferences=["high-protein"],
        use_ai=True
    )
    
    if results:
        total_calories = 0
        print(f"📊 Generated {len(results)} dishes:")
        for i, meal in enumerate(results, 1):
            calories = meal.get('nutrition', {}).get('calories', 0)
            total_calories += calories
            print(f"   {i}. {meal.get('name', 'Unknown')}: {calories} cal")
        
        print(f"\n📈 Total calories: {total_calories}/600")
        print(f"   Target achievement: {(total_calories/600)*100:.1f}%")
        
        if total_calories >= 540:  # 90% of target
            print("✅ SUCCESS: Adequate calories achieved!")
        else:
            print("⚠️ WARNING: Calories still insufficient")
    
    print("\n" + "=" * 50)

def test_low_calories_scenario():
    """Test scenario calories thấp để trigger bổ sung"""
    print("🔍 TESTING LOW CALORIES SCENARIO")
    print("=" * 50)
    
    groq_service = GroqService()
    
    # Test với target calories rất cao để chắc chắn cần bổ sung
    print("\n📋 Test: Very high calorie dinner (800 cal)")
    results = groq_service.generate_meal_suggestions(
        calories_target=800,
        protein_target=50,
        fat_target=30,
        carbs_target=90,
        meal_type="bữa tối",
        preferences=["high-protein"],
        use_ai=True
    )
    
    if results:
        total_calories = 0
        print(f"📊 Generated {len(results)} dishes:")
        for i, meal in enumerate(results, 1):
            calories = meal.get('nutrition', {}).get('calories', 0)
            total_calories += calories
            name = meal.get('name', 'Unknown')
            
            # Check if this is an additional dish
            is_additional = "bổ sung" in name.lower()
            marker = "🔧" if is_additional else "🍽️"
            
            print(f"   {marker} {i}. {name}: {calories} cal")
            
            if is_additional:
                print(f"      → Additional dish detected!")
        
        print(f"\n📈 Total calories: {total_calories}/800")
        print(f"   Target achievement: {(total_calories/800)*100:.1f}%")
        
        # Check if additional dishes were generated
        additional_dishes = [meal for meal in results if "bổ sung" in meal.get('name', '').lower()]
        if additional_dishes:
            print(f"✅ SUCCESS: {len(additional_dishes)} additional dish(es) generated!")
        else:
            print("ℹ️ INFO: No additional dishes needed")
    
    print("\n" + "=" * 50)

def main():
    """Main test function"""
    print("🧪 TESTING GROQ INTEGRATION IMPROVEMENTS")
    print("=" * 60)
    
    try:
        # Test 1: Health benefits improvement
        test_health_benefits_improvement()
        
        # Test 2: Calories adequacy
        test_calories_adequacy()
        
        # Test 3: Low calories scenario
        test_low_calories_scenario()
        
        print("\n🎉 ALL TESTS COMPLETED!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
